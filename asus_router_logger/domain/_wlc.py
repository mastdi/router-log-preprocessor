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
import enum

import pydantic.dataclasses

from asus_router_logger.domain._message import Message


class WlcEvent(enum.Enum):
    DISASSOCIATION = 0
    DEAUTH_IND = 1
    AUTH = 2

    @classmethod
    def from_event(cls, event: str) -> "WlcEvent":
        event = event.lstrip().lower()
        if event.startswith("disassoc"):
            return cls.DISASSOCIATION
        if event.startswith("deauth_ind"):
            return cls.DEAUTH_IND
        if event.startswith("auth"):
            return cls.AUTH
        raise ValueError("Unknown event")


@pydantic.dataclasses.dataclass
class WlcEventModel(Message):
    location: str
    event: WlcEvent
    status: int
    rssi: int
    reason: str
