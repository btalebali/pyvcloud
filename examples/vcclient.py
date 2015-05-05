import time, datetime, os
from pyvcloud.vcloudair import *
import time
import logging
from random import randint
from requests.exceptions import SSLError
from twisted.trial.unittest import Todo

maxwait =  120


# print information
def print_vca(vca):
    if vca:
        print 'vca token:            ', vca.token
        if vca.vcloud_session:
            print 'vcloud session token: ', vca.vcloud_session.token
            print 'org name:             ', vca.vcloud_session.org
            print 'org url:              ', vca.vcloud_session.org_url
            print 'organization:         ', vca.vcloud_session.organization
        else:
            print 'vca vcloud session:   ', vca.vcloud_session
    else:
        print 'vca: ', vca
        

# test vcloud session
def test_vcloud_session(vca, vdc, vapp):
    the_vdc = vca.get_vdc(vdc)
    for x in range(1, 5):
        print datetime.datetime.now(), the_vdc.get_name(), vca.vcloud_session.token
        the_vdc = vca.get_vdc(vdc)       
        if the_vdc: print the_vdc.get_name(), vca.vcloud_session.token
        else: print False                
        the_vapp = vca.get_vapp(the_vdc, vapp)
        if the_vapp: print the_vapp.me.name
        else: print False
        time.sleep(2)

# test vcloud session
def list_catalogue(vca):
    catalogues=vca.get_catalogs()
    if catalogues:
        for i in range(0,len(catalogues)):
            print(catalogues[i].name)

def list_vapptemplate(vdc,vca):
    var=vca.get_vapptemplate(vdc)
    if var:
        for i in range(0,len(var)):
            print(var[i].name)


def get_all_vapp(self, vdc):
    refs = filter(lambda ref: ref.type_ == 'application/vnd.vmware.vcloud.vApp+xml', vdc.ResourceEntities.ResourceEntity)
    listvApp=[]
    for i in range(1, len(refs)):
        self.response = requests.get(refs[i][0].href, headers=self.vcloud_session.get_vcloud_headers(), verify=self.verify)
        if self.response.status_code == requests.codes.ok:
            vapp = VAPP(vAppType.parseString(self.response.content, True), self.vcloud_session.get_vcloud_headers(), self.verify)
            listvApp = listvApp + vapp
    return listvApp

def authenticatevcd(host,org,username,password,service_type,VCD_version,verify,logging):
    vca = VCA(host=host, username=username, service_type=service_type, version=VCD_version, verify=False)
    bool = vca.login(password = password, org=org)
    if(bool):
        logging.info("authenification succeeded")
        bool = vca.login(token = vca.token, org=org, org_url=vca.vcloud_session.org_url)
        return vca
    else:
        logging.warning("authenification failed, please verify credentials")
        sys.exit(0)


def findvDC(vca,vdc_name,logging):
    vDC = vca.get_vdc(vdc_name=vdc_name)
    if (vDC):
        logging.info("virtual datacenter founded")
        return vDC
    else:
        logging.error(("virtual datacenter not founded, please verify vDC name"))
        sys.exit(0)


def findvApptemplate(vca,vDC,vApptemplate,logging):
    listvApptemplate = vca.get_vapptemplate(vDC)
    for i in range(len(listvApptemplate)):
        if(listvApptemplate[i].name==vApptemplate):
            logging.info("vAppTemplate "+vApptemplate+" found")
            return True
    logging.error("vAppTemplate "+vApptemplate+" not found, please verify vApptemplate")
    return False

def findvApp(vca,vdc_name,vAppname,logging):
    vDC = vca.get_vdc(vdc_name=vdc_name)
    vappc = vca.get_vapp(vDC, vAppname)
    if(vappc):
        logging.info(" "+vAppname+" found" )
        return vappc
    else:
        logging.error(" "+vAppname+" not found" )
        return None

