# Router Log Preprocessor
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
