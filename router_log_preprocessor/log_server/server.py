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
import asyncio_zabbix_sender
from anyio import create_task_group, create_udp_socket

import router_log_preprocessor.hooks.zabbix
import router_log_preprocessor.log_server.handler
import router_log_preprocessor.preprocessors.dnsmasq_dhcp as preprocessors_dnsmasq_dhcp
import router_log_preprocessor.preprocessors.wlc as preprocessors_wlc
import router_log_preprocessor.settings
import router_log_preprocessor.util.logging as logging
import router_log_preprocessor.util.rfc3164_parser


def log_handler_factory() -> router_log_preprocessor.log_server.handler.LogHandler:
    """Create the log handler used for preprocessing and sending measurements to hooks.

    :return: Instantiated log handler.
    """
    # Set up preprocessors
    preprocessors = {
        "wlceventd": preprocessors_wlc.preprocess_wireless_lan_controller_event,
        "dnsmasq-dhcp": preprocessors_dnsmasq_dhcp.preprocess_dnsmasq_dhcp_event,
    }
    # Set up hooks
    settings = router_log_preprocessor.settings.settings()

    sender = asyncio_zabbix_sender.ZabbixSender(
        zabbix_host=settings.zabbix_host, zabbix_port=settings.zabbix_port
    )
    zabbix_trapper = router_log_preprocessor.hooks.zabbix.ZabbixTrapper(sender)
    hooks = [zabbix_trapper]

    return router_log_preprocessor.log_server.handler.LogHandler(preprocessors, hooks)


async def start_log_server() -> None:
    """Start the log server."""

    log_handler = log_handler_factory()

    settings = router_log_preprocessor.settings.settings()
    async with await create_udp_socket(
        local_host=settings.log_server_host,
        local_port=settings.log_server_port,
        reuse_port=settings.log_server_reuse_port,
    ) as udp:
        logging.logger.info(
            "Listen for logs on UDP %s:%d - Reuse port: %r",
            settings.log_server_host,
            settings.log_server_port,
            settings.log_server_reuse_port,
        )
        async with create_task_group() as task_group:
            async for packet, (host, port) in udp:
                task_group.start_soon(log_handler.handle, packet, host, port)
