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

import asus_router_logger.settings
from asus_router_logger.log_server.rfc3164_parser import LogRecord


async def handle_wireless_lan_controller_event(record: LogRecord) -> None:
    settings = asus_router_logger.settings.settings()
    logger = logging.getLogger(settings.logging_name_base)
    logger.debug("Received WLC event daemon log: %r", record)

    assert record.process == "wlceventd"
