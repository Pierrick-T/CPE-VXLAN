# -*- coding: utf-8 -*-
from class_ip import ipaddress, split_in_subs
from copy import copy
import pprint


fabric_def = {
    'underlay': {'snet': '10.1.200.0/23', 'as': '65000'},
    # numéro d'AS à utiliser pour les leafs et les spines (Route reflector)
    'devices': {
        'spines': {
            1: {'name': 'CPE-ADMspSM1-01', 'addr': '192.168.10.1', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'spine.conf'},
            2: {'name': 'CPE-ADMspSM1-02', 'addr': '192.168.10.2', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'spine.conf'},
            3: {'name': 'CPE-ADMspSM2-03', 'addr': '192.168.10.3', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'spine.conf'},
            4: {'name': 'CPE-ADMspSM2-04', 'addr': '192.168.10.4', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'spine.conf'},
        },
        'leaves': {
            1: {'name': 'CPE-ADMlfMIX-SM1-A1', 'addr': '192.168.10.5', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'leaf.conf'},
            2: {'name': 'CPE-ADMlfMIX-SM1-A2', 'addr': '192.168.10.6', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'leaf.conf'},
            3: {'name': 'CPE-ADMlfMIX-SM2-A1', 'addr': '192.168.10.7', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'leaf.conf'},
            4: {'name': 'CPE-ADMlfMIX-SM2-A2', 'addr': '192.168.10.8', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'leaf.conf'},
            5: {'name': 'CPE-ADMlfMIX-SM3-A1', 'addr': '192.168.10.9', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'leaf.conf'},
            6: {'name': 'CPE-ADMlfMIX-SM3-A2', 'addr': '192.168.10.10', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'leaf.conf'},
            7: {'name': 'CPE-ADMlfMIX-SM4-A1', 'addr': '192.168.10.11', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'leaf.conf'},
            8: {'name': 'CPE-ADMlfMIX-SM4-A2', 'addr': '192.168.10.12', 'mask': '24', 'gw': '192.168.10.254',
                'template': 'leaf.conf'},
        }
    },
    'overlay': {
        'vrf': {},
    },
}

snet = ipaddress(fabric_def['underlay']['snet'])
nb_spines = len(fabric_def['devices']['spines'])
nb_leaves = len(fabric_def['devices']['leaves'])


# Creating the skeleton for the network map
network_map = {'spines': {}, 'leaves': {}}
for i in range(nb_spines):
    network_map['spines'].update({i+1: {}})
for i in range(nb_leaves):
    network_map['leaves'].update({i+1: {}})

# Implementing the network map
snets_24 = snet.netsplit(24)
device_ip = snets_24[0].netsplit(26)

for x in range(nb_spines):
# Creating the connections between the leaves and the spines
    for y in range(int(nb_leaves/2)):
        network_map['spines'][x + 1].update({  # interface of the spine
            'Ethernet1/' + str(y + 1): {
                'ip': device_ip[x].get_ipstr(),
                'mask': 31,
                'target_name': fabric_def['devices']['leaves'][2 * y + (x%2) + 1]['name'],
                'target_port': 'Ethernet1/' + str(x + 49)
            }})

        device_ip[x].address[3] += 1
        network_map['leaves'][2 * y + (x%2) + 1].update({  # interface of the leaf
            'Ethernet1/' + str((x>1) + 49): {
                'ip': device_ip[x].get_ipstr(),
                'mask': 31,
                'target_name': fabric_def['devices']['spines'][x + 1]['name'],
                'target_port': 'Ethernet1/' + str(y + 1),
                'x':x
            }})  # first interface leaf
        device_ip[x].address[3] += 1

    counter = 0
    while counter + nb_leaves/2 < 26:  # Remaining interfaces that are not yet connected
        network_map['spines'][x + 1].update({
            'Ethernet1/' + str(counter + 1 + int(nb_leaves/2)): {
                'ip': device_ip[x].get_ipstr(),
                'mask': device_ip[x].get_mask(),
                'target_name': 'no leaf',
                'target_port': 'no port'
            }})  # unused interface
        device_ip[x].address[3] += 2
        counter += 1

# Creating the loopback on the leaves 

# Preparing the subnets to use
snets_24 = snet.netsplit(24)
snets_29 = snets_24[1].netsplit(29)

for x in range(int(nb_leaves/2)):
    snet_31 = snets_29[x].netsplit(31)
    snet_32 = snets_29[x].netsplit(32)

    for y in range(2):  # setting up VLAN2
        network_map['leaves'][2*x+1+y].update({
            'Vlan2': {
                'ip': snet_31[0].get_ipstr(),
                'mask': '32',
                'target_name' : "leaf " + str(2*x+1+y) + ' to ' + 'leaf ' + str(2*x+1+(y+1)%2),
                'target_port': 'vlan2'
            }
        })
        snet_31[1].address[3] += 1
        
        network_map['leaves'][2*x+1+y].update({
            'loopback0': {
                'ip': snet_32[5+y].get_ipstr(),
                'mask': '32',
                'description' : "routing interface",
            }
        })

        network_map['leaves'][2*x+1+y].update({
            'loopback1': {
                'ip': snet_32[3+y].get_ipstr(),
                'mask': '32',
                'ip2': snet_32[2].get_ipstr(),
                'mask2': '32',
                'description' : "VXLAN interface"
            }
        })


# from PRD import vrf_def as PRD
# vrf de PRODUCTION
#  fabric_def['overlay']['vrf']['PRD'] = PRD
#
#  from RQT import vrf_def as RQT   # vrf de RECETTE
#  fabric_def['overlay']['vrf']['RQT'] = RQT


if __name__ == '__main__': # debug purpose
    pprint.pprint(network_map['leaves'][1], width=2)

