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
import datetime
import json
import typing

import anyio
import pyzabbix

import asus_router_logger.domain as domain
import asus_router_logger.hooks.abc as abc
import asus_router_logger.settings
import asus_router_logger.util.logging as logging


class ZabbixTrapper(abc.Hook):
    def __init__(self):
        super().__init__()
        settings = asus_router_logger.settings.settings()
        zabbix_servers = settings.zabbix_servers
        self._sender = pyzabbix.ZabbixSender(
            zabbix_server=zabbix_servers[0][0], zabbix_port=zabbix_servers[0][1]
        )
        self._known_mac: typing.Dict[
            typing.Tuple[domain.MAC, str], datetime.datetime
        ] = dict()

    async def send(self, record: domain.LogRecord, message: domain.Message) -> None:
        seconds_until_discovered = await self.discover_client(record, message)
        if seconds_until_discovered > 0:
            # Allow the Zabbix server(s) to discover and create prototype items
            await anyio.sleep(seconds_until_discovered)
        measurements = []
        if isinstance(message, domain.WlcEventModel):
            measurements.append(
                pyzabbix.ZabbixMetric(
                    host=record.hostname,
                    key=f"rlp.wlceventd[location,{message.mac_address}]",
                    value=message.location,
                    clock=int(record.timestamp.timestamp()),
                )
            )
            measurements.append(
                pyzabbix.ZabbixMetric(
                    host=record.hostname,
                    key=f"rlp.wlceventd[event,{message.mac_address}]",
                    value=message.event.name,
                    clock=int(record.timestamp.timestamp()),
                )
            )
            measurements.append(
                pyzabbix.ZabbixMetric(
                    host=record.hostname,
                    key=f"rlp.wlceventd[status,{message.mac_address}]",
                    value=str(message.status),
                    clock=int(record.timestamp.timestamp()),
                )
            )
            measurements.append(
                pyzabbix.ZabbixMetric(
                    host=record.hostname,
                    key=f"rlp.wlceventd[rssi,{message.mac_address}]",
                    value=str(message.rssi),
                    clock=int(record.timestamp.timestamp()),
                )
            )
        elif isinstance(message, domain.DnsmasqDhcpAcknowledge):
            measurements.append(
                pyzabbix.ZabbixMetric(
                    host=record.hostname,
                    key=f"rlp.dnsmasq_dhcp[ip_address,{message.mac_address}]",
                    value=str(message.ip_address),
                    clock=int(record.timestamp.timestamp()),
                )
            )
            measurements.append(
                pyzabbix.ZabbixMetric(
                    host=record.hostname,
                    key=f"rlp.dnsmasq_dhcp[hostname,{message.mac_address}]",
                    value=message.hostname,
                    clock=int(record.timestamp.timestamp()),
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

        :param record: The log record containing hostname, process name and timestamp.
        :param message: The message containing the mac address.
        """
        assert record.process is not None
        known_key = (message.mac_address, record.process)
        default_wait_time = 60
        if known_key in self._known_mac:
            # MAC address is already known, so no need to rediscover it,
            # but we might need to wait in the case that the discovery were just sent
            now = datetime.datetime.utcnow()
            discovered_at = self._known_mac[known_key]

            seconds_since_discovery = (now - discovered_at).total_seconds()
            if seconds_since_discovery >= default_wait_time:
                # Discovery were sent some time ago
                return 0
            # Wait until the default wait time have elapsed
            time_left = default_wait_time - seconds_since_discovery
            logging.logger.debug(
                "Another task have issued a discovery event of %s. Waiting %f seconds",
                message.mac_address,
                time_left,
            )
            return time_left
        self._known_mac[known_key] = datetime.datetime.utcnow()

        value = json.dumps([{"mac": str(mac[0])} for mac in self._known_mac])
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
        return default_wait_time
