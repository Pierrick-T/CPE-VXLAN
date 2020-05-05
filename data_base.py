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
snets_26 = snets_24[0].netsplit(26)

for x in range(nb_spines):
# Creating the connections between the leaves and the spines
    snet_26 = snets_26[x]
    snets_31 = snet_26.netsplit(31)
    
    for y in range(int(nb_leaves/2)):
        network_map['spines'][x + 1].update({  # interface of the spine
            'Ethernet1/' + str(y + 1): {
                'ip': snets_31[y].get_ipstr(),
                'mask': snets_31[y].mask,
                'target_name': fabric_def['devices']['leaves'][2 * y + (x%2) + 1]['name'],
                'target_port': 'Ethernet1/' + str(x + 49)
            }})

        snets_31[y].address[3] += 1
        network_map['leaves'][2 * y + (x%2) + 1].update({  # interface of the leaf
            'Ethernet1/' + str((x>1) + 49): {
                'ip': snets_31[y].get_ipstr(),
                'mask': snets_31[y].mask,
                'target_name': fabric_def['devices']['spines'][x + 1]['name'],
                'target_port': 'Ethernet1/' + str(y + 1),
                'x':x
            }})  
        snets_31[y].address[3] -= 1 # reset it to the first address of the subnet

    counter = int(nb_leaves/2)
    while counter  < 26:  # Remaining interfaces that are not yet connected
        network_map['spines'][x + 1].update({
            'Ethernet1/' + str(counter + 1 + int(nb_leaves/2)): {
                'ip': snets_31[counter].get_ipstr(),
                'mask': snets_31[counter].get_mask(),
                'target_name': 'no leaf',
                'target_port': 'no port'
            }})  # unused interface
        counter += 1
    
    
    snets_31.pop() # the last /31 is used for the port channel 
    last_snets_32 = snets_31[-1].netsplit(32)
    
    network_map['spines'][x + 1].update({
            'loopback0': {
                'ip': last_snets_32[-1].get_ipstr(),
                'mask': last_snets_32[-1].mask,
                'description': 'Router-ID',
            }})  # define the router id 
    
    network_map['spines'][x + 1].update({
        'loopback1': {
            'ip': snets_24[0].netsplit(32)[-1].get_ipstr(),
            'mask': snets_24[0].netsplit(32)[-1].mask,
            'description': 'Router-ID',
        }})  # common loopback on all the routers
for x in range(int(nb_spines/2)): #connection between spines
    snets_31 = snets_26[2*x].netsplit(31)
    for y in range(2):
        #print("pour le spine ",(2*x+1+y), "l'ip est ", snets_31[-1].get_ipstr() )
        network_map['spines'][2*x + 1 + y].update({
            'port_channel1': {
                'ip': snets_31[-1].get_ipstr(),
                'mask': snets_31[-1].mask,
                'target_name': fabric_def['devices']['spines'][x+1+(x+1)%2]['name'],
                'target_port': 'port_channel1'
            }})  # connexion between spines
        snets_31[-1].address[3] += 1


# Creating the loopback on the leaves 
# Preparing the subnets to use
snets_29 = snets_24[1].netsplit(29)

for x in range(int(nb_leaves/2)): # configuring the loopbacks for the leaves 
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
    pprint.pprint(network_map['spines'][2], width=2)

