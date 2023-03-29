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
import contextlib
import socket
import typing
import unittest.mock

import anyio.abc
from anyio._core._sockets import AnyIPAddressFamily
from anyio.abc._streams import T_Item


class MockUdpSocket(anyio.abc.UDPSocket):
    def __init__(self, data):
        self._data = iter(data)
        self.family = None
        self.local_host = None
        self.local_port = None
        self.reuse_port = None

    async def receive(self) -> T_Item:
        try:
            return next(self._data)
        except StopIteration as stop:
            raise StopAsyncIteration from stop

    async def send(self, item: T_Item) -> None:
        raise NotImplementedError("Cannot send data")

    async def aclose(self) -> None:
        pass

    @property
    def _raw_socket(self) -> socket.socket:
        raise NotImplementedError("No access to raw socket")


def mock_create_udp_socket_factory(data):
    """Creates a mock of create_udp_socket that returns a mocked UDPSocket that will
    iterate the provided data given.

    :param data: On the format [(b"packet", (ipaddress, port))]
    :return: A mock of create_udp_socket method
    """
    mock_socket = MockUdpSocket(data)

    async def wrapper(
        family: AnyIPAddressFamily = socket.AddressFamily.AF_UNSPEC,
        *,
        local_host: typing.Optional[anyio.abc.IPAddressType] = None,
        local_port: int = 0,
        reuse_port: bool = False,
    ) -> anyio.abc.UDPSocket:
        mock_socket.family = family
        mock_socket.local_host = local_host
        mock_socket.local_port = local_port
        mock_socket.reuse_port = reuse_port
        return typing.cast(anyio.abc.UDPSocket, mock_socket)

    return mock_socket, wrapper


def mock_create_task_group_factory():
    """Creates a mock of create_task_group where the mock is returned"""
    mock = unittest.mock.MagicMock()
    mock.start_soon = unittest.mock.MagicMock()

    @contextlib.asynccontextmanager
    async def mock_create_task_group():
        yield mock

    return mock, mock_create_task_group
