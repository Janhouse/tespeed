#!/usr/bin/env python2
#
# Copyright 2012-2013 Janis Jansons (janis.jansons@janhouse.lv)
#

import argparse
args=argparse.Namespace()
args.suppress=None
args.store=None

from SocksiPy import socks
import socket

# Magic!
def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
socket.getaddrinfo = getaddrinfo

socket.setdefaulttimeout(None)

import urllib
import urllib2
import gzip
import sys
from multiprocessing import Process, Pipe, Manager
from lxml import etree
import time
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
    
    def read(self, n=10240):
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
            print_debug("Uploaded %d of %d bytes (%0.2f%%) in %d threads\r" %
               (down, self.total, percent, self.th))

        #if down >= self.total:
        #    print_debug('\n')
        #    self.d['done']=1

        return next
        
    def __len__(self):
        return self.len


class TeSpeed:

    def __init__(self, server = "", numTop = 0, servercount = 3, store = False, suppress = False, unit = False, chunksize=10240, downloadtests=15, uploadtests=10):

        self.headers = {
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0',
            'Accept-Language' : 'en-us,en;q=0.5',
            'Connection' : 'keep-alive',
            'Accept-Encoding' : 'gzip, deflate',
            #'Referer' : 'http://c.speedtest.net/flash/speedtest.swf?v=301256',
        }

        self.num_servers=servercount;
        self.servers=[]
        if server != "":
            self.servers=[server]

        self.server=server
        self.down_speed=-1
        self.up_speed=-1
        self.latencycount=10
        self.bestServers=5

        self.units="Mbit"
        self.unit=0
        
        self.chunksize=chunksize
        
        self.downloadtests=downloadtests
        self.uploadtests=uploadtests
        
        if unit:
            self.units="MiB"
            self.unit=1

        self.store=store
        self.suppress=suppress
        if store:
            print_debug("Printing CSV formated results to STDOUT.\n")
        self.numTop=int(numTop)
        #~ self.downList=['350x350', '500x500', '750x750', '1000x1000',
            #~ '1500x1500', '2000x2000', '2000x2000', '2500x2500', '3000x3000',
            #~ '3500x3500', '4000x4000', '4000x4000', '4000x4000', '4000x4000']
        #~ self.upSizes=[1024*256, 1024*256, 1024*512, 1024*512, 
            #~ 1024*1024, 1024*1024, 1024*1024*2, 1024*1024*2, 
            #~ 1024*1024*2, 1024*1024*2]

        self.downList=[
'350x350', '350x350', '500x500', '500x500', '750x750', '750x750', '1000x1000', '1500x1500', '2000x2000', '2500x2500',

'3000x3000','3500x3500','4000x4000','1000x1000','1000x1000','1000x1000','1000x1000','1000x1000','1000x1000','1000x1000',
'1000x1000','1000x1000','1000x1000','1000x1000','1000x1000','1000x1000','1000x1000','1000x1000','1000x1000','1000x1000',

'2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000',
'2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000','2000x2000',

'4000x4000', '4000x4000', '4000x4000', '4000x4000', '4000x4000'
]

