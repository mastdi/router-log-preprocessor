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
import dataclasses
import enum
import json

import anyio
import pyzabbix

import asus_router_logger.domain as domain
import asus_router_logger.hooks.abc as abc
import asus_router_logger.hooks.zabbix._known_clients as known_clients
import asus_router_logger.util.logging as logging


class ZabbixTrapper(abc.Hook):
    def __init__(self, sender, default_wait_time=60):
        super().__init__()
        self._sender = sender
        self._wait_time = default_wait_time
        self._known_clients = known_clients.KnownClients(default_wait_time)

    async def send(self, record: domain.LogRecord, message: domain.Message) -> None:
        seconds_until_discovered = await self.discover_client(record, message)
        if seconds_until_discovered > 0:
            # Allow the Zabbix server(s) to discover and create prototype items
            await anyio.sleep(seconds_until_discovered)
        assert record.process is not None
        # Ensure process is formatted according to Zabbix recommendations
        process = record.process.lower().replace("-", "_")
        # Convert record datetime to timestamp in full seconds
        clock = int(record.timestamp.timestamp())

        # Construct the measurements from the model
        measurements = []
        model_fields = dataclasses.fields(message)  # type: ignore
        for field in model_fields:
            if field.name == "mac_address":
                continue
            value = getattr(message, field.name)
            if isinstance(value, enum.Enum):
                value = value.value
            measurements.append(
                pyzabbix.ZabbixMetric(
                    host=record.hostname,
                    key=f"rlp.{process}[{field.name},{message.mac_address}]",
                    value=value,
                    clock=clock,
                )
            )
        # py-zabbix does not support async communication, so for now we utilize anyio
        # to overcome this.
        logging.logger.info("Sending data: %r", measurements)
        response = await anyio.to_thread.run_sync(self._sender.send, measurements)
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
            remaining_wait_time = self._known_clients.remaining_wait_time(
                record.process, message.mac_address
            )
            logging.logger.debug(
                "Another task have issued a discovery event of %s. Waiting %f seconds",
                message.mac_address,
                remaining_wait_time,
            )
            return remaining_wait_time
        # Mark client as known
        self._known_clients.add_client(record.process, message.mac_address)

        value = json.dumps(
            [{"mac": str(mac)} for mac in self._known_clients.clients(record.process)]
        )
        metric = pyzabbix.ZabbixMetric(
            host=record.hostname,
            key=f"rlp.client_discovery[{record.process.lower()}]",
            value=value,
            clock=int(record.timestamp.timestamp()),
        )
        # py-zabbix does not support async communication, so for now we utilize anyio
        # to overcome this.
        logging.logger.info("Discovering: %r", metric)
        response = await anyio.to_thread.run_sync(self._sender.send, [metric])
        logging.logger.info("Response: %r", response)
        assert response.processed == 1, response
        return self._wait_time
