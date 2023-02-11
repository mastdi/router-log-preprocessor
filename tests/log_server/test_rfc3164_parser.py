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

import pytest

import asus_router_logger.log_server.rfc3164_parser

_NOW = datetime.datetime.now().replace(microsecond=0)


@pytest.mark.parametrize(
    "arguments,expected",
    [
        (
            ["Jan", "27", "01", "12", "01"],
            _NOW.replace(month=1, day=27, hour=1, minute=12, second=1),
        ),
        (
            ["Feb", "14", "22", "22", "22"],
            _NOW.replace(month=2, day=14, hour=22, minute=22, second=22),
        ),
        (
            ["Mar", "11", "06", "00", "00"],
            _NOW.replace(month=3, day=11, hour=6, minute=0, second=0),
        ),
        (
            ["Apr", "9", "00", "00", "00"],
            _NOW.replace(month=4, day=9, hour=0, minute=0, second=0),
        ),
        (
            ["May", "5", "05", "25", "13"],
            _NOW.replace(month=5, day=5, hour=5, minute=25, second=13),
        ),
        (
            ["Jun", "30", "12", "12", "12"],
            _NOW.replace(month=6, day=30, hour=12, minute=12, second=12),
        ),
        (
            ["Jul", "4", "23", "59", "59"],
            _NOW.replace(month=7, day=4, hour=23, minute=59, second=59),
        ),
        (
            ["Aug", "5", "17", "21", "51"],
            _NOW.replace(month=8, day=5, hour=17, minute=21, second=51),
        ),
        (
            ["Sep", "19", "10", "10", "10"],
            _NOW.replace(month=9, day=19, hour=10, minute=10, second=10),
        ),
        (
            ["Oct", "1", "12", "00", "00"],
            _NOW.replace(month=10, day=1, hour=12, minute=0, second=0),
        ),
        (
            ["Nov", "15", "02", "51", "19"],
            _NOW.replace(month=11, day=15, hour=2, minute=51, second=19),
        ),
        (
            ["Dec", "24", "18", "01", "37"],
            _NOW.replace(month=12, day=24, hour=18, minute=1, second=37),
        ),
    ],
)
def test_timestamp_to_datetime(arguments, expected):
    timestamp = asus_router_logger.log_server.rfc3164_parser.timestamp_to_datetime(
        *arguments
    )

    assert timestamp == expected


_MSG1 = (
    "<13>Feb  2 13:02:51 GT-AX11000-ABCD-1234567-E wlceventd: "
    "wlceventd_proc_event(511): eth7: Disassoc AB:CD:EF:01:23:45, status: 0, "
    "reason: Disassociated because sending station is leaving (or has left) "
    "BSS (8), rssi:0"
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
_MSG2 = (
    "<30>Feb 12 13:02:57 GT-AX11000-ABCD-1234567-E dnsmasq-dhcp[23568]: "
    "DHCPDISCOVER(br0) ab:cd:ef:01:23:45"
)
_RECORD2 = asus_router_logger.log_server.rfc3164_parser.LogRecord(
    facility=3,
    severity=6,
    timestamp=asus_router_logger.log_server.rfc3164_parser.timestamp_to_datetime(
        "Feb", "12", "13", "02", "57"
    ),
    hostname="GT-AX11000-ABCD-1234567-E",
    process="dnsmasq-dhcp",
    process_id=23568,
    message="DHCPDISCOVER(br0) ab:cd:ef:01:23:45",
)


@pytest.mark.parametrize(
    "message,expected_record", [(_MSG1, _RECORD1), [_MSG2, _RECORD2]]
)
def test_parse(message, expected_record):
    record = asus_router_logger.log_server.rfc3164_parser.parse(message)

    assert record == expected_record
