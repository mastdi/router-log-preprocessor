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

## As a service

This part will go through the steps to set up the Router Log Preprocessor as a service on Ubuntu.
The following steps will be explained in details below:

- Create a service user
- Create a virtual environment
- Configure environment variables
- Set up the logging directory
- Create the service file
- Start the service and check its status
- Debugging the service using journalctl

### Prerequisites

To install and set up the Router Log Preprocessor as a service on Ubuntu, you will need:

- Python 3.8 installed or higher
- `venv` package (can be installed via `apt-get install python3-venv` command)
- `pip` package manager (should be included after activating the virtual environment)
- Internet connection to download the Router Log Preprocessor package from PyPI and the `.env` file from the GitHub repository

Note that some of these prerequisites may already be installed on your Ubuntu system.
You can check if Python and pip are installed by running the following commands:

```console
python3 --version
pip --version
```

If both of these commands return the version number of Python and pip, respectively, you're good to go.
Otherwise, you will need to install Python and pip on your Ubuntu system before proceeding.

### Creating a service user

First, we will create a service user to run the Router Log Preprocessor.
This is a good security practice as running the script as a root user is not needed.

Run the following commands to create a new user called `rlp`:

```console
sudo adduser rlp --disabled-password --gecos ""
sudo su rlp
cd ~
```

The first command creates a new user called `rlp` with a disabled password and no additional information. 
The second command switches to the new user and moves to their home directory.

### Creating a virtual environment

Now that we have a service user set up, we can create a virtual environment to install the Router Log Preprocessor.
The following commands create a virtual environment using Python 3.8 and install the Router Log Preprocessor package:

```console
python3 -m venv venv
cd venv
source bin/activate
pip install router-log-preprocessor
```

These commands create a new virtual environment in the venv directory, activate the environment, and install the Router Log Preprocessor package.

### Configuring the environment variables 
We will create a .env file in the virtual environment directory to store these variables.
You can copy the default [.env](https://raw.githubusercontent.com/mastdi/router-log-preprocessor/master/.env) file from the Router Log Preprocessor repository and customize it according to your needs:
```console
curl -o .env https://raw.githubusercontent.com/mastdi/router-log-preprocessor/master/.env
nano .env
```
This will download the .env file from the Router Log Preprocessor repository and open it in the Nano text editor. 
Customize the file to set the environment variables you need.

We are done setting up the servie user:

```console
exit
```

### Setting up the logging directory

If you have set the `LOGGING_DIRECTORY` variable in the .env file to `/var/log/rlp`, you need to create the directory and set the ownership to the rlp user:

```console
sudo mkdir /var/log/rlp
sudo chown rlp:rlp /var/log/rlp
```

These commands will create the `/var/log/rlp` directory and set the ownership to the `rlp` user.

### Creating the service file

The next step is to create a service file for the Router Log Preprocessor.
This file specifies how the service should be started and managed by the system.
Create a new file called rlp.service in the /etc/systemd/system/ directory using the following command:

```console
sudo nano /etc/systemd/system/rlp.service
```

This will open the text editor with a new file.
Copy the following text into the file:

```ini
[Unit]
Description=Router Log Preprocessor service
After=network.target

[Service]
User=rlp
WorkingDirectory=/home/rlp/venv
Environment="PATH=/home/rlp/venv/bin"
EnvironmentFile=/home/rlp/venv/.env
ExecStart=/home/rlp/venv/bin/router-log-preprocessor
Restart=on-failure
RestartSec=5s
StartLimitInterval=60s
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
```


### Starting the service

The service is now ready to be started.
The final step is to start the service, check if it is running, and ensuring that the service starts automatically on system boot.
Start the service using the following command:
```console
sudo systemctl start rlp.service
```

This starts the service based on the configuration we just provided.
Check that the service is started using the following command:

```console
sudo systemctl status rlp.service
```

This should show `active (running)` in the console.
To make sure the service is started on system boot use the following command:

```console
sudo systemctl enable rlp.service 
```

### Debugging the service creation

To debug any issues with the service, you can use the `journalctl` command.
For example, to view the logs of the `rlp` service, run the following command:

```console
sudo journalctl -u rlp.service -e
```

This will show the logs of the `rlp` service and the `-e` flag will show the end of the logs.
You can use other flags like `-f` to follow the logs in real-time, `-n` to specify the number of lines to show, and `-r` to show the logs in reverse order (most recent first).

If the service crashes, you can also use the `--since` and `--until` flags to show the logs between a specific time range.
For example, to show the logs of the last 10 minutes, run the following command:

```console
sudo journalctl -u rlp.service --since "10 minutes ago"
```
This will show the logs of the `rlp` service that were generated in the last 10 minutes.
Use this command to debug any issues with the service.