def findEdgegateway(vca,vdc_name, GWname ,logging):
    GWs=vca.get_gateways(vdc_name)
    for i in range(len(GWs)):
        if(GWs[i].get_name()==GWname):
            return GWs[i]
    logging.error("Edge gateway Not found, please verify edge gateway")    

def get_or_create_vDCnet(vca,vdc_name,vCloudvDCnet,logging):
    listvDCnet=vca.get_networks(vdc_name)
    b=False
    for i in range(len(listvDCnet)):
        if(listvDCnet[i].get_name()==vCloudvDCnet['vDCorg_net']):
            b=True
            logging.info(vCloudvDCnet['vDCorg_net']+" is founded")
    if(not(b)):
        task = vca.create_vdc_network(vdc_name, network_name=vCloudvDCnet['vDCorg_net'],gateway_name=vCloudvDCnet['GWname'],start_address=vCloudvDCnet['start_address'],
                                      end_address=vCloudvDCnet['end_address'],gateway_ip=vCloudvDCnet['gateway_ip'],netmask=vCloudvDCnet['netmask'], dns1=vCloudvDCnet['dns1'],
                                      dns2=vCloudvDCnet['dns2'], dns_suffix=vCloudvDCnet['dns_suffix'])
        #print(task.get_Progress())
        #pyvcloud.schema.vcd.v1_5.schemas.vcloud.networkType.TaskType
        if((task[0] == False) | (task == None)):
            logging.error('An error occured while creating vDC Network, please contact your cloud administrator')
            sys.exit(0)
        else:
            result = vca.block_until_completed(task[1])
            if(result == False):
                logging.error('An error occured while creating vDC Network, please contact your cloud administrator')
                sys.exit(0)
            else:
                logging.info("creating vDC Network succeeded")
    Nethref = vca.get_admin_network_href(vdc_name, network_name=vCloudvDCnet['vDCorg_net'])
    return Nethref


def connect_VM_to_vDCnet(vca,vcloudconfig,vcloudVM,vCloudvDCnet,Nethref,logging):
    
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    task = vappc.connect_to_network(network_name=vCloudvDCnet['vDCorg_net'], network_href = Nethref)
    ### Block until task completed
    if((task == False) | (task == None)):
        logging.error('An error occured while connecting vApp to vDC network, please contact your cloud administrator')
        sys.exit(0)
    else:
        result = vca.block_until_completed(task)
        if(result == False):
            logging.error('An error occured while connecting vApp to vDC network, please contact your cloud administrator')
            sys.exit(0)
        else:
            logging.info("Adding vDC net to vApp succeeded")
    
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    task=vappc.connect_vms(network_name=vCloudvDCnet['vDCorg_net'],connection_index = 0, ip_allocation_mode = 'POOL')

    ### Block until task completed
    if((task == False) | (task == None)):
        logging.error('An error occured while connecting vApp to vDC network, please contact your cloud administrator')
        sys.exit(0)
    else:
        result = vca.block_until_completed(task)
        if(result == False):
            logging.error('An error occured while connecting vApp to vDC network, please contact your cloud administrator')
            sys.exit(0)
        else:
            logging.info("Connecting vDC net to vApp succeeded")
    #block task
    return True

def allocate_publicIP_on_GW(GW, vcloudVM,logging):
    publiciplist = GW.get_public_ips()
    if (len(publiciplist) > 0):
        vcloudVM['publicaddress'] = publiciplist[randint(1,len(publiciplist))]
        return True
    else:
        logging.warning('No available public IP in the Gateway. Pleese Contact your Cloud administrator \n')
        return False


def configuredhcp(GW,vCloudvDCnet,logging):
    result=GW.enable_dhcp(enable=False)
    logging.info('save services configuration')
    try:
        result = GW.save_services_configuration()
    except SSLError:
        logging.warning("Certificate verify failed")
        return False
    return True

