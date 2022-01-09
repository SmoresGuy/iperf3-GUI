Graphical User Interface for iperf3
===================================

This is a python 3 program to give a graphical front end to local iperf3 tests

## Revision History

V1.3 - forked from NickWaterton and removed all internet related and ping stuff, ported to python3
V1.2 - Added Yandex maps service due to impending google requirement for API key (both services now supported)
V1.1 - Big re-write with new features, including google maps
V1.0 : First release


## Introduction
This program has the following features:
* enter your own server ip/fqdn
* ports configurable (and presets)
* several (not all) options graphically configurable
* large gauge display
* auto ranging
* works on windows or linux
* gives download and upload speeds

## Pre-Requisites
You need iperf3 installed. It can be downloaded from here: https://iperf.fr/iperf-download.php


## Install
First you need python 3.x installed

now clone the repository from GitHub (obviously you need `git` installed)
```bash
git clone https://github.com/onemarcfifty/iperf3-GUI.git
cd iperf3-GUI
```
You should now have the program `iperf.py` - make sure the file is executable

No need to install anything, you can just run the program as is.

run `./iperf.py -h` (or `python ./iperf.py -h` if you are on windows)

```
usage: iperf.py [-h] [-I IPERF_EXEC] [-ip [IP_ADDRESS [IP_ADDRESS ...]]]
                [-l LOCAL_IP] [-p PORT] [-r RANGE] [-R] [-m {OFF,Track,Peak}]
                [-G] [-g GOOGLE_API_KEY] [-D] [-V] [-v]

Iperf3 GUI Network Speed Tester

optional arguments:
  -h, --help            show this help message and exit
  -I IPERF_EXEC, --iperf_exec IPERF_EXEC
                        location and name of iperf3 executable
                        (default=D://utils//iperf3.exe)
  -ip [IP_ADDRESS [IP_ADDRESS ...]], --ip_address [IP_ADDRESS [IP_ADDRESS ...]]
                        default server address('s) can be a list
                        (default=[u'192.168.100.119'])
  -p PORT, --port PORT  server port (default=5201)
  -r RANGE, --range RANGE
                        range to start with in Mbps (default=10)
  -R, --reset_range     Reset range to Default for Upload test (default =
                        True)
  -m {OFF,Track,Peak}, --max_mode {OFF,Track,Peak}
                        Show Peak Mode (default = Peak)
  -D, --debug           debug mode
  -V, --verbose         print everything
  -v, --version         show program's version number and exit
```

## Quick Start
You need to know the pathname of your iperf3 executable, the default is `iperf3`, but you can use the `-I` option to specify the pathname
for example on my Windows system I use
```bash
python .\iperf.py -I D:\utils\iperf3.exe
```
Because my `iperf3.exe` is in my `D:/utils directory`.
Using Linux, the default usually works just fine (if iperf3 was installed using `apt-get` or is otherwise in your `PATH`, so you would use:
```bash
.\iperf.py
```

You may need to be Administrator to use ping - it works fine for me as none-Administrator, but read the pyping page (if you are using it).

To test on your local network, you will need another computer running another copy of iperf3 as as server:
```bash
.\iperf3 -s
```
You can then test your local network/wifi speeds against the new server you just started using it's ip address.

If you select a remote server, you can test your actual internet speeds.

You can enter a new server in the 'server' combobox, if it validates as an iperf3 server, the new server (plus maps etc) will be saved in the config.ini file, and automatically loaded the next time the program is started.

You can add your own servers/ip addresses as a command line option `-ip` as a list of servers - these will not be saved in the config.ini file.
Only remote servers are saved in the config.ini file, all local/private ip addresses are stored under your external ip address.
If your external ip address cannot be determined, then maps are disabled. Also, if your external ip address changes, then new maps/distances will be stored in the config.ini file - in addition to the existing ones. So if you use a laptop, and move around, various maps/distances will be stored and reused depending on where you are. This is all automatic. If it goes wrong somehow, just delete config.ini and start again.

That's it!
