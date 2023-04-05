# Router Log Preprocessor
![router-log-preprocessor](https://user-images.githubusercontent.com/105678820/228938795-66dbd955-813b-4fb3-a559-4f3a41f55bb9.png)

> Garbage in, garbage out
>
> &mdash; <cite>George Fuechsel</cite>

Preprocessors upcycle garbage input data into well-structured data to ensure reliable and accurate event handling in third-party systems such as Zabbix.
By parsing and filtering the input log data, the preprocessor helps to ensure that only high-quality data are sent for further analysis and alerting.
This helps to minimize false positives and ensure that network administrators receive reliable and actionable alerts about potential security threats or other issues.


Key features:
- **Wireless LAN Controller event** log entries are parsed to tangible enumerations
- **DNSMASQ DHCP** log entries are parsed to catch which IP a given client is assigned to
- **Zabbix** templates are included to ensure that the logs are can lead to actionable alerts
- **Extendable** preprocessors and hooks to ensure future reliable information to network administrators

## Installation
```console
$ pip install router-log-preprocessor
```

If needed it can also be installed from sources.
Requires [Poetry 1.3.2](https://python-poetry.org/).
```console
$ git pull https://github.com/mastdi/router-log-preprocessor.git
$ cd router-log-preprocessor
$ poetry install
```

## Usage
Installing the package using pip also creates the executable script named `router-log-preprocessor`.
On Linux systems the router log preprocessor can be run by

```console
./router-log-preprocessor
```

The configuration solely happens through environment variables or a `.env` configuration file located in the current working directory.
The most important variables are documented below. 
A full sample can be found in [.env](https://raw.githubusercontent.com/mastdi/router-log-preprocessor/master/.env).
The application reads, in order of the least priority to the highest file:
1. `.env`,
2. `.env.dev`,
3. `.env.test`,
4. `.env.staging`,
5. `.env.prod`,

meaning that values stored in `.env.prod` will overwrite any values from other dovenv files.
Parameters stored in environment variables will always take priority over values loaded from a dotenv file.

```dotenv
# Purpose: Specifies the IP address or hostname of the local interface to which the
# logging system should bind.
# Format: A string containing a valid IP address or hostname, such as "192.168.0.1" or
# "example.com".
LOG_SERVER_HOST="0.0.0.0"

# Purpose: Specifies the port number of the server to which log data should be sent.
# Format: An integer representing a valid port number, such as 514.
LOG_SERVER_PORT=8514

# Purpose: Specifies the hostname or IP address of the Zabbix server to which the
# Zabbix Sender should send monitoring data.
# Format: A string containing a valid hostname or IP address, such as "example.com" or
# "192.168.0.1".
ZABBIX_HOST="example.com"

# Purpose: Specifies the port number on which the Zabbix server is running and to
# which the Zabbix Sender should send monitoring data.
# Format: An integer representing a valid port number, such as 10051.
ZABBIX_PORT=10051
```