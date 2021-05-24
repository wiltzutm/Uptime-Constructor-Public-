Uptime-Constructor
Howden Australia

This software is used to change the construction of the csv files that are output by the IFM Reader software.

CSV files has a timestmp column and data columns. Each data column has a title, which has the form 'Project_SensorName'.

These column titles can be changed in the config.json file.

other settings in the config.json file are:

    IP Addresses: these are set in the appsettings.json file in the IFM Reader folder. the ip addresses ic config.json should match exactly with appsettings.json
    Contract: contract number of project where the hardware is deployed
    sensorspermodule: this should also match exactly with appsettings.json
    locations: these are the sonsor locations or where the sensor is installed on the bearing. each sensor location corresponds to an ip address and sensor        number. This ip address and sensor number is from the IFM modules.
    