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

import asus_router_logger.domain as domain
import asus_router_logger.hooks.zabbix._known_clients as known_clients


def test_is_client_known():
    process = "wlceventd"
    mac_address = domain.MAC("AB:CD:EF:01:23:45")
    repository = known_clients.KnownClients(42)
    repository.add_client(process, mac_address)

    is_known = repository.is_client_known(process, mac_address)

    assert is_known


def test_is_client_not_known():
    process = "wlceventd"
    mac_address = domain.MAC("AB:CD:EF:01:23:45")
    repository = known_clients.KnownClients(42)

    is_known = repository.is_client_known(process, mac_address)

    assert not is_known


def test_remaining_wait_time_new_client():
    process = "wlceventd"
    mac_address = domain.MAC("AB:CD:EF:01:23:45")
    repository = known_clients.KnownClients(42)
    repository.add_client(process, mac_address)

    remaining_wait_time = repository.remaining_wait_time(process, mac_address)

    assert 42 == pytest.approx(remaining_wait_time, 0.1)


def test_remaining_wait_time_known_client():
    added_at = datetime.datetime.utcnow()
    checked_at = added_at + datetime.timedelta(seconds=10)
    process = "wlceventd"
    mac_address = domain.MAC("AB:CD:EF:01:23:45")
    repository = known_clients.KnownClients(42)
    known_clients.KnownClients._now = lambda: added_at
    repository.add_client(process, mac_address)
    known_clients.KnownClients._now = lambda: checked_at

    remaining_wait_time = repository.remaining_wait_time(process, mac_address)

    assert 32 == pytest.approx(remaining_wait_time, 0.1)


def test_clients():
    process = "wlceventd"
    expected_clients = {
        domain.MAC("AB:CD:EF:01:23:45"),
        domain.MAC("01:23:45:67:89:AB"),
    }
    non_expected = domain.MAC("FE:CD:BA:98:76:54")
    repository = known_clients.KnownClients(42)
    repository.add_client("dnsmasq-dhcp", non_expected)
    for client in expected_clients:
        repository.add_client(process, client)

    clients = {client for client in repository.clients(process)}

    assert expected_clients == clients
