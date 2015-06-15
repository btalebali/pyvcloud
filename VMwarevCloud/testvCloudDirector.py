
from manageVM import  *
from time import sleep


############## vCloud Director Standalone loding params (two dictionaries)
vcloudconfig={'host': 'vcloudcell.prologue.prl', 'username': 'uicbm', 'password': 'u15i21cb21m0',
              'org': 'prologue', 'instance':'','vdc_name': 'vDC_prologue','service_type_name': 'vcd','VCD_version':'5.5','cert': False,'logFile':'pyvcd.log'}
#cert=/root/git/pyvcloud/VMwarevCloud/vcloudcell.prologue.prl

vcloudVM= {'vApptemplate': 'Ubuntu12.04 x86_64', 'cataloguen': 'Linux','vAppname': 'VM40','status':'','name':'','cpus':'','memory':'',
           'owner':'','os':'','rootpassword':'','computer_name':'uicb','privateaddress':'','publicaddress':'','macaddress':''
           ,'customization_script':'touch /tmp/file1219','access':'public','region':''}


vCloudvDCnet={'GWname':'EdgeGW','vDCorg_net':'vDCORGnet4','start_address':'10.40.0.2','end_address':'10.40.0.50','gateway_ip':'10.40.0.1',
              'netmask':'255.255.255.0','dns1':'8.8.8.8','dns2':'8.8.4.4','dns_suffix':None,'FWrules':'' }

#First call to create Vm with Network configuration
result = create_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)
'''
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
'''