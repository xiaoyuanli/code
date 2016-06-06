#!/usr/bin/python
# Created by: Xiaoyuan Li
import subprocess
import re
import urllib
import urllib2
import requests
from requests.auth import HTTPBasicAuth
import socket
import time

# splunk indexer proxy object
class SplunkProxy:
    # token value is for example but not valid.
    __url = 'http://latitude.work.com:8088/services/collector/event'
    __headers = {'Authorization': 'Splunk 91F82F8C-0E99-6F8C-A723-F8C8693AEFEF', 'Content-Type': 'application/json'}
    __cmd = "POST"

    def __init__( self, server, port ):
        self.__url = "http://" + server + ":" + str(port) + "/services/collector/event"

    def setHeader( self, name, value ):
        self.__headers[name] = value

    def getRESTpoint(self):
        return self.__url

    # send request
    def post( self, data ):
        print "sending ..."
        print self.__url
        print self.__headers
        print data
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        req = urllib2.Request(self.__url, data, self.__headers)
        req.get_method = lambda: self.__cmd
        try:
            connection = opener.open(req)
        except urllib2.HTTPError, e:
            connection = e
        print "Response: ", connection.code


# event builder
class EventBuilder:
    __fields = None
    __hostname = "localhost"
    __timestamp = 0
    __jsondata = None

    def __init__( self, fields ):
        self.__fields = fields
        self.__hostname = socket.gethostname()
        self.__timestamp = time.time()
        self.reset()

    def reset( self ):
        self.__jsondata = '{"source": "pycode", "sourcetype": "appstat"' + ', "host": "' + self.__hostname + '", "time": "' + str(self.__timestamp) + '"'

    def getHostname(self):
        return self.__hostname

    def getTimestamp(self):
        return self.__timestamp

    # build json event
    def buildEvent(self, data):
        print "Build event with fields:", self.__fields
        event = '"event": {'
        totalItems = len(data)
        if (len(self.__fields) != totalItems):
            print "ERROR: unexpected number of data items:", totalItems
            event = '"event": "CANNOT EXTRACT"'
            return event

        sep = ""
        for i in range(totalItems):
            event = event + sep + '"' + self.__fields[i] + '": "' + data[i] + '"'
            print "%s: %s" % (self.__fields[i], data[i])
            sep = ", "

        event = event + "}"
        print "Built event: ", event
        self.__jsondata = self.__jsondata + ', ' + event

    def getJSONdata(self):
        data = self.__jsondata + "}"
        return data

"""
# App perf object
class PerfStat:
    class Service:
        __name = None
        __host = None
        __url = None
        __defaultText = None

        def __init__( self, service, host, url, text ):
            self.__name = service
            self.__host = host
            self.__url = url
            self.__defaultText = text

        def getServiceName(self):
            return __name

        def getHost(self):
            return __host

        def getURL(self):
            return __url

        def getDefaultText(self):
            return __defaultText

    __result = None
    __serviceMap = {'TestApp': None}

    def __init__( self ):
        self.reset()
        artifactory = Service('Artifactory','repo.work.com', 'http://repo.work.com/artifactory/api/system/ping', None)
        self.__servcieMap[artifactory.getServiceName()] = artifactory
        bamboo = Service('Bamboo', 'bamboo.work.com', 'http://bamboo.work.com', 'HTML page')
        self.__servcieMap[bamboo.getServiceName()] = bamboo

    def reset(self, service = 'None'):
        self.__result = {'Service': service, 'Method': 'None', 'Code': '0', 'RespText': 'None', 'RespTime': 0}

    def ping(self, svc):
        t0 = time.time()
        connection = requests.get(svc.getURL())
        self.__result['RespTime'] = int((time.time() - t0) * 1000)
        self.__result['Method'] = svc.getURL()
        self.__result['Code'] = str(connection.status_code)
        text = svc.getDefaultText()
        if (text):
            self.__result['RespText'] = text
        else:
            self.__result['RespText'] = str(connection.text)

    def check(self, service):
        self.reset(service)
        if (service in self.__serviceMap):
            svcObj = self.__serviceMap[service]
            if (svcObj):
                self.ping(svcObj)

    def getResult(self):
        return self.__result


# Artivactory
host = 'repo.work.com'
builder.setHostname(host)
url="http://" + host + "/artifactory/api/system/ping"
response = None
connection = None
t0 = time.time()

# ping server
connection = requests.get(url)

resptime = int((time.time() - t0) * 1000)
# floatformat = format(resptime, '.3f')

appMap = {'Service': 'Artifactory', 'Method': url, 'Code': str(connection.status_code), 'RespText': str(connection.text), 'RespTime': str(resptime)}
builder.buildEventWithKVmap(appMap)
splunk.post( builder.getJSONdata() )
"""

##################################################################
splunk = SplunkProxy("latitude.work.com", "8088")

fields = ('Application', 'User', 'PID', 'CPU%', 'MEM%', 'VSZ', 'RSS', 'State', 'Start', 'Time', 'Command')
builder = EventBuilder(fields)

# Get process info
ps = subprocess.Popen(['ps', '-aux'], stdout=subprocess.PIPE).communicate()[0]

# Process disk stat
# apps map: key = cmd, value = appname:
appsToMonitor = {'splunkd' : 'splunkd', 'myapp' : 'TestApp'}
# appsToMonitor = {'splunkd' : 'splunkd', '/usr/lib/virtualbox/VBoxXPCOMIPCD' : 'VirtualBox', 'myapp' : 'TestApp'}
appCmds = appsToMonitor.keys()
appsNotRun = appsToMonitor.keys()

processes = ps.split('\n')

sep = re.compile('[\s]+')
for row in processes:
    dataItems = sep.split(row)
    if (len(dataItems) < 10):
        break
    appIdx = -1
    found = False
    for appIdx in range(len(appCmds)):
        if (appCmds[appIdx] in dataItems):
            found = True
            break
    if (found is False):
        continue
    print "DEBUG: should post:", row
    appData = [str(appsToMonitor[appCmds[appIdx]]), str(dataItems[0]), str(dataItems[1]), str(dataItems[2]), str(dataItems[3]), str(dataItems[4]), str(dataItems[5]), str(dataItems[7]), str(dataItems[8]), str(dataItems[9])]
    cmd = dataItems[10]
    for j in range(11, len(dataItems)):
        cmd = cmd + " " + str(dataItems[j])
    appData.append(cmd)
    builder.reset()
    builder.buildEvent(appData)
    splunk.post( builder.getJSONdata() )
    if appCmds[appIdx] in appsNotRun:
        appsNotRun.remove(appCmds[appIdx])

for app in appsNotRun:
    appData = [str(appsToMonitor[app]), 'None', 'None', '0', '0', '0', '0', 'X', 'None', '0', app]
    builder.reset()
    builder.buildEvent(appData)
    splunk.post( builder.getJSONdata() )

# exit()
