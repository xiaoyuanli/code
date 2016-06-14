#!/usr/bin/python
'''
# -*- coding: utf-8 -*-
'''

import subprocess
import re
import urllib
import urllib2
import socket
import time
import httplib
import requests
import json

# splunk indexer object
class SplunkProxy:
    __url = 'http://latitude.work.com:8088/services/collector/event'
    # __url = 'http://localhost:8088/services/collector/event'
    # resystem index
    # __headers = {'Authorization': 'Splunk 91E82F8C-0E99-9F8C-A723-F8C8693AEFEF', 'Content-Type': 'application/json'}
    # resystem/testidx index
    __headers = {'Authorization': 'Splunk 90F68F68-9EAF-8E65-9D89-361F65D265C1', 'Content-Type': 'application/json'}
    # test index:
    # __headers = {'Authorization': 'Splunk FE8B331E-2695-8525-86E5-5A5FAB7928CF',}
    #__headers = {'Authorization': 'Splunk FE9B331E-2695-9525-86E5-5A5FAB7928CF', 'Content-Type': 'application/json','charset':'utf-8'}
    __cmd = "POST"
    __events = None

    def __init__( self, server, port ):
        self.__url = "http://" + server + ":" + str(port) + "/services/collector/event"

    def setHeader( self, name, value ):
        self.__headers[name] = value

    def setTestMode( self ):
        self.setHeader('Authorization', 'Splunk FE4B331E-2695-4525-86E5-5A5FAB7928CF')

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

            headers = {'Authorization': 'Splunk 90E68F68-9EAF-8D65-9D88-391F65E265C1',}
                # 'Authorization': 'Splunk FE9B331E-2695-8525-86E5-5A5FAB7928CF',

            data = '{"event": "hello world 3"}'
            #data = '{"event": {"source": "pyagent", "index": "testidx"}}'
            #data =  '{"event": {"reactivated: 2389314.": "Pages", "active: 1752582.": "Pages"}}'
            #data =  '{"source": "pyagent", "event": {"active": "100", "inactive": "200"}}'
   

	    print "sending"	
            try:
                r = requests.post(self.__url, headers=headers, data=self.__events)
                print  r.status_code
            except:
                print "fail"
'''
            if(r.status_code==400):
                exit()
'''






# event builder
class EventBuilder:
    __fields = []
    __hostname = "localhost"
    __timestamp = 0
    __jsondata = ""
    # __index = 'resystem'
    __index = 'testidx'
    # __index = None
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
            self.__jsondata = '{"source": "pyagent", "index": "' + self.__index + '", "sourcetype": "' + self.__sourcetype + '", "host": "' + self.__hostname + '", "time": "' + str(self.__timestamp) + '"'
        else:
            self.__jsondata = '{"source": "pyagent", "sourcetype": "' + self.__sourcetype + '", "host": "' + self.__hostname + '", "time": "' + str(self.__timestamp) + '"'

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
            event = event + sep + '"' + str(self.__fields[i]) + '": "' + str(data[i]) + '"'
            print "%s: %s" % (self.__fields[i], data[i])
            sep = ", "

        event = event + "}"
        print "Built event:\r\n", event
        self.__jsondata = self.__jsondata + ', ' + event

    def getJSONdata(self):
        data = self.__jsondata + "}"
        return data

############################################################################
# Splunk proxy instance
# splunk = SplunkProxy("10.19.3.196", "8088")
splunk = SplunkProxy("latitude.work.com", "8088")
index = 'test'
# index = 'system'
runningBuild = '0'



############################################################################
# Get vmstat data

sourcetype = 'vmstat'

# vmstat fields
# fields = ('total memory', 'free memory', 'used memory', 'active memory', 'inactive memory', 'buffer memory', 'swap cache', 'total swap', 'used swap', 'free swap', 'bootTime', 'io_in_rate', 'io_out_rate', 'CPU%_user', 'CPU%_sys', 'CPU%_idle', 'CPU%_io')
vmfields = ['total memory', 'free memory', 'total swap', 'free swap', 'used swap', 'used memory']

