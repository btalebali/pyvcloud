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
import urlparse



def create_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
        #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    #TODO Add rotate to log file
    
    #generate root password
    lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(8)]
    vcloudVM['rootpassword'] ="".join(lst)
    vca = authenticatevc_service(vcloudconfig=vcloudconfig,logging=logging)
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
                         catalog_name=vcloudVM['cataloguen'], network_name=None, vm_name=None, vm_cpus = None,
                         vm_memory=None, deploy='false',poweron='false')
    
    ###Block until task completed
    bool = block_task_to_complete(vca,task,logging)

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
    result= allocate_publicIP_on_GW(vca=vca,GW=GW,vcloudVM=vcloudVM,vcloudconfig=vcloudconfig,vCloudvDCnet=vCloudvDCnet,logging=logging)
    print(vcloudVM['publicaddress'])
    #Configure dhcp
    # Notes: For VCA 'add_dhcp_service' is not defined !!!
    #result = configuredhcp(GW=GW,vCloudvDCnet=vCloudvDCnet,logging=logging)

    #Configure Firewall rules
    vca = authenticatevc_service(vcloudconfig=vcloudconfig,logging=logging)
    result = configureFWrules(vca=vca,GW=GW,vcloudVM=vcloudVM,vCloudvDCnet=vCloudvDCnet,logging=logging)

        ##power on vApp
    logging.info("First powering on with force guest customization")
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    task  = vappc.force_customization(vm_name=vcloudVM['name'])
    
    bool = block_task_to_complete(vca,task,logging)
        #Configure Nat rules
    vca = authenticatevc_service(vcloudconfig=vcloudconfig,logging=logging)
    result = configureSNat(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,vCloudvDCnet=vCloudvDCnet,logging=logging)
    if(vcloudVM['access']=='public'):
        result = configureDNat(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,vCloudvDCnet=vCloudvDCnet,logging=logging)

    time.sleep(5)
    result = updateVMstatus(vca=vca,vcloudconfig=vcloudconfig,vcloudVM=vcloudVM,logging=logging)
    return True

def poweroff_VM(vcloudVM,vcloudconfig,vCloudvDCnet):
    #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    #TODO Add rotate to log file
    vca = authenticatevc_service(vcloudconfig=vcloudconfig, logging=logging)
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
    #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    #TODO Add rotate to log file
    
    vca = authenticatevc_service(vcloudconfig=vcloudconfig, logging=logging)
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
            #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    #TODO Add rotate to log file
    
    logging.info("rebooting vApp")
    vca = authenticatevc_service(vcloudconfig=vcloudconfig,logging=logging)
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
            #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    #TODO Add rotate to log file
    
    logging.info("resetting  vApp")
    vca = authenticatevc_service(vcloudconfig=vcloudconfig,logging=logging)
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
            #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    #TODO Add rotate to log file
    
    logging.info("suspending  vApp")
    vca = authenticatevc_service(vcloudconfig=vcloudconfig,logging=logging)
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
            #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    #TODO Add rotate to log file
    
    if(vcloudVM['status']=="Powered on"):
        vca = authenticatevc_service(vcloudconfig=vcloudconfig,logging=logging)
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
        vca = authenticatevc_service(vcloudconfig=vcloudconfig,logging=logging)
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


#### Actions for VCA
def get_vca_regions(vcloudconfig):
            #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    
    if(vcloudconfig['service_type_name']=='vcd'):
        logging.error('Get region is not allowed for local vCloud Director')
        return False
    if((vcloudconfig['service_type_name']=='ondemand')|(vcloudconfig['service_type_name']=='subscription')):
        vca = VCA(host=vcloudconfig['host'], username=vcloudconfig['username'], service_type=vcloudconfig['service_type_name'], version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'])
        bool1 = vca.login(password = vcloudconfig['password'], org=vcloudconfig['org'])
        if(bool1==False):
            logging.error('Authentification failed, please verify credentials')
        instances=vca.get_instances()
        if(instances):
            regions={}
            for n in range(len(instances)):
                regions[n]= instances[n]['region']
            return regions
        else:
            logging.error('Unable to retreive VCA regions')
            return False
    else:
        logging.error('verify VCA Cloud service Subscription')
        return False


def get_vca_Orgname_per_region(vcloudconfig,region):
            #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    
    if(vcloudconfig['service_type_name']=='vcd'):
        # TODO Add vCloud Director standalone region
        logging.error('function not allowed for local vCloud Director')
        return False
    if((vcloudconfig['service_type_name']=='ondemand')|(vcloudconfig['service_type_name']=='subscription')):
        #authentication to service
        vca = VCA(host=vcloudconfig['host'], username=vcloudconfig['username'], service_type=vcloudconfig['service_type_name'], version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'])
        bool1 = vca.login(password = vcloudconfig['password'], org=vcloudconfig['org'])
        if(bool1==False):
            logging.error('Authentification failed, please verify credentials')
        instances=vca.get_instances()
        if(instances):
            regions={}
            for n in range(len(instances)):
                regions[n]= instances[n]['region']
                if(instances[n]['region']==region):
                    decoded = json.loads(instances[n]['instanceAttributes'])
                    orgName=decoded["orgName"]
                    return orgName
        else:
            logging.error('Unable to retreive VCA org name')
            return False
    else:
        logging.error('verify VCA Cloud service Subscription')
        return False




def get_vca_InstanceId_per_region(vcloudconfig,region):
            #### Initialise Logging params*
    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig(filename=vcloudconfig['logFile'],level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    
    if(vcloudconfig['service_type_name']=='vcd'):
        # TODO Add vCloud Director standalone region
        logging.error('function not allowed for local vCloud Director')
        return False
    if((vcloudconfig['service_type_name']=='ondemand')|(vcloudconfig['service_type_name']=='subscription')):
                #authentication to service
        vca = VCA(host=vcloudconfig['host'], username=vcloudconfig['username'], service_type=vcloudconfig['service_type_name'], version=vcloudconfig['VCD_version'], verify=vcloudconfig['cert'])
        bool1 = vca.login(password = vcloudconfig['password'], org=vcloudconfig['org'])
        if(bool1==False):
            logging.error('Authentification failed, please verify credentials')
        instances=vca.get_instances()
        if(instances):
            regions={}
            for n in range(len(instances)):
                regions[n]= instances[n]['region']
                if(instances[n]['region']==region):
                    url=instances[n]['dashboardUrl']
                    parsed = urlparse.urlparse(url)
                    instanceId=urlparse.parse_qs(parsed.query)['serviceInstanceId']
                    return instanceId
        else:
            logging.error('Unable to retreive VCA InstanceId')
            return False
    else:
        logging.error('verify VCA Cloud service Subscription')
        return False










