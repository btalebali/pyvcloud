from manageVM import *
from time import sleep



############## vCloud Air ondemad subscription loading params (three dictionaries)
vcloudconfig={'host': 'iam.vchs.vmware.com', 'username': 'vcloudair@prologue.fr', 'password': 'P1Dps45!sd@21q',
              'org': '', 'instance':'','vdc_name': 'VDC1','service_type_name': 'ondemand','VCD_version':'5.7','cert': True,'logFile':'pyvca.log'}


vcloudVM= {'vApptemplate': 'CentOS64-32BIT', 'cataloguen': 'Public Catalog','vAppname': 'VM01','status':'','name':'','cpus':'',
           'memory':'','owner':'','os':'','rootpassword':'','computer_name':'uicb','privateaddress':'','publicaddress':'','macaddress':'','customization_script':'touch /tmp/file1219','access':'public','region':''}


vCloudvDCnet={'GWname':'gateway','vDCorg_net':'default-routed-network0','start_address':'10.10.0.2','end_address':'10.10.0.50','gateway_ip':'10.10.0.1',
              'netmask':'255.255.255.0','dns1':'8.8.8.8','dns2':'8.8.4.4','dns_suffix':None,'FWrules':'' }

#First call to create Vm with Network configuration
#Notes: Make sure that there is not any vcloud air session is active where This code is executed (to avoid he use of the same source IP authetification)

#get regions
regions=get_vca_regions(vcloudconfig)

# select region
region=regions[0]
print("region = ",str(region))
vcloudVM['region']=str(region)

#get instanceID
Instance = get_vca_InstanceId_per_region(vcloudconfig,vcloudVM['region'])
vcloudconfig['instance']=str(Instance[0])

#Get org name
orgname=get_vca_Orgname_per_region(vcloudconfig,vcloudVM['region'])
vcloudconfig['org']=str(orgname)
print("organization  = ",str(orgname))

##Get available catalogs


##Get vApptemplate per catalogues




result = create_VM(vcloudVM,vcloudconfig,vCloudvDCnet)
print(result,vcloudVM)
time.sleep(30)
print(region)


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

