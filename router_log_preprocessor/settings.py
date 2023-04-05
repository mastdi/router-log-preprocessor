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
import pathlib
from functools import lru_cache
from typing import List, Tuple, Union

import pydantic
from pydantic import BaseSettings, Field, IPvAnyAddress


class Settings(BaseSettings):
    """Define the settings of the application."""

    log_server_host: Union[IPvAnyAddress, str] = Field(
        default="0.0.0.0",
        description="IP address or host name of the local interface to bind to.",
    )
    log_server_port: int = Field(default=8514, description="Local port to bind to.")
    log_server_reuse_port: bool = Field(
        default=False,
        description="True to allow multiple sockets to bind to the same address/port "
        "(not supported on Windows)",
    )
    logging_name_base: str = Field(
        default="rlp",
        description="The base name of the logger used internally. "
        "<logging_name_base>.echo is used to log the logs received.",
    )
    logging_level: str = Field(
        default="INFO", description="The log level used by this application."
    )
    logging_directory: pydantic.DirectoryPath = Field(
        default=pathlib.Path.cwd(),
        description="The base directory where logs from this application resides.",
    )
    zabbix_host: str = Field(
        default="",
        description="A IP address or DNS name of the Zabbix instance.",
    )
    zabbix_port: int = Field(
        default=10051,
        description="The port used in the Zabbix instance.",
    )

    class Config:
        env_file = '.env', '.env.dev', '.env.test', '.env.staging', '.env.prod'
        env_file_encoding = 'utf-8'


@lru_cache
def settings() -> Settings:
    """Get the settings of the applications.
    :return:
    """
    return Settings()
