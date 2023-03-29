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
import unittest.mock

import pytest

import asus_router_logger.settings
import tests.mocks.anyio
from asus_router_logger.log_server.server import start_log_server


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_server():
    settings = asus_router_logger.settings.settings()
    (
        mock_udp_socket,
        mock_create_udp_socket,
    ) = tests.mocks.anyio.mock_create_udp_socket_factory(
        [
            (b"first", ("localhost", 514)),
            (b"second", ("127.0.0.1", 8514)),
        ]
    )
    (
        mock_task_group,
        mock_task_group_context,
    ) = tests.mocks.anyio.mock_create_task_group_factory()

    with unittest.mock.patch(
        "asus_router_logger.log_server.server.create_udp_socket", mock_create_udp_socket
    ):
        with unittest.mock.patch(
            "asus_router_logger.log_server.server.create_task_group",
            mock_task_group_context,
        ):

            await start_log_server()

        # The most important part of the server is that the log handler is called for
        # every packet received by the bound UDP socket.

        # First check the UDP socket is bound according to the settings
        assert mock_udp_socket.local_host == settings.log_server_host
        assert mock_udp_socket.local_port == settings.log_server_port
        assert mock_udp_socket.reuse_port == settings.log_server_reuse_port

        # Then check that it sends the packets to the log handler
        assert isinstance(mock_task_group.start_soon, unittest.mock.MagicMock)
        assert mock_task_group.start_soon.call_count == 2
        assert callable(mock_task_group.start_soon.call_args_list[0].args[0])
        assert mock_task_group.start_soon.call_args_list[0].args[1] == b"first"
        assert mock_task_group.start_soon.call_args_list[0].args[2] == "localhost"
        assert mock_task_group.start_soon.call_args_list[0].args[3] == 514
        assert callable(mock_task_group.start_soon.call_args_list[1].args[0])
        assert mock_task_group.start_soon.call_args_list[1].args[1] == b"second"
        assert mock_task_group.start_soon.call_args_list[1].args[2] == "127.0.0.1"
        assert mock_task_group.start_soon.call_args_list[1].args[3] == 8514
