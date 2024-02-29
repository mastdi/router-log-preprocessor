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
import typing_extensions

import pydantic.dataclasses
from macaddress import EUI48


class MAC(EUI48):
    """Implementation of EUI48 which contains validators used by pydantic."""


def validate_mac(value: typing.Union[MAC, str]) -> MAC:
    if isinstance(value, MAC):
        return value
    try:
        return MAC(value)
    except Exception as exception:
        raise ValueError("Invalid MAC address") from exception


@pydantic.dataclasses.dataclass
class Message:
    mac_address: typing_extensions.Annotated[MAC, pydantic.PlainValidator(validate_mac)]
