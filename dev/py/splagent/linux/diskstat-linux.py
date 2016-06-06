#!/usr/bin/python
# Created by: Xiaoyuan Li
import subprocess
import re
import urllib
import urllib2
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
    __fields = ('Filesystem', 'Total 1K-blocks', 'Used', 'Available', 'Use%', 'Mounted on')
    __hostname = "localhost"
    __timestamp = 0
    __jsondata = ""

    def __init__( self, fields ):
        self.__fields = fields
        self.__hostname = socket.gethostname()
        self.__timestamp = time.time()
        self.reset()

    def reset( self ):
        self.__jsondata = '{"source": "pycode", "sourcetype": "diskstat"' + ', "host": "' + self.__hostname + '", "time": "' + str(self.__timestamp) + '"'

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
            if (self.__fields[i] == 'Use%'):
                data[i] = data[i][:-1]
            event = event + sep + '"' + self.__fields[i] + '": "' + data[i] + '"'
            print "%s: %s" % (self.__fields[i], data[i])
            sep = ", "

        event = event + "}"
        print "Built event: ", event
        self.__jsondata = self.__jsondata + ', ' + event

    def getJSONdata(self):
        data = self.__jsondata + "}"
        return data

splunk = SplunkProxy("re-latitude.sv.splunk.com", "8088")

# print "Filesystem     1K-blocks     Used Available Use% Mounted on"
fields = ('Filesystem', 'Total 1K-blocks', 'Used', 'Available', 'Use%', 'Mounted on')
builder = EventBuilder(fields)

# Get process info
df = subprocess.Popen(['df', '-k'], stdout=subprocess.PIPE).communicate()[0]

# Process disk stat
monitoredVolumes = ('/', '/run')
dfLines = df.split('\n')
print "df lines:"
print dfLines
totalLines = len(dfLines)
dataMatrix = []
idx = 1
while (idx < totalLines):
    print idx
    dataItems = []
    dataLine = dfLines[idx].split()
    if (len(dataLine) > 1):
        dataItems = dataLine
    elif (len(dataLine) == 0):
        idx += 1
        continue
    else:
        dataItems.append(dataLine[0])
        idx += 1
        if (idx < totalLines):
            dataLine = dfLines[idx].split()
            for j in range(len(dataLine)):
                dataItems.append(dataLine[j])
    if (len(dataItems) == 6):
    	dataMatrix.append(dataItems)
        if dataItems[5] in monitoredVolumes:
            print "DEBUG: should post:", dataItems
            builder.reset()
            builder.buildEvent(dataItems)
            splunk.post( builder.getJSONdata() )
    idx += 1

print "Retrieved items:"
print dataMatrix

# Process disk stat

# dfdata = df.split('\n')[1].split()
# dfdata0 = df.split('\n')[2].split()
# print dfdata
# print dfdata0

# hostname = socket.gethostname()
# timestamp = time.time()
# jsondata = '{"source": "pycode", "sourcetype": "diskstat"' + ', "host": "' + builder.getHostname() + '", "time": "' + str(timestamp) + '"'

# build event
# fieldSep = ""
# jsondata = jsondata + ', "event": {'
# line1Items = len(dfdata)
# useLine2 = False
# if (len(fields) != line1Items):
#    print "Info: number of data items in line 1 is different from expected: %d" % line1Items
#    useLine2 = True

# for i in range(len(dfdata)):
#    jsondata = jsondata + fieldSep + '"' + fields[i] + '": "' + dfdata[i] + '"'
#    print "%s: %s KB" % (fields[i], dfdata[i])
#    fieldSep = ", "

# if useLine2:
#    dataIndex = 0
#    for i in range(len(dfdata), len(fields)):
#        print i
#        jsondata = jsondata + fieldSep + '"' + fields[i] + '": "' + dfdata0[dataIndex] + '"'
#        print "%s: %s KB" % (fields[i], dfdata0[dataIndex])
#        dataIndex += 1
#        fieldSep = ", "

# jsondata = jsondata + "}}"

# send
# splunk.post(jsondata)

exit()
