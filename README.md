Tespeed (terminal speedtest) - Copyright 2012 Janis Jansons (janis.jansons@janhouse.lv)


    This is a new Tespeed version written in Python (for the purpose of learning it).

    The old one was written in PHP years ago and wasn't really made for general
    public (was fine tuned and possibly working only on my server).

    Even though the old version didn't work on most boxes, it somehow got
    almost 17 000 downloads on Sourceforge. I guess some people could use this
    (those who hate Flash, JavaScript, has GUI-less servers, etc.) so I'll
    try to make this one a bit better working in time.

    Let's call this version 1.0-alpha


    Of course, this script could not work like this without the best speed 
    testing site out there - http://www.speedtest.net/
    Support them in any way you can (going to their website and clicking on
    ads could probably make them a bit happier). :)
    
    Also there is an ALTERNATIVE SPEEDTEST TOOL written in Python.
    It is probably better maintained and should work with Python 3: 
    https://github.com/sivel/speedtest-cli
    If you don't need testing through socks proxy, go check it out. :)


Requirements:

    This script requires recent Python (preferably 2.7 or newer) and Python2
    modules lxml and argparse.
    Install python-lxml and python-argparse (Debian) 

    $ sudo apt-get install python-lxml python-argparse

    or python2-lxml (Archlinux).

Installation:

    If you have Debian, you might have to change the python executable in tuper.py
    or create a symlink for your existing python2.x executable by doing:
    
        sudo ln -s /usr/bin/python2.7 /usr/bin/python2
        
    If you have python2.6 then replace python2.7 with python2.6.
    
    

    When doing the checkout, remember to pull submodules.
    
    If you have a decent git version (1.6.5 and up), get everything by doing:

        git clone --recursive git://github.com/Janhouse/tespeed.git

    Otherwise do:
    
        git clone git://github.com/Janhouse/tespeed.git
        cd tespeed
        git submodule init
        git submodule update


Usage:

    usage: tespeed.py [-h] [-ls [LISTSERVERS]] [-w] [-s] [-mib] [-n [SERVERCOUNT]]
                      [-p [USE_PROXY]] [-ph [PROXY_HOST]] [-pp [PROXY_PORT]]
                      [server]
    
        TeSpeed, CLI SpeedTest.net
    
        positional arguments:
          server                Use the specified server for testing (skip checking
                                for location and closest server).
        
        optional arguments:
          -h, --help            show this help message and exit
          -ls [LISTSERVERS], --list-servers [LISTSERVERS]
                                List the servers sorted by distance, nearest first.
                                Optionally specify number of servers to show.
          -w, --csv             Print CSV formated output to STDOUT.
          -s, --suppress        Suppress debugging (STDERR) output.
          -mib, --mebibit       Show results in mebibits.
          -n [SERVERCOUNT], --server-count [SERVERCOUNT]
                                Specify how many different servers should be used in
                                paralel. (Defaults to 1.) (Increase it for >100Mbit
                                testing.)
          -p [USE_PROXY], --proxy [USE_PROXY]
                                Specify 4 or 5 to use SOCKS4 or SOCKS5 proxy.
          -ph [PROXY_HOST], --proxy-host [PROXY_HOST]
                                Specify socks proxy host (defaults to 127.0.0.1).
          -pp [PROXY_PORT], --proxy-port [PROXY_PORT]
                                Specify socks proxy port (defaults to 9050).
          -cs [CHUNKSIZE], --chunk-size [CHUNKSIZE]
                                Specify chunk size after wich tespeed calculates
                                speed. Increase this number 4 or 5 times if you use
                                weak hardware like RaspberryPi. (Default: 10240)


What the script does:

 *  Loads config from speedtest.net (http://speedtest.net/speedtest-config.php).

 *  Gets server list (http://speedtest.net/speedtest-servers.php).

 *  Picks 5 closests servers using the coordinates provides by speedtest.net 
    config and serverlist.

 *  Checks latency for those servers and picks one with the lowest.

 *  Does download speed test and returns results.

 *  Does upload speed test and returns results.

 *  Optionally can return CSV formated results.

 *  Can measure through SOCKS proxy.


Logging to file

	Execute manually or add to crontab:
	
		echo $(date +"%Y-%m-%d,%H:%M"),$(./tespeed.py -w) >> speedtest-log.txt


TODO (ideas):

 *  Make it less messy.
 *  Send found results to speedtest.net API (needs some hash?) and get the link
    to the generated image.
 *  Measure the speed for the whole network interface (similar like it was in the
    old version of Tespeed).
 *  Start upload timer only after 1st byte is read.
 *  Figure out the ammount of data that was transfered only when all threads were
    actively sendong/receiving data at the same time. (Should provide more precise 
    test results.)


