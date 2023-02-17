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
import asus_router_logger.log_server.rfc3164_parser
from asus_router_logger.domain.mac_base import MAC
from asus_router_logger.domain.wlc import WlcEvent
from asus_router_logger.preprocessors.wlc import (
    preprocess_wireless_lan_controller_event,
)

_RECORD1 = asus_router_logger.log_server.rfc3164_parser.LogRecord(
    facility=1,
    severity=5,
    timestamp=asus_router_logger.log_server.rfc3164_parser.timestamp_to_datetime(
        "Feb", "2", "13", "02", "51"
    ),
    hostname="GT-AX11000-ABCD-1234567-E",
    process="wlceventd",
    process_id=None,
    message="wlceventd_proc_event(511): eth7: Disassoc AB:CD:EF:01:23:45, status: 0, "
    "reason: Disassociated because sending station is leaving (or has left) "
    "BSS (8), rssi:0",
)


def test_disassociated_message():
    model = preprocess_wireless_lan_controller_event(_RECORD1)

    assert model.location == "eth7"
    assert model.mac_address == MAC("AB:CD:EF:01:23:45")
    assert model.status == 0
    assert model.event == WlcEvent.DISASSOCIATION
    assert model.rssi == 0
