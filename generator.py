import jinja2
import sys
from data_base import fabric_def, network_map


template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'))

#Check if there is an argument as a name
# Lets define which device we are configuring
try :
    name_of_device = sys.argv[1]
except : 
    print("Please enter the name of the device you wish to configure")
    sys.exit()

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
    print("list of devices available : ", available_leaves, available_spines)
    sys.exit()

config = {}

if hw_type == 'spines':
    template = template_env.get_template('spine.jinja2')
    config["hostname"] = fabric_def['devices'][hw_type][hw_number+1]['name']
    config["setup"] = network_map['spines'][hw_number+1]

if hw_type == 'leaves':
    template = template_env.get_template('leaf.jinja2')
    config["hostname"] = fabric_def['devices'][hw_type][hw_number+1]['name']

    config["setup"] = network_map['leaves'][hw_number+1]
    config["unused"] = [i for i in range(1, 49)]


output = template.render(config)
file_name = config['hostname'] + '.conf'
with open("config/"+file_name, 'w') as f:
    f.write(output)

print("The file ", file_name, "has been successfuly created")