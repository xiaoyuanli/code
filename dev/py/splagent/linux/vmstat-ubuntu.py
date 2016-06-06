#!/usr/bin/python
# Created by: Xiaoyuan Li
import subprocess
import re
import urllib
import urllib2
import socket
import time

# Get process info
vm = subprocess.Popen(['vmstat', '-s'], stdout=subprocess.PIPE).communicate()[0]

# Process vm_stat
vmLines = vm.split('\n')
sep = re.compile(':[\s]+')
vmStats = {}
for row in vmLines:
    fields = row.split()
    if ((len(fields) == 4) and (fields[1] == 'K')):
        fieldname = fields[2] + ' ' + fields[3]
        vmStats[fieldname] = fields[0]

# print vmStats
# token value is for example but not valid.
url = "http://latitude.work.com:8088/services/collector/event"
cmd = "POST"
headers = {'Authorization': 'Splunk 91E62F8C-0E99-6F8C-A723-F8C8693AEFEF', 'Content-Type': 'application/json'}
hostname = socket.gethostname()
timestamp = time.time()
jsondata = '{"source": "pycode", "sourcetype": "vmstat"' + ', "host": "' + hostname + '", "time": "' + str(timestamp) + '"'
# jsondata = jsondata + ', "host": "' + hostname + '"'

# build event
fieldSep = ""
jsondata = jsondata + ', "event": {'
for key in vmStats:
    # print key, ": ", vmStats[key]
    val = int(vmStats[key]) / 1024
    jsondata = jsondata + fieldSep + '"' + key + '": "' + str(val) + '"'
    print "%s: %s MB" % (key, val)
    fieldSep = ", "

jsondata = jsondata + "}}"
print "json data:"
print jsondata
print headers
print url
# print 'Wired Memory:\t\t%d MB' % ( vmStats["Pages wired down"]/1024/1024 )
# print 'Active Memory:\t\t%d MB' % ( vmStats["Pages active"]/1024/1024 )
# print 'Inactive Memory:\t%d MB' % ( vmStats["Pages inactive"]/1024/1024 )
# print 'Free Memory:\t\t%d MB' % ( vmStats["Pages free"]/1024/1024 )
#print 'Real Mem Total (ps):\t%.3f MB' % ( rssTotal/1024/1024 )

# send request:
handler = urllib2.HTTPHandler()
opener = urllib2.build_opener(handler)
req = urllib2.Request(url, jsondata, headers)
# req.add_header(headers)
req.get_method = lambda: cmd

try:
    connection = opener.open(req)
except urllib2.HTTPError, e:
    connection = e

print connection.code

# res = response.read()

exit()
