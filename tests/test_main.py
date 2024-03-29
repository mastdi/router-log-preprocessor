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

import router_log_preprocessor.__main__
import router_log_preprocessor.log_server.server


def test_main():
    with unittest.mock.patch("anyio.run", unittest.mock.MagicMock()) as runner:
        router_log_preprocessor.__main__.main()

    # Test that the main method starts the log server
    runner.assert_called_with(
        router_log_preprocessor.log_server.server.start_log_server
    )