def configureNat(GW,vcloudVM,vCloudvDCnet,logging):
#Configure SNAT
    result = GW.add_nat_rule(rule_type='SNAT', original_ip=vcloudVM['privateaddress'], original_port='Any', translated_ip=vcloudVM['publicaddress'], translated_port='Any', protocol='Any')
#configure DNAT
    result = GW.add_nat_rule(rule_type='DNAT', original_ip=vcloudVM['publicaddress'], original_port='Any', translated_ip=vcloudVM['privateaddress'], translated_port='Any', protocol='Any')
    try:
        result = GW.save_services_configuration()
    except SSLError:
        logging.warning("Certificate verification failed")
        return False
    return True

def configureFWrules(GW,vcloudVM,vCloudvDCnet,logging):
    result=GW.enable_fw(enable=True)
    # TODO : Setting firewall rules vCloudvDCnet['FWrules']
    result = GW.add_fw_rule(is_enable=True, description='external SSH access', policy='allow', protocol='Any', dest_port='22', dest_ip=vcloudVM['publicaddress'],source_port='Any', source_ip='external', enable_logging=False)
    result = GW.add_fw_rule(is_enable=True, description='external http access', policy='allow', protocol='Any', dest_port='80', dest_ip=vcloudVM['publicaddress'],source_port='Any', source_ip='external', enable_logging=False)
    result = GW.add_fw_rule(is_enable=True, description='external https access', policy='allow', protocol='Any', dest_port='443', dest_ip=vcloudVM['publicaddress'],source_port='Any', source_ip='external', enable_logging=False)
    result = GW.add_fw_rule(is_enable=True, description='external cosacs access', policy='allow', protocol='Any', dest_port='8286', dest_ip=vcloudVM['publicaddress'],source_port='Any', source_ip='external', enable_logging=False)
    logging.info('save services configuration')
    try:
        result = GW.save_services_configuration()
    except SSLError:
        logging.warning("Certificate verify failed")
        return False
    return True



def updateVMdetails(vca,vcloudconfig,vcloudVM,logging):
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    vmdetails=vappc.get_vms_details()
    if len(vmdetails)==1:
        vcloudVM['status'] = vmdetails[0]['status']
        vcloudVM['name']   = vmdetails[0]['name']
        vcloudVM['cpus']   = vmdetails[0]['cpus']
        vcloudVM['memory'] = vmdetails[0]['memory']
        vcloudVM['owner']  = vmdetails[0]['owner']
        vcloudVM['os']     = vmdetails[0]['os']
    else:
        logging.warning("Many VMs exists in this vAppTemplate , please reconfigure a vApptemplate with one VM ")
        return False
    return True


def customizevApp(vca,vcloudconfig,vcloudVM,logging):
    
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    task  = vappc.customize_guest_os(vm_name=vcloudVM['name'], customization_script=vcloudVM['customization_script'],computer_name = vcloudVM['computer_name'],
                                     admin_password = vcloudVM['rootpassword'], reset_password_required = False)
    ### Block until task completed
    if((task == False) | (task == None)):
        logging.error('An error occured while reconfiguring vApp, please contact your cloud administrator')
        return False
    else:
        result = vca.block_until_completed(task)
        if(result == False):
            logging.error('An error occured while reconfiguring vApp, please contact your cloud administrator')
            return False
        else:
            logging.info("reconfiguring vApp succeeded")
            return True

def update_VM_net_info(vca,vcloudVM,vcloudconfig,logging):
    vappc = findvApp(vca=vca,vdc_name=vcloudconfig['vdc_name'], vAppname=vcloudVM['vAppname'],logging=logging)
    list_VM_net_info = vappc.get_vms_network_info()
    if list_VM_net_info :
        vcloudVM['privateaddress'] = list_VM_net_info[0][0]['ip']
        vcloudVM['macaddress']     = list_VM_net_info[0][0]['mac']
        return True
    else:
        logging.warn("Unable to retreive Bm 's net info")
        return False
