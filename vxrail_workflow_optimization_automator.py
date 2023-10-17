
# Copyright 2023 VMware, Inc.  All rights reserved. -- VMware Confidential
# Description: Add Domain/Add Cluster using Workflow Optimization

import copy
import getpass
import ipaddress
import json
import time
import requests
import re
from utils.utils import Utils
from nsxt.nsxtautomator import NsxtAutomator
from network.networkautomator import NetworkAutomator
from license.licenseautomator import LicenseAutomator
from hosts.hostsautomator import HostsAutomator
from vxrailDetails.vxrailauthautomator import VxRailAuthAutomator
from vxrailDetails.vxrailjsonconverter import VxRailJsonConverter
from vxrailDetails.vxrailjsonconverterpatch import VxRailJsonConverterPatch

__author__ = 'virtis'

REQ_VCF_VER = ['5.1']
VCF_SUBSCRIPTION_FT = 'feature.vcf.plus.subscription'
VXRAIL_SUBSCRIPTION_FT = 'feature.vcf.plus.subscription.vxrail'
VXRAIL_DVPG = 'feature.vcf.vcfeeng-17914.vsphere.dvpg.separation'
VXRAIL_PRIMARY_HOST_MAJOR_VERSION_8 = 8
VLCM_VXRAIL_FT = 'feature.vxrail.vlcm.integration'
VSAN_ESA_FT = 'feature.vcf.vsan.esa.vxrail'
#TO-DO: VLCM_CLUSTER_IMAGE_ID will be fetched from backend later
VLCM_CLUSTER_IMAGE_ID = 'VCF-VxRail-Cluster-Image'


