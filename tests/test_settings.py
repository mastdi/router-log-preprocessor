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
import asus_router_logger.settings


def test_zabbix_servers_property():
    settings = asus_router_logger.settings.Settings(
        zabbix_addresses="localhost:8010,example.org"
    )

    servers = settings.zabbix_servers

    assert len(servers) == 2
    assert servers[0] == ("localhost", 8010)
    assert servers[1] == ("example.org", 10051)