#'350x350', '500x500', '750x750', '1000x1000',
#            '1500x1500', '2000x2000', '2000x2000', '2500x2500', '3000x3000',
#            '3500x3500', '4000x4000', '4000x4000', '4000x4000', '4000x4000'
#]
        self.upSizes=[

1024*256, 1024*256, 1024*512, 1024*512, 1024*1024, 1024*1024, 1024*1024*2, 1024*1024*2, 1024*1024*2,  1024*512,
1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256,

1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512,
1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512,

1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256, 1024*256,
1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512, 1024*512,

1024*1024*2, 1024*1024*2, 1024*1024*2, 1024*1024*2,  1024*1024*2, 1024*1024*2, 1024*1024*2, 1024*1024*2, 1024*1024*2, 1024*1024*2,
1024*1024*2, 1024*1024*2, 1024*1024*2, 1024*1024*2,  1024*1024*2, 1024*1024*2, 1024*1024*2, 1024*1024*2, 1024*1024*2, 1024*1024*2,
#            1024*1024, 1024*1024, 1024*1024*2, 1024*1024*2, 
#            1024*1024*2, 1024*1024*2]
]

        self.postData=""
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


    def Closest(self, center, points, num=5):
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
            if n >= num and num!=0:
                break
        return ret


    def TestLatency(self, servers):
    # Finding servers with lowest latency
        print_debug("Testing latency...\n")
        po = []
        for server in servers:
            now=self.TestSingleLatency(server['url']+"latency.txt?x=" + str( time.time() ))*1000
            now=now/2 # Evil hack or just pure stupidity? Nobody knows...
            if now == -1 or now == 0:
                continue
            print_debug("%0.0f ms latency for %s (%s, %s, %s) [%0.2f km]\n" % 
                (now, server['url'], server['sponsor'], server['name'], server['country'], server['distance']))

            server['latency']=now

            # Pick specified ammount of servers with best latency for testing
            if int(len(po)) < int(self.num_servers):
                po.append(server)
            else:
                largest = -1

                for x in range(len(po)):
                    if largest < 0:
                        if now < po[x]['latency']:
                            largest = x
                    elif po[largest]['latency'] < po[x]['latency']:
                        largest = x
                    #if cur['latency']

                if largest >= 0:
                    po[largest]=server

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
            except (urllib2.URLError, socket.timeout), e:
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
    # Receiving status update from download thread
        
        if w==1:
            return
        d[num]=bytes_so_far
        down=0
        for i in range(th):
            down=down+d.get(i, 0)

        if num==0 or down >= total_size*th:

            percent = float(down) / (total_size*th)
            percent = round(percent*100, 2)

            print_debug("Downloaded %d of %d bytes (%0.2f%%) in %d threads\r" %
               (down, total_size*th, percent, th))

        #if down >= total_size*th:
        #   print_debug('\n')


    def ChunkRead(self, response, num, th, d, w=0, chunk_size=False, report_hook=None):
        #print_debug("Thread num %d %d %d starting to report\n" % (th, num, d))

        if not chunk_size:
            chunk_size=self.chunksize

        if(w==1):
            return [0,0,0]

        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)
        bytes_so_far = 0

        start=0
        while 1:
            chunk=0
            if start == 0:
                #print_debug("Started receiving data\n")
                chunk = response.read(1)
                start = time.time()
                
            else:
                chunk = response.read(chunk_size)
            if not chunk:
                break
            bytes_so_far += len(chunk)
            if report_hook:
                report_hook(bytes_so_far, chunk_size, total_size, num, th, d, w)
        end = time.time()

        return [ bytes_so_far, start, end ]


    def AsyncGet(self, conn, uri, num, th, d):

        request=self.GetRequest(uri)
        
        start=0
        end=0
        size=0
        
        try:
            response = urllib2.urlopen(request, timeout = 30);
            size, start, end=self.ChunkRead(response, num, th, d, report_hook=self.ChunkReport)
        #except urllib2.URLError, e:
        #    print_debug("Failed downloading.\n")
        except:
            print_debug('                                                                                           \r')
            print_debug("Failed downloading.\n")
            conn.send([0, 0, False])
            conn.close()
            return

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
        #except urllib2.URLError, e:
        #    print_debug("Failed uploading.\n")
        except:
            print_debug('                                                                                           \r')
            print_debug("Failed uploading.\n")
            conn.send([0, 0, False])
            conn.close()
            return

        conn.send([postlen, start, end])
        conn.close()


    def LoadConfig(self):
    # Load the configuration file
        print_debug("Loading speedtest configuration...\n")
        uri = "http://speedtest.net/speedtest-config.php?x=" + str( time.time() )
        request=self.GetRequest(uri)
        response = None
        try:
            response = urllib2.urlopen(request, timeout=5)
        except (urllib2.URLError, socket.timeout), e:
            print_debug("Failed to get Speedtest.net config file.\n")
            print_result("%0.2f,%0.2f,\"%s\",\"%s\"\n" % (self.down_speed, self.up_speed, self.units, self.servers))
            sys.exit(1)

        # Load etree from XML data
        config = etree.fromstring(self.DecompressResponse(response))
        
        ip=config.find("client").attrib['ip']
        isp=config.find("client").attrib['isp']
        lat=float(config.find("client").attrib['lat'])
        lon=float(config.find("client").attrib['lon'])
        
        print_debug("IP: %s; Lat: %f; Lon: %f; ISP: %s\n" % (ip, lat, lon, isp))
        
        return { 'ip': ip, 'lat': lat, 'lon': lon, 'isp': isp }
        

    def LoadServers(self):
    # Load server list
        print_debug("Loading server list...\n")
        uri = "http://speedtest.net/speedtest-servers.php?x=" + str( time.time() )
        request=self.GetRequest(uri)
        response=None
        try:
            response = urllib2.urlopen(request);
        except (urllib2.URLError, socket.timeout), e:
            print_debug("Failed to get Speedtest.net server list.\n")
            print_result("%0.2f,%0.2f,\"%s\",\"%s\"\n" % (self.down_speed, self.up_speed, self.units, self.servers))
            sys.exit(1)

        # Load etree from XML data
        servers_xml = etree.fromstring(response.read())
        servers=servers_xml.find("servers").findall("server")
        server_list=[]

        for server in servers:
            try:
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
            except:
                server_list.append({
                    'lat': float(server.attrib['lat']), 
                    'lon': float(server.attrib['lon']),
                    'url': server.attrib['url'][:-10], 
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
        try:
            return gzipper.read()
        except IOError as e:
            # Response isn't gzipped, therefore return the data.
            return data.getvalue()

    def FindBestServer(self):
        print_debug("Looking for closest and best server...\n")
        best=self.TestLatency(self.Closest([self.config['lat'], self.config['lon']], self.server_list, self.bestServers))
        for server in best:
            self.servers.append(server['url'])

    def AsyncRequest(self, url, num, upload=0):
        connections=[]
        d=Manager().dict()
        start=time.time()
        for i in range(num):
            full_url=self.servers[i % len(self.servers)]+url
            #print full_url
            connection={}
            connection['parent'], connection['child']= Pipe()
            if upload==1:
                connection['connection'] = Process(target=self.AsyncPost, args=(connection['child'], full_url, i, num, d))
            else:
                connection['connection'] = Process(target=self.AsyncGet, args=(connection['child'], full_url, i, num, d))
            connection['connection'].start()
            connections.append(connection)

        for c in range(num):
            connections[c]['size'], connections[c]['start'], connections[c]['end']=connections[c]['parent'].recv()
            connections[c]['connection'].join()

        end=time.time()
        
        print_debug('                                                                                           \r')

        sizes=0
        #tspeed=0
        for c in range(num):
            if connections[c]['end'] is not False:
                #tspeed=tspeed+(connections[c]['size']/(connections[c]['end']-connections[c]['start']))
                sizes=sizes+connections[c]['size']
                
                # Using more precise times for downloads
                if upload==0:
                    if c==0:
                        start=connections[c]['start']
                        end=connections[c]['end']
                    else:
                        if connections[c]['start'] < start:
                            start=connections[c]['start']
                        if connections[c]['end'] > end:
                            end=connections[c]['end']

        took=end-start

        return [sizes, took]

    def TestUpload(self):
    # Testing upload speed

        url="upload.php?x=" + str( time.time() )

        sizes, took=[0,0]
        counter=0
        failures=0
        data=""
        for i in range(0, len(self.upSizes)):
            if len(data) == 0 or self.upSizes[i] != self.upSizes[i-1]:
                #print_debug("Generating new string to upload. Length: %d\n" % (self.upSizes[i]))
                data=''.join("1" for x in xrange(self.upSizes[i]))
            self.postData=urllib.urlencode({'upload6': data })
            
            if i<2:
                thrds=1
            elif i<5:
                thrds=2
            elif i<7:
                thrds=2
            elif i<10:
                thrds=3
            elif i<25:
                thrds=6
            elif i<45:
                thrds=4
            elif i<65:
                thrds=3
            else:
                thrds=2
            
            sizes, took=self.AsyncRequest(url, thrds, 1)
            #sizes, took=self.AsyncRequest(url, (i<4 and 1 or (i<6 and 2 or (i<6 and 4 or 8))), 1)
            
            # Stop testing if too many failures            
            counter=counter+1
            if sizes==0:
                failures=failures+1
                if failures>2:
                    break
                continue

            size=self.SpeedConversion(sizes)
            speed=size/took
            print_debug("Upload size: %0.2f MiB; Uploaded in %0.2f s\n" % 
                (size, took))
            print_debug("\033[92mUpload speed: %0.2f %s/s\033[0m\n" % 
                (speed, self.units))
            
            if self.up_speed<speed:
                self.up_speed=speed

            if took>5 or counter>=self.uploadtests:
                break
                
        #print_debug("Upload size: %0.2f MiB; Uploaded in %0.2f s\n" % (self.SpeedConversion(sizes), took))
        #print_debug("Upload speed: %0.2f MiB/s\n" % (self.SpeedConversion(sizes)/took))

    def SpeedConversion(self, data):
        if self.unit==1:
            result=(float(data)/1024/1024)
        else:
            result=(float(data)/1024/1024)*1.048576*8
        return result

    def TestDownload(self):
    # Testing download speed
        sizes, took=[0,0]
        counter=0
        failures=0
        for i in range(0, len(self.downList)):
            url="random"+self.downList[i]+".jpg?x=" + str( time.time() ) + "&y=3"
            
            
            if i<2:
                thrds=1
            elif i<5:
                thrds=2
            elif i<11:
                thrds=2
            elif i<13:
                thrds=4
            elif i<25:
                thrds=2
            elif i<45:
                thrds=3
            elif i<65:
                thrds=2
            else:
                thrds=2
            
            sizes, took=self.AsyncRequest(url, thrds )
            #sizes, took=self.AsyncRequest(url, (i<1 and 2 or (i<6 and 4 or (i<10 and 6 or 8))) )
            
            # Stop testing if too many failures            
            counter=counter+1
            if sizes==0:
                failures=failures+1
                if failures>2:
                    break
                continue

            size=self.SpeedConversion(sizes)
            speed=size/took
            print_debug("Download size: %0.2f MiB; Downloaded in %0.2f s\n" % 
                (size, took))
            print_debug("\033[91mDownload speed: %0.2f %s/s\033[0m\n" % 
                (speed, self.units))

            if self.down_speed<speed:
                self.down_speed=speed

            if took>5 or counter>=self.downloadtests:
                break

        #print_debug("Download size: %0.2f MiB; Downloaded in %0.2f s\n" % (self.SpeedConversion(sizes), took))
        #print_debug("Download speed: %0.2f %s/s\n" % (self.SpeedConversion(sizes)/took, self.units))

    def TestSpeed(self):

        if self.server=='list-servers':
            self.config=self.LoadConfig()
            self.server_list=self.LoadServers()
            self.ListServers(self.numTop)
            return
            
        if self.server == '':
            self.config=self.LoadConfig()
            self.server_list=self.LoadServers()
            self.FindBestServer()

        self.TestDownload()
        self.TestUpload()

        print_result("%0.2f,%0.2f,\"%s\",\"%s\"\n" % (self.down_speed, self.up_speed, self.units, self.servers))

    def ListServers(self, num=0):
        
        allSorted=self.Closest([self.config['lat'], self.config['lon']], self.server_list, num)

        for i in range(0, len(allSorted)):
            print_result("%s. %s (%s, %s, %s) [%0.2f km]\n" % 
                (i+1, allSorted[i]['url'], allSorted[i]['sponsor'], allSorted[i]['name'], allSorted[i]['country'], allSorted[i]['distance']))

def print_debug(string):
    if args.suppress!=True:
        sys.stderr.write(string.encode('utf8'))
    #return

def print_result(string):
    if args.store==True:
        sys.stdout.write(string.encode('utf8'))
    #return

# Thx to Ryan Sears for http://bit.ly/17HhSli
def set_proxy(typ=socks.PROXY_TYPE_SOCKS4, host="127.0.0.1", port=9050):
    socks.setdefaultproxy(typ, host, port)
    socket.socket = socks.socksocket

def main(args):

    if args.version:
        print_debug("Tespeed v1.1\nNetwork speedtest using speedtest.net infrastructure - https://github.com/Janhouse/tespeed\n")
        sys.exit(0)

    if args.use_proxy:
        if args.use_proxy==5:
            set_proxy(typ=socks.PROXY_TYPE_SOCKS5, host=args.proxy_host, port=args.proxy_port)
        else:
            set_proxy(typ=socks.PROXY_TYPE_SOCKS4, host=args.proxy_host, port=args.proxy_port)

    if args.listservers:
        args.store=True

    if args.listservers!=True and args.server=='' and args.store!=True:
        print_debug("Getting ready. Use parameter -h or --help to see available features.\n")
    else:
        print_debug("Getting ready\n")
    try:
        t=TeSpeed(
            args.listservers and 'list-servers' or args.server, 
            args.listservers, args.servercount, 
            args.store and True or False, 
            args.suppress and True or False, 
            args.unit and True or False, 
            chunksize=args.chunksize,
            downloadtests=args.downloadtests, 
            uploadtests=args.uploadtests, 
        )
    except (KeyboardInterrupt, SystemExit):
        print_debug("\nTesting stopped.\n")
        #raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TeSpeed, CLI SpeedTest.net')

    parser.add_argument('server', nargs='?', type=str, default='', help='Use the specified server for testing (skip checking for location and closest server).')
    parser.add_argument('-ls', '--list-servers', dest='listservers', nargs='?', default=0, const=10, help='List the servers sorted by distance, nearest first. Optionally specify number of servers to show.')
    parser.add_argument('-w', '--csv', dest='store', action='store_const', const=True, help='Print CSV formated output to STDOUT.')
    parser.add_argument('-s', '--suppress', dest='suppress', action='store_const', const=True, help='Suppress debugging (STDERR) output.')
    parser.add_argument('-mib', '--mebibit', dest='unit', action='store_const', const=True, help='Show results in mebibits.')
    parser.add_argument('-n', '--server-count', dest='servercount', nargs='?', default=1, const=1, help='Specify how many different servers should be used in paralel. (Default: 1) (Increase it for >100Mbit testing.)')

    parser.add_argument('-p', '--proxy', dest='use_proxy', type=int, nargs='?', const=4, help='Specify 4 or 5 to use SOCKS4 or SOCKS5 proxy.')
    parser.add_argument('-ph', '--proxy-host', dest='proxy_host', type=str, nargs='?', default='127.0.0.1', help='Specify socks proxy host. (Default: 127.0.0.1)')
    parser.add_argument('-pp', '--proxy-port', dest='proxy_port', type=int, nargs='?', default=9050, help='Specify socks proxy port. (Default: 9050)')

    parser.add_argument('-cs', '--chunk-size', dest='chunksize', nargs='?', type=int, default=10240, help='Specify chunk size after wich tespeed calculates speed. Increase this number 4 or 5 times if you use weak hardware like RaspberryPi. (Default: 10240)')
    parser.add_argument('-dt', '--max-download-tests', dest='downloadtests', nargs='?', type=int, default=15, help='Specify maximum number of download tests to be performed. (Default: 15)')
    parser.add_argument('-ut', '--max-upload-tests', dest='uploadtests', nargs='?', type=int, default=10, help='Specify maximum number of upload tests to be performed. (Default: 10)')

    #parser.add_argument('-i', '--interface', dest='interface', nargs='?', help='If specified, measures speed from data for the whole network interface.')

    parser.add_argument('-v', '--version', dest='version', nargs='?', const=True, help='Show Tespeed version.')

    args = parser.parse_args()
    main(args)
