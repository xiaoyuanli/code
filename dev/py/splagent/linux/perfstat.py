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
import json

##############################################################
# splunk indexer proxy object
class SplunkProxy:
    # Token value is for example but not valid. Need to get from real splunk indexer.
    __url = 'http://latitude.work.com:8088/services/collector/event'
    __token = 'Splunk 91D8G8R8-0E99-6F8C-A723-F8C8693AEFEF'
    __headers = {'Authorization': token, 'Content-Type': 'application/json'}
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
        print "INFO: Posting event to: ", self.__url
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

##############################################################
# event builder
class EventBuilder:
    __fields = None
    __hostname = "localhost"
    __timestamp = 0
    __jsondata = None
    __kvMap = None

    def __init__( self, fields ):
        self.__fields = fields
        self.__hostname = socket.gethostname()
        self.__timestamp = time.time()
        self.reset()

    def reset( self ):
        self.__jsondata = '{"source": "pycode", "sourcetype": "perfstat"' + ', "host": "' + self.__hostname + '", "time": "' + str(self.__timestamp) + '"'

    def getHostname(self):
        return self.__hostname

    def setHostname(self, host):
        self.__hostname = host
        self.reset()

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

    def buildEventWithKVmap(self, kvMap):
        print "INFO: Build event with kv map."
        print kvMap

        event = '"event": {'
        totalItems = len(kvMap)
        if (len(self.__fields) != totalItems):
            print "WARN: unexpected number of data items:", totalItems
            if (totalItems == 0):
                event = '"event": "CANNOT EXTRACT"'
                return event

        sep = ""
        for key,value in kvMap.items():
            event = event + sep + '"' + key + '": "' + str(value) + '"'
            sep = ", "

        event = event + "}"
        self.__jsondata = self.__jsondata + ', ' + event
        print "Built json msg: ", self.__jsondata

    def getJSONdata(self):
        data = self.__jsondata + "}"
        return data

##############################################################
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
        return self.__name

    def getHost(self):
        return self.__host

    def getURL(self):
        return self.__url

    def getDefaultText(self):
        return self.__defaultText

    def setDefaultText(self, text):
        self.__defaultText = text


##############################################################
class HTTP:
    @staticmethod
    def getCodeDefinition(code):
        definition = "No message."
        if (code == 200):
            definition = "Service OK."
        elif (code == 400):
            definition = "Bad Request."
        elif (code == 401):
            definition = "Unauthorized."
        elif (code == 407):
            definition = "Proxy Authentication Required."
        elif (code == 408):
            definition = "Request Timeout."
        elif (code == 500):
            definition = "Internal Server Error."
        elif (code == 501):
            definition = "Not Implemented."
        elif (code == 502):
            definition = "Bad gateway."
        elif (code == 503):
            definition = "Service Unavailable."
        elif (code == 504):
            definition = "Gateway Timeout."
        elif (code == 505):
            definition = "HTTP Version Not Supported."
        else:
            definition = "HTTP code: " + str(code) + "."
        return definition


##############################################################
# App perf object
class PerfStat:
    __serviceMap = {'TestApp': None}
    __currentSvc = None
    __result = None
    __recvdText = None

    def __init__( self ):
        self.reset()
        art = Service('Artifactory','artifactory.work.com', 'http://artifactory.work.com/artifactory/api/system/ping', None)
        self.__serviceMap[art.getServiceName()] = art
        bam = Service('Bamboo', 'bamboo.work.com', 'http://bamboo.work.com', 'HTML page')
        self.__serviceMap[bam.getServiceName()] = bam
        jenkins = Service('Jenkins', 'jenkins.work.com', 'https://jenkins.work.com/overallLoad/api/json?pretty=true&tree=queueLength[min[latest]]', 'HTML page')
        self.__serviceMap[jenkins.getServiceName()] = jenkins
        releases = Service('Release', 'release.work.com', 'http://release.work.com/', 'HTML page')
        self.__serviceMap[releases.getServiceName()] = releases

        print "INFO: Available services: "
        self.__serviceMap

    def reset(self, service = 'None'):
        self.__currentSvc = service
        self.__result = {'Service': self.__currentSvc, 'Method': 'None', 'Code': '0', 'RespText': 'None', 'RespTime': 0}

    def ping(self, svc):
        t0 = time.time()
        text = svc.getDefaultText()
        status_code = "0"
        
        try:
            connection = requests.get(svc.getURL())
            self.__result['RespTime'] = str(int((time.time() - t0) * 1000))
            self.__recvdText = connection.text
            status_code = str(connection.status_code)
            if (connection.status_code == 200):
                if (text):
                    self.__result['RespText'] = text
                else:
                    self.__result['RespText'] = str(connection.text)
            else:
                self.__result['RespText'] = HTTP.getCodeDefinition(connection.status_code)
        except requests.ConnectionError as e:
            self.__result['RespText'] = str(e)
            status_code = "902"   # self-defined code.
            self.__result['RespTime'] = "-100"
            self.__recvdText = "None"
        except Exception as e:
            self.__result['RespText'] = str(e)
            status_code = "901"   # self-defined code.
            self.__result['RespTime'] = "-100"
            self.__recvdText = "None"
        except:
            self.__result['RespText'] = "Exception caught at connecting to server."
            status_code = "900"  # self-defined code. 
            self.__result['RespTime'] = "-100"
            self.__recvdText = "None"

        self.__result['Code'] = status_code
        self.__result['Method'] = svc.getURL()

        return status_code

    def check(self, service):
        self.reset(service)
        if (service in self.__serviceMap):
            svcObj = self.__serviceMap[service]
            if (svcObj):
                return self.ping(svcObj)
        return -1

    def getService(self, service):
        if (service in self.__serviceMap):
            svcObj = self.__serviceMap[service]
            if (svcObj):
                return svcObj
        return None

    def getResult(self):
        return self.__result

    def setResult(self, key, val):
        self.__result[key] = val

    def getReceivedText(self):
        return self.__recvdText

    def getHostname(self):
        return self.__serviceMap[self.__currentSvc].getHost()


