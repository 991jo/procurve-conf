#!/usr/bin/env python3

""" procurve conf is a script to configure HP Procurve Switches starting at
    factory defaults via a serial interface.

    Further information at https://github.com/991jo/procurve-conf
"""

from time import sleep
from sys import stdout, exit, argv  

import serial
from pexpect import fdpexpect

import config

""" Assumptions made in the code:
    - every function assumes to be in operator-mode and ready to execute a command
    - every function leaves the cli in the operator-mode but not in configure mode
"""

def debug_msg(message):
    if debug_mode:
        print(message)

def gen_ssh_keys(child):
    """generates a new ssh key pair"""
    child.sendline("end")
    child.expect(".*?(?!\(.*?\))#")
    child.sendline("conf term")
    child.expect(".*\(config\)#")
    child.sendline("crypto key generate ssh rsa")
    child.expect("Installing new RSA key", timeout=60)
    child.expect(".*\(config\)#")


def set_passwords(child, manager_pw, operator_pw):
    """ sets the passwords for manager and operator user accounts """
    child.sendline("configure terminal")
    child.expect(".+\(config\)#")
    child.sendline("password all")
    child.expect(".+password.+Operator")
    child.sendline(operator_pw)
    child.expect(".+password.+Operator")
    child.sendline(operator_pw)
    child.expect(".+password.+Manager")
    child.sendline(manager_pw)
    child.expect(".+password.+Manager")
    child.sendline(manager_pw)


def wait_for_boot(child):
    """ waits for the switch to boot and handles the Speed Sense and License
    messages """
    debug_msg("debug: waiting for boot")
    child.send("\r")
    child.send("\r")
    pattern_list = child.compile_pattern_list(
            [   "Speed Sense.+?<Enter> twice.+continue\.", 
                "Press any key to continue",
                ".+#"   ])
    ptrn_nr = child.expect_list(pattern_list, timeout=400)
    debug_msg("debug: I FOUND SOMETHING")
    if ptrn_nr == 0:
        debug_msg("debug: case 0")
        # it seems like multiple \r are needed for this to work reliably
        child.send("\r")
        child.send("\r")
        sleep(1)
        child.send("\r")
        child.send("\r")
        sleep(1)
        child.send("\r")
        child.send("\r")
        wait_for_boot(child) # recursive call for the next "screen"
    elif ptrn_nr == 1:
        debug_msg("debug: case 1")
        child.sendline("\r")
        child.expect(".#")
    else:
        debug_msg("debug: case 2")
        return


def apply_config(child, config):
    """ reads the config file stored in the config and applies it line-wise.
    You have to make shure, that your commands do not exit configure-mode and
    do not need further input.
    This means that "end" is not allowed, because it leaves configure mode and
    "password" is not allowed, because it needs further user input.
    """
    child.sendline("end")
    child.expect(".*#")
    child.sendline("configure terminal")
    with open(config) as f:
        for line in f:
            child.sendline(line)
            child.expect(".*#")
    child.sendline("end")
    child.expect(".*#")

def write_memory(child):
    """ writes the running-config to startup-config aka saves the currently running
    config."""
    child.sendline("end")
    child.expect(".*#")
    child.sendline("write memory")

def check_script_config(config, switch_name):
    """ this function makes some checks for the config file.
    It either prints warnings when something non-critical is wrong in the config
    or it raises an exception for critical cases, e.g. when no template or tty device
    is given. """

    # mandatory settings
    assert "device" in dir(config)
    assert "template" in dir(config)

    # optional settings
    if not "default_manager_pw" in dir(config):
        print("WARNING: no default_manager_pw in config")
    if not "default_operator_pw" in dir(config):
        print("WARNING: no default_operator_pw in config")

    assert "config" in dir(config)
    if len(config.config) == 0:
        print("WARNING: config section for switches is empty")

    if switch_name not in config.config:
        print("WARNING: switch-name %s not in config. Using template without special insertions" % switch_name)

def create_config(config, switch_name):
    template = ""
    with open(config.template) as f:
        template = f.read()

    
    from jinja2 import Template
    template = Template(template)
    template_render = template.render(config.config[switch_name])

    return template_render

if __name__ == '__main__':

    if len(argv) < 2:
        print("""usage: %s <switch-name>""" % argv[0])
        exit(1)

    switch_name = argv[1]

    check_script_config(config, switch_name)

    templated_config = create_config(config, switch_name)

    # set passwords
    manager_pw = config.default_manager_pw
    operator_pw = config.default_operator_pw

    if switch_name in config.config.keys():
        if "manager_pw" in config.config[switch_name]:
            manager_pw = config.config[switch_name]["manager_pw"]
        if "operator_pw" in config.config[switch_name]:
            operator_pw = config.config[switch_name]["operator_pw"]

    ser = serial.Serial(config.device)
    child = fdpexpect.fdspawn(ser, encoding='utf-8')
    child.logfile = stdout
    wait_for_boot(child)

    child.send("\r")
    child.expect(".*#", timeout=3)
    gen_ssh_keys(child)
    apply_config(child, templated_config)
    set_passwords(child, manager_pw, operator_pw)
    write_memory(child)
