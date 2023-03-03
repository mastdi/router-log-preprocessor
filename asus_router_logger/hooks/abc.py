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
import abc

import asus_router_logger.domain as domain


class Hook(abc.ABC):
    async def send(self, record: domain.LogRecord, message: domain.Message) -> None:
        """Send the log record and preprocessed message using the hook.

        :param record: The parsed log record.
        :param message: The preprocessed log message.
        """
        raise NotImplementedError()
