####################################################################
####################################################################
from pyvcloud.vcloudair import *
from pyvcloud.vapp import *
import json
import requests
from vcrestclient import *
import time
import urllib2
import re
import uuid
from pyclient import *
from pyvcloud.vcloudair import *
from pyvcloud.vapp import *
host='https://vcloudcell.prologue.prl'
username = "xxxx"
password = "xxxxx"
servicetype = "vcd"
organisation = "prologue"
vdcname="vDC_prologue"
gatewayname="EdgeGW"
version="5.1"
from vcclient import *

while True:
  vca = vcloud_connect(host, username, password, organisation, version, servicetype = "vcd")
  the_gateway = vca.get_gateway(vdcname,gatewayname)
  gwbusy=the_gateway.is_busy()
  print "gwbusy=", gwbusy
  tstep = 5
  i = 0
  while (gwbusy == True):
    i = i + tstep
    time.sleep(tstep)
    vca.logout()
    vca = vcloud_connect(host, username, password, organisation, version, servicetype = "vcd")
    the_gateway = vca.get_gateway(vdcname,gatewayname)
    gwbusy = the_gateway.is_busy()
    print "gwbusy=", gwbusy
    if (( i >= 120) and (gwbusy==True)):
      vca.logout()
      print "the gateway is busy for more than two mn"
      sys.exit()
  the_gateway.add_fw_rule(is_enable=True, description='external http access', policy='allow', protocol='Tcp', dest_port='80', dest_ip='external',source_port='Any', source_ip='internal', enable_logging=False) 
  task = the_gateway.save_services_configuration()
  result=block_task_completed(host,username,password,organisation,version,task,60)
  if (the_gateway.response.ok==True):
    break

print "result=", result
print "response=", the_gateway.response.text

