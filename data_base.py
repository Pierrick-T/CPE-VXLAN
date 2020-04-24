# -*- coding: utf-8 -*-
from class_ip import ipaddress
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

network_map = {
    'spines': {
        1: {},
        2: {},
        3: {},
        4: {},
    },
    'leaves': {
        1: {},
        2: {},
        3: {},
        4: {},
    }
}

snet = ipaddress(fabric_def['underlay']['snet'])
nb_spines = len(fabric_def['devices']['spines'])

device_ip = [[] for i in range(nb_spines)]

for x in range(nb_spines):
    if x < 2:
        interface_leaf = 49
    else:
        interface_leaf = 50
    if x % 2 == 0:
        connected_leaf = [1, 3]
    else:
        connected_leaf = [2, 4]

    device_ip[x] = copy(snet)
    device_ip[x].mask = 31
    device_ip[x].address[3] += 64 * x
    network_map['spines'][x + 1].update({
        'Ethernet1/'+str(x+1): {
            'ip': device_ip[x].get_ipstr(),
            'mask': device_ip[x].get_mask(),
            'target_name': fabric_def['devices']['leaves'][connected_leaf[0]]['name'],
            'target_port': 'Ethernet1/' + str(interface_leaf)
        }})  # first interface spine
    device_ip[x].address[3] += 1
    network_map['leaves'][connected_leaf[0]].update({
        'Ethernet1/' + str(interface_leaf): {
            'ip': device_ip[x].get_ipstr(),
            'mask': device_ip[x].get_mask(),
            'target_name': fabric_def['devices']['spines'][x + 1]['name'],
            'target_port': 'Ethernet1/1'
        }})  # first interface leaf
    device_ip[x].address[3] -= 1

    device_ip[x].address[3] += 2
    network_map['spines'][x + 1].update({
        'Ethernet1/'+str(x+2): {
            'ip': device_ip[x].get_ipstr(),
            'mask': device_ip[x].get_mask(),
            'target_name': fabric_def['devices']['leaves'][connected_leaf[1]]['name'],
            'target_port': 'Ethernet1/' + str(interface_leaf)
        }})  # second interface spine
    device_ip[x].address[3] += 1

    network_map['leaves'][connected_leaf[1]].update({
        'Ethernet1/' + str(interface_leaf): {
            'ip': device_ip[x].get_ipstr(),
            'mask': device_ip[x].get_mask(),
            'target_name': fabric_def['devices']['spines'][x + 1]['name'],
            'target_port': 'Ethernet1/2'
        }})  # second interface leaf

# from PRD import vrf_def as PRD
# vrf de PRODUCTION
#  fabric_def['overlay']['vrf']['PRD'] = PRD
#
#  from RQT import vrf_def as RQT   # vrf de RECETTE
#  fabric_def['overlay']['vrf']['RQT'] = RQT


if __name__ == '__main__':
    pass