##############################################################

splunk = SplunkProxy("latitude.work.com", "8088")
fields = ('Service', 'Method', 'Code', 'RespText', 'RespTime')
builder = EventBuilder(fields)
perfstat = PerfStat()

##############################################################
# Artifactory
respcode = perfstat.check("Artifactory")

"""
host = 'artifactory.work.com'
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
"""
builder.setHostname(perfstat.getHostname())
builder.buildEventWithKVmap(perfstat.getResult())
splunk.post( builder.getJSONdata() )

##############################################################
# Bamboo server
respcode = perfstat.check("Bamboo")
"""
host = 'bamboo.work.com'
url = 'http://' + host
builder.setHostname(host)
response = None
connection = None
t0 = time.time()

# ping server
connection = requests.get(url)

resptime = int((time.time() - t0) * 1000)
# floatformat = format(resptime, '.3f')

appMap = {'Service': 'Bamboo', 'Method': url, 'Code': str(connection.status_code), 'RespText': 'HTML page', 'RespTime': str(resptime)}

builder.buildEventWithKVmap(appMap)
"""

builder.setHostname(perfstat.getHostname())
builder.buildEventWithKVmap(perfstat.getResult())
splunk.post( builder.getJSONdata() )


##############################################################
# Jenkins server
respcode = perfstat.check("Jenkins")
if (respcode == 200):
    jsonObj = json.loads(perfstat.getReceivedText())
    # qSize = 'Qsize = ' + str(float("{0:.1f}".format(jsonObj['queueLength']['min']['latest'])))
    qSize = str(float("{0:.1f}".format(jsonObj['queueLength']['min']['latest'])))
    perfstat.setResult('QSize', qSize)
    # perfstat.setResult('RespText', qSize)

"""
host = 'jenkins.wrok.com'
# url = 'https://' + host + "/api/"
# curl use url = 'https://jenkins.work.com/overallLoad/api/json?pretty=true&tree=queueLength\[min\[latest\]\]'
url = 'https://' + host + '/overallLoad/api/json?pretty=true&tree=queueLength[min[latest]]'
builder.setHostname(host)
response = None
connection = None
t0 = time.time()

# ping server
connection = requests.get(url)

resptime = int((time.time() - t0) * 1000)
# floatformat = format(resptime, '.3f')
# print url
# print connection.text
jsonObj = json.loads(connection.text)
qSize = 'Qsize = ' + str(float("{0:.1f}".format(jsonObj['queueLength']['min']['latest'])))

appMap = {'Service': 'Jenkins', 'Method': url, 'Code': str(connection.status_code), 'RespText': qSize, 'RespTime': str(resptime)}

builder.buildEventWithKVmap(appMap)
"""

builder.setHostname(perfstat.getHostname())
builder.buildEventWithKVmap(perfstat.getResult())
splunk.post( builder.getJSONdata() )

##############################################################
# Splunkd Server
respcode = perfstat.check("splunkd")
"""
host = 'latitude'
url = 'http://' + host + ':8000/'
builder.setHostname(host)
response = None
connection = None
t0 = time.time()

# ping server
connection = requests.get(url)

resptime = int((time.time() - t0) * 1000)
# floatformat = format(resptime, '.3f')

appMap = {'Service': 'splunkd', 'Method': url, 'Code': str(connection.status_code), 'RespText': 'HTML page', 'RespTime': str(resptime)}

builder.buildEventWithKVmap(appMap)
"""

builder.setHostname(perfstat.getHostname())
builder.buildEventWithKVmap(perfstat.getResult())
splunk.post( builder.getJSONdata() )



##############################################################
# releases.work.com
respcode = perfstat.check("Release")
builder.setHostname(perfstat.getHostname())
builder.buildEventWithKVmap(perfstat.getResult())
splunk.post( builder.getJSONdata() )

##############################################################
# exit()
##############################################################