# Get process info
#vm = subprocess.Popen([systeminfo], stdout=subprocess.PIPE).communicate()[0]
vm = subprocess.Popen("systeminfo|findstr Memory", shell=True, stdout=subprocess.PIPE).communicate()[0]
print vm

# Process vm_stat
vmLines = vm.split('\r\n')
sep = re.compile(':[\s]+')
vmStats = {}
allFields = []
allEntries = []


for row in vmLines:
	if row != "":
		splitRow = row.split(": ")
		field = re.findall("[\a-z :]+:", row)[0]
		entry = re.findall("[0-9,]+[ A-Z]+", row)[0]
		field = field[:-1]
		entry = entry[:-3]
		entry = entry.translate(None, ',')
		allFields.append(field)
		allEntries.append(entry)

TotalMemory = int(allEntries[0])
usedMemory = TotalMemory - int(allEntries[1])
allFields.append('Used Physical Memory')
allEntries.append(usedMemory)

print allFields
print allEntries
print "TotalMemory =", TotalMemory

#fields = vmStats.keys()

#dataItems = vmStats.values()
builder = EventBuilder(index, sourcetype, vmfields)
# builder = EventBuilder(index, sourcetype, allFields)
#builder.buildEvent(dataItems)
builder.buildEvent(allEntries)
print "Built event is "
print builder.getJSONdata()

splunk.addEvent( builder.getJSONdata() )

# test mvstat
# exit()

##################################################################

#Process diskstat info

sourcetype = "diskstat"
fields = ['Free', 'Total 1K-blocks', 'Available', 'Used', 'Use%', 'Mounted on']
diskstat = subprocess.Popen("fsutil volume diskfree C:", shell=True, stdout=subprocess.PIPE).communicate()[0]
print diskstat

diskstatLines = diskstat.split('\r\n')
sep = re.compile(':[\s]+')
vmStats = {}
allFields = []
allEntries = []


for row in diskstatLines:
	if row != "":
		splitRow = row.split(": ")
		field = re.findall("[\a-z :]+:", row)[0]
		entry = re.findall("[0-9,]+[ A-Z]*", row)[0]
		field = str(field)
		field = field[:-1]
		allFields.append(field)
		entry = int(entry) / 1024
		allEntries.append(entry)

print allFields
print allEntries

TotalVolume = int(allEntries[1])
used = TotalVolume - int(allEntries[0])
allEntries.append(used)

use_percent = (used * 100) / TotalVolume
allEntries.append(use_percent)
allEntries.append('c:')


builder = EventBuilder(index, sourcetype, fields)
#builder.buildEvent(dataItems)
builder.buildEvent(allEntries)
print "Built event is "
print builder.getJSONdata()

splunk.addEvent( builder.getJSONdata() )

# test diskstat
# exit()

###################################################################

#Process appstat info

sourcetype = "appstat"
appsToMonitor = {'slave.jar' : 'JenkinsAgent', 'cmd.exe' : 'TestCmd'}
appsToExclude = ['cd']
appCmds = appsToMonitor.keys()
appsNotRun = appsToMonitor.keys()

fields = ('Command', 'PID', 'SessionName', 'Session', 'MEM%', 'State', 'User', 'CPUtime')
# fields = ('Command', 'PID', 'SessionName', 'Session', 'MEM%', 'State', 'User', 'CPUtime', 'Window Title')

appstat = subprocess.Popen("tasklist -v", shell=True, stdout=subprocess.PIPE).communicate()[0]

appstatLines = appstat.split('\r\n')
sep = re.compile(':[\s]+')
#allEntries = []

print "Commads to look up", appCmds
print "num lines is "
print len(appstatLines)

