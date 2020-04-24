import jinja2
import sys
from data_base import fabric_def, network_map
import ipaddress as ip

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'))

# Lets define which device we are configuring
name_of_device = sys.argv[1]

# Define the net on which we are working
snet = ip.IPv4Network(fabric_def['underlay']['snet'])

# We need to create a list with all the available devices to configure
available_spines, available_leaves = [], []
for x in range(len(fabric_def['devices']['spines'])):
    available_spines.append(fabric_def['devices']['spines'][x + 1]['name'])
for x in range(len(fabric_def['devices']['leaves'])):
    available_leaves.append(fabric_def['devices']['leaves'][x + 1]['name'])

# lets find out if the name is in one of the list
if name_of_device in available_spines:
    hw_type = 'spines'
    hw_number = available_spines.index(name_of_device)
elif name_of_device in available_leaves:
    hw_type = 'leaves'
    hw_number = available_leaves.index(name_of_device)
else:
    print("device name unknown")

config = {}

if hw_type == 'spines':
    template = template_env.get_template('spine.conf')
    config["hostname"] = fabric_def['devices'][hw_type][hw_number+1]['name']
    config["setup"] = network_map['spines'][hw_number+1]

if hw_type == 'leaves':
    template = template_env.get_template('leaf.conf')
    config["hostname"] = fabric_def['devices'][hw_type][hw_number+1]['name']

    config["setup"] = network_map['leaves'][hw_number+1]
    config["unused"] = [i for i in range(1, 49)]


output = template.render(config)
file_name = config['hostname'] + '.conf'

with open(file_name, 'w') as f:
    f.write(output)
