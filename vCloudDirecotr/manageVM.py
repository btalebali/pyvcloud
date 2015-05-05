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
        return False
    else:
        result = vca.block_until_completed(task)
        if(result == False):
            logging.error('An error occured while powering on vApp')
            return False
        else:
            logging.info("Powering on vApp succeeded")
    time.sleep(5)
    result = updateVMstatus(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,logging=logging)
    return True

def poweroff_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    vca = authenticatevcd(host=vcloudconfig['host'], org=vcloudconfig['org'], username=vcloudconfig['username'], password=vcloudconfig['password'],service_type=vcloudconfig['service_type_name'], VCD_version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'], logging=logging)
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc == None):
        logging.info('canno\'t retreive vApp, please verify vApp status')
    task = vappc.poweroff()
    #block task
    if((task == False) | (task == None)):
        logging.error('An error occured while powering off vApp')
        return False
    else:
        result = vca.block_until_completed(task)
        if(result == False):
            logging.error('An error occured while powering off vApp')
            return False
        else:
            logging.info("Powering off vApp succeeded")
    time.sleep(5)
    result = updateVMstatus(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,logging=logging)
    return True


def poweron_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    vca = authenticatevcd(host=vcloudconfig['host'], org=vcloudconfig['org'], username=vcloudconfig['username'], password=vcloudconfig['password'],service_type=vcloudconfig['service_type_name'], VCD_version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'], logging=logging)
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc == None):
        logging.info('canno\'t retreive vApp, please verify vApp status')
    task = vappc.poweron()
    #block task
    if((task == False) | (task == None)):
        logging.error('An error occured while powering on vApp')
        return False
    else:
        result = vca.block_until_completed(task)
        if(result == False):
            logging.error('An error occured while powering on vApp')
            return False
        else:
            logging.info("Powering on vApp succeeded")
    time.sleep(5)
    result = updateVMstatus(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,logging=logging)
    return True


def reboot_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    logging.info("rebooting vApp")
    vca = authenticatevcd(host=vcloudconfig['host'], org=vcloudconfig['org'], username=vcloudconfig['username'], password=vcloudconfig['password'],service_type=vcloudconfig['service_type_name'], VCD_version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'], logging=logging)
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc==None):
        logging.warn('canno\'t retreive vApp')
        return False
    task = vappc.reboot()
    #block task
    if(task == None):
        time.sleep(30)
    result = updateVMstatus(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,logging=logging)
    return True

def reset_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    logging.info("resetting  vApp")
    vca = authenticatevcd(host=vcloudconfig['host'], org=vcloudconfig['org'], username=vcloudconfig['username'], password=vcloudconfig['password'],service_type=vcloudconfig['service_type_name'], VCD_version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'], logging=logging)
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc==None):
        logging.warn('canno\'t reset vApp')
        return False
    task = vappc.reset()
    if(task == None):
        time.sleep(40)
    result = updateVMstatus(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,logging=logging)
    return True

def suspend_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    logging.info("suspending  vApp")
    vca = authenticatevcd(host=vcloudconfig['host'], org=vcloudconfig['org'], username=vcloudconfig['username'], password=vcloudconfig['password'],service_type=vcloudconfig['service_type_name'], VCD_version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'], logging=logging)
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    if(vappc==None):
        logging.warn('canno\'t suspend vApp')
        return False
    task = vappc.suspend()
    if(task == None):
        time.sleep(15)
    result = updateVMstatus(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,logging=logging)
    return True

def delete_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    
    if(vcloudVM['status']=="Powered on"):
        vca = authenticatevcd(host=vcloudconfig['host'], org=vcloudconfig['org'], username=vcloudconfig['username'], password=vcloudconfig['password'],service_type=vcloudconfig['service_type_name'], VCD_version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'], logging=logging)
        vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
        task = vappc.undeploy()
        #block task
        if((task == False) | (task == None)):
            logging.error('An error occured while undeplo vApp')
            return False
        else:
            result = vca.block_until_completed(task)
            if(result == False):
                logging.error('An error occured while undeplo vApp')
                return False
            else:
                logging.info("undeploy vApp succeeded")

        vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
        task = vappc.delete()
        if((task == False) | (task == None)):
            logging.error('An error occured while deleting vApp')
            return False
        else:
            result = vca.block_until_completed(task)
            if(result == False):
                logging.error('An error occured while deleting vApp')
                return False
            else:
                logging.info("deleting vApp succeeded")
                vcloudVM['status']='deleted'
                return True
        
    if(vcloudVM['status']=="Powered off"):
        vca = authenticatevcd(host=vcloudconfig['host'], org=vcloudconfig['org'], username=vcloudconfig['username'], password=vcloudconfig['password'],service_type=vcloudconfig['service_type_name'], VCD_version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'], logging=logging)
        vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
        task = vappc.delete()
        if((task == False) | (task == None)):
            logging.error('An error occured while deleting vApp')
            return False
        else:
            result = vca.block_until_completed(task)
            if(result == False):
                logging.error('An error occured while deleting vApp')
                return False
            else:
                logging.info("deleting vApp succeeded")
                vcloudVM['status']='deleted'
                return True
    return False

