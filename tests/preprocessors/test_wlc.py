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
import pytest

import asus_router_logger.domain as domain
import asus_router_logger.util.rfc3164_parser
from asus_router_logger.preprocessors.wlc import (
    preprocess_wireless_lan_controller_event,
)


def _log_record_factory(message: str) -> asus_router_logger.domain.LogRecord:
    return asus_router_logger.domain.LogRecord(
        facility=1,
        severity=5,
        timestamp=asus_router_logger.util.rfc3164_parser.timestamp_to_datetime(
            "Feb", "2", "13", "02", "51"
        ),
        hostname="GT-AX11000-ABCD-1234567-E",
        process="wlceventd",
        process_id=None,
        message=message,
    )


@pytest.mark.parametrize(
    argnames="message,expected_wlc_event,expected_rssi",
    argvalues=[
        (
            "wlceventd_proc_event(511): wl0.1: Disassoc AB:CD:EF:01:23:45, status: 0, "
            "reason: Disassociated because sending station is leaving (or has left) "
            "BSS (8), rssi:0",
            domain.WlcEvent.DISASSOCIATION,
            0,
        ),
        (
            "wlceventd_proc_event(494): wl0.1: Deauth_ind AB:CD:EF:01:23:45, "
            "status: 0, reason: Unspecified reason (1), rssi:0",
            domain.WlcEvent.DEAUTH_IND,
            0,
        ),
        (
            "wlceventd_proc_event(530): wl0.1: Auth AB:CD:EF:01:23:45, "
            "status: Successful (0), rssi:0",
            domain.WlcEvent.AUTHENTICATE,
            0,
        ),
        (
            "wlceventd_proc_event(559): wl0.1: Assoc AB:CD:EF:01:23:45, "
            "status: Successful (0), rssi:-74",
            domain.WlcEvent.ASSOCIATION,
            -74,
        ),
        (
            "wlceventd_proc_event(540): wl0.1: ReAssoc AB:CD:EF:01:23:45, "
            "status: Successful (0), rssi:-70",
            domain.WlcEvent.REASSOCIATION,
            -70,
        ),
    ],
)
def test_disassociated_message(
    message: str, expected_wlc_event: domain.WlcEvent, expected_rssi: int
):
    record = _log_record_factory(message)

    model = preprocess_wireless_lan_controller_event(record)

    assert model.location == "wl0.1"
    assert model.mac_address == domain.MAC("AB:CD:EF:01:23:45")
    assert model.status == 0
    assert model.event == expected_wlc_event
    assert model.rssi == expected_rssi
