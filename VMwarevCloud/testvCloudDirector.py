
from manageVM import  *
from time import sleep


############## Internat Prologue 's VMware vCloud Director
vcloudconfig={'host': 'vcloudcell.prologue.prl', 'username': 'xxxxx', 'password': 'xxxxxx',
              'org': 'prologue', 'instance':'','vdc_name': 'vDC_prologue','service_type_name': 'vcd','VCD_version':'5.5','cert': False,'logFile':'pyvcd.log'}



vcloudVM= {'vApptemplate': 'Ubuntu12.04 x86_64', 'cataloguen': 'Linux','vAppname': 'VMkh','status':'','name':'','cpus':'','memory':'',
           'owner':'','os':'','rootpassword':'','computer_name':'uicb','privateaddress':'','publicaddress':'','macaddress':''
           ,'customization_script':'touch /tmp/file1219','access':'public','region':''}

vCloudvDCnet={'GWname':'EdgeGW','vDCorg_net':'vDCORGnetkh','start_address':'10.10.0.2','end_address':'10.10.0.254','gateway_ip':'10.10.0.1',
              'netmask':'255.255.255.0','dns1':'8.8.8.8','dns2':'8.8.4.4','dns_suffix':None,'FWrules':'' }


'''
############## Alhambra'is VMware vCloud director
vcloudconfig={'host': 'clouddemo.a-e.es', 'username': 'adminco', 'password': 'prologue',
              'org': 'PROLOGUE', 'instance':'','vdc_name': 'vDC-PROLOGUE-CLOUDPORT','service_type_name': 'vcd','VCD_version':'1.5','cert': False,'logFile':'pyvcd.log'}
#cert=/root/git/pyvcloud/VMwarevCloud/vcloudcell.prologue.prl

vcloudVM= {'vApptemplate': 'Ubuntu12.04 x86_64', 'cataloguen': 'Linux','vAppname': 'VM40','status':'','name':'','cpus':'','memory':'',
           'owner':'','os':'','rootpassword':'','computer_name':'uicb','privateaddress':'','publicaddress':'','macaddress':''
           ,'customization_script':'touch /tmp/file1219','access':'public','region':''}


vCloudvDCnet={'GWname':'EdgeGW','vDCorg_net':'vDCORGnet0','start_address':'10.10.0.2','end_address':'10.10.0.50','gateway_ip':'10.10.0.1',
              'netmask':'255.255.255.0','dns1':'8.8.8.8','dns2':'8.8.4.4','dns_suffix':None,'FWrules':'' }
'''

#First call to create Vm with Network configuration

result = create_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)


result = poweroff_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)

result = poweron_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)


result = reboot_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)

result = reset_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)


result = suspend_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)

result = poweron_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)


result = delete_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)