for i in range(3,len(appstatLines)-1):

        line = appstatLines[i]
        allEntries = []
	
        # print "line is "
        # print i
        # print line 
	
        #create delimiter for Image Name 
        delim = re.compile(".*?(?=\s{2})")
        #extract the field from regex
        cmd = re.search(delim, line).group(0)
        #split into a new line without delimiter 
        line = delim.split(line,1)[1]
        #escape \ characters
        cmd = json.dumps(cmd, encoding="utf8")
        cmd = cmd.replace('\"', " ")
        cmd = cmd.strip()

        # print "image name is "
        # print cmd

        if (cmd in appCmds):
            allEntries.append(str(cmd))
            print "found", cmd
        else:
            # print "ignore it."
            continue
        
        print "remaining line is "
        print line

        #create delimiter for PID
        delim = re.compile("[0-9]+")
        pid = re.search(delim, line).group(0)
        line = delim.split(line,1)[1]
        allEntries.append(pid)
        
        print "PID =", pid
        print "remaining line is =", line

        #create delimiter for Session Name
        delim = re.compile("[^\s].*?(?=\s{2})")
        sessionName = re.search(delim, line).group(0)
        line = delim.split(line,1)[1]
        allEntries.append(str(sessionName))

        print "Session Name =", sessionName
        print "remaining line =", line

        #create delimiter for Session Number 
        delim = re.compile("[0-9]+")
        session = re.search(delim, line).group(0)
        line = delim.split(line,1)[1]
        allEntries.append(str(session))

        print "Session =", session
        print "remaining line =", line

        #create delimiter for Mem Usage
        delim = re.compile("[0-9,]+\s\w+\s")
        mem = re.search(delim, line).group(0)
        line = delim.split(line,1)[1]
        mem = mem.strip(' K')
        mem = mem.replace(',', '')
        mem = (float(mem) / 10) / TotalMemory
        mem_percent = "%.2f" % mem
        allEntries.append(str(mem_percent))

        print "Mem% is "
        print mem
        print "remaining line is "
        print line
        # print "Total Memory", TotalMemory

        #create delimiter for Status 
        delim = re.compile(".*?(?=\s{2})")
        entry = re.search(delim, line).group(0)
        line = delim.split(line,1)[1]
        allEntries.append(str(entry))

        print "Status is "
        print entry
        print "new line is "
        print line
        print ""

        # create delimiter for User Name (regex is first nonspace char to two consecutive spaces)
        delim = re.compile("[^\s].*?(?=\s{2})")
        entry = re.search(delim, line).group(0)
        line = delim.split(line,1)[1]
        entry = str(entry)

        # print "json dump is "
        #entry = entry.replace("\\","\\\\")
        entry = json.dumps(entry, encoding="utf8")
        entry = entry.replace('\"', " ")
        # print entry

        print "user name =", entry
        print "remaining line =", line

        allEntries.append(entry)

        #create delimiter for time 
        delim = re.compile("[0-9:]+")
        entry = re.search(delim, line).group(0)
        line = delim.split(line,1)[1]
        allEntries.append(str(entry))

        print "Time is "
        print entry
        print "new line is "
        print line
        print ""

        #create delimiter for Window Title 
        #delim = re.compile("[^\s].*?(?=\s{2})")
        delim = re.compile("[^\s].*")
        
        entry = re.search(delim, line).group(0)
        line = delim.split(line,1)[1]
        entry = json.dumps(entry, encoding="utf8")
        entry = entry.replace('\"', " ")
        # allEntries.append(str(entry))

        print "window title =", entry
        print "remaining line =", line

        builder = EventBuilder(index, sourcetype, fields)
        builder.buildEvent(allEntries)
        print "Built event is "
        print builder.getJSONdata()
        splunk.addEvent( builder.getJSONdata() )

        # test appstat
        # exit()

        # splunk.post()
	
# print "finished tasklist"	
	
# test only
# exit()


# Send data to splunk.
splunk.post()

# exit()
