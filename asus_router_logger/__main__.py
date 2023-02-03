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
import anyio

import asus_router_logger.log_server.server
import asus_router_logger.settings


async def runner() -> None:
    async with anyio.create_task_group() as task_group:
        task_group.start_soon(asus_router_logger.log_server.server.start_log_server)


def main() -> None:
    """Main entry point of the Asus Router Logger (ARL)"""
    anyio.run(runner)
