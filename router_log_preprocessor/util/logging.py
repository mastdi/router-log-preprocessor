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
import logging

import router_log_preprocessor.settings

__all__ = ["echo_logger", "logger"]


def echo_logger_factory() -> logging.Logger:
    settings = router_log_preprocessor.settings.settings()
    # Only log the actual message
    formatter = logging.Formatter(fmt="%(message)s")

    # Setup a file handler to log in desired directory
    handler = logging.FileHandler(
        filename=settings.logging_directory / f"{settings.logging_name_base}.echo.log"
    )
    handler.setFormatter(formatter)

    # Configure the logger
    base_logger = logging.getLogger(f"{settings.logging_name_base}.echo")
    base_logger.addHandler(handler)
    base_logger.setLevel(logging.DEBUG)

    return base_logger


def logger_factory() -> logging.Logger:
    settings = router_log_preprocessor.settings.settings()
    # Add metadata to the log message
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Setup a file handler to log in desired directory
    handler = logging.FileHandler(
        filename=settings.logging_directory / f"{settings.logging_name_base}.app.log"
    )
    handler.setFormatter(formatter)

    # Configure the logger
    base_logger = logging.getLogger(f"{settings.logging_name_base}.app")
    base_logger.addHandler(handler)
    base_logger.setLevel(settings.logging_level)

    return base_logger


logger = logger_factory()
echo_logger = echo_logger_factory()
