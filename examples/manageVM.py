from pyvcloud.vcloudair import *
from pyvcloud.vapp import *
from vcclient import  *
import string
import random
import sys, traceback
import requests
from random import randint
####logging
import logging
import httplib
from twisted.spread.ui.gtk2util import login
from time import sleep


#### Initialise Logging params*
httplib.HTTPConnection.debuglevel = 1
logging.basicConfig(filename='pyvcloud.log',level=logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)


def create_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    #generate root password
    lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(8)]
    vcloudVM['rootpassword'] ="".join(lst)
    
    vca = authenticatevcd(host=vcloudconfig['host'], org=vcloudconfig['org'], username=vcloudconfig['username'], password=vcloudconfig['password'],service_type=vcloudconfig['service_type_name'], VCD_version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'], logging=logging)

    vDC= findvDC(vca=vca,vdc_name=vcloudconfig['vdc_name'],logging=logging)
    
    result = findvApptemplate(vca=vca, vDC=vDC, vApptemplate=vcloudVM['vApptemplate'], logging=logging)
    
    ###List vailable vApps not already implemented
    
    pass
    
    ######Get quota not already implemented
    
    pass
    
    ###verify if vApp exists
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc):
        logging.warn("vApp already exists, please delete vApp before creating")
        return False
    else:
        pass

    ###create vApp from existing vApptemplate
    ### Set up VM flavor not already implementded
    
    task = vca.create_vapp(vdc_name=vcloudconfig['vdc_name'], vapp_name=vcloudVM['vAppname'], template_name=vcloudVM['vApptemplate'],
                         catalog_name=vcloudVM['cataloguen'], network_name=None, vm_name=None, vm_cpus=None,
                         vm_memory=None, deploy='false',poweron='false')
    
    ###Block until task completed
    if(task == False):
        logging.error('An error occured while deploying, please contact your cloud administrator')
    else:
        result = vca.block_until_completed(task)
        if(result == False):
            logging.error('An error occured while deploying, please contact your cloud administrator')
        else:
            logging.info("deploying vApp succeeded")
    
    
    
    ###Update VM details
    result = updateVMdetails(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,logging=logging)
    
    ##customize vApp 
    result = customizevApp(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,logging=logging) 
    
    #################Network Configuration
    ##### Find Edge gateway
    GW = findEdgegateway ( vca = vca, vdc_name = vcloudconfig['vdc_name'], GWname = vCloudvDCnet['GWname'],logging = logging)
    
    
    ###create or get vDC net
    Nethref= get_or_create_vDCnet(vca=vca,vdc_name = vcloudconfig['vdc_name'],vCloudvDCnet=vCloudvDCnet,logging=logging)
    
    #### Connect VM under vApp to  vDC network
    result = connect_VM_to_vDCnet(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,vCloudvDCnet=vCloudvDCnet,Nethref=Nethref,logging=logging) 
    
    ###Update VM's Network params
    result=update_VM_net_info(vca=vca,vcloudVM=vcloudVM,vcloudconfig=vcloudconfig,logging=logging)
    
    
    ####Configure Firewall rules , DNAT, SNAT in the Edge gateway
    #Allocate public IP
    #Allocate public IP in the chosen Gateway
    result= allocate_publicIP_on_GW(GW=GW,vcloudVM=vcloudVM,logging=logging)
    #Configure dhcp
    result = configuredhcp(GW=GW,vCloudvDCnet=vCloudvDCnet,logging=logging)
    #Configure Nat rules
    result = configureNat(GW=GW,vcloudVM=vcloudVM,vCloudvDCnet=vCloudvDCnet,logging=logging)
    #Configure Firewall rules
    result = configureFWrules(GW=GW,vcloudVM=vcloudVM,vCloudvDCnet=vCloudvDCnet,logging=logging)
    
    
    ##power on vApp
    logging.info("First powering on with force guest customization")
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    task  = vappc.force_customization(vm_name=vcloudVM['name'])
    #block task
    if((task == False) | (task == None)):
        logging.error('An error occured while powering on vApp')
        sys.exit(0)
    else:
        result = vca.block_until_completed(task)
        if(result == False):
            logging.error('An error occured while powering on vApp')
            sys.exit(0)
        else:
            logging.info("Powering on vApp succeeded")
    return True
    


def poweroff_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    ##power on vApp
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc == None):
        logging.info('canno\'t retreive vApp, please verify vApp existance')
    result = vappc.poweroff()
    return True


def rebooting_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
##power off vApp
    logging.info("rebooting vApp")
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc==None):
        logging.warn('canno\'t retreive vApp')
        return False
    result = vappc.reboot()
    wait(20)
    return True

def resetting_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    logging.info("resetting  vApp")
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc==None):
        logging.warn('canno\'t reset vApp')
        return False
    result = vappc.reset()
    wait(20)
    return True
    

def suspend_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    logging.info("suspending  vApp")
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc==None):
        logging.warn('canno\'t suspend vApp')
        return False
    result = vappc.suspend()
    wait(20)
    return True


def suspend_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    logging.info("suspending  vApp")
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc==None):
        logging.warn('canno\'t suspend vApp')
        return False
    result = vappc.suspend()
    wait(20)
    return True



def delete_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    ##Disconnect vApp from Network
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    task = vappc.disconnect_from_network(network_name=vCloudvDCnet['vDCorg_net'])
    ###Block until task completed
    if(task == False):
        logging.error('An error occured while deconnecting vApp form vDC network')
    else:
        result = vca.block_until_completed(task)
        if(result == False):
            logging.error('An error occured while deconnecting vApp form vDC network')
        else:
            logging.info("deconnecting vApp from vDC net succeeded")

    logging.info("deleting  vApp")
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc==None):
        logging.warn('canno\'t delete vApp')
        return False
    result = vappc.delete()
    wait(20)
    return True


