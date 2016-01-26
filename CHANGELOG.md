# 1.0.3 (January 22, 2016)
Features:

* Switch from subscribe-unsubscribe mechanism to persistent subscription for shadow response processing, avoiding slow rate of shadow requests
* Multiple shadow support

Bugfixes/Improvements:

* Detailed error code for better debugging experience directly in Arduino IDE
* New example of device shadow: Thermostat App/Device simulator, with sketch for device and scripts for App both included

# 1.0.2 (November 5, 2015)
Features:

N/A

Bugfixes/Improvements:

* Added compatibility for Linino openWRT embedded Linux OS (BusyBox v1.19.4 2015-10-03 14:03:26 CEST)
* Refactored file names for credential/codebase upload shell scripts and environment setup shell scripts

# 1.0.1 (November 3, 2015)
Features:

N/A

Bugfixes/Improvements:

* Updated README.md
* Updated examples with error detection
* Fixed timeout interrupt handler function signature
* Improved background thread termination in Python script

# 1.0.0 (October 8, 2015)
Features:

* Release to github
* SDK zip file made available for public download

Bugfixes/Improvements:

* Updated README.md

# 0.2.0 (October 6, 2015)
Features:

* MQTT publish and subscribe with TLS
* Thing Shadow Actions - Update, Get, Delete for any Thing Name
* Thing Shadow Version Control support for current device Thing Name

Bugfixes/Improvements:

* N/A
