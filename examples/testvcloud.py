
from manageVM import  *



############## vCloud Director Standalone loding params (two dictionaries)
vcloudconfig={'host': 'vcloudcell.prologue.prl', 'username': 'uicbm', 'password': 'u15i21cb21m0',
              'org': 'prologue', 'vdc_name': 'vDC_prologue','service_type_name': 'vcd','VCD_version':'5.5','cert': False}

vcloudVM= {'vApptemplate': 'Ubuntu12.04 x86_64', 'cataloguen': 'Linux','vAppname': 'VM21','status':'','name':'','cpus':'',
           'memory':'','owner':'','os':'','rootpassword':'','computer_name':'uicb','privateaddress':'','publicaddress':'','macaddress':'','customization_script':'touch /tmp/file1219'}


vCloudvDCnet={'GWname':'EdgeGW','vDCorg_net':'vDCORGnet2','start_address':'10.10.20.2','end_address':'10.10.20.50','gateway_ip':'10.10.20.1',
              'netmask':'255.255.255.0','dns1':'8.8.8.8','dns2':'8.8.4.4','dns_suffix':None,'FWrules':'' }


result = create_VM(vcloudVM,vcloudconfig,vCloudvDCnet)