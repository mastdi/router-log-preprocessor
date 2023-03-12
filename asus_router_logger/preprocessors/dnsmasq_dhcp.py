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
import asus_router_logger.util.logging as logging


def preprocess_dnsmasq_dhcp_event(
    record: domain.LogRecord,
) -> typing.Optional[domain.DnsmasqDhcpAcknowledge]:
    logging.logger.debug("Received dnsmasq-dhcp event log: %r", record)

    if not record.message.startswith("DHCPACK"):
        return None
    dhcp_acknowledge_parts = record.message.split()
    ip_address = dhcp_acknowledge_parts[1]
    mac_address = dhcp_acknowledge_parts[2]
    hostname = ""
    if len(dhcp_acknowledge_parts) == 4:
        # Hostname is not always present in DHCPACK message
        hostname = dhcp_acknowledge_parts[3]

    return domain.DnsmasqDhcpAcknowledge(
        mac_address=domain.MAC(mac_address),
        ip_address=ip_address,  # type: ignore
        hostname=hostname,
    )
