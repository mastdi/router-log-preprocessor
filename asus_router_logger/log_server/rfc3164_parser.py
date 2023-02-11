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
import dataclasses
import datetime
import re
from typing import Optional

_RFC3164_PATTERN = re.compile(
    # Start of log
    r"^"
    # Pri
    r"<(\d+)>"
    # Timestamp
    r"([a-zA-Z]{3})\s{1,2}(\d{1,2})\s(\d\d):(\d\d):(\d\d)\s"
    # Hostname
    r"(\S+)\s"
    # Optional process information
    r"(\S+?)(?:\[([0-9]+)])?:\s"
    # Message
    r"(.*)"
    # End of log
    r"$"
)

_MONTH = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


@dataclasses.dataclass
class LogRecord:
    """The parsed log record with information contained in an RFC 3164 log line"""

    facility: int
    severity: int
    timestamp: datetime.datetime
    hostname: str
    process: Optional[str]
    process_id: Optional[int]
    message: str


def timestamp_to_datetime(
    month: str, day: str, hour: str, minute: str, second: str
) -> datetime.datetime:
    """The TIMESTAMP field is the local time.

    It is assumed that the log entry timestamp is within the same timezone as this
    instance and that the log entry is from the current year.

    :param month: The English language abbreviation for the month of the year with the
                  first character in uppercase and the other two characters in
                  lowercase.
    :param day: The day of the month
    :param hour: The hour is represented in a 24-hour format in local time. Valid
                 entries are between 00 and 23, inclusive.
    :param minute: The minute entry is between 00 and 59 inclusive in local time.
    :param second: The second entry is between 00 and 59 inclusive in local time.
    :return: The date and time of the timestamp.
    """
    now = datetime.datetime.now()
    return now.replace(
        month=_MONTH[month],
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        second=int(second),
        microsecond=0,
    )


def parse(record: str) -> LogRecord:
    """Parse the raw log record according to The BSD syslog Protocol (RFC 3164).

    The message part has two fields known as the TAG field and the CONTENT field. The
    value in the TAG field will be the name of the program or process that generated
    the message. The CONTENT contains the details of the message.

    :param record: A single text log record.
    :return: A parsed log record.
    """
    match = _RFC3164_PATTERN.match(record)
    if match is None:
        raise RuntimeError("")
    groups = match.groups()
    # Priority is facility * 8 + severity, so divmod is the inverse of that
    facility, severity = divmod(int(groups[0]), 8)
    return LogRecord(
        facility=facility,
        severity=severity,
        timestamp=timestamp_to_datetime(*groups[1:6]),
        hostname=groups[6],
        process=groups[7],
        process_id=int(groups[8]) if groups[8] is not None else None,
        message=groups[9],
    )
