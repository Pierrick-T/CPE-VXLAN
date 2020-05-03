# -*- coding: utf-8 -*-
from class_ip import ipaddress, split_in_subs
from copy import copy

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
device_subs = []
split_in_subs(snet.get_ipstr(), snet.mask, 26, device_subs)
device_ip = [ipaddress(x, 31) for x in device_subs]

for x in range(nb_spines):
    if x % 2 == 0: # if even
        even = 0
    else :
        even = 1

    for y in range(int(nb_leaves/2)):
        network_map['spines'][x + 1].update({  # interface of the spine
            'Ethernet1/' + str(y + 1): {
                'ip': device_ip[x].get_ipstr(),
                'mask': device_ip[x].get_mask(),
                'target_name': fabric_def['devices']['leaves'][2 * y + even + 1]['name'],
                'target_port': 'Ethernet1/' + str(x + 49)
            }})

        device_ip[x].address[3] += 1
        network_map['leaves'][2 * y + even + 1].update({  # interface of the leaf
            'Ethernet1/' + str(x + 49): {
                'ip': device_ip[x].get_ipstr(),
                'mask': device_ip[x].get_mask(),
                'target_name': fabric_def['devices']['spines'][x + 1]['name'],
                'target_port': 'Ethernet1/' + str(y + 1)
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


# from PRD import vrf_def as PRD
# vrf de PRODUCTION
#  fabric_def['overlay']['vrf']['PRD'] = PRD
#
#  from RQT import vrf_def as RQT   # vrf de RECETTE
#  fabric_def['overlay']['vrf']['RQT'] = RQT


if __name__ == '__main__': # debug purpose
    pass
