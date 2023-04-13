#  Copyright (c) 2023. Martin Storgaard Dieu <martin@storgaarddieu.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import typing

import anyio
import asyncio_zabbix_sender

import router_log_preprocessor.domain as domain
import router_log_preprocessor.hooks.abc as abc
import router_log_preprocessor.hooks.zabbix._known_clients as known_clients
import router_log_preprocessor.hooks.zabbix._mapper as mapper
import router_log_preprocessor.util.logging as logging


class ZabbixTrapper(abc.Hook):
    def __init__(
        self, sender, client_discovery_wait_time=50, measurement_bundle_wait_time=10
    ):
        super().__init__()
        self._sender = sender
        self._client_discovery_wait_time = client_discovery_wait_time
        self._known_clients = known_clients.KnownClients(client_discovery_wait_time)
        self._measurement_bundle_wait_time = measurement_bundle_wait_time
        self._is_bundling_measurements = False
        self._measurements = asyncio_zabbix_sender.Measurements()

    async def send(
        self, record: domain.LogRecord, message: typing.Optional[domain.Message]
    ) -> None:
        """Send the preprocessed message to the corresponding Zabbix Trapper item(s).

        For client messages a low-level discovery will be sent first and the
        corresponding Zabbix Trapper item(s) will be delayed until Zabbix have been
        given time to synchronize caches.

        If the message is None, then this method returns immediately.

        :param record: The log record containing hostname, process name and timestamp.
        :param message: The message containing the mac address.
        """
        if message is None:
            return
        seconds_until_discovered = await self.discover_client(record, message)
        if seconds_until_discovered > 0:
            # Allow the Zabbix server(s) to discover and create prototype items
            logging.logger.debug(
                "Pending discovery event of %s on %s. Waiting %f seconds",
                message.mac_address,
                record.process,
                seconds_until_discovered,
            )
            await anyio.sleep(seconds_until_discovered)

        for measurement in mapper.map_client_message(record, message):
            self._measurements.add_measurement(measurement)

        if self._is_bundling_measurements:
            # This process is done and have handed over the responsibility to send the
            # measurements to another process
            return

        # Allow other processes to add measurements while this process sleeps
        self._is_bundling_measurements = True
        await anyio.sleep(self._measurement_bundle_wait_time)

        # Get the measurements and prepare an empty measurement container
        # Once control is handed back to this process we have control of the
        # measurements until the next await statement
        self._is_bundling_measurements = False
        measurements = self._measurements
        self._measurements = asyncio_zabbix_sender.Measurements()

        logging.logger.info("Sending data: %r", measurements)
        response = await self._sender.send(measurements)
        logging.logger.info("Response: %r", response)

    async def discover_client(
        self, record: domain.LogRecord, message: domain.Message
    ) -> float:
        """Discover a new client based on the mac address in the message.

        There are three cases of client discovery:
        1) The client have not been discovered before
        2) The client have recently been discovered
        3) The client have been discovered for a long time

        A discovery packet will only be sent to Zabbix in the first case and the callee
        will be instructed to wait for the full default_wait_time period before sending
        the actual data to Zabbix. This ensures that the Zabbix Trapper process is aware
        of the (newly created) item prototype(s).

        If a client have recently been discovered the callee will be instructed to wait
        the remaining time of the default_wait_time before sending the actual data to
        Zabbix.

        For the last case the callee will be instructed to wait 0 seconds, i.e. they can
        send the data to Zabbix immediately.

        :param record: The log record containing hostname, process name and timestamp.
        :param message: The message containing the mac address.
        """
        assert record.process is not None
        if self._known_clients.is_client_known(record.process, message.mac_address):
            # MAC address is already known, so no need to rediscover it,
            # but we might need to wait in the case that the discovery were just sent
            return self._known_clients.remaining_wait_time(
                record.process, message.mac_address
            )
        # Mark client as known
        self._known_clients.add_client(record.process, message.mac_address)

        measurements = mapper.map_client_discovery(record, self._known_clients)

        logging.logger.info("Discovering: %r", measurements)
        response = await self._sender.send(measurements)
        logging.logger.info("Response: %r", response)
        assert response.processed == 1, response
        return self._client_discovery_wait_time
