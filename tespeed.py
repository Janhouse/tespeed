#!/usr/bin/env python2
#
# Copyright 2012 Janis Jansons (janis.jansons@janhouse.lv)
#

import os
import urllib
import urllib2
import gzip
import sys
from multiprocessing import Process, Pipe, Manager
from lxml import etree
import time
import gzip
import time
import string
import random
from math import radians, cos, sin, asin, sqrt

from StringIO import StringIO

# Using StringIO with callback to measure upload progress
class CallbackStringIO(StringIO):   
    def __init__(self, num, th, d, buf = ''):
        # Force self.buf to be a string or unicode
        if not isinstance(buf, basestring):
            buf = str(buf)
        self.buf = buf
        self.len = len(buf)
        self.buflist = []
        self.pos = 0
        self.closed = False
        self.softspace = 0
        self.th=th
        self.num=num
        self.d=d
        self.total=self.len*self.th
    
    def read(self, n=100000):
        next = StringIO.read(self, n)
        #if 'done' in self.d:
        #    return
        
        self.d[self.num]=self.pos
        down=0
        for i in range(self.th):
            down=down+self.d.get(i, 0)
        if self.num==0:
            percent = float(down) / (self.total)
            percent = round(percent*100, 2)
            sys.stdout.write("Uploaded %d of %d bytes (%0.2f%%) in %d threads\r" %
               (down, self.total, percent, self.th))

        #if down >= self.total:
        #    sys.stdout.write('\n')
        #    self.d['done']=1

        return next
        
    def __len__(self):
        return self.len


