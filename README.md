# Workflow Optimization Script

## Table of contents
- [Quick start](#quick-start)
- [Usage](#usage)

## Quick start

Unzip the file and copy the directory WorkflowOptimization to /home/vcf/ directory on the SDDC Manager VM.

> Please note:
> - You are running the script in sddc-manager VM as vcf user.
> - Forward and reverse DNS settings for vCenter, NSX, VxRail Manager and ESXi components should be preconfigured.
> - If you choose DHCP as IP Allocation for TEP IPs option then make sure DHCP server must be configured for NSX VTEPS.
> - You must have run following pre-requisites before triggering script for Add Domain/Add Cluster workflow.
>   - Change VxRail Manager IP from static IP 192.168.10.200 to Management IP.
>   - Update VxRail Manager certificate with CN as valid VxRail Manager hostname.

## Usage

### Step by step input configuration for Add domain/Add cluster :

1. Add Domain
```python
vcf@wdc1sddc-1 [ ~/WorkflowOptimization ]$ python vxrail_workflow_optimization_automator.py
 Enter the Management domain SSO username: administrator@vsphere.local
 Enter the Management domain SSO password:


 Please choose one of the below option:
 1) Create Domain
 2) Add Cluster
 Enter your choice(number): 1


 Enter the domain name: wld-1


 Please choose one of the SSO Domain configuration input options:
 1) Create a new SSO Domain
 2) Join Management Domain's SSO Domain
 Enter your choice(number): 2


 Enter datastore name: datastore-wld


 ** ADVANCED_VXRAIL_SUPPLIED_VDS nic profile is supported only via VxRail JSON input
 Please choose one of the cluster configuration input options:
 1) VxRail JSON input
 2) Step by step input
 Enter your choice(number): 2


 Please select the type of storage for this cluster :
 1) vSAN
 2) VMFS on FC
 Enter your choice(number): 1
 Do you want to enable vSAN ESA ?('yes' or 'no'): no


 Lifecycle Management
 This option will set up clusters in this workload domain with vLCM images and cannot be changed once the workload domain is deployed.
 Do you want to manage clusters in this workload domain using vLCM images?('yes' or 'no'): yes


 Please enter vCenter details:
 vCenter FQDN: wdc1vc-2.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.40
 Gateway IP address: 172.16.10.1
 Subnet Mask(255.255.255.0):

 Enter root password:
 Confirm password:


 Enter Datacenter name: VxRail-Datacenter


 Please enter cluster name: cluster-1


 Please enter VxRail Manager FQDN: wdc1-vxrm-2.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.78


 Getting ssl and ssh thumbprint for VxRail Manager wdc1-vxrm-2.vxrail.local...


 Fetched ssl thumbprint: B3:4A:9D:B1:B1:96:BC:C7:0D:88:90:A5:8B:8D:5C:74:BC:D2:30:0C:CF:E4:48:78:F0:9A:18:39:91:EF:C3:CE
 Fetched ssh thumbprint: SHA256:YvCkFKqPxddimcqAcC50BPBRqrsDfQJDWBCo9F1PHA0


 Do you want to trust the same?('yes' or 'no'): yes


 Discovering hosts by VxRail Manager...


 ** By Default primary node gets selected. Please select atleast 2 other node(s).
 Hosts discovered by the VxRail Manager are:
 VxRail Manager is detected on primary node : HPHY0Q20000000
 1) HPJV0Q20000000
 2) HPJT0Q20000000
 Enter your choices(numbers by comma separated): 1,2


 Please enter host details for serial no HPHY0Q20000000:
 Enter FQDN: wdc1-005.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.60


 Please enter host details for serial no HPJV0Q20000000:
 Enter FQDN: wdc1-006.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.61


 Please enter host details for serial no HPJT0Q20000000:
 Enter FQDN: wdc1-007.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.62


 Please choose password option:
 1) Input one password that is applicable to all the hosts (default)
 2) Input password individually for each host
 Enter your choice(number): 1


 Enter root password for hosts:
 Confirm password:


 ** For e.g. vSAN Network VLAN ID: 1407, CIDR: 172.18.60.0/24,
    IP Range for hosts vSAN IP assignment: 172.18.60.55-172.18.60.60, Range for MTU: 1280-9000
 Please enter vSAN Network details:
 Enter VLAN Id: 2013
 Enter CIDR: 172.16.13.0/24
 Enter subnet mask(255.255.255.0):
 Enter gateway IP: 172.16.13.1
 Enter IP Range: 172.16.13.60-172.16.13.62
 Enter MTU value(1500): 1450


 ** For e.g. vMotion Network VLAN ID: 1406, CIDR: 172.18.59.0/24,
    IP Range for hosts vMotion IP assignment: 172.18.59.55-172.18.59.60, Range for MTU: 1280-9000
 Please enter vMotion Network details:
 Enter VLAN Id: 2012
 Enter CIDR: 172.16.12.0/24
 Enter subnet mask(255.255.255.0):
 Enter gateway IP: 172.16.12.1
 Enter IP Range: 172.16.12.60-172.16.12.62
 Enter MTU value(1500):


 ** By default the tool takes Management domain mgmt network for Create Domain and Primary cluster mgmt network for Create Cluster
 ** Existing mgmt network details: VLAN ID: 2010, CIDR: 172.16.10.0/24
 Do you want to provide Management Network details?('yes' or 'no'): no
 Enter MTU value(1500): 1500


 Do you want to provide VM_Management Network details?('yes' or 'no') - If no, we will use management network for VM: no


 ** ADVANCED_VXRAIL_SUPPLIED_VDS nic profile is supported only via VxRail JSON input
 Please select nic profile:
 1) TWO_HIGH_SPEED
 2) FOUR_HIGH_SPEED
 Enter your choice(number): 2


 Select the DVS option to proceed:
 1) System DVS for Overlay
 2) Separate DVS for Overlay
 Enter your choice(number): 1


 Please enter DVS details:

 Enter System DVS name: dvs-1
 Enter MTU value(9000): 9000

 Enter portgroup name for type MANAGEMENT: Management Network-1
 Enter portgroup name for type VSAN: vsan-1
 Enter portgroup name for type VMOTION: vmotion-1


 (Multi NSX VDS) Please choose the DVS for which NSX VLAN needs to be tagged (optional):
 -----id-----vds-----
 ----------------------
 1) dvs-1
 Enter your choices(comma separated if multiple / Empty):


 Getting shared NSX cluster information...
 ** No shared NSX instance was found, you need to create a new one


 Enter Geneve vLAN ID (0-4096): 2011


 Enter NSX manager root password:
 Confirm password:


 Please Enter NSX details:

 Enter FQDN for NSX VIP: wdc1vip-2.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.67


 Enter FQDN for 1st NSX Manager: wdc1-wld-nsxt-1.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.64


 Enter FQDN for 2nd NSX Manager: wdc1-wld-nsxt-2.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.65


 Enter FQDN for 3rd NSX Manager: wdc1-wld-nsxt-3.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.66


 Please choose IP Allocation for TEP IPs option:
 1) DHCP (default)
 2) Static IP Pool
 Enter your choice(number): 1


 Please enter VxRail Manager's root credentials:
 Enter password:
 Confirm password:


 Please enter VxRail Manager's admin credentials:
 Enter username (mystic):
 Enter password:
 Confirm password:


 Getting license information...


 Please choose a VSAN license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (ACTIVE)
 Enter your choice(number): 1


 Please choose a NSX-T license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (NEVER_EXPIRES)
 Enter your choice(number): 1


 Do you want to apply vSphere license('yes' or 'no'): yes


 ** Please make sure license has enough CPU slots required for the cluster
 Please choose a vSphere license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (ACTIVE)
 Enter your choice(number): 1


 vLCM Image Details
 vLCM Image: VCF-VxRail-Cluster-Image
 ESXi Version: 8.0.2-0.0.22380479
 Firmware/Driver Addon: vxrail-hsp:8.0.200-28263644
 Additional Components:
 MRVL-E4-CNA-Driver-Bundle : {'version': '6.0.345.0-1OEM.800.1.0.20143090'}
 Intel-icen : {'version': '1.11.3.0-1OEM.800.1.0.20613240'}
 BCM-vmware-perccli64-esxi8 : {'version': '007.2110.0000.0000-02'}
 Intel-ixgben : {'version': '1.15.1.0-1OEM.800.1.0.20613240'}
 Intel-igbn : {'version': '1.10.2.0-1OEM.700.1.0.15843807'}
 Broadcom-bnxt-Net-RoCE : {'version': '226.0.245.4-1OEM.800.1.0.20613240'}
 Intel-i40en : {'version': '2.5.2.0-1OEM.700.1.0.15843807'}
 MRVL-QLogic-FC : {'version': '5.4.80.0-1OEM.800.1.0.20143090'}


{
  "computeSpec": {
    "clusterSpecs": [
      {
        "clusterImageId": "VCF-VxRail-Cluster-Image",
        "datastoreSpec": {
          "vsanDatastoreSpec": {
            "datastoreName": "datastore-wld",
            "esaConfig": {
              "enabled": false
            },
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
          }
        },
        "hostSpecs": [
          {
            "hostName": "wdc1-005.vxrail.local",
            "ipAddress": "172.16.10.60",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPHY0Q20000000",
            "softwareInfo": {
              "baseImage": {
                "version": "8.0.2-0.0.22380479"
              },
              "components": {
                "BCM-vmware-perccli64-esxi8": {
                  "version": "007.2110.0000.0000-02"
                },
                "Broadcom-bnxt-Net-RoCE": {
                  "version": "226.0.245.4-1OEM.800.1.0.20613240"
                },
                "Intel-i40en": {
                  "version": "2.5.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-icen": {
                  "version": "1.11.3.0-1OEM.800.1.0.20613240"
                },
                "Intel-igbn": {
                  "version": "1.10.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-ixgben": {
                  "version": "1.15.1.0-1OEM.800.1.0.20613240"
                },
                "MRVL-E4-CNA-Driver-Bundle": {
                  "version": "6.0.345.0-1OEM.800.1.0.20143090"
                },
                "MRVL-QLogic-FC": {
                  "version": "5.4.80.0-1OEM.800.1.0.20143090"
                }
              },
              "hardwareSupport": {
                "packages": {
                  "com.vxrail.hsm": {
                    "pkg": "vxrail-hsp",
                    "version": "8.0.200-28263644"
                  }
                }
              }
            },
            "sshThumbprint": "SHA256:bNwti3geK+oVJOCyFPfKtezOAc5ohWF6dyrHZJ4sp4I",
            "username": "root"
          },
          {
            "hostName": "wdc1-006.vxrail.local",
            "ipAddress": "172.16.10.61",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPJV0Q20000000",
            "softwareInfo": {
              "baseImage": {
                "version": "8.0.2-0.0.22380479"
              },
              "components": {
                "BCM-vmware-perccli64-esxi8": {
                  "version": "007.2110.0000.0000-02"
                },
                "Broadcom-bnxt-Net-RoCE": {
                  "version": "226.0.245.4-1OEM.800.1.0.20613240"
                },
                "Intel-i40en": {
                  "version": "2.5.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-icen": {
                  "version": "1.11.3.0-1OEM.800.1.0.20613240"
                },
                "Intel-igbn": {
                  "version": "1.10.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-ixgben": {
                  "version": "1.15.1.0-1OEM.800.1.0.20613240"
                },
                "MRVL-E4-CNA-Driver-Bundle": {
                  "version": "6.0.345.0-1OEM.800.1.0.20143090"
                },
                "MRVL-QLogic-FC": {
                  "version": "5.4.80.0-1OEM.800.1.0.20143090"
                }
              },
              "hardwareSupport": {
                "packages": {
                  "com.vxrail.hsm": {
                    "pkg": "vxrail-hsp",
                    "version": "8.0.200-28263644"
                  }
                }
              }
            },
            "sshThumbprint": "SHA256:5DyYH7oxhNq3l1EoFoNz1L9rWWkPVqLD24PNageLVPg",
            "username": "root"
          },
          {
            "hostName": "wdc1-007.vxrail.local",
            "ipAddress": "172.16.10.62",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPJT0Q20000000",
            "softwareInfo": {
              "baseImage": {
                "version": "8.0.2-0.0.22380479"
              },
              "components": {
                "BCM-vmware-perccli64-esxi8": {
                  "version": "007.2110.0000.0000-02"
                },
                "Broadcom-bnxt-Net-RoCE": {
                  "version": "226.0.245.4-1OEM.800.1.0.20613240"
                },
                "Intel-i40en": {
                  "version": "2.5.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-icen": {
                  "version": "1.11.3.0-1OEM.800.1.0.20613240"
                },
                "Intel-igbn": {
                  "version": "1.10.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-ixgben": {
                  "version": "1.15.1.0-1OEM.800.1.0.20613240"
                },
                "MRVL-E4-CNA-Driver-Bundle": {
                  "version": "6.0.345.0-1OEM.800.1.0.20143090"
                },
                "MRVL-QLogic-FC": {
                  "version": "5.4.80.0-1OEM.800.1.0.20143090"
                }
              },
              "hardwareSupport": {
                "packages": {
                  "com.vxrail.hsm": {
                    "pkg": "vxrail-hsp",
                    "version": "8.0.200-28263644"
                  }
                }
              }
            },
            "sshThumbprint": "SHA256:TiFLJ9LQa/1wovdNv2fqHpqvmY666fSfwEkFkk0utN4",
            "username": "root"
          }
        ],
        "name": "cluster-1",
        "networkSpec": {
          "nsxClusterSpec": {
            "nsxTClusterSpec": {
              "geneveVlanId": "2011"
            }
          },
          "vdsSpecs": [
            {
              "isUsedByNsxt": true,
              "mtu": 9000,
              "name": "dvs-1",
              "portGroupSpecs": [
                {
                  "name": "Management Network-1",
                  "transportType": "MANAGEMENT"
                },
                {
                  "name": "vmotion-1",
                  "transportType": "VMOTION"
                },
                {
                  "name": "vsan-1",
                  "transportType": "VSAN"
                }
              ]
            }
          ]
        },
        "skipThumbprintValidation": false,
        "vxRailDetails": {
          "adminCredentials": {
            "credentialType": "SSH",
            "password": "*******",
            "username": "mystic"
          },
          "dnsName": "wdc1-vxrm-2.vxrail.local",
          "ipAddress": "172.16.10.78",
          "networks": [
            {
              "gateway": "172.16.12.1",
              "ipPools": [
                {
                  "end": "172.16.12.62",
                  "start": "172.16.12.60"
                }
              ],
              "mask": "255.255.255.0",
              "mtu": 1500,
              "subnet": "172.16.12.0/24",
              "type": "VMOTION",
              "vlanId": 2012
            },
            {
              "gateway": "172.16.13.1",
              "ipPools": [
                {
                  "end": "172.16.13.62",
                  "start": "172.16.13.60"
                }
              ],
              "mask": "255.255.255.0",
              "mtu": 1450,
              "subnet": "172.16.13.0/24",
              "type": "VSAN",
              "vlanId": 2013
            },
            {
              "gateway": "172.16.10.1",
              "mask": "255.255.255.0",
              "mtu": 1500,
              "subnet": "172.16.10.0/24",
              "type": "MANAGEMENT",
              "vlanId": 2010
            }
          ],
          "nicProfile": "FOUR_HIGH_SPEED",
          "rootCredentials": {
            "credentialType": "SSH",
            "password": "*******",
            "username": "root"
          },
          "sshThumbprint": "SHA256:YvCkFKqPxddimcqAcC50BPBRqrsDfQJDWBCo9F1PHA0",
          "sslThumbprint": "B3:4A:9D:B1:B1:96:BC:C7:0D:88:90:A5:8B:8D:5C:74:BC:D2:30:0C:CF:E4:48:78:F0:9A:18:39:91:EF:C3:CE"
        }
      }
    ]
  },
  "domainName": "wld-1",
  "nsxTSpec": {
    "formFactor": "large",
    "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
    "nsxManagerAdminPassword": "*******",
    "nsxManagerSpecs": [
      {
        "name": "wdc1-wld-nsxt-1",
        "networkDetailsSpec": {
          "dnsName": "wdc1-wld-nsxt-1.vxrail.local",
          "gateway": "172.16.10.1",
          "ipAddress": "172.16.10.64",
          "subnetMask": "255.255.255.0"
        }
      },
      {
        "name": "wdc1-wld-nsxt-2",
        "networkDetailsSpec": {
          "dnsName": "wdc1-wld-nsxt-2.vxrail.local",
          "gateway": "172.16.10.1",
          "ipAddress": "172.16.10.65",
          "subnetMask": "255.255.255.0"
        }
      },
      {
        "name": "wdc1-wld-nsxt-3",
        "networkDetailsSpec": {
          "dnsName": "wdc1-wld-nsxt-3.vxrail.local",
          "gateway": "172.16.10.1",
          "ipAddress": "172.16.10.66",
          "subnetMask": "255.255.255.0"
        }
      }
    ],
    "vip": "172.16.10.67",
    "vipFqdn": "wdc1vip-2.vxrail.local"
  },
  "ssoDomainSpec": null,
  "vcenterSpec": {
    "datacenterName": "VxRail-Datacenter",
    "name": "wdc1vc-2",
    "networkDetailsSpec": {
      "dnsName": "wdc1vc-2.vxrail.local",
      "gateway": "172.16.10.1",
      "ipAddress": "172.16.10.40",
      "subnetMask": "255.255.255.0"
    },
    "rootPassword": "*******",
    "storageSize": "lstorage",
    "vmSize": "medium"
  }
}

 Enter to continue ...
 Validating the input....
 Validation started for create domain operation. The validation id is: ab14e71f-fdac-410f-9f07-b25eef97aae3
 Polling on validation api https://localhost/v1/domains/validations/ab14e71f-fdac-410f-9f07-b25eef97aae3
 Validation IN_PROGRESS. It will take some time to complete. Please wait...
 Validation is in progress
 Validation is in progress
 Validation is in progress
 Validation ended with status: SUCCEEDED

 Enter to create domain...
 Triggered create domain, monitor the status of the task(task-id:ecd9346a-b7c8-472a-b0ad-6e0beaee3805) from sddc-manager ui
```

2. Add Cluster
```python
vcf@wdc1sddc-1 [ ~/WorkflowOptimization ]$ python vxrail_workflow_optimization_automator.py
 Enter the Management domain SSO username: administrator@vsphere.local
 Enter the Management domain SSO password:


 Please choose one of the below option:
 1) Create Domain
 2) Add Cluster
 Enter your choice(number): 2


 Getting the domains...


 Please choose the domain to which cluster has to be added:
 1) MGMT
 Enter your choice(number): 1


 Enter datastore name: datastore-wld


 ** ADVANCED_VXRAIL_SUPPLIED_VDS nic profile is supported only via VxRail JSON input
 Please choose one of the cluster configuration input options:
 1) VxRail JSON input
 2) Step by step input
 Enter your choice(number): 2


 Please select the type of storage for this cluster :
 1) vSAN
 2) VMFS on FC
 Enter your choice(number): 1


 Do you want to mount a remote datastore?('yes' or 'no'): no
 Do you want to enable vSAN ESA ?('yes' or 'no'): no


 Please enter cluster name: cluster-1


 Please enter VxRail Manager FQDN: wdc1-vxrm-2.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.78


 Getting ssl and ssh thumbprint for VxRail Manager wdc1-vxrm-2.vxrail.local...


 Fetched ssl thumbprint: B3:4A:9D:B1:B1:96:BC:C7:0D:88:90:A5:8B:8D:5C:74:BC:D2:30:0C:CF:E4:48:78:F0:9A:18:39:91:EF:C3:CE
 Fetched ssh thumbprint: SHA256:YvCkFKqPxddimcqAcC50BPBRqrsDfQJDWBCo9F1PHA0


 Do you want to trust the same?('yes' or 'no'): yes


 Discovering hosts by VxRail Manager...


 ** By Default primary node gets selected. Please select atleast 2 other node(s).
 Hosts discovered by the VxRail Manager are:
 VxRail Manager is detected on primary node : HPHY0Q20000000
 1) HPJV0Q20000000
 2) HPJT0Q20000000
 Enter your choices(numbers by comma separated): 1,2


 Please enter host details for serial no HPHY0Q20000000:
 Enter FQDN: wdc1-005.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.60


 Please enter host details for serial no HPJV0Q20000000:
 Enter FQDN: wdc1-006.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.61


 Please enter host details for serial no HPJT0Q20000000:
 Enter FQDN: wdc1-007.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.62


 Please choose password option:
 1) Input one password that is applicable to all the hosts (default)
 2) Input password individually for each host
 Enter your choice(number): 1


 Enter root password for hosts:
 Confirm password:


 ** For e.g. vSAN Network VLAN ID: 1407, CIDR: 172.18.60.0/24,
    IP Range for hosts vSAN IP assignment: 172.18.60.55-172.18.60.60, Range for MTU: 1280-9000
 Please enter vSAN Network details:
 Enter VLAN Id: 2013
 Enter CIDR: 172.16.13.0/24
 Enter subnet mask(255.255.255.0):
 Enter gateway IP: 172.16.13.1
 Enter IP Range: 172.16.13.60-172.16.13.62
 Enter MTU value(1500): 1450


 ** For e.g. vMotion Network VLAN ID: 1406, CIDR: 172.18.59.0/24,
    IP Range for hosts vMotion IP assignment: 172.18.59.55-172.18.59.60, Range for MTU: 1280-9000
 Please enter vMotion Network details:
 Enter VLAN Id: 2012
 Enter CIDR: 172.16.12.0/24
 Enter subnet mask(255.255.255.0):
 Enter gateway IP: 172.16.12.1
 Enter IP Range: 172.16.12.60-172.16.12.62
 Enter MTU value(1500): 1500


 ** By default the tool takes Management domain mgmt network for Create Domain and Primary cluster mgmt network for Create Cluster
 ** Existing mgmt network details: VLAN ID: 2010, CIDR: 172.16.10.0/24
 Do you want to provide Management Network details?('yes' or 'no'): yes


 Please enter Management Network details:
 Enter VLAN Id: 2010
 Enter CIDR: 172.16.10.0/24
 Enter subnet mask(255.255.255.0):
 Enter gateway IP: 172.16.10.1
 Enter MTU value(1500): 1500


 Do you want to provide VM_Management Network details?('yes' or 'no') - If no, we will use management network for VM: no


 ** ADVANCED_VXRAIL_SUPPLIED_VDS nic profile is supported only via VxRail JSON input
 Please select nic profile:
 1) TWO_HIGH_SPEED
 2) FOUR_HIGH_SPEED
 Enter your choice(number): 1


 Select the DVS option to proceed:
 1) System DVS for Overlay
 2) Separate DVS for Overlay
 Enter your choice(number): 2


 Please enter DVS details:

 Enter System DVS name: dvs-1
 Enter MTU value(9000):

 Enter portgroup name for type MANAGEMENT: Management Network-1
 Enter portgroup name for type VSAN: vsan-1
 Enter portgroup name for type VMOTION: vmotion-1

 ** Overlay DVS uses default MTU value of 9000
 Enter Overlay DVS name: sep-overlay-dvs


 Please choose the nics for overlay traffic:
 -----id-----speed-----
 ----------------------
 1) vmnic2 - 10000
 2) vmnic3 - 10000
 3) vmnic4 - 10000
 4) vmnic5 - 10000
 Enter your choices(minimum 2 numbers comma separated): 1,2


 (Multi NSX VDS) Please choose the DVS for which NSX VLAN needs to be tagged (optional):
 -----id-----vds-----
 ----------------------
 1) dvs-1
 2) sep-overlay-dvs
 Enter your choices(comma separated if multiple / Empty): 1


 Getting shared NSX cluster information...


 Enter Geneve vLAN ID (0-4096):  2011


 Found NSX instance : wdc1-vip-nsx-mgmt.vxrail.local


 Please choose IP Allocation for TEP IPs option:
 1) DHCP (default)
 2) Static IP Pool
 Enter your choice(number): 2


 Select the option for Static IP Pool:
 1) Create New Static IP Pool(default)
 2) Re-use an Existing Static Pool
 Enter your choice(number): 1


 Create New Static IP Pool
 Enter Pool Name: ip-pool-1
 Enter Description(Optional): IP_POOL


 Subnet #1
 Enter CIDR: 172.16.14.0/24
 ** Multiple IP Ranges are supported by comma separated
 Enter IP Range: 172.16.14.10-172.16.14.100
 Enter Gateway IP: 172.16.14.1


 Do you want to add another subnet ? (Enter 'yes' or 'no'): no


 Please enter VxRail Manager's root credentials:
 Enter password:
 Confirm password:


 Please enter VxRail Manager's admin credentials:
 Enter username (mystic):
 Enter password:
 Confirm password:


 Getting license information...


 Please choose a VSAN license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (ACTIVE)
 Enter your choice(number): 1


 Please choose a NSX-T license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (NEVER_EXPIRES)
 Enter your choice(number): 1


 Do you want to apply vSphere license('yes' or 'no'): yes


 ** Please make sure license has enough CPU slots required for the cluster
 Please choose a vSphere license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX(ACTIVE)
 Enter your choice(number): 1


{
  "computeSpec": {
    "clusterSpecs": [
      {
        "datastoreSpec": {
          "vsanDatastoreSpec": {
            "datastoreName": "datastore-wld",
            "esaConfig": {
              "enabled": false
            },
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
          }
        },
        "hostSpecs": [
          {
            "hostName": "wdc1-005.vxrail.local",
            "hostNetworkSpec": {
              "vmNics": [
                {
                  "id": "vmnic2",
                  "vdsName": "sep-overlay-dvs"
                },
                {
                  "id": "vmnic3",
                  "vdsName": "sep-overlay-dvs"
                }
              ]
            },
            "ipAddress": "172.16.10.60",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPHY0Q20000000",
            "sshThumbprint": "SHA256:bNwti3geK+oVJOCyFPfKtezOAc5ohWF6dyrHZJ4sp4I",
            "username": "root"
          },
          {
            "hostName": "wdc1-006.vxrail.local",
            "hostNetworkSpec": {
              "vmNics": [
                {
                  "id": "vmnic2",
                  "vdsName": "sep-overlay-dvs"
                },
                {
                  "id": "vmnic3",
                  "vdsName": "sep-overlay-dvs"
                }
              ]
            },
            "ipAddress": "172.16.10.61",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPJV0Q20000000",
            "sshThumbprint": "SHA256:5DyYH7oxhNq3l1EoFoNz1L9rWWkPVqLD24PNageLVPg",
            "username": "root"
          },
          {
            "hostName": "wdc1-007.vxrail.local",
            "hostNetworkSpec": {
              "vmNics": [
                {
                  "id": "vmnic2",
                  "vdsName": "sep-overlay-dvs"
                },
                {
                  "id": "vmnic3",
                  "vdsName": "sep-overlay-dvs"
                }
              ]
            },
            "ipAddress": "172.16.10.62",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPJT0Q20000000",
            "sshThumbprint": "SHA256:TiFLJ9LQa/1wovdNv2fqHpqvmY666fSfwEkFkk0utN4",
            "username": "root"
          }
        ],
        "name": "cluster-1",
        "networkSpec": {
          "nsxClusterSpec": {
            "nsxTClusterSpec": {
              "geneveVlanId": "2011",
              "ipAddressPoolSpec": {
                "description": "IP_POOL",
                "name": "ip-pool-1",
                "subnets": [
                  {
                    "cidr": "172.16.14.0/24",
                    "gateway": "172.16.14.1",
                    "ipAddressPoolRanges": [
                      {
                        "end": "172.16.14.100",
                        "start": "172.16.14.10"
                      }
                    ]
                  }
                ]
              }
            }
          },
          "vdsSpecs": [
            {
              "mtu": 9000,
              "name": "dvs-1",
              "nsxtSwitchConfig": {
                "transportZones": [
                  {
                    "transportType": "VLAN"
                  }
                ]
              },
              "portGroupSpecs": [
                {
                  "name": "Management Network-1",
                  "transportType": "MANAGEMENT"
                },
                {
                  "name": "vmotion-1",
                  "transportType": "VMOTION"
                },
                {
                  "name": "vsan-1",
                  "transportType": "VSAN"
                }
              ]
            },
            {
              "mtu": 9000,
              "name": "sep-overlay-dvs",
              "nsxtSwitchConfig": {
                "transportZones": [
                  {
                    "transportType": "OVERLAY"
                  }
                ]
              }
            }
          ]
        },
        "skipThumbprintValidation": false,
        "vxRailDetails": {
          "adminCredentials": {
            "credentialType": "SSH",
            "password": "*******",
            "username": "mystic"
          },
          "dnsName": "wdc1-vxrm-2.vxrail.local",
          "ipAddress": "172.16.10.78",
          "networks": [
            {
              "gateway": "172.16.12.1",
              "ipPools": [
                {
                  "end": "172.16.12.62",
                  "start": "172.16.12.60"
                }
              ],
              "mask": "255.255.255.0",
              "mtu": 1500,
              "subnet": "172.16.12.0/24",
              "type": "VMOTION",
              "vlanId": 2012
            },
            {
              "gateway": "172.16.13.1",
              "ipPools": [
                {
                  "end": "172.16.13.62",
                  "start": "172.16.13.60"
                }
              ],
              "mask": "255.255.255.0",
              "mtu": 1450,
              "subnet": "172.16.13.0/24",
              "type": "VSAN",
              "vlanId": 2013
            },
            {
              "gateway": "172.16.10.1",
              "mask": "255.255.255.0",
              "mtu": 1500,
              "subnet": "172.16.10.0/24",
              "type": "MANAGEMENT",
              "vlanId": 2010
            }
          ],
          "nicProfile": "TWO_HIGH_SPEED",
          "rootCredentials": {
            "credentialType": "SSH",
            "password": "*******",
            "username": "root"
          },
          "sshThumbprint": "SHA256:YvCkFKqPxddimcqAcC50BPBRqrsDfQJDWBCo9F1PHA0",
          "sslThumbprint": "B3:4A:9D:B1:B1:96:BC:C7:0D:88:90:A5:8B:8D:5C:74:BC:D2:30:0C:CF:E4:48:78:F0:9A:18:39:91:EF:C3:CE"
        }
      }
    ]
  },
  "domainId": "48f320ac-1adf-4106-8608-f3ea00362c8a"
}

 Enter to continue ...
 Validating the input....
 Validation started for add cluster operation. The validation id is: 1a100ccf-3d86-49b8-8432-8de525130906
 Polling on validation api https://localhost/v1/clusters/validations/1a100ccf-3d86-49b8-8432-8de525130906
 Validation IN_PROGRESS. It will take some time to complete. Please wait...
 Validation is in progress
 Validation is in progress
 Validation ended with status: SUCCEEDED

 Enter to add cluster...
 Triggered add cluster, monitor the status of the task(task-id:36c0cff3-9160-4c45-a67e-685361d1d0b8) from sddc-manager ui
```

### VxRail JSON input configuration for Add domain/Add cluster :

1. Add Domain
```python
vcf@wdc1sddc-1 [ ~/WorkflowOptimization ]$ python vxrail_workflow_optimization_automator.py
 Enter the Management domain SSO username: administrator@vsphere.local
 Enter the Management domain SSO password:


 Please choose one of the below option:
 1) Create Domain
 2) Add Cluster
 Enter your choice(number): 1


 Enter the domain name: wld-1


 Please choose one of the SSO Domain configuration input options:
 1) Create a new SSO Domain
 2) Join Management Domain's SSO Domain
 Enter your choice(number): 1


 Please enter SSO Domain details:
 Enter the SSO domain name: vrack.local
 Enter SSO Administration password:
 Confirm password:


 Enter datastore name: datastore-wld


 ** ADVANCED_VXRAIL_SUPPLIED_VDS nic profile is supported only via VxRail JSON input
 Please choose one of the cluster configuration input options:
 1) VxRail JSON input
 2) Step by step input
 Enter your choice(number): 1


 Please enter VxRail JSON location: /home/vcf/createwld_2x10.json
 Do you want to enable vSAN ESA ?('yes' or 'no'): no


 Lifecycle Management
 This option will set up clusters in this workload domain with vLCM images and cannot be changed once the workload domain is deployed.
 Do you want to manage clusters in this workload domain using vLCM images?('yes' or 'no'): yes




 Enter Gateway IP address for vCenter wdc1vc-2.vxrail.local: 172.16.10.1
 Enter Subnet Mask for vCenter wdc1vc-2.vxrail.local(255.255.255.0):
 Enter vCenter wdc1vc-2.vxrail.local root password:
 Confirm password:


 Getting ssl thumbprint for the passed VxRail Manager wdc1-vxrm-2.vxrail.local


 Fetched ssl thumbprint: B3:4A:9D:B1:B1:96:BC:C7:0D:88:90:A5:8B:8D:5C:74:BC:D2:30:0C:CF:E4:48:78:F0:9A:18:39:91:EF:C3:CE
 Fetched ssh thumbprint: SHA256:YvCkFKqPxddimcqAcC50BPBRqrsDfQJDWBCo9F1PHA0


 Do you want to trust the same?('yes' or 'no'): yes


 Getting ssh thumbprint for the hosts passed in Json
 Discovering hosts by VxRail Manager...


 Fetched ssh thumbprint for hosts passed in Json:
 --Serial Number--------------SSH Thumbprint--------------------------
 ---------------------------------------------------------------------
  HPHY0Q20000000 : SHA256:bNwti3geK+oVJOCyFPfKtezOAc5ohWF6dyrHZJ4sp4I
  HPJV0Q20000000 : SHA256:5DyYH7oxhNq3l1EoFoNz1L9rWWkPVqLD24PNageLVPg
  HPJT0Q20000000 : SHA256:TiFLJ9LQa/1wovdNv2fqHpqvmY666fSfwEkFkk0utN4


 Select the DVS option to proceed:
 1) System DVS for Overlay
 2) Separate DVS for Overlay
 Enter your choice(number): 2


 Please enter DVS details:

 Enter System DVS name: dvs-1

 Enter portgroup name for type MANAGEMENT: Management Network-1
 Enter portgroup name for type VSAN: vsan-1
 Enter portgroup name for type VMOTION: vmotion-1

 ** Overlay DVS uses default MTU value of 9000
 Enter Overlay DVS name: sep-overlay


 Please choose the nics for overlay traffic:
 -----id-----speed-----
 ----------------------
 1) vmnic2 - 10000
 2) vmnic3 - 10000
 3) vmnic4 - 10000
 4) vmnic5 - 10000
 Enter your choices(minimum 2 numbers comma separated): 1,2


 (Multi NSX VDS) Please choose the DVS for which NSX VLAN needs to be tagged (optional):
 -----id-----vds-----
 ----------------------
 1) dvs-1
 2) sep-overlay
 Enter your choices(comma separated if multiple / Empty): 1


 Getting shared NSX cluster information...
 ** No shared NSX instance was found, you need to create a new one


 Enter Geneve vLAN ID (0-4096): 2011


 Enter NSX manager root password:
 Confirm password:


 Please Enter NSX details:

 Enter FQDN for NSX VIP: wdc1vip-2.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.67


 Enter FQDN for 1st NSX Manager: wdc1-wld-nsxt-1.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.64


 Enter FQDN for 2nd NSX Manager: wdc1-wld-nsxt-2.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.65


 Enter FQDN for 3rd NSX Manager: wdc1-wld-nsxt-3.vxrail.local
 Resolving IP from DNS...
 Resolved IP address: 172.16.10.66


 Please choose IP Allocation for TEP IPs option:
 1) DHCP (default)
 2) Static IP Pool
 Enter your choice(number): 2


 Create New Static IP Pool
 Enter Pool Name: ip-pool-1
 Enter Description(Optional): IP_POOL


 Subnet #1
 Enter CIDR: 172.16.14.0/24
 ** Multiple IP Ranges are supported by comma separated
 Enter IP Range: 172.16.14.10-172.16.14.100
 Enter Gateway IP: 172.16.14.1


 Do you want to add another subnet ? (Enter 'yes' or 'no'): no


 Getting license information...


 Please choose a VSAN license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX(ACTIVE)
 Enter your choice(number): 1


 Please choose a NSX-T license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX(NEVER_EXPIRES)
 Enter your choice(number): 1


 Do you want to apply vSphere license('yes' or 'no'): yes


 ** Please make sure license has enough CPU slots required for the cluster
 Please choose a vSphere license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (ACTIVE)
 Enter your choice(number): 1


 vLCM Image Details
 vLCM Image: VCF-VxRail-Cluster-Image
 ESXi Version: 8.0.2-0.0.22380479
 Firmware/Driver Addon: vxrail-hsp:8.0.200-28263644
 Additional Components:
 MRVL-E4-CNA-Driver-Bundle : {'version': '6.0.345.0-1OEM.800.1.0.20143090'}
 Intel-icen : {'version': '1.11.3.0-1OEM.800.1.0.20613240'}
 BCM-vmware-perccli64-esxi8 : {'version': '007.2110.0000.0000-02'}
 Intel-ixgben : {'version': '1.15.1.0-1OEM.800.1.0.20613240'}
 Intel-igbn : {'version': '1.10.2.0-1OEM.700.1.0.15843807'}
 Broadcom-bnxt-Net-RoCE : {'version': '226.0.245.4-1OEM.800.1.0.20613240'}
 Intel-i40en : {'version': '2.5.2.0-1OEM.700.1.0.15843807'}
 MRVL-QLogic-FC : {'version': '5.4.80.0-1OEM.800.1.0.20143090'}


{
  "computeSpec": {
    "clusterSpecs": [
      {
        "clusterImageId": "VCF-VxRail-Cluster-Image",
        "datastoreSpec": {
          "vsanDatastoreSpec": {
            "datastoreName": "datastore-wld",
            "esaConfig": {
              "enabled": false
            },
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
          }
        },
        "hostSpecs": [
          {
            "hostName": "wdc1-005.vxrail.local",
            "hostNetworkSpec": {
              "vmNics": [
                {
                  "id": "vmnic2",
                  "vdsName": "sep-overlay"
                },
                {
                  "id": "vmnic3",
                  "vdsName": "sep-overlay"
                }
              ]
            },
            "ipAddress": "172.16.10.60",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPHY0Q20000000",
            "softwareInfo": {
              "baseImage": {
                "version": "8.0.2-0.0.22380479"
              },
              "components": {
                "BCM-vmware-perccli64-esxi8": {
                  "version": "007.2110.0000.0000-02"
                },
                "Broadcom-bnxt-Net-RoCE": {
                  "version": "226.0.245.4-1OEM.800.1.0.20613240"
                },
                "Intel-i40en": {
                  "version": "2.5.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-icen": {
                  "version": "1.11.3.0-1OEM.800.1.0.20613240"
                },
                "Intel-igbn": {
                  "version": "1.10.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-ixgben": {
                  "version": "1.15.1.0-1OEM.800.1.0.20613240"
                },
                "MRVL-E4-CNA-Driver-Bundle": {
                  "version": "6.0.345.0-1OEM.800.1.0.20143090"
                },
                "MRVL-QLogic-FC": {
                  "version": "5.4.80.0-1OEM.800.1.0.20143090"
                }
              },
              "hardwareSupport": {
                "packages": {
                  "com.vxrail.hsm": {
                    "pkg": "vxrail-hsp",
                    "version": "8.0.200-28263644"
                  }
                }
              }
            },
            "sshThumbprint": "SHA256:bNwti3geK+oVJOCyFPfKtezOAc5ohWF6dyrHZJ4sp4I",
            "username": "root"
          },
          {
            "hostName": "wdc1-006.vxrail.local",
            "hostNetworkSpec": {
              "vmNics": [
                {
                  "id": "vmnic2",
                  "vdsName": "sep-overlay"
                },
                {
                  "id": "vmnic3",
                  "vdsName": "sep-overlay"
                }
              ]
            },
            "ipAddress": "172.16.10.61",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPJV0Q20000000",
            "softwareInfo": {
              "baseImage": {
                "version": "8.0.2-0.0.22380479"
              },
              "components": {
                "BCM-vmware-perccli64-esxi8": {
                  "version": "007.2110.0000.0000-02"
                },
                "Broadcom-bnxt-Net-RoCE": {
                  "version": "226.0.245.4-1OEM.800.1.0.20613240"
                },
                "Intel-i40en": {
                  "version": "2.5.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-icen": {
                  "version": "1.11.3.0-1OEM.800.1.0.20613240"
                },
                "Intel-igbn": {
                  "version": "1.10.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-ixgben": {
                  "version": "1.15.1.0-1OEM.800.1.0.20613240"
                },
                "MRVL-E4-CNA-Driver-Bundle": {
                  "version": "6.0.345.0-1OEM.800.1.0.20143090"
                },
                "MRVL-QLogic-FC": {
                  "version": "5.4.80.0-1OEM.800.1.0.20143090"
                }
              },
              "hardwareSupport": {
                "packages": {
                  "com.vxrail.hsm": {
                    "pkg": "vxrail-hsp",
                    "version": "8.0.200-28263644"
                  }
                }
              }
            },
            "sshThumbprint": "SHA256:5DyYH7oxhNq3l1EoFoNz1L9rWWkPVqLD24PNageLVPg",
            "username": "root"
          },
          {
            "hostName": "wdc1-007.vxrail.local",
            "hostNetworkSpec": {
              "vmNics": [
                {
                  "id": "vmnic2",
                  "vdsName": "sep-overlay"
                },
                {
                  "id": "vmnic3",
                  "vdsName": "sep-overlay"
                }
              ]
            },
            "ipAddress": "172.16.10.62",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPJT0Q20000000",
            "softwareInfo": {
              "baseImage": {
                "version": "8.0.2-0.0.22380479"
              },
              "components": {
                "BCM-vmware-perccli64-esxi8": {
                  "version": "007.2110.0000.0000-02"
                },
                "Broadcom-bnxt-Net-RoCE": {
                  "version": "226.0.245.4-1OEM.800.1.0.20613240"
                },
                "Intel-i40en": {
                  "version": "2.5.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-icen": {
                  "version": "1.11.3.0-1OEM.800.1.0.20613240"
                },
                "Intel-igbn": {
                  "version": "1.10.2.0-1OEM.700.1.0.15843807"
                },
                "Intel-ixgben": {
                  "version": "1.15.1.0-1OEM.800.1.0.20613240"
                },
                "MRVL-E4-CNA-Driver-Bundle": {
                  "version": "6.0.345.0-1OEM.800.1.0.20143090"
                },
                "MRVL-QLogic-FC": {
                  "version": "5.4.80.0-1OEM.800.1.0.20143090"
                }
              },
              "hardwareSupport": {
                "packages": {
                  "com.vxrail.hsm": {
                    "pkg": "vxrail-hsp",
                    "version": "8.0.200-28263644"
                  }
                }
              }
            },
            "sshThumbprint": "SHA256:TiFLJ9LQa/1wovdNv2fqHpqvmY666fSfwEkFkk0utN4",
            "username": "root"
          }
        ],
        "name": "cluster-2",
        "networkSpec": {
          "nsxClusterSpec": {
            "nsxTClusterSpec": {
              "geneveVlanId": "2011"
            }
          },
          "vdsSpecs": [
            {
              "name": "dvs-1",
              "nsxtSwitchConfig": {
                "transportZones": [
                  {
                    "transportType": "VLAN"
                  }
                ]
              },
              "portGroupSpecs": [
                {
                  "name": "Management Network-1",
                  "transportType": "MANAGEMENT"
                },
                {
                  "name": "vmotion-1",
                  "transportType": "VMOTION"
                },
                {
                  "name": "vsan-1",
                  "transportType": "VSAN"
                }
              ]
            },
            {
              "mtu": 9000,
              "name": "sep-overlay",
              "nsxtSwitchConfig": {
                "transportZones": [
                  {
                    "transportType": "OVERLAY"
                  }
                ]
              }
            }
          ]
        },
        "skipThumbprintValidation": false,
        "vxRailDetails": {
          "adminCredentials": {
            "credentialType": "SSH",
            "password": "*******",
            "username": "mystic"
          },
          "arrayContextWithKeyValuePair": {
            "hosts.geo_location": [
              {
                "arrayAssociationContext": {
                  "arrayAttributeIdsKeyValue": {
                    "host_psnt": "HPHY0Q20000000",
                    "hostname": "wdc1-005"
                  }
                },
                "simpleAttributes": [
                  {
                    "attributeName": "rack_name",
                    "datatype": "STRING",
                    "value": "wdc-1"
                  },
                  {
                    "attributeName": "position",
                    "datatype": "INTEGER",
                    "value": 5
                  }
                ]
              },
              {
                "arrayAssociationContext": {
                  "arrayAttributeIdsKeyValue": {
                    "host_psnt": "HPJV0Q20000000",
                    "hostname": "wdc1-006"
                  }
                },
                "simpleAttributes": [
                  {
                    "attributeName": "rack_name",
                    "datatype": "STRING",
                    "value": "wdc-1"
                  },
                  {
                    "attributeName": "position",
                    "datatype": "INTEGER",
                    "value": 6
                  }
                ]
              },
              {
                "arrayAssociationContext": {
                  "arrayAttributeIdsKeyValue": {
                    "host_psnt": "HPJT0Q20000000",
                    "hostname": "wdc1-007"
                  }
                },
                "simpleAttributes": [
                  {
                    "attributeName": "rack_name",
                    "datatype": "STRING",
                    "value": "wdc-1"
                  },
                  {
                    "attributeName": "position",
                    "datatype": "INTEGER",
                    "value": 7
                  }
                ]
              }
            ]
          },
          "dnsName": "wdc1-vxrm-2.vxrail.local",
          "ipAddress": "172.16.10.78",
          "networks": [
            {
              "gateway": "172.16.12.1",
              "ipPools": [
                {
                  "end": "172.16.12.62",
                  "start": "172.16.12.60"
                }
              ],
              "mask": "255.255.255.0",
              "subnet": "172.16.12.0/24",
              "type": "VMOTION",
              "vlanId": 2012
            },
            {
              "gateway": "172.16.13.1",
              "ipPools": [
                {
                  "end": "172.16.13.160",
                  "start": "172.16.13.61"
                }
              ],
              "mask": "255.255.255.0",
              "subnet": "172.16.13.0/24",
              "type": "VSAN",
              "vlanId": 2013
            },
            {
              "gateway": "172.16.10.1",
              "mask": "255.255.255.0",
              "subnet": "172.16.10.0/24",
              "type": "MANAGEMENT",
              "vlanId": 2010
            }
          ],
          "nicProfile": "TWO_HIGH_SPEED",
          "rootCredentials": {
            "credentialType": "SSH",
            "password": "*******",
            "username": "root"
          },
          "sshThumbprint": "SHA256:YvCkFKqPxddimcqAcC50BPBRqrsDfQJDWBCo9F1PHA0",
          "sslThumbprint": "B3:4A:9D:B1:B1:96:BC:C7:0D:88:90:A5:8B:8D:5C:74:BC:D2:30:0C:CF:E4:48:78:F0:9A:18:39:91:EF:C3:CE"
        }
      }
    ]
  },
  "domainName": "wld-1",
  "nsxTSpec": {
    "formFactor": "large",
    "ipAddressPoolSpec": {
      "description": "IP_POOL",
      "name": "ip-pool-1",
      "subnets": [
        {
          "cidr": "172.16.14.0/24",
          "gateway": "172.16.14.1",
          "ipAddressPoolRanges": [
            {
              "end": "172.16.14.100",
              "start": "172.16.14.10"
            }
          ]
        }
      ]
    },
    "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
    "nsxManagerAdminPassword": "*******",
    "nsxManagerSpecs": [
      {
        "name": "wdc1-wld-nsxt-1",
        "networkDetailsSpec": {
          "dnsName": "wdc1-wld-nsxt-1.vxrail.local",
          "gateway": "172.16.10.1",
          "ipAddress": "172.16.10.64",
          "subnetMask": "255.255.255.0"
        }
      },
      {
        "name": "wdc1-wld-nsxt-2",
        "networkDetailsSpec": {
          "dnsName": "wdc1-wld-nsxt-2.vxrail.local",
          "gateway": "172.16.10.1",
          "ipAddress": "172.16.10.65",
          "subnetMask": "255.255.255.0"
        }
      },
      {
        "name": "wdc1-wld-nsxt-3",
        "networkDetailsSpec": {
          "dnsName": "wdc1-wld-nsxt-3.vxrail.local",
          "gateway": "172.16.10.1",
          "ipAddress": "172.16.10.66",
          "subnetMask": "255.255.255.0"
        }
      }
    ],
    "vip": "172.16.10.67",
    "vipFqdn": "wdc1vip-2.vxrail.local"
  },
  "ssoDomainSpec": {
    "ssoDomainName": "vrack.local",
    "ssoDomainPassword": "*******"
  },
  "vcenterSpec": {
    "datacenterName": "VxRail-Datacenter",
    "name": "wdc1vc-2",
    "networkDetailsSpec": {
      "dnsName": "wdc1vc-2.vxrail.local",
      "gateway": "172.16.10.1",
      "ipAddress": "172.16.10.40",
      "subnetMask": "255.255.255.0"
    },
    "rootPassword": "*******",
    "storageSize": "lstorage",
    "vmSize": "medium"
  }
}

 Enter to continue ...
 Validating the input....
 Validation started for create domain operation. The validation id is: ad87bfb7-e19d-4476-98f6-5e7b8fb0be30
 Polling on validation api https://localhost/v1/domains/validations/ad87bfb7-e19d-4476-98f6-5e7b8fb0be30
 Validation IN_PROGRESS. It will take some time to complete. Please wait...
 Validation is in progress
 Validation is in progress
 Validation ended with status: SUCCEEDED

 Enter to create domain...
 Triggered create domain, monitor the status of the task(task-id:46c0cff3-9160-4c45-a67e-685361d1d0b8) from sddc-manager ui
```

2. Add Cluster
```python
vcf@wdc1sddc-1 [ ~/WorkflowOptimization ]$ python vxrail_workflow_optimization_automator.py
 Enter the Management domain SSO username: administrator@vsphere.local
 Enter the Management domain SSO password:


 Please choose one of the below option:
 1) Create Domain
 2) Add Cluster
 Enter your choice(number): 2


 Getting the domains...


 Please choose the domain to which cluster has to be added:
 1) MGMT
 Enter your choice(number): 1


 Enter datastore name: vxrail-datastore-wld


 ** ADVANCED_VXRAIL_SUPPLIED_VDS nic profile is supported only via VxRail JSON input
 Please choose one of the cluster configuration input options:
 1) VxRail JSON input
 2) Step by step input
 Enter your choice(number): 1


 Please enter VxRail JSON location: /home/vcf/addCluster_4x10.json
 Do you want to enable vSAN ESA ?('yes' or 'no'): no


 Getting ssl thumbprint for the passed VxRail Manager wdc1-vxrm-2.vxrail.local


 Fetched ssl thumbprint: B3:4A:9D:B1:B1:96:BC:C7:0D:88:90:A5:8B:8D:5C:74:BC:D2:30:0C:CF:E4:48:78:F0:9A:18:39:91:EF:C3:CE
 Fetched ssh thumbprint: SHA256:YvCkFKqPxddimcqAcC50BPBRqrsDfQJDWBCo9F1PHA0


 Do you want to trust the same?('yes' or 'no'): yes


 Getting ssh thumbprint for the hosts passed in Json
 Discovering hosts by VxRail Manager...


 Fetched ssh thumbprint for hosts passed in Json:
 --Serial Number--------------SSH Thumbprint--------------------------
 ---------------------------------------------------------------------
  HPHY0Q20000000 : SHA256:bNwti3geK+oVJOCyFPfKtezOAc5ohWF6dyrHZJ4sp4I
  HPJV0Q20000000 : SHA256:5DyYH7oxhNq3l1EoFoNz1L9rWWkPVqLD24PNageLVPg
  HPJT0Q20000000 : SHA256:TiFLJ9LQa/1wovdNv2fqHpqvmY666fSfwEkFkk0utN4


 Select the DVS option to proceed:
 1) System DVS for Overlay
 2) Separate DVS for Overlay
 Enter your choice(number): 1


 Please enter DVS details:

 Enter System DVS name: dvs-1

 Enter portgroup name for type MANAGEMENT: Management Network-1
 Enter portgroup name for type VSAN: vsan-1
 Enter portgroup name for type VMOTION: vmotion-1


 (Multi NSX VDS) Please choose the DVS for which NSX VLAN needs to be tagged (optional):
 -----id-----vds-----
 ----------------------
 1) dvs-1
 Enter your choices(comma separated if multiple / Empty):


 Getting shared NSX cluster information...


 Enter Geneve vLAN ID (0-4096):  2011


 Found NSX instance : wdc1-vip-nsx-mgmt.vxrail.local


 Please choose IP Allocation for TEP IPs option:
 1) DHCP (default)
 2) Static IP Pool
 Enter your choice(number): 1


 Getting license information...


 Please choose a VSAN license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (ACTIVE)
 Enter your choice(number): 1


 Please choose a NSX-T license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (NEVER_EXPIRES)
 Enter your choice(number): 1


 Do you want to apply vSphere license('yes' or 'no'): yes


 ** Please make sure license has enough CPU slots required for the cluster
 Please choose a vSphere license:
 1) XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (ACTIVE)
 Enter your choice(number): 1


{
  "computeSpec": {
    "clusterSpecs": [
      {
        "datastoreSpec": {
          "vsanDatastoreSpec": {
            "datastoreName": "vxrail-datastore-wld",
            "esaConfig": {
              "enabled": false
            },
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
          }
        },
        "hostSpecs": [
          {
            "hostName": "wdc1-005.vxrail.local",
            "ipAddress": "172.16.10.60",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPHY0Q20000000",
            "sshThumbprint": "SHA256:bNwti3geK+oVJOCyFPfKtezOAc5ohWF6dyrHZJ4sp4I",
            "username": "root"
          },
          {
            "hostName": "wdc1-006.vxrail.local",
            "ipAddress": "172.16.10.61",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPJV0Q20000000",
            "sshThumbprint": "SHA256:5DyYH7oxhNq3l1EoFoNz1L9rWWkPVqLD24PNageLVPg",
            "username": "root"
          },
          {
            "hostName": "wdc1-007.vxrail.local",
            "ipAddress": "172.16.10.62",
            "licenseKey": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
            "password": "*******",
            "serialNumber": "HPJT0Q20000000",
            "sshThumbprint": "SHA256:TiFLJ9LQa/1wovdNv2fqHpqvmY666fSfwEkFkk0utN4",
            "username": "root"
          }
        ],
        "name": "cluster-2",
        "networkSpec": {
          "nsxClusterSpec": {
            "nsxTClusterSpec": {
              "geneveVlanId": "2011"
            }
          },
          "vdsSpecs": [
            {
              "isUsedByNsxt": true,
              "name": "dvs-1",
              "portGroupSpecs": [
                {
                  "name": "Management Network-1",
                  "transportType": "MANAGEMENT"
                },
                {
                  "name": "vmotion-1",
                  "transportType": "VMOTION"
                },
                {
                  "name": "vsan-1",
                  "transportType": "VSAN"
                }
              ]
            }
          ]
        },
        "skipThumbprintValidation": false,
        "vxRailDetails": {
          "adminCredentials": {
            "credentialType": "SSH",
            "password": "*******",
            "username": "mystic"
          },
          "arrayContextWithKeyValuePair": {
            "hosts.geo_location": [
              {
                "arrayAssociationContext": {
                  "arrayAttributeIdsKeyValue": {
                    "host_psnt": "HPHY0Q20000000",
                    "hostname": "wdc1-005"
                  }
                },
                "simpleAttributes": [
                  {
                    "attributeName": "rack_name",
                    "datatype": "STRING",
                    "value": "wdc-1"
                  },
                  {
                    "attributeName": "position",
                    "datatype": "INTEGER",
                    "value": 5
                  }
                ]
              },
              {
                "arrayAssociationContext": {
                  "arrayAttributeIdsKeyValue": {
                    "host_psnt": "HPJV0Q20000000",
                    "hostname": "wdc1-006"
                  }
                },
                "simpleAttributes": [
                  {
                    "attributeName": "rack_name",
                    "datatype": "STRING",
                    "value": "wdc-1"
                  },
                  {
                    "attributeName": "position",
                    "datatype": "INTEGER",
                    "value": 6
                  }
                ]
              },
              {
                "arrayAssociationContext": {
                  "arrayAttributeIdsKeyValue": {
                    "host_psnt": "HPJT0Q20000000",
                    "hostname": "wdc1-007"
                  }
                },f
                "simpleAttributes": [
                  {
                    "attributeName": "rack_name",
                    "datatype": "STRING",
                    "value": "wdc-1"
                  },
                  {
                    "attributeName": "position",
                    "datatype": "INTEGER",
                    "value": 7
                  }
                ]
              }
            ]
          },
          "dnsName": "wdc1-vxrm-2.vxrail.local",
          "ipAddress": "172.16.10.78",
          "networks": [
            {
              "gateway": "172.16.12.1",
              "ipPools": [
                {
                  "end": "172.16.12.62",
                  "start": "172.16.12.60"
                }
              ],
              "mask": "255.255.255.0",
              "subnet": "172.16.12.0/24",
              "type": "VMOTION",
              "vlanId": 2012
            },
            {
              "gateway": "172.16.13.1",
              "ipPools": [
                {
                  "end": "172.16.13.160",
                  "start": "172.16.13.61"
                }
              ],
              "mask": "255.255.255.0",
              "subnet": "172.16.13.0/24",
              "type": "VSAN",
              "vlanId": 2013
            },
            {
              "gateway": "172.16.10.1",
              "mask": "255.255.255.0",
              "subnet": "172.16.10.0/24",
              "type": "MANAGEMENT",
              "vlanId": 2010
            }
          ],
          "nicProfile": "FOUR_HIGH_SPEED",
          "rootCredentials": {
            "credentialType": "SSH",
            "password": "*******",
            "username": "root"
          },
          "sshThumbprint": "SHA256:YvCkFKqPxddimcqAcC50BPBRqrsDfQJDWBCo9F1PHA0",
          "sslThumbprint": "B3:4A:9D:B1:B1:96:BC:C7:0D:88:90:A5:8B:8D:5C:74:BC:D2:30:0C:CF:E4:48:78:F0:9A:18:39:91:EF:C3:CE"
        }
      }
    ]
  },
  "domainId": "48f320ac-1adf-4106-8608-f3ea00362c8a"
}

 Enter to continue ...
 Validating the input....
 Validation started for add cluster operation. The validation id is: 27cf12b1-d734-4c2f-9f56-d39e8be28ad3
 Polling on validation api https://localhost/v1/clusters/validations/27cf12b1-d734-4c2f-9f56-d39e8be28ad3
 Validation IN_PROGRESS. It will take some time to complete. Please wait...
 Validation is in progress
 Validation is in progress
 Validation ended with status: SUCCEEDED

 Enter to add cluster...
 Triggered add cluster, monitor the status of the task(task-id:870a523a-fc76-49f3-a8df-27fd0abfaed9) from sddc-manager ui
```