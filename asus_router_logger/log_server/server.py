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
import socket

import pyzabbix
from anyio import create_task_group, create_udp_socket

import asus_router_logger.hooks.zabbix
import asus_router_logger.log_server.handler
import asus_router_logger.settings
import asus_router_logger.util.logging as logging
import asus_router_logger.util.rfc3164_parser


def log_handler_factory() -> asus_router_logger.log_server.handler.LogHandler:
    """Create the log handler used for preprocessing and sending measurements to hooks.

    :return: Instantiated log handler.
    """
    settings = asus_router_logger.settings.settings()
    zabbix_servers = settings.zabbix_servers
    sender = pyzabbix.ZabbixSender(
        zabbix_server=zabbix_servers[0][0], zabbix_port=zabbix_servers[0][1]
    )
    zabbix_trapper = asus_router_logger.hooks.zabbix.ZabbixTrapper(sender)
    return asus_router_logger.log_server.handler.LogHandler(zabbix_trapper)


async def start_log_server() -> None:
    """Start the log server."""

    log_handler = log_handler_factory()

    settings = asus_router_logger.settings.settings()
    async with await create_udp_socket(
        family=socket.AF_INET,
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
