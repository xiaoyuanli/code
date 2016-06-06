#!/usr/bin/python
# Created by: Xiaoyuan Li
import subprocess
import re
import urllib
import urllib2
import socket
import time

# splunk indexer object
class SplunkProxy:
    # Token value is for example but not valid. Need to get from real splunk indexer.
    __url = 'http://latitude.work.com:8088/services/collector/event'
    # system index
    # __headers = {'Authorization': 'Splunk 91F82F6C-0E99-6F8C-A723-F8C8693AEFEF', 'Content-Type': 'application/json'}
    # test index:
    __headers = {'Authorization': 'Splunk 90F68E68-9EAF-8D65-9D88-361F65E265C1', 'Content-Type': 'application/json'}
    __cmd = "POST"
    __events = None

    def __init__( self, server, port ):
        self.__url = "http://" + server + ":" + str(port) + "/services/collector/event"

    def setHeader( self, name, value ):
        self.__headers[name] = value

    def setTestMode( self ):
        self.setHeader('Authorization', 'Splunk 90F68E68-9EAF-8D65-9D88-361F65E265C1')

    def getRESTpoint(self):
        return self.__url

    def addEvent( self, data ):
        print "adding event: ", data
        if (self.__events):
            self.__events = self.__events + data
        else:
            self.__events = data
        print "Events: ", self.__events

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

    def post( self ):
        if (self.__events):
            print "sending all ..."
            print self.__url
            print self.__headers
            print self.__events
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            req = urllib2.Request(self.__url, self.__events, self.__headers)
            req.get_method = lambda: self.__cmd
            try:
                connection = opener.open(req)
            except urllib2.HTTPError, e:
                connection = e
            print "Response: ", connection.code

# event builder
class EventBuilder:
    __fields = []
    __hostname = "localhost"
    __timestamp = 0
    __jsondata = ""
    __index = None
    __sourcetype = "testdata"

    def __init__( self, fields ):
        self.__fields = fields
        self.__hostname = socket.gethostname()
        self.__timestamp = time.time()
        self.reset()

    def __init__( self, index, sourcetype, fields ):
        self.__index = index
        self.__sourcetype = sourcetype
        self.__fields = fields
        self.__hostname = socket.gethostname()
        self.__timestamp = time.time()
        self.reset()

    def reset( self ):
        if (self.__index):
            self.__jsondata = '{"source": "pycode", "index": "' + self.__index + '", "sourcetype": "' + self.__sourcetype + '", "host": "' + self.__hostname + '", "time": "' + str(self.__timestamp) + '"'
        else:
            self.__jsondata = '{"source": "pycode", "sourcetype": "' + self.__sourcetype + '", "host": "' + self.__hostname + '", "time": "' + str(self.__timestamp) + '"'

    def reinit( self, index, sourcetype ):
        self.setIndex(index)
        self.setSourcetype(sourcetype)
        self.reset()

    def setIndex(self, index):
        self.__index = index;

    def setSourcetype(self, sourcetype):
        self.__sourcetype = sourcetype;

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
            # if (self.__fields[i] == 'Use%'):
            #    data[i] = data[i][:-1]
            event = event + sep + '"' + self.__fields[i] + '": "' + data[i] + '"'
            print "%s: %s" % (self.__fields[i], data[i])
            sep = ", "

        event = event + "}"
        print "Built event: ", event
        self.__jsondata = self.__jsondata + ', ' + event

    def getJSONdata(self):
        data = self.__jsondata + "}"
        return data

############################################################################
# Splunk proxy instance
splunk = SplunkProxy("latitude.work.com", "8088")
# index = 'testidx'
index = 'bamboo_clnt_sys'
runningBuild = '0'

############################################################################
# Get vmstat data

# index = 'testidx'
# index = 'jenkins_clnt_sys'
sourcetype = 'vmstat'

# vmstat fields
# fields = ('total memory', 'used memory', 'active memory', 'inactive memory', 'free memory', 'buffer memory', 'swap cache', 'total swap', 'used swap', 'free swap', 'bootTime', 'io_in_rate', 'io_out_rate', 'CPU%_user', 'CPU%_sys', 'CPU%_idle', 'CPU%_io')

# Get process info
vm = subprocess.Popen(['vmstat', '-s'], stdout=subprocess.PIPE).communicate()[0]