class VxRailWorkflowOptimizationAutomator:
    def __init__(self):
        args = ["localhost", input("\033[1m Enter the Management domain SSO username: \033[0m"),
                getpass.getpass("\033[1m Enter the Management domain SSO password: \033[0m")]
        self.utils = Utils(args)
        self.hosts = HostsAutomator(args)
        self.nsxt = NsxtAutomator(args)
        self.network = NetworkAutomator(args)
        self.vxrailmanager = VxRailAuthAutomator(args)
        self.licenses = LicenseAutomator(args)
        self.converter = VxRailJsonConverter(args)
        self.converter_patch = VxRailJsonConverterPatch(args)
        self.hostname = args[0]
        self.two_line_separator = ['', '']
        self.enable_vlcm = False
        self.esa_enabled = False
        self.feature_list = {}
        self.remote_storage = False
        self.datastore_uuid = []

    def run(self):
        try:
            print(*self.two_line_separator, sep='\n')
            self.check_sddc_manager_version()
            self.get_feature_toggle_list()
            self.utils.printCyan("Please choose one of the below option:")
            self.utils.printBold("1) Create Domain")
            self.utils.printBold("2) Add Cluster")
            workflow_selection = self.utils.valid_input("\033[1m Enter your choice(number): \033[0m", None,
                                                        self.utils.valid_option, ["1", "2"])
            print(*self.two_line_separator, sep='\n')

            if self.check_lock_acquired_by_workflows():
                self.utils.printRed("Deployment lock is already acquired by other workflow. "
                                    "Please wait for it's completion.")
                exit(1)
            if workflow_selection == "1":
                self.allow_operations(None)
                product_type_to_version = self.get_compliance_matrix()
                self.check_wld_images(product_type_to_version)
                self.create_domain_workflow()
            elif workflow_selection == "2":
                self.add_cluster_workflow()
            print()
        except KeyboardInterrupt:
            print()

    def check_sddc_manager_version(self):
        url = 'https://' + self.hostname + '/v1/sddc-managers'
        sddc_json = self.utils.get_request(url)
        sddc_ver = None
        for sddc_manager in sddc_json['elements']:
            sddc_ver = sddc_manager['version'].split("-")[0]
        for req_ver in REQ_VCF_VER:
            if sddc_ver is not None and sddc_ver.startswith(req_ver):
                return
        print('\033[91m Fetched VCF version is {} which is not matching with required version {}'.format(sddc_ver,
                                                                                                         REQ_VCF_VER))
        print('\033[91m Please make sure the VCF version should be {}'.format(REQ_VCF_VER))
        exit(1)

    def check_vcf_bom(self, domainId):
        url = 'http://' + self.hostname + '/domainmanager/vxrail/clusters/allowed-operations/' + domainId
        header = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=header, verify=False)
        if response.status_code != 200:
            self.utils.printRed("Error executing API: {}, status code: {}".format(url, response.status_code))
            exit(1)
        data = json.loads(response.text)
        wfo_supported = False
        for operations in data:
            if operations['operation'] == 'WFO_CLUSTER_CREATION':
                wfo_supported = operations['isAllowed']
        return wfo_supported

    def check_domain_vlcm_enabled(self, domainId):
        domain_vlcm_enabled = False
        data = self.get_clusters_inventory()
        for cluster in data:
            if cluster['domainId'] == domainId and  cluster['isDefault'] and 'isImageBased' in cluster:
                domain_vlcm_enabled = cluster['isImageBased']
                break
        return domain_vlcm_enabled

    def allow_operations(self, domain_id):
        if domain_id is None:
            # Create Domain operation
            licensing_info_url = 'https://' + self.hostname + '/v1/resource-functionalities?resourceType=SYSTEM'
            operation_to_check = 'VXRAIL_CREATE_DOMAIN'
        else:
            # Add Cluster operation
            licensing_info_url = 'https://' + self.hostname +\
                                 '/v1/resource-functionalities?resourceType=DOMAIN&resourceIds={}'.format(domain_id)
            operation_to_check = 'VXRAIL_ADD_SECONDARY_CLUSTER'

        is_allowed = None
        response = self.utils.get_request(licensing_info_url)
        for resourceFunc in response['elements'][0]['functionalities']:
            if resourceFunc['type'] == operation_to_check:
                if resourceFunc['isAllowed'] is False:
                    self.utils.printRed('{} operation is not allowed. Error: {}'.format(
                        operation_to_check, resourceFunc['errorMessage']))
                    exit(1)
                is_allowed = True
        if is_allowed is None:
            self.utils.printRed('Resource functionality not found for type {}'.format(operation_to_check))
            exit(1)
        return is_allowed

    def check_is_subscription_active_mode(self, domain_id,vcf_ft_value,vxrail_ft_value):
        if vcf_ft_value == 'true' and vxrail_ft_value == 'true':
            # Both FTs on, fetching licensing information
            licensing_info = self.get_licensing_info(domain_id)
            return (self.is_subscription_active(licensing_info) or self.remote_storage)
        return False

    def get_feature_toggles(self):
        vcf_ft_value = vxrail_ft_value = None
        vcf_ft_value = self.get_feature_toggle_value(VCF_SUBSCRIPTION_FT)
        vxrail_ft_value = self.get_feature_toggle_value(VXRAIL_SUBSCRIPTION_FT)
        vxrail_dvpg =  self.get_feature_toggle_value(VXRAIL_DVPG)
        return vcf_ft_value, vxrail_ft_value,vxrail_dvpg

    def get_feature_toggle_value(self, key):
        if key in self.feature_list:
            return self.feature_list[key]
        else:
            self.utils.printRed("Feature key {} not found from API /domainmanager/features/list".format(key))
            exit(1)

    def print_vlcm_image_details(self, hosts_spec):
        vlcm_spec = {}
        for host in hosts_spec:
            vlcm_spec = host['softwareInfo']
            break
        self.utils.printCyan("vLCM Image Details")
        self.utils.printBold("vLCM Image: {}".format(VLCM_CLUSTER_IMAGE_ID))
        self.utils.printBold("ESXi Version: {}".format(vlcm_spec['baseImage']['version']))
        for package, pkg_details in vlcm_spec['hardwareSupport']['packages'].items():
            self.utils.printBold("Firmware/Driver Addon: {}:{}".format(pkg_details['pkg'], pkg_details['version']))
        self.utils.printBold("Additional Components:")
        for component, version in vlcm_spec['components'].items():
            self.utils.printBold("{} : {}".format(component, version))
        print(*self.two_line_separator, sep='\n')

    def get_feature_toggle_list(self):
        url = 'http://' + self.hostname + '/domainmanager/features/list'
        header = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=header, verify=False)
        if response.status_code == 200:
            self.feature_list = json.loads(response.text)
        else:
            self.utils.printRed("Error while getting features list from API /domainmanager/features/list")
            exit(1)

    def get_licensing_info(self, domain_id):
        licensing_info_url = 'https://' + self.hostname + '/v1/licensing-info'
        response = self.utils.get_request(licensing_info_url)
        if domain_id is None:
            licensing_info = self.extract_system_licensing_info(response)
        else:
            licensing_info = self.extract_domain_licensing_info(response, domain_id)
        return licensing_info

    def get_system_licensing_info(self):
        system_licensing_info_url = 'https://' + self.hostname + '/v1/licensing-info/system'
        return self.utils.get_request(system_licensing_info_url)

    def extract_system_licensing_info(self, response):
        licensing_info = None
        for resource in response:
            if resource['resourceType'] == 'SYSTEM':
                licensing_info = resource
        if licensing_info is None:
            self.utils.printRed('No licensing information found for SYSTEM resource type')
            exit(1)
        return licensing_info

    def extract_domain_licensing_info(self, response, domain_id):
        licensing_info = None
        for resource in response:
            if resource['resourceType'] == 'DOMAIN' and resource['resourceId'] == domain_id:
                licensing_info = resource
        if licensing_info is None:
            self.utils.printRed('No licensing information found for domain {}'.format(domain_id))
            exit(1)
        return licensing_info

    def is_subscription_active(self, licensing_info):
        return licensing_info['licensingMode'] == 'SUBSCRIPTION' and licensing_info['subscriptionStatus'] == 'ACTIVE'

    def is_perpetual(self, licensing_info):
        return licensing_info['licensingMode'] == 'PERPETUAL'

    def check_lock_acquired_by_workflows(self):
        url = 'http://' + self.hostname + '/locks'
        header = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=header, verify=False)
        if response.status_code == 200:
            data = json.loads(response.text)
            if len(data) > 0:
                for lock in data:
                    if lock['status'] == 'ACTIVE' and lock['resourceType'] == 'DEPLOYMENT':
                        return True
        else:
            self.utils.printRed("Error reaching the server.")
            exit(1)
        return False

    def get_compliance_matrix(self):
        url = 'http://' + self.hostname + '/lcm/compliance/matrix?domainType=VI'
        header = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=header, verify=False)
        if response.status_code == 200:
            data = json.loads(response.text)
            product_type_to_version = {}
            for versionMatrice in data['versionMatrices']:
                if versionMatrice['productVersions']:
                    for productVersion in versionMatrice['productVersions']:
                        if productVersion['productType'] in ['VCENTER', 'NSX_T_MANAGER']:
                            product_type_to_version[productVersion['productType']] = productVersion['version']
        else:
            self.utils.printRed("Error executing API: {}, status code: {}".format(url, response.status_code))
            exit(1)
        return product_type_to_version

    def check_wld_images(self, product_type_to_version):
        image = True
        for type, version in product_type_to_version.items():
            url = 'http://' + self.hostname + '/lcm/images?productType={}&imageType=INSTALL&version={}' \
                .format(type, version)
            header = {'Content-Type': 'application/json'}
            response = requests.get(url, headers=header, verify=False)
            if response.status_code == 200:
                data = json.loads(response.text)
                if len(data) <= 0:
                    image = False
                    break
            else:
                self.utils.printRed("Error executing API: {}, status code: {}".format(url, response.status_code))
                exit(1)
        if not image:
            self.utils.printRed("Please check vCenter/NSX-Manager images for Add VI operation. Make sure they are "
                                "compliant with correct BOM versions")
            exit(1)

    def get_clusters_inventory(self):
        get_cluster_url = 'http://' + self.hostname + '/inventory/clusters'
        header = {'Content-Type': 'application/json'}
        response = requests.get(get_cluster_url, headers=header, verify=False)
        if response.status_code == 200:
            clusters_data = json.loads(response.text)
        else:
            self.utils.printRed("Error executing API: {}, status code: {}".format(get_cluster_url, response.status_code))
            exit(1)
        return clusters_data

    def get_management_network_details(self, domain_id):
        mgmt_network_obj = {}
        default_cluster_id = None
        # Finding default cluster in management domain
        data = self.get_clusters_inventory()
        for cluster in data:
            if cluster['domainId'] == domain_id and cluster['isDefault']:
                default_cluster_id = cluster['id']
                get_vdses_url = 'https://' + self.hostname + '/v1/clusters/' + cluster['id'] + '/vdses'
                vds_details = self.utils.get_request(get_vdses_url)
                mgmt_vlan_id = None
                for vds in vds_details:
                    for port_group in vds['portGroups']:
                        if port_group['transportType'] == 'MANAGEMENT':
                            mgmt_vlan_id = port_group['vlanId']
                            break
                    if mgmt_vlan_id:
                        break
                mgmt_network_obj['vlanId'] = mgmt_vlan_id
        if default_cluster_id is None:
            self.utils.printRed("Default cluster not found in domain {}. Please check isDefault field in "
                                "inventory for clusters exists in selected domain".format(domain_id))
            exit(1)
        # Checking subnet field present for hosts in default cluster
        url = 'http://' + self.hostname + '/inventory/extensions/vi/esxis'
        header = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=header, verify=False)
        if response.status_code == 200:
            data = json.loads(response.text)
            for host in data:
                if host['clusterId'] == default_cluster_id:
                    if 'subnet' in host and 'gateway' in host:
                        mgmt_network_obj['subnet'] = str(ipaddress.IPv4Network((host['gateway'], host['subnet']),
                                                                               strict=False))
                        mgmt_network_obj['gateway'] = host['gateway']
                        mgmt_network_obj['mask'] = host['subnet']
                        break
        else:
            self.utils.printRed("Error executing API: {}, status code: {}".format(url, response.status_code))
            exit(1)
        return mgmt_network_obj

    def create_domain_workflow(self):
        domains = self.get_domains()
        existing_domain_names = []
        existing_vcenters_fqdn = []
        for domain in domains['elements']:
            existing_domain_names.append(domain['name'])
            for vcenter in domain['vcenters']:
                existing_vcenters_fqdn.append(vcenter['fqdn'])

        check_domain_name = True
        while check_domain_name:
            domain_name = self.utils.valid_input("\033[1m Enter the domain name: \033[0m", None,
                                                 self.utils.valid_domain_name)
            if domain_name in existing_domain_names:
                self.utils.printRed("Domain with name {} already exists. Please pass different domain name"
                                    .format(domain_name))
            else:
                check_domain_name = False

        system_licensing_info = self.get_system_licensing_info()
        is_system_licensing_mixed = system_licensing_info['licensingMode'] == 'MIXED'
        use_keyless_in_mixed_mode = False
        if is_system_licensing_mixed:
            print(*self.two_line_separator, sep='\n')
            self.utils.printCyan("Please select the type of licensing for the Domain:")
            self.utils.printBold("1) Based on License Keys")
            self.utils.printBold("2) Keyless from VMware Cloud")
            licensing_selection = self.utils.valid_input("\033[1m Enter your choice(number): \033[0m", None,
                                                         self.utils.valid_option, ["1", "2"])
            if licensing_selection == "2":
                use_keyless_in_mixed_mode = True

        print(*self.two_line_separator, sep='\n')
        self.utils.printCyan("Please choose one of the SSO Domain configuration input options:")
        self.utils.printBold("1) Create a new SSO Domain")
        self.utils.printBold("2) Join Management Domain's SSO Domain")
        sso_input_selection = self.utils.valid_input("\033[1m Enter your choice(number): \033[0m", None,
                                                 self.utils.valid_option, ["1", "2"])

        sso_payload = None
        if sso_input_selection == "1":
            print(*self.two_line_separator, sep='\n')
            sso_payload = self.enter_sso_domain_inputs_and_prepare_payload()

        print(*self.two_line_separator, sep='\n')
        datastore_name = self.utils.valid_input("\033[1m Enter datastore name: \033[0m", None,
                                                self.utils.valid_resource_name)
        print(*self.two_line_separator, sep='\n')

        self.utils.printYellow("** ADVANCED_VXRAIL_SUPPLIED_VDS nic profile is supported only via VxRail JSON input")
        self.utils.printCyan("Please choose one of the cluster configuration input options:")
        self.utils.printBold("1) VxRail JSON input")
        self.utils.printBold("2) Step by step input")
        input_selection = self.utils.valid_input("\033[1m Enter your choice(number): \033[0m", None,
                                                 self.utils.valid_option, ["1", "2"])

        vcenter_payload = vxm_payload = hosts_spec = cluster_name = dvs_payload = nsxt_payload = licenses = None
        if input_selection == "1":
            vcenter_payload, vxm_payload, hosts_spec, cluster_name, dvs_payload, nsxt_payload, licenses = \
                self.get_specs_from_vxrail_json(None, True, existing_vcenters_fqdn, use_keyless_in_mixed_mode)
        elif input_selection == "2":
            domains = self.get_domains()
            mgmt_domain_id = None
            for domain in domains['elements']:
                if domain['type'] == 'MANAGEMENT':
                    mgmt_domain_id = domain['id']

            vsan_storage, fc_storage = self.enter_storage_input(True, mgmt_domain_id)
            # check if vlcm is not enabled and provide option to user to enable vLCM
            vlcm_ft =  self.get_feature_toggle_value(VLCM_VXRAIL_FT)
            self.enable_vlcm = self.utils.user_option_to_enable_vlcm(vlcm_ft, self.enable_vlcm)
            vcenter_payload, gateway, netmask = self.enter_vcenter_inputs_and_prepare_payload(existing_vcenters_fqdn)
            cluster_name, hosts_spec, nsxt_payload, vxm_payload, dvs_payload, licenses = \
                self.enter_inputs(True, gateway, netmask, mgmt_domain_id, vsan_storage, fc_storage,
                                  use_keyless_in_mixed_mode)

        if self.enable_vlcm:
            self.print_vlcm_image_details(hosts_spec)

        # Common code for both option 1 & 2
        domain_payload = self.prepare_payload_for_create_domain(domain_name, cluster_name, vcenter_payload,
                                                                hosts_spec, nsxt_payload, vxm_payload, dvs_payload,
                                                                licenses, sso_payload, datastore_name)
        domain_payload_copy = copy.deepcopy(domain_payload)
        self.utils.maskPasswords(domain_payload_copy)
        print(json.dumps(domain_payload_copy, indent=2, sort_keys=True))
        print()
        input("\033[1m Enter to continue ...\033[0m")

        validations_url = 'https://{}/v1/domains/validations'
        validate_get_url = 'https://{}/v1/domains/validations/{}'
        creation_url = 'https://{}/v1/domains'
        self.trigger_workflow(domain_payload, validations_url, validate_get_url, creation_url, 'create domain')
        exit(1)

    def enter_vcenter_inputs_and_prepare_payload(self, existing_vcenters_fqdn):
        print(*self.two_line_separator, sep='\n')
        self.utils.printCyan("Please enter vCenter details: ")
        while True:
            vcenter_fqdn = self.utils.valid_input("\033[1m vCenter FQDN: \033[0m", None, self.utils.valid_fqdn)
            if vcenter_fqdn in existing_vcenters_fqdn:
                self.utils.printRed("vCenter with FQDN {} already exists as part of different domain. Please "
                                    "pass new vCenter FQDN for Create Domain".format(vcenter_fqdn))
            else:
                break
        vcenter_gateway = self.utils.valid_input("\033[1m Gateway IP address: \033[0m", None, self.utils.valid_ip)
        vcenter_netmask = self.utils.valid_input("\033[1m Subnet Mask(255.255.255.0): \033[0m", "255.255.255.0",
                                                 self.utils.valid_ip)
        print()
        while True:
            vcenter_password = self.utils.handle_password_input()
            res = self.utils.valid_vcenter_password(vcenter_password)
            if res:
                break

        print(*self.two_line_separator, sep='\n')
        datacenter = self.utils.valid_input("\033[1m Enter Datacenter name: \033[0m", None,
                                            self.utils.valid_resource_name)
        print(*self.two_line_separator, sep='\n')

        vcenter_spec = {
            'name': vcenter_fqdn[0:vcenter_fqdn.find('.')],
            'networkDetailsSpec': {
                'ipAddress': self.utils.nslookup_ip_from_dns(vcenter_fqdn),
                'dnsName': vcenter_fqdn,
                'gateway': vcenter_gateway,
                'subnetMask': vcenter_netmask
            },
            'rootPassword': vcenter_password,
            'datacenterName': datacenter,
            'vmSize': 'medium',
            'storageSize': 'lstorage'
        }
        return vcenter_spec, vcenter_gateway, vcenter_netmask

    def enter_sso_domain_inputs_and_prepare_payload(self):
        self.utils.printCyan("Please enter SSO Domain details: ")
        sso_domain_name = self.utils.valid_input("\033[1m Enter the SSO domain name: \033[0m", None,
                                                 self.utils.valid_sso_domain_name)
        while True:
            sso_domain_password = self.utils.handle_password_input("Enter SSO Administration password:")
            res = self.utils.valid_vcenter_password(sso_domain_password)
            if res:
                break
        sso_spec = {
            'ssoDomainName': sso_domain_name,
            'ssoDomainPassword': sso_domain_password
        }
        return sso_spec

    # --------- Hong Test ------------------------------------------------------------
    def get_specs_from_vxrail_json(self, selected_domain_id, is_primary=True, existing_vcenters_fqdn=None,
                                   use_keyless_in_mixed_mode=False):
        vcf_ft_value, vxrail_ft_value, dvpg_ft_value = self.get_feature_toggles()

        dvpg_is_on = True if dvpg_ft_value == 'true' else False

        print(*self.two_line_separator, sep='\n')

        json_location = input("\033[1m Please enter VxRail JSON location: \033[0m")
        error_msgs = self.converter.parse(selected_domain_id, json_location, is_primary, self.enable_vlcm, existing_vcenters_fqdn, dvpg_is_on)

        if error_msgs and len(error_msgs) > 0:
            self.utils.printRed("Find following errors:")
            for err in error_msgs:
                self.utils.printRed(err)
                exit(1)

        if not is_primary:
            self.converter.get_remote_datastore_uuids(selected_domain_id)
            self.datastore_uuid = self.converter.get_datastore_uuid()
            self.remote_storage = len(self.datastore_uuid) != 0
            self.converter_patch.remote_storage = self.remote_storage

        # If NIC profile FOUR_EXTREME_SPEED is present in input json file and VxRail version starting >= 8,
        # then incorrect nic profile has been provided in input json.
        vxm_payload = self.converter.get_vxm_payload()
        if int(self.converter.vxrm_version[0]) >= VXRAIL_PRIMARY_HOST_MAJOR_VERSION_8\
                and vxm_payload['nicProfile'] == 'FOUR_EXTREME_SPEED':
            self.utils.printRed("Nic profile FOUR_EXTREME_SPEED is not supported for VxRail version"
                                " {}".format(self.converter.vxrm_version))
            exit(1)

        # If VM_MANAGEMENT is not in vxm_payload['networks'] at this point, it means that network details
        # (gateway/mask) were not provided. Therefore, we will not create VM_MANAGEMENT. In other words,
        # we can treat dvpg_is_on as false.
        if dvpg_is_on:
            vm_management_exists = False
            for network in vxm_payload['networks']:
                if network['type'] == 'VM_MANAGEMENT':
                    vm_management_exists = True
                    break
            dvpg_is_on = vm_management_exists

        vsanesa_featureswitch = False
        if (self.get_feature_toggle_value(VSAN_ESA_FT) == 'true') :
            vsanesa_featureswitch = True

        vlcm_ft =  self.get_feature_toggle_value(VLCM_VXRAIL_FT)

        converter_patch = self.converter_patch.do_patching(self.converter, is_primary, dvpg_is_on, vlcm_ft, self.enable_vlcm, vsanesa_featureswitch, selected_domain_id)
        vxm_payload = converter_patch.get_vxm_payload()
        hosts_spec = converter_patch.get_hosts_spec()
        cluster_name = converter_patch.get_cluster_name()
        dvs_payload = converter_patch.get_vds_payload()
        if is_primary:
            self.enable_vlcm = converter_patch.is_vlcm_enabled()

        vcenter_payload = gateway = subnet = None
        if is_primary:
            vcenter_payload = converter_patch.get_vcenter_spec()
            gateway = vcenter_payload['networkDetailsSpec']['gateway']
            subnet = vcenter_payload['networkDetailsSpec']['subnetMask']
        nsxt_payload = self.nsxt.prepare_nsxt_instance(selected_domain_id, is_primary, gateway, subnet)

        if len(vxm_payload["rootCredentials"]["password"].strip()) == 0:
            self.utils.printCyan("Please enter VxRail Manager's root credentials:")
            vxm_payload["rootCredentials"]["password"] = self.utils.handle_password_input("Enter password:")
            print(*self.two_line_separator, sep='\n')

        if len(vxm_payload["adminCredentials"]["password"].strip()) == 0:
            self.utils.printCyan("Please enter VxRail Manager's admin credentials:")
            vxm_payload["adminCredentials"]["password"] = self.utils.handle_password_input("Enter password:")
            print(*self.two_line_separator, sep='\n')

        licenses = self.get_licenses(selected_domain_id, hosts_spec, is_primary, vcf_ft_value,
                                     self.check_vsan_storage(vxm_payload['networks']), vxrail_ft_value,
                                     use_keyless_in_mixed_mode)

        # Check if vSAN ESA is enabled and update the esa_enabled variable
        self.esa_enabled = converter_patch.is_esa_enabled()
        return vcenter_payload, vxm_payload, hosts_spec, cluster_name, dvs_payload, nsxt_payload, licenses

    def check_vsan_storage(self, networks):
        for network in networks:
            if network["type"] == "VSAN":
                # VSAN Network info exist
                return True
        return False

    def enter_storage_input(self, is_primary, domain_id):
        print(*self.two_line_separator, sep='\n')
        self.utils.printCyan("Please select the type of storage for this cluster :")
        self.utils.printBold("1) vSAN")
        self.utils.printBold("2) VMFS on FC")
        storage_selection = self.utils.valid_input("\033[1m Enter your choice(number): \033[0m", None,
                                                   self.utils.valid_option, ["1", "2"])
        vsan_storage = True if storage_selection == "1" else False
        if vsan_storage and not is_primary:
            converter_patch = self.converter_patch.input_remote_datastore_details(domain_id, self.converter)
            self.remote_storage = converter_patch.is_remote_storage()
            self.datastore_uuid = self.converter.get_datastore_uuid()

        fc_storage = True if storage_selection == "2" else False

        if vsan_storage == True and self.remote_storage == False:
            if (self.get_feature_toggle_value(VSAN_ESA_FT) == 'true') :
                is_vsanesa_enabled = input("\033[1m Do you want to enable vSAN ESA ?('yes' or 'no'): \033[0m")
                print(*self.two_line_separator, sep='\n')
                regex_yes = 'y(es)?'
                if re.match(regex_yes, is_vsanesa_enabled, re.IGNORECASE) != None:
                    self.esa_enabled = True
        if self.esa_enabled == True:
            self.utils.printGreen("vLCM is mandatory to enable vSAN ESA, vLCM will be enabled by default in case of vSAN ESA")
            self.enable_vlcm = True

        return vsan_storage, fc_storage

    def enter_inputs(self, is_primary, gateway, netmask, domain_id, vsan_storage, fc_storage,
                     use_keyless_in_mixed_mode=False):
        vcf_ft_value, vxrail_ft_value, dvpg_ft_value = self.get_feature_toggles()

        dvpg_is_on = True if dvpg_ft_value == 'true' else False
        cluster_name = self.utils.valid_input("\033[1m Please enter cluster name: \033[0m", None,
                                              self.utils.valid_resource_name)
        print(*self.two_line_separator, sep='\n')
        vxrm_fqdn = self.utils.valid_input("\033[1m Please enter VxRail Manager FQDN: \033[0m", None,
                                           self.utils.valid_fqdn)
        self.vxrailmanager.check_reachability(vxrm_fqdn)
        print(*self.two_line_separator, sep='\n')

        self.utils.printGreen("Getting ssl and ssh thumbprint for VxRail Manager {}...".format(vxrm_fqdn))
        print(*self.two_line_separator, sep='\n')
        vxrm_ssl_thumbprint = self.vxrailmanager.get_ssl_thumbprint(vxrm_fqdn)
        vxrm_ssh_thumbprint = self.vxrailmanager.get_ssh_thumbprint(vxrm_fqdn)
        self.utils.printGreen("Fetched ssl thumbprint: {}".format(vxrm_ssl_thumbprint))
        self.utils.printGreen("Fetched ssh thumbprint: {}".format(vxrm_ssh_thumbprint))

        print(*self.two_line_separator, sep='\n')
        select_option = input("\033[1m Do you want to trust the same?('yes' or 'no'): \033[0m")
        if select_option.lower() == 'yes' or select_option.lower() == 'y':
            print(*self.two_line_separator, sep='\n')
            discovered_hosts = self.hosts.discover_hosts(vxrm_fqdn, vxrm_ssl_thumbprint, self.enable_vlcm, self.esa_enabled)
            hosts_spec = self.hosts.input_hosts_details(discovered_hosts, fc_storage, self.enable_vlcm)

            self.converter.get_vxrm_version(domain_id)
            is_mtu_supported = self.utils.is_mtu_supported(self.converter.vxrm_version)
            vxrm_network_payload = self.vxrailmanager.prepare_network_info_and_payload(len(hosts_spec),
                                                                                       self.get_management_network_details(
                                                                                           domain_id),
                                                                                       vsan_storage,dvpg_is_on=dvpg_is_on, is_mtu_supported=is_mtu_supported)

            selected_nic_profile = self.vxrailmanager.select_nic_profile(self.converter.vxrm_version)

            # If VM_MANAGEMENT is not in vxm network payload at this point, it means user chose not
            # to create VM_MANAGEMENT. In other words, we can treat dvpg_is_on as false.
            if dvpg_is_on:
                vm_management_exists = False
                for obj in vxrm_network_payload:
                    if obj['type'] == "VM_MANAGEMENT":
                        vm_management_exists = True
                        break
                dvpg_is_on = vm_management_exists

            print(*self.two_line_separator, sep='\n')
            # mtu value will be asked only if is_step_by_step is True, so we can take vxrail json as source of input
            dvs_payload, vmnics = self.network.prepare_dvs_info(
                self.hosts.get_physical_nics(discovered_hosts), selected_nic_profile, vsan_storage=vsan_storage,
                dvpg_is_on=dvpg_is_on, is_step_by_step=True, is_mtu_supported=is_mtu_supported)
            if vmnics:
                for host_spec in hosts_spec:
                    host_spec['hostNetworkSpec'] = {'vmNics': vmnics}

            print(*self.two_line_separator, sep='\n')
            nsxt_payload = self.nsxt.prepare_nsxt_instance(domain_id, is_primary, gateway, netmask)

            vxm_payload = self.vxrailmanager.main_func()
            vxm_payload['networks'] = vxrm_network_payload
            vxm_payload['dnsName'] = vxrm_fqdn
            vxm_payload['ipAddress'] = self.utils.nslookup_ip_from_dns(vxrm_fqdn)
            vxm_payload['nicProfile'] = selected_nic_profile
            vxm_payload['sshThumbprint'] = vxrm_ssh_thumbprint
            vxm_payload['sslThumbprint'] = vxrm_ssl_thumbprint

            licenses = self.get_licenses(domain_id, hosts_spec, is_primary, vcf_ft_value, vsan_storage,
                                         vxrail_ft_value, use_keyless_in_mixed_mode)

            return cluster_name, hosts_spec, nsxt_payload, vxm_payload, dvs_payload, licenses
        else:
            self.utils.printRed("Exiting as VxRail Manager ssl/ssh thumbprint is not trusted")
            exit(1)

    def get_licenses(self, domain_id, hosts_spec, is_primary, vcf_ft_value,
                     vsan_storage, vxrail_ft_value, use_keyless_in_mixed_mode):
        if is_primary:
            is_sub_active = self.check_is_subscription_active_mode(None, vcf_ft_value, vxrail_ft_value)
        else:
            is_sub_active = self.check_is_subscription_active_mode(domain_id, vcf_ft_value, vxrail_ft_value)
        licenses = None
        if not (is_sub_active or use_keyless_in_mixed_mode):
            licenses = self.licenses.main_func(vsan_storage)
            if 'vSphere' in licenses.keys():
                for host_spec in hosts_spec:
                    host_spec['licenseKey'] = licenses['vSphere']
        return licenses

    def prepare_payload_for_create_domain(self, domain_name, cluster_name, vcenter_payload, hosts_spec,
                                          nsxt_payload, vxm_payload, dvs_payload, licenses, sso_payload, datastore_name):
        compute_spec = self.prepare_compute_spec_payload(cluster_name, hosts_spec, nsxt_payload,
                                                         vxm_payload, dvs_payload, licenses, datastore_name)
        nsxt_payload['nsxTSpec']['formFactor'] = 'large'
        if licenses is None:
            nsxt_license_key = ""
        else:
            nsxt_license_key = licenses['NSX-T']
        nsxt_payload['nsxTSpec']['licenseKey'] = nsxt_license_key
        domain_payload = {'domainName': domain_name,
                          'ssoDomainSpec': sso_payload,
                          'vcenterSpec': vcenter_payload,
                          'computeSpec': compute_spec,
                          'nsxTSpec': nsxt_payload['nsxTSpec']}
        return domain_payload

    def prepare_compute_spec_payload(self, cluster_name, hosts_spec,
                                     nsxt_payload, vxm_payload, dvs_payload, licenses, datastore_name):
        cluster_spec = {'name': cluster_name,
                        'skipThumbprintValidation': False,
                        'vxRailDetails': vxm_payload,
                        'hostSpecs': hosts_spec}

        vsan_storage = False
        for network in vxm_payload['networks']:
            if network['type'] == 'VSAN':
                vsan_storage = True

        if vsan_storage:
            license_key = None
            if licenses is None:
                license_key = ""
            elif 'VSAN' in licenses.keys():
                license_key = licenses['VSAN']
            datastore_spec = {
                'vsanDatastoreSpec': {
                    'licenseKey': license_key,
                    'datastoreName': datastore_name,
                    'esaConfig': {
                        "enabled": self.esa_enabled
                    }

                }
            }
            if self.remote_storage:
                vsanRemoteDatastoreSpec = []
                for uuid in self.datastore_uuid:
                    vsanRemoteDatastoreSpec.append({'datastoreUuid': uuid.strip()})

                datastore_spec = {
                    'vsanRemoteDatastoreClusterSpec': {
                        'vsanRemoteDatastoreSpec': vsanRemoteDatastoreSpec
                    }
                }
        else:
            datastore_spec = {
                'vmfsDatastoreSpec': {'fcSpec': [{'datastoreName': datastore_name}]}
            }

        cluster_spec['datastoreSpec'] = datastore_spec
        cluster_spec['networkSpec'] = {'vdsSpecs': dvs_payload,
                                       'nsxClusterSpec': nsxt_payload['nsxClusterSpec']}
        if self.enable_vlcm:
            cluster_spec['clusterImageId'] = VLCM_CLUSTER_IMAGE_ID
        compute_spec = {'clusterSpecs': [cluster_spec]}
        return compute_spec

    def trigger_workflow(self, payload, validations_url, validate_get_url, creation_url, workflow_name):
        # validations
        validations_post_url = validations_url.format(self.hostname)
        self.utils.printGreen('Validating the input....')
        response = self.utils.post_request(payload, validations_post_url)

        # only poll if validation is actually in progress (i.e. did not instantly fail)
        if 'resultStatus' not in response:
            self.utils.printGreen('Validation started for {} operation. The validation id is: {}'
                                  .format(workflow_name, response['id']))

            validate_poll_url = validate_get_url.format(self.hostname, response['id'])
            self.utils.printGreen('Polling on validation api {}'.format(validate_poll_url))
            time.sleep(10)
            self.utils.printGreen('Validation IN_PROGRESS. It will take some time to complete. Please wait...')
            validation_status = self.utils.poll_on_id(validate_poll_url)
            self.utils.printGreen('Validation ended with status: {}'.format(validation_status))

            if validation_status != 'SUCCEEDED':
                self.utils.printRed('Validation Failed.')
                self.utils.print_validation_errors(validate_poll_url)
                exit(1)
        else:
            self.utils.printRed('Validation Failed.')
            self.utils.print_validation_errors_with_response_body(response)
            exit(1)

        # Create operation
        print()
        input("\033[1m Enter to {}...\033[0m".format(workflow_name))
        wf_url = creation_url.format(self.hostname)
        response = self.utils.post_request(payload, wf_url)
        self.utils.printGreen('Triggered {}, monitor the status of the task(task-id:{}) from '
                              'sddc-manager ui'.format(workflow_name, response['id']))


    def add_cluster_workflow(self):
        self.utils.printGreen('Getting the domains...')
        domains = self.get_domains()
        print(*self.two_line_separator, sep='\n')
        self.utils.printCyan("Please choose the domain to which cluster has to be added:")

        id_to_selected_domain_id = {}
        i = 1
        for domain in domains['elements']:
            self.utils.printBold("{}) {}".format(i, domain['name']))
            id_to_selected_domain_id[str(i)] = domain['id']
            i = i + 1
        selected_domain = self.utils.valid_input("\033[1m Enter your choice(number): \033[0m", None,
                                                 self.utils.valid_option, list(id_to_selected_domain_id.keys()))
        selected_domain_id = id_to_selected_domain_id[selected_domain]
        if not self.check_vcf_bom(selected_domain_id):
            self.utils.printRed('BOM is below WFO supported VCF version 4300. So WFO add cluster not supported')
            exit(1)
        print(*self.two_line_separator, sep='\n')

        self.allow_operations(selected_domain_id)

        datastore_name = self.utils.valid_input("\033[1m Enter datastore name: \033[0m", None,
                                                self.utils.valid_resource_name)
        print(*self.two_line_separator, sep='\n')

        self.utils.printYellow("** ADVANCED_VXRAIL_SUPPLIED_VDS nic profile is supported only via VxRail JSON input")
        self.utils.printCyan("Please choose one of the cluster configuration input options:")
        self.utils.printBold("1) VxRail JSON input")
        self.utils.printBold("2) Step by step input")
        input_selection = self.utils.valid_input("\033[1m Enter your choice(number): \033[0m", None,
                                                 self.utils.valid_option, ["1", "2"])

        vxm_payload = hosts_spec = cluster_name = dvs_payload = nsxt_payload = licenses = None
        existing_vcenters_fqdn = []
        # If vlcm ft is true and domain is vlcm enabled add clusterImageId in the add cluster payload
        vlcm_ft =  self.get_feature_toggle_value(VLCM_VXRAIL_FT)
        if vlcm_ft == 'true' or self.enable_vlcm == True:
            self.enable_vlcm = self.check_domain_vlcm_enabled(selected_domain_id)

        if input_selection == "1":
            for domain in domains['elements']:
                if domain['id'] == selected_domain_id:
                    # There should only one vc per domain
                    for vcenter in domain['vcenters']:
                        existing_vcenters_fqdn.append(vcenter['fqdn'])
            vcenter_payload, vxm_payload, hosts_spec, cluster_name, dvs_payload, nsxt_payload, licenses = \
                self.get_specs_from_vxrail_json(selected_domain_id, False, existing_vcenters_fqdn)
        elif input_selection == "2":
            print(*self.two_line_separator, sep='\n')
            vsan_storage, fc_storage = self.enter_storage_input(False, selected_domain_id)
            cluster_name, hosts_spec, nsxt_payload, vxm_payload, dvs_payload, licenses = \
                self.enter_inputs(False, None, None, selected_domain_id, vsan_storage, fc_storage)

        if self.esa_enabled == True and self.enable_vlcm == False:
            self.utils.printRed("vSAN ESA is not supported on non vLCM based domain, Please enable vLCM on the domain and try")
            exit(1)

        cluster_payload = self.prepare_payload_for_create_cluster(selected_domain_id, cluster_name, hosts_spec,
                                                                  nsxt_payload, vxm_payload, dvs_payload, licenses,
                                                                  datastore_name)

        if self.enable_vlcm:
            self.print_vlcm_image_details(hosts_spec)

        cluster_payload_copy = copy.deepcopy(cluster_payload)
        self.utils.maskPasswords(cluster_payload_copy)
        print(json.dumps(cluster_payload_copy, indent=2, sort_keys=True))
        print()
        input("\033[1m Enter to continue ...\033[0m")

        validations_url = 'https://{}/v1/clusters/validations'
        validate_get_url = 'https://{}/v1/clusters/validations/{}'
        creation_url = 'https://{}/v1/clusters'
        self.trigger_workflow(cluster_payload, validations_url, validate_get_url,
                              creation_url, 'add cluster')
        exit(1)

    def get_domains(self):
        # get domains
        domains_url = 'https://' + self.hostname + '/v1/domains'
        response = self.utils.get_request(domains_url)
        return response

    def prepare_payload_for_create_cluster(self, domain_id, cluster_name, hosts_spec,
                                           nsxt_payload, vxm_payload, dvs_payload, licenses,
                                           datastore_name):
        compute_spec = self.prepare_compute_spec_payload(cluster_name, hosts_spec, nsxt_payload,
                                                         vxm_payload, dvs_payload, licenses, datastore_name)
        cluster_payload = {'domainId': domain_id,
                           'computeSpec': compute_spec}
        return cluster_payload


if __name__ == "__main__":
    VxRailWorkflowOptimizationAutomator().run()
