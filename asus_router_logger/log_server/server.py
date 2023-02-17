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
import socket

from anyio import create_udp_socket

import asus_router_logger.log_server.rfc3164_parser
import asus_router_logger.settings
from asus_router_logger.preprocessors.wlc import handle_wireless_lan_controller_event


async def _no_op(
    record: asus_router_logger.log_server.rfc3164_parser.LogRecord,
) -> None:
    return


async def start_log_server() -> None:
    """Start the log server."""
    settings = asus_router_logger.settings.settings()
    echo_logger = logging.getLogger(f"{settings.logging_name_base}.echo")
    preprocessors = {"wlceventd": handle_wireless_lan_controller_event}
    async with await create_udp_socket(
        family=socket.AF_INET,
        local_host=settings.log_server_host,
        local_port=settings.log_server_port,
        reuse_port=settings.log_server_reuse_port,
    ) as udp:
        async for packet, (host, port) in udp:
            # The packet is a single log entry encoded in ascii according to RFC3164
            raw_record = packet.decode("ascii")
            echo_logger.debug(raw_record)
            # Parse the log record
            record = asus_router_logger.log_server.rfc3164_parser.parse(raw_record)
            # Pre-process the record
            if record.process is None:
                continue
            preprocessor = preprocessors.get(record.process, _no_op)
            model = preprocessor(record)
            # Store the model to storage
            if model is None:
                # Nothing further to process here
                continue
            # Act if needed
            print(host, port, model)