# Process vm_stat
vmLines = vm.split('\n')
sep = re.compile(':[\s]+')
vmStats = {}
for row in vmLines:
    fields = row.split()
    if (len(fields) == 3):
        fieldname = fields[1] + ' ' + fields[2]
        vmStats[fieldname] = fields[0]
    elif ((len(fields) == 4) and (fields[1] == 'K')):
        fieldname = fields[2] + ' ' + fields[3]
        vmStats[fieldname] = fields[0]

fields = vmStats.keys()
dataItems = vmStats.values()
builder = EventBuilder(index, sourcetype, fields)
builder.buildEvent(dataItems)
splunk.addEvent( builder.getJSONdata() )



##################################################################
# Get appstat data

# index = 'testidx'
# index = 'jenkins_clnt_sys'
sourcetype = 'appstat'

fields = ('Application', 'User', 'PID', 'CPU%', 'MEM%', 'VSZ', 'RSS', 'State', 'Start', 'Time', 'Command')
wranglerCmd = 'run.py'
builder = EventBuilder(index, sourcetype, fields)

# Get process info
ps = subprocess.Popen(['/usr/ucb/ps', '-auxww'], stdout=subprocess.PIPE).communicate()[0]

# Process disk stat
# apps map: key = cmd, value = appname:
appsToMonitor = {'-Dbamboo.home=/export/home/release/bamboo' : 'BambooAgent'}
appsToExclude = ['cd']
appCmds = appsToMonitor.keys()
appsNotRun = appsToMonitor.keys()

processes = ps.split('\n')

sep = re.compile('[\s]+')
for row in processes:
    dataItems = sep.split(row)

    # Check whether build is currently running.
    if (wranglerCmd in dataItems):
        runningBuild = '1'

    appIdx = -1
    found = False
    for excmd in appsToExclude:
        if (excmd in dataItems):
            found = True
            break
    if (found is True):
        continue
    for appIdx in range(len(appCmds)):
        if (appCmds[appIdx] in dataItems):
            found = True
            break
    if (found is False):
        continue
    print "DEBUG: should post:", row
    appData = [str(appsToMonitor[appCmds[appIdx]]), str(dataItems[0]), str(dataItems[1]), str(dataItems[2]), str(dataItems[3]), '', '', str(dataItems[5])]
    startdatetime = str(dataItems[6]) + ' ' + str(dataItems[7])
    appData.append(startdatetime)
    appData.append(str(dataItems[8]))
    cmd = dataItems[9]
    for j in range(10, len(dataItems)):
        cmd = cmd + " " + str(dataItems[j])
    appData.append(cmd)
    builder.reset()
    builder.buildEvent(appData)
    splunk.addEvent( builder.getJSONdata() )
    if appCmds[appIdx] in appsNotRun:
        appsNotRun.remove(appCmds[appIdx])

for app in appsNotRun:
    appData = [str(appsToMonitor[app]), 'None', 'None', '0', '0', '0', '0', 'X', 'None', '0', app]
    builder.reset()
    builder.buildEvent(appData)
    splunk.addEvent( builder.getJSONdata() )

###############################################
# Get diskstat data
# print "Filesystem     1K-blocks     Used Available Use% Mounted on"

# index = 'testidx'
# index = 'clnt_sys'
sourcetype = 'diskstat'
fields = ('Filesystem', 'Total 1K-blocks', 'Used', 'Available', 'Use%', 'Mounted on', 'RunningBuild')
builder = EventBuilder(index, sourcetype, fields)

# Get process info
df = subprocess.Popen(['df', '-k'], stdout=subprocess.PIPE).communicate()[0]

# Process disk stat
monitoredVolumes = ('/', '/export/home', '/mnt/releases')
dfLines = df.split('\n')
# print "df lines:"
# print dfLines
totalLines = len(dfLines)
dataMatrix = []
idx = 1
while (idx < totalLines):
    # print idx
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
        dataItems.append(runningBuild)
    	dataMatrix.append(dataItems)
        if dataItems[5] in monitoredVolumes:
            print "DEBUG: should post:", dataItems
            dataItems[4] = dataItems[4][:-1]
            builder.reset()
            builder.buildEvent(dataItems)
            splunk.addEvent( builder.getJSONdata() )
    idx += 1

print "Retrieved items:"
print dataMatrix


##################################################################
# Send data to splunk.
splunk.post()
# exit()
