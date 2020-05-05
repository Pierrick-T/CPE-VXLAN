import jinja2
import sys
from data_base import fabric_def, network_map


template_env = jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'))


# We need to create a list with all the available devices to configure
available_spines, available_leaves = [], []
for x in range(len(fabric_def['devices']['spines'])):
    available_spines.append(fabric_def['devices']['spines'][x + 1]['name'])
for x in range(len(fabric_def['devices']['leaves'])):
    available_leaves.append(fabric_def['devices']['leaves'][x + 1]['name'])
    

#Check if there is an argument as a name
# Lets define which device we are configuring
if sys.argv[1] in ['-n', '--name']:
    try :
        name_of_device = sys.argv[2]
    except : 
        print("Please enter the name of the device you wish to configure, for more informations use -h")
        sys.exit()

if sys.argv[1] in ['-l', '--list']:
    print("List of devices available : ","\navailable leaves : ", available_leaves,"\navailable spines : ", available_spines)
    sys.exit()

if sys.argv[1] in ['-h', '--help']:
    print("Options : \n-n or --name [name of device to configure] --> creates a .conf file for the name of the device")
    print("-l or --list                               --> displays the list of all the available devices to configure")
    print("-h or --help --> displays the documentation")
    sys.exit()


# lets find out if the name is in one of the list
if name_of_device in available_spines:
    hw_type = 'spines'
    hw_number = available_spines.index(name_of_device)
elif name_of_device in available_leaves:
    hw_type = 'leaves'
    hw_number = available_leaves.index(name_of_device)
else:
    print("device name unknown, press -l for the list of available devices")
    sys.exit()

config = {}

if hw_type == 'spines':
    template = template_env.get_template('spine.jinja2')
    

if hw_type == 'leaves':
    template = template_env.get_template('leaf.jinja2')
    config["unused"] = [i for i in range(1, 49)]
    
config["hostname"] = fabric_def['devices'][hw_type][hw_number+1]['name']
config["id"] = network_map['leaves'][hw_number+1]['loopback0']['ip']
config["setup"] = network_map[hw_type][hw_number+1]


output = template.render(config)
file_name = config['hostname'] + '.conf'
with open("config/"+file_name, 'w') as f:
    f.write(output)

print("The file ", file_name, "has been successfuly created")