class TeSpeed:

    def __init__(self, server = ""):

        self.headers = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept-Language' : 'en-us,en;q=0.5',
        'Connection' : 'keep-alive',
        'Accept-Encoding' : 'gzip, deflate',
        #'Referer' : 'http://c.speedtest.net/flash/speedtest.swf?v=301256',
        }

        self.server=server
        print "Getting ready"
        self.latencycount=10
        self.TestSpeed()


    def Distance(self, one, two):
    #Calculate the great circle distance between two points 
    #on the earth specified in decimal degrees (haversine formula)
    #(http://stackoverflow.com/posts/4913653/revisions)
    # convert decimal degrees to radians 

        lon1, lat1, lon2, lat2 = map(radians, [one[0], one[1], two[0], two[1]])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6367 * c
        return km 


    def Closest(self, center, points):
    # Returns object that is closest to center
        closest={}
        for p in range(len(points)):
            now = self.Distance(center, [points[p]['lat'], points[p]['lon']])
            points[p]['distance']=now
            while True:
                if now in closest:
                    now=now+00.1
                else:
                    break
            closest[now]=points[p]
        n=0
        ret=[]
        for key in sorted(closest):
            ret.append(closest[key])
            n+=1
            if n >= 5:
                break
        return ret


    def TestLatency(self, servers):
    # Finding the server with lowest latency
        print "Testing latency..."
        shortest = -1.0
        po = []
        for server in servers:
            now=self.TestSingleLatency(server['url']+"latency.txt?x=" + str( time.time() ))*1000
            if now == -1:
                continue
            print "%0.0f ms latency for %s (%s, %s, %s) [%0.2f km]" % (now, server['url'], server['sponsor'], server['name'], server['country'], server['distance'])

            if (now < shortest and shortest > 0) or shortest < 0:
                shortest = now
                po = server

        print "Best server with average latency %0.0fms - %s, %s, %s" % (shortest, po['sponsor'], po['name'], po['country'])

        return po


    def TestSingleLatency(self, dest_addr):
    # Checking latency for single server
    # Does that by loading latency.txt (empty page)
        request=self.GetRequest(dest_addr)
        
        averagetime=0
        total=0
        for i in range(self.latencycount):
            error=0
            startTime = time.time()
            try:
                response = urllib2.urlopen(request, timeout = 5)
            except urllib2.URLError, e:
                error=1

            if error==0:
                averagetime = averagetime + (time.time() - startTime)
                total=total+1
                
            if total==0:
                return False

        return averagetime/total


    def GetRequest(self, uri):
    # Generates a GET request to be used with urlopen
        req = urllib2.Request(uri, headers = self.headers)
        return req


    def PostRequest(self, uri, stream):
    # Generate a POST request to be used with urlopen
        req = urllib2.Request(uri, stream, headers = self.headers)
        return req


    def ChunkReport(self, bytes_so_far, chunk_size, total_size, num, th, d, w):
    # Receiving status update from download/upload thread
        if w==1:
            return
        d[num]=bytes_so_far
        down=0
        for i in range(th):
            down=down+d.get(i, 0)

        if num==0 or down >= total_size*th:

            percent = float(down) / (total_size*th)
            percent = round(percent*100, 2)

            sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%) in %d threads\r" %
               (down, total_size*th, percent, th))

        #if down >= total_size*th:
        #   sys.stdout.write('\n')


    def ChunkRead(self, response, num, th, d, w=0, chunk_size=8192, report_hook=None):
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
             report_hook(bytes_so_far, chunk_size, total_size, num, th, d, w)
        end = time.time()

        return [ bytes_so_far, start, end ]


    def AsyncGet(self, conn, uri, num, th, d):

        request=self.GetRequest(uri)
        response = urllib2.urlopen(request, timeout = 30);
        size, start, end=self.ChunkRead(response, num, th, d, report_hook=self.ChunkReport)

        conn.send([size, start, end])
        conn.close()


    def AsyncPost(self, conn, uri, num, th, d):
        postlen=len(self.postData)
        stream = CallbackStringIO(num, th, d, self.postData)
        request=self.PostRequest(uri, stream)

        start=0
        end=0

        try:
            response = urllib2.urlopen(request,  timeout = 30);
        
            size, start, end=self.ChunkRead(response, num, th, d, 1, report_hook=self.ChunkReport)
        
        except urllib2.URLError, e:
            print "Failed uploading..."

        conn.send([postlen, start, end])
        conn.close()


    def LoadConfig(self):
    # Load the configuration file
        print "Loading speedtest configuration..."
        uri = "http://speedtest.net/speedtest-config.php?x=" + str( time.time() )
        request=self.GetRequest(uri)
        response = urllib2.urlopen(request)

        # Load etree from XML data
        config = etree.fromstring(self.DecompressResponse(response))
        
        ip=config.find("client").attrib['ip']
        isp=config.find("client").attrib['isp']
        lat=float(config.find("client").attrib['lat'])
        lon=float(config.find("client").attrib['lon'])
        
        print "IP: %s; Lat: %f; Lon: %f; ISP: %s" % (ip, lat, lon, isp)
        
        return { 'ip': ip, 'lat': lat, 'lon': lon, 'isp': isp }
        

    def LoadServers(self):
    # Load server list
        print "Loading server list..."
        uri = "http://speedtest.net/speedtest-servers.php?x=" + str( time.time() )
        request=self.GetRequest(uri)
        response = urllib2.urlopen(request);

        # Load etree from XML data
        servers_xml = etree.fromstring(self.DecompressResponse(response))
        servers=servers_xml.find("servers").findall("server")
        server_list=[]

        for server in servers:
            server_list.append({
            'lat': float(server.attrib['lat']), 
            'lon': float(server.attrib['lon']),
            'url': server.attrib['url'][:-10], 
            'url2': server.attrib['url2'][:-10], 
            'name': server.attrib['name'], 
            'country': server.attrib['country'], 
            'sponsor': server.attrib['sponsor'], 
            'id': server.attrib['id'], 
            })

        return server_list


    def DecompressResponse(sefl, response):
    # Decompress gzipped response
        data = StringIO(response.read())
        gzipper = gzip.GzipFile(fileobj=data)
        return gzipper.read()


    def FindBestServer(self):
        print "Looking for closest and best server..."
        best=self.TestLatency(self.Closest([self.config['lat'], self.config['lon']], self.server_list))
        self.server=best['url']
        print "Best server: ", self.server


    def TestUpload(self):
    # Testing upload speed

        num=2
        getone=self.server+"upload.php?x=" + str( time.time() )
        
        self.postData=urllib.urlencode({'upload6': ''.join(random.choice(string.ascii_uppercase) for x in range(1024*1024)) })

        start=time.time()

        connections=[]
        d=Manager().dict()
        for i in range(num):
            connection={}
            connection['parent'], connection['child']= Pipe()
            connection['connection'] = Process(target=self.AsyncPost, args=(connection['child'], getone, i, num, d))
            connection['connection'].start()
            connections.append(connection)

        for c in range(num):
            connections[c]['size'], connections[c]['start'], connections[c]['end']=connections[c]['parent'].recv()
            connections[c]['connection'].join()

        end=time.time()
        
        sys.stdout.write('                                                                                           \r')

        sizes=0
        tspeed=0
        for c in range(num):
            if connections[c]['end'] is not False:
                tspeed=tspeed+(connections[c]['size']/(connections[c]['end']-connections[c]['start']))
                sizes=sizes+connections[c]['size']
        took=end-start
        print "Upload size: %0.2f MB; Uploaded in upload: %0.2f s" % (sizes/1024/1024, took)
        print "Upload speed: %0.2f MB/s" % ((sizes/1024/1024)/took)


    def TestDownload(self):
    # Testing download speed

        num=4
        getone=self.server+"random1500x1500.jpg?x=1348097022034&y=3"
        start=time.time()
        connections=[]
        d=Manager().dict()
        for i in range(num):
            connection={}
            connection['parent'], connection['child']= Pipe()
            connection['connection'] = Process(target=self.AsyncGet, args=(connection['child'], getone, i, num, d))
            connection['connection'].start()
            connections.append(connection)

        for c in range(num):
            connections[c]['size'], connections[c]['start'], connections[c]['end']=connections[c]['parent'].recv()
            connections[c]['connection'].join()

        end=time.time()

        sizes=0
        tspeed=0
        for c in range(num):
            tspeed=tspeed+(connections[c]['size']/(connections[c]['end']-connections[c]['start']))
            sizes=sizes+connections[c]['size']
            
        took=end-start
        
        sys.stdout.write('                                                                                           \r')

        #print "Download speed (v2): ", tspeed/1024/1024, " MB/s"
        print "Download size: %0.2f MB; Uploaded in upload: %0.2f s" % (sizes/1024/1024, took)
        print "Download speed: %0.2f MB/s" % ((sizes/1024/1024)/took)


    def TestSpeed(self):

        if self.server == '':
            self.config=self.LoadConfig()
            self.server_list=self.LoadServers()
            self.FindBestServer()
            
        self.TestDownload()
        self.TestUpload()


def main(argv):
    t=TeSpeed(len(argv)>1 and argv[1] or '')


if __name__ == '__main__':
    main(sys.argv)

