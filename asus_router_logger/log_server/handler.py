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

import asus_router_logger.domain as domain
import asus_router_logger.hooks.zabbix
import asus_router_logger.preprocessors.typing as preprocessors_typing
import asus_router_logger.settings
import asus_router_logger.util.logging as logging
import asus_router_logger.util.rfc3164_parser


class LogHandler:
    def __init__(
        self,
        preprocessors: typing.Mapping[str, preprocessors_typing.Preprocessor],
        zabbix_trapper: asus_router_logger.hooks.zabbix.ZabbixTrapper,
    ):
        self.zabbix_trapper = zabbix_trapper
        self._preprocessors = preprocessors
        logging.logger.info("Log handler is ready")

    async def handle(self, packet: bytes, host: str, port: int) -> None:
        # The packet is a single log entry encoded in ascii according to RFC3164
        entry = packet.decode("ascii")
        logging.echo_logger.debug(entry.strip())

        # Parse the log record
        record = asus_router_logger.util.rfc3164_parser.parse(entry)

        # Pre-process the record
        preprocessor: typing.Optional[preprocessors_typing.Preprocessor] = None
        message: typing.Optional[domain.Message] = None
        if record.process is not None:
            preprocessor = self._preprocessors.get(record.process)
        if preprocessor is not None:
            message = preprocessor(record)

        # Act
        await self.zabbix_trapper.send(record, message)
