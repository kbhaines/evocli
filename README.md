# EvoCLI 
CLI to control a Honeywell EvoHome system. It is a work in progress

## Installation

    python setup.py install

Create a configuration file '.evoc' with your Honeywell username & password in your
home directory: 

```` 
username: user@user.com 
password: mypassword 
````

## Running

Only a few commands work so far:

    # display temperatures
    evoc temps

    # set zone temperature to 21 for an hour
    evoc zone Lounge 21.0 --duration 60

    # set hotwater on for an hour
    evoc hotwater on --duration 60


