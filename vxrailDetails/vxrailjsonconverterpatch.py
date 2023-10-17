# Copyright 2021 VMware, Inc.  All rights reserved. -- VMware Confidential
# Description: Prepare VCF spec after VxRail Json Conversion
# This class is to fill the missed items after VxRail JSON convertion
# - VDS name
# - Thumbprints of vxrail manager and hosts
# - Used by nsx
# - Portgroup names for management, vsan, vmotion

from vxrailDetails.vxrailjsonconverter import VxRailJsonConverter
from utils.utils import Utils
from vxrailDetails.vxrailauthautomator import VxRailAuthAutomator
from hosts.hostsautomator import HostsAutomator, HostDiscovery
from network.networkautomator import NetworkAutomator
import json
import re

__author__ = 'Hong.Yuan'


class VxRailJsonConverterPatch:
    def __init__(self, args):
        self.description = "VxRail Manager JSON file conversion patch"
        self.utils = Utils(args)
        self.hostname = args[0]
        self.converter = None
        self.vxrail_auth_automator = VxRailAuthAutomator(args)
        self.host_automator = HostsAutomator(args)
        self.network_automator = NetworkAutomator(args)
        self.two_line_separator = ['', '']
        self.vds_payload = None
        self.esa_enabled = False
        self.enable_vlcm = False
        self.remote_storage = False

    def __update_thumbprints_for_hosts(self, host_spec, discovered_hosts):
        primary_node_serial_no = self.host_automator.get_primary_node_serialno(discovered_hosts)
        input_hosts_serial_no = []
        serialno_to_thumbprint = self.host_automator.get_serialno_to_thumbprint_mapping(discovered_hosts)
        notfound_hosts = []
        for h in host_spec:
            input_hosts_serial_no.append(h["serialNumber"])
            if h["serialNumber"] in serialno_to_thumbprint:
                h["sshThumbprint"] = serialno_to_thumbprint[h["serialNumber"]]
            else:
                notfound_hosts.append(h["serialNumber"])

        if primary_node_serial_no not in input_hosts_serial_no:
            self.utils.printRed("The input hosts {} do not contain the primary host (with serial number - {}) found "
                                "in the set of discovered hosts".format(input_hosts_serial_no, primary_node_serial_no))
            exit(1)

        if len(input_hosts_serial_no) != len(set(input_hosts_serial_no)):
            self.utils.printRed("Duplicate hosts found in input hosts {}".format(input_hosts_serial_no))
            exit(1)
        return notfound_hosts

    def __update_pg_name(self, vds_spec, net_type, value):
        for pg in vds_spec[0]["portGroupSpecs"]:
            if pg["transportType"] == net_type:
                pg["name"] = value if len(value) > 0 else pg["name"]
                return

    def get_vxm_payload(self):
        return self.converter.get_vxm_payload()

    def get_vcenter_spec(self):
        return self.converter.get_vcenter_spec()

    def get_vds_payload(self):
        return self.vds_payload

    def is_remote_storage(self):
        return self.remote_storage

    def is_esa_enabled(self):
        return self.esa_enabled

    def get_hosts_spec(self):
        return self.converter.get_host_spec()

    def is_vlcm_enabled(self):
        return self.enable_vlcm

    def get_cluster_name(self):
        return self.converter.get_cluster_name()

    def input_remote_datastore_details(self, domain_id, converter):
        print(*self.two_line_separator, sep='\n')
        remote_storage = input("\033[1m Do you want to mount a remote datastore?('yes' or 'no'): \033[0m")
        if remote_storage.lower() == 'yes' or remote_storage.lower() == 'y':
            self.utils.printGreen("The datastore name provided above will be ignored since remote datastore configuration is selected.")
            self.remote_storage = True
            remote_datastores = converter.get_remote_datastores(domain_id)
            i=1
            id_to_selected_remote_datastores = {}
            for datastore in remote_datastores.keys():
                self.utils.printBold("{}) {}".format(i, datastore))
                id_to_selected_remote_datastores[str(i)] = remote_datastores[datastore]
                i = i + 1
            while True:
                var = True
                remote_datastore_options = input("\033[1m Enter your choices(numbers by comma separated): \033[0m").strip().split(',')
                for remote_datastore_option in remote_datastore_options:
                    if len(remote_datastore_option.strip()) == 0:
                        self.utils.printRed("Please select atleast 1 remote datastore")
                        var = False
                    if var:
                        if int(remote_datastore_option.strip()) not in range(1, len(remote_datastores.keys()) + 1):
                            self.utils.printRed("Please enter valid options for selecting remote datastores")
                            var = False
                if var and len(remote_datastore_options) >= 1:
                    for option in remote_datastore_options:
                        converter.datastore_uuid.append(id_to_selected_remote_datastores[option])
                        self.utils.printGreen('Datastore uuid {}'.format(id_to_selected_remote_datastores[option]))
                    break
        return self

    def do_patching(self, converter, is_primary, dvpg_is_on,  vlcm_feature_switch, is_vlcm_enabled, vsanesa_featureswitch, domain_id):
        if type(converter) == VxRailJsonConverter:
            self.converter = converter
        else:
            return
        vxm_spec = self.converter.get_vxm_payload()
        hosts_spec = self.converter.get_host_spec()
        vds_pg_map = self.converter.get_pg_name_map()
        is_mtu_supported = self.converter.get_is_mtu_supported()
        self.enable_vlcm = is_vlcm_enabled
        self.vxrail_auth_automator.check_reachability(vxm_spec["dnsName"])

        vsan_storage = False
        for nw in vxm_spec['networks']:
            if nw['type'] == 'VSAN':
                vsan_storage = True

        if vsan_storage and  vsanesa_featureswitch and self.converter.get_hci_mesh_primary_datastore_name() is None:
            is_vsanesa_enabled = input("\033[1m Do you want to enable vSAN ESA ?('yes' or 'no'): \033[0m")
            print(*self.two_line_separator, sep='\n')
            regex_yes = 'y(es)?'
            if re.match(regex_yes, is_vsanesa_enabled, re.IGNORECASE) != None:
                self.esa_enabled = True

        if self.esa_enabled == True:
            self.utils.printGreen("vLCM is mandatory to enable vSAN ESA, vLCM will be enabled by default in case of vSAN ESA")
            self.enable_vlcm = True

        # Provide user to enable vLCM if not enabled in add domain workflow
        if is_primary and self.enable_vlcm == False:
            self.enable_vlcm = self.utils.user_option_to_enable_vlcm(vlcm_feature_switch, self.enable_vlcm)

        if is_primary:
            vcenter_spec = self.converter.get_vcenter_spec()
            print(*self.two_line_separator, sep='\n')
            vcenter_spec['networkDetailsSpec']['gateway'] = \
                self.utils.valid_input("\033[1m Enter Gateway IP address for vCenter {}: \033[0m"
                                       .format(vcenter_spec['networkDetailsSpec']['dnsName']), None,
                                       self.utils.valid_ip)
            vcenter_spec['networkDetailsSpec']['subnetMask'] = \
                self.utils.valid_input("\033[1m Enter Subnet Mask for vCenter {}(255.255.255.0): \033[0m"
                                       .format(vcenter_spec['networkDetailsSpec']['dnsName']), "255.255.255.0",
                                       self.utils.valid_ip)
            while True:
                vcenter_password = self.utils.handle_password_input("Enter vCenter {} root password:"
                                                                    .format(
                    vcenter_spec['networkDetailsSpec']['dnsName']))
                res = self.utils.valid_vcenter_password(vcenter_password)
                if res:
                    break
            vcenter_spec['rootPassword'] = vcenter_password

        print(*self.two_line_separator, sep='\n')
        selected_nic_profile = vxm_spec['nicProfile']

        vxrm_fqdn = vxm_spec["dnsName"]
        self.utils.printGreen("Getting ssl thumbprint for the passed VxRail Manager {}".format(vxrm_fqdn))
        print(*self.two_line_separator, sep='\n')
        vxrm_ssl_thumbprint = self.vxrail_auth_automator.get_ssl_thumbprint(vxrm_fqdn)
        vxrm_ssh_thumbprint = self.vxrail_auth_automator.get_ssh_thumbprint(vxrm_fqdn)
        self.utils.printGreen("Fetched ssl thumbprint: {}".format(vxrm_ssl_thumbprint))
        self.utils.printGreen("Fetched ssh thumbprint: {}".format(vxrm_ssh_thumbprint))
        vxm_spec["sslThumbprint"] = vxrm_ssl_thumbprint
        vxm_spec["sshThumbprint"] = vxrm_ssh_thumbprint
        print(*self.two_line_separator, sep='\n')
        select_option = input("\033[1m Do you want to trust the same?('yes' or 'no'): \033[0m")
        if select_option.lower() == 'yes' or select_option.lower() == 'y':
            print(*self.two_line_separator, sep='\n')
            self.utils.printGreen("Getting ssh thumbprint for the hosts passed in Json")
            discovered_hosts = self.host_automator.discover_hosts(vxrm_fqdn, vxrm_ssl_thumbprint, self.enable_vlcm, self.esa_enabled)
            notfound_hosts = self.__update_thumbprints_for_hosts(hosts_spec, discovered_hosts)
            self.utils.printCyan("Fetched ssh thumbprint for hosts passed in Json:")
            self.utils.printBold("--Serial Number--------------SSH Thumbprint--------------------------")
            self.utils.printBold("---------------------------------------------------------------------")
            for h in hosts_spec:
                if len(h["sshThumbprint"]) > 0:
                    self.utils.printBold(" {} : {}".format(h["serialNumber"], h["sshThumbprint"]))
            if len(notfound_hosts) > 0:
                print(*self.two_line_separator, sep='\n')
                self.utils.printRed(
                    "Unable to find hosts {} in set of discovered hosts, please correct the VxRail JSON "
                    "input and pass only discovered hosts".format(notfound_hosts))
                exit(1)

            if self.enable_vlcm:
                vlcm_spec = self.host_automator.get_vlcm_spec(discovered_hosts)
                for host_spec in hosts_spec:
                    host_spec['softwareInfo'] = vlcm_spec

            print(*self.two_line_separator, sep='\n')
            self.hosts_spec_password_input(hosts_spec)
            vm_spec_exists = False
            # Set vds_mtu if it is Single System DVS
            vds_mtu = None
            pg_types_to_vmnics = pgtypes_to_vmnicuplink_mapping = pg_type_to_active_uplinks = pg_types_to_mtu = None
            if selected_nic_profile == 'ADVANCED_VXRAIL_SUPPLIED_VDS':
                pg_types_to_vmnics, pg_types_to_mtu = self.converter.get_vmnics_mapped_to_system_dvs(dvpg_is_on, is_mtu_supported)
                pg_type_to_active_uplinks = self.converter.get_portgroup_to_active_uplinks(dvpg_is_on)
                pgtypes_to_vmnicuplink_mapping = self.converter.get_vmnic_to_uplink_mapping_for_vdss(dvpg_is_on)
                if pg_types_to_mtu and len(pg_types_to_mtu) == 1:
                    vds_mtu = self.converter.get_single_system_dvs_mtu()
            else:
                if is_mtu_supported:
                    vds_mtu = self.converter.get_single_system_dvs_mtu()

            vm_management_pg = None
            if dvpg_is_on:
                vm_management_pg = vds_pg_map["VM_MANAGEMENT"]

            self.vds_payload, vmnics = self.network_automator.prepare_dvs_info(
                self.host_automator.get_physical_nics(discovered_hosts), selected_nic_profile,
                vds_pg_map["MANAGEMENT"], vds_pg_map["VSAN"], vds_pg_map["VMOTION"], pg_types_to_vmnics,
                pg_type_to_active_uplinks, self.get_cluster_name(), vsan_storage, vm_management_pg, dvpg_is_on, pg_types_to_mtu, vds_mtu, is_mtu_supported=is_mtu_supported)

            if vmnics:
                for host_spec in hosts_spec:
                    host_spec['hostNetworkSpec'] = {'vmNics': vmnics}
            if pg_types_to_vmnics and pgtypes_to_vmnicuplink_mapping is not None:
                vmnics_list = []
                for vds in self.vds_payload:
                    if "portGroupSpecs" in vds:
                        portgroup_types = []
                        for pg in vds['portGroupSpecs']:
                            if pg['transportType'] == 'VM_MANAGEMENT':
                                portgroup_types.append('VXRAILSYSTEMVM')
                            elif pg['transportType'] == 'HOSTDISCOVERY':
                                portgroup_types.append('VXRAILDISCOVERY')
                            else:
                                portgroup_types.append(pg['transportType'])
                        for (key, value) in pg_types_to_vmnics.items():
                            key_list = json.loads(key)
                            # Remove VSAN PG if it is passed from VxRail JSON Input in case of COMPUTE cluster
                            if not vsan_storage and "VSAN" in key_list:
                                key_list.remove("VSAN")
                            if set(key_list) == set(portgroup_types):
                                vmnics_list = vmnics_list + self.create_vmnics_spec_for_system_dvs_advanced_profile(
                                    value, vds['name'], pgtypes_to_vmnicuplink_mapping[key])
                for host_spec in hosts_spec:
                    if 'hostNetworkSpec' in host_spec and 'vmNics' in host_spec['hostNetworkSpec']:
                        # Append to existing in case of Multi dvs
                        for i in vmnics_list:
                            if i not in host_spec['hostNetworkSpec']['vmNics']:
                                host_spec['hostNetworkSpec']['vmNics'].append(i)
                    else:
                        # Create New in case of single dvs
                        host_spec['hostNetworkSpec'] = {'vmNics': vmnics_list}

            print(*self.two_line_separator, sep='\n')

            return self
        else:
            self.utils.printRed("Exiting as VxRail Manager ssl/ssh thumbprint is not trusted")
            exit(1)

    def create_vmnics_spec_for_system_dvs_advanced_profile(self, dvs_vmnics_mapping, dvs_name, vmnic_uplink_mapping):
        vmnics = []
        for vmnic in dvs_vmnics_mapping:
            vmnics.append({'id': vmnic, 'vdsName': dvs_name, 'uplink': vmnic_uplink_mapping[vmnic]})
        return vmnics

    def hosts_spec_password_input(self, hosts_spec):
        password_provided = True
        for host_spec in hosts_spec:
            if len(host_spec["password"].strip()) == 0:
                password_provided = False
                break
        if not password_provided:
            self.utils.printCyan("Please choose password option:")
            self.utils.printBold("1) Input one password that is applicable to all the hosts (default)")
            self.utils.printBold("2) Input password individually for each host")
            option = self.utils.valid_input("\033[1m Enter your choice(number): \033[0m", "1", self.utils.valid_option,
                                            ["1", "2"])

            print(*self.two_line_separator, sep='\n')

            if option == "1":
                password = self.utils.handle_password_input("Enter root password for hosts:")
                print(*self.two_line_separator, sep='\n')
                for host_spec in hosts_spec:
                    host_spec["password"] = password
            elif option == "2":
                for host_spec in hosts_spec:
                    password = self.utils.handle_password_input("Enter root password for host {}:"
                                                                .format(host_spec["hostName"]))
                    print(*self.two_line_separator, sep='\n')
                    host_spec["password"] = password

    # this is for dump test
    def to_string(self):
        fjson_obj = {
            "cluster_name": self.get_cluster_name(),
            "vxrail_details": self.get_vxm_payload(),
            "host_spec": self.get_hosts_spec(),
            "vds_payload": self.get_vds_payload()
        }
        return json.dumps(fjson_obj)
