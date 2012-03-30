#!/usr/bin/env python2

#
#
# install python-lxml (debian) or python2-lxml (arch)
#
#
#
# http://speedtest.net/speedtest-config.php?x=1333142532313 - load config
#
# http://speedtest.net/speedtest-servers.php?x=1333142532313 - serverlist
#
# pick closest servers
#
# check latency for each server
#
# pick fastest
#
# do download tests
#
# do upload tests
#
# send results to api
#
# print link to image
#
#
#

import urllib2
import sys
from multiprocessing import Process, Pipe
import os
from lxml import etree
import time

print "Getting ready"

def info(title):
    print title
    print 'module name:', __name__
    print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

def get_request(uri):


    headers = {
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Accept-Language' : 'en-us,en;q=0.5',
    'Connection' : 'keep-alive',
    'Accept-Encoding' : 'gzip, deflate',

    }

    print uri

    #data = urllib.urlencode(values)
    req = urllib2.Request(uri, headers = headers)
    return req
    #handle = urllib2.urlopen(req)
    #page = handle.read()

    #print page

    # result.read() will contain the data
    # result.info() will contain the HTTP headers

    # To get say the content-length header
    #length = handle.info()['Content-Length']



def post_request(uri):

    headers = {
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Accept-Language' : 'en-us,en;q=0.5',
    'Connection' : 'keep-alive',
    'Accept-Encoding' : 'gzip, deflate',
    'Referer' : 'http://c.speedtest.net/flash/speedtest.swf?v=301256',
    }

    print uri

    #data = urllib.urlencode(values)
    req = urllib2.Request(uri, headers = headers)
    return req
    #handle = urllib2.urlopen(req)
    #page = handle.read()

    #print page

    # result.read() will contain the data
    # result.info() will contain the HTTP headers

    # To get say the content-length header
    #length = handle.info()['Content-Length']


def chunk_report(bytes_so_far, chunk_size, total_size):
   percent = float(bytes_so_far) / total_size
   percent = round(percent*100, 2)
   sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
       (bytes_so_far, total_size, percent))

   if bytes_so_far >= total_size:
      sys.stdout.write('\n')

def chunk_read(response, chunk_size=8192, report_hook=None):
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0

    start = time.time()

    while 1:
      chunk = response.read(chunk_size)
      bytes_so_far += len(chunk)

      if not chunk:
         break

      if report_hook:
         report_hook(bytes_so_far, chunk_size, total_size)

    end = time.time()

    return [ bytes_so_far, start, end ]

def async_get(conn, uri):

    request=get_request(uri)
    response = urllib2.urlopen(request);
    size, start, end=chunk_read(response, report_hook=chunk_report)

    conn.send([size, start, end])
    conn.close()


if __name__ == '__main__':

    getone='http://speedtest1.datagrupa.lv/speedtest/random2000x2000.jpg?x=1333139184092&y=1'


    info('main line')

    start = time.time()
    print start
    print "Start", start


    parent_conn1, child_conn1 = Pipe()
    p = Process(target=async_get, args=(child_conn1, getone, ))

    parent_conn2, child_conn2 = Pipe()
    k = Process(target=async_get, args=(child_conn2, getone, ))

    p.start()
    k.start()

    size1, start1, end1=parent_conn1.recv()
    size2, start2, end2=parent_conn2.recv()
    total_size=size1+size2

    print "Total size: ", total_size

    p.join()
    k.join()


    end = time.time()
    print "whaat", end

    time_elapsed=end - start

    print "Time elapsed = ", time_elapsed, "seconds"

    speed=( size1 + size2 ) / time_elapsed

    print "Speed: ", speed / 1024, " Kbytes/sec"

    speed1=( size1 / ( end1 - start1 ) ) / 1024
    speed2=( size2 / ( end2 - start2 ) ) / 1024

    print "Better speed1", speed1
    print "Better speed2", speed2

    print "Total speed: ", speed1 + speed2, " KB/s"

    #print "Better speed: ", ( size1 + size2 ) / ( end1 - start1 ) + 




