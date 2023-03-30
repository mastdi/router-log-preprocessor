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
import collections
import datetime
import typing

import router_log_preprocessor.domain as domain


class KnownClients:
    def __init__(self, client_discovery_wait_time: float) -> None:
        self._total_wait_time = client_discovery_wait_time
        self._known_clients: typing.DefaultDict[
            str, typing.Dict[domain.MAC, datetime.datetime]
        ] = collections.defaultdict(dict)

    @staticmethod
    def _now() -> datetime.datetime:
        return datetime.datetime.utcnow()

    def add_client(self, process: str, mac_address: domain.MAC) -> None:
        """Add a client to the repository marking the date and time of the addition.

        :param process: The process of the log entry.
        :param mac_address: The mac address of the client.
        """
        self._known_clients[process][mac_address] = KnownClients._now()

    def is_client_known(self, process: str, mac_address: domain.MAC) -> bool:
        """Verify if a client (mac address) is known for a given process.

        :param process: The process of the log entry.
        :param mac_address: The mac address of the client.
        :return: True if the client is already known and False otherwise.
        """
        return mac_address in self._known_clients[process]

    def remaining_wait_time(self, process: str, mac_address: domain.MAC) -> float:
        """Calculate the remaining wait time before a client is assumed to be
        discovered by Zabbix.

        :param process: The process of the log entry.
        :param mac_address: The mac address of the client.
        :return: The remaining wait time. 0 if the client can be assumed to be
                 discovered.
        """
        now = KnownClients._now()
        known_at = self._known_clients[process][mac_address]
        known_for = (now - known_at).total_seconds()
        remaining_wait_time = self._total_wait_time - known_for
        if remaining_wait_time < 0:
            return 0.0
        return remaining_wait_time

    def clients(self, process: str) -> typing.Generator[domain.MAC, None, None]:
        """Generate a list of clients known for the given process.

        :param process: The process of the log entry.
        """
        for key in self._known_clients[process]:
            yield key
