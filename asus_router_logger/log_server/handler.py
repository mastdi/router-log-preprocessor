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
import logging

import asus_router_logger.preprocessors.wlc as wlc_preprocessor
import asus_router_logger.settings
import asus_router_logger.util.rfc3164_parser


class LogHandler:
    def __init__(self):
        settings = asus_router_logger.settings.settings()
        self.logger = logging.getLogger(f"{settings.logging_name_base}")
        self.echo_logger = logging.getLogger(f"{settings.logging_name_base}.echo")
        self.logger.info("Log handler is ready")

    async def handle(self, packet: bytes, host: str, port: int) -> None:
        # The packet is a single log entry encoded in ascii according to RFC3164
        entry = packet.decode("ascii")
        self.echo_logger.debug("%s %d: %s", host, port, entry)

        # Parse the log record
        record = asus_router_logger.util.rfc3164_parser.parse(entry)

        # Pre-process the record
        if record.process == "wlceventd":
            model = wlc_preprocessor.preprocess_wireless_lan_controller_event(record)
        else:
            # Only preprocessors for logs with a named process is supported
            return

        # Act if needed
        print(host, port, model)
