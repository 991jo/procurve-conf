# This is the config file for procurve conf.
# this is just a python script that gets imported at the beginning of the script.
# You can run python code here, e.g. for-loops to generate the config.
# for further infos read the annotations in this file.


# Default passwords for operator and manager logins
default_operator_pw = "operatorpw"
default_manager_pw = "managerpw"

# The config dict contains switch-names as keys and a dict as values.
# These inner dicts are used to populate the template
config = {
        'access-1':{
            'address': '192.18.2.11',
            'hostname': 'access-1',
            'manager_pw': 'otherpw', # how to specify an other password on a switch
            'operator_pw': 'yetanotherpw'
            },
        'access-2':{
            'address': '192.18.2.12',
            'hostname': 'access-2'
            },
        'access-3':{
            'address': '192.18.2.13',
            'hostname': 'access-3'
            },
        }

#to demonstrate some python code here
for i in range(4,9):
    config['access-%d' % i] = {
            'address' : '192.18.2.%d' % (10+i),
            'hostname' : 'access-%d' %i }

print(config)

# Template is a jinja2 template that is used to configure the switches.
# This is mandatory.
template = "template.conf"
# this is the tty serial device that is used to configure the switch.
# This is mandatory.
device = "/dev/ttyUSB0"
