#!/usr/bin/env python3

""" procurve conf is a script to configure HP Procurve Switches starting at
    factory defaults via a serial interface.

    Further information at https://github.com/991jo/procurve-conf
"""

from time import sleep
from sys import stdout

import serial
from pexpect import fdpexpect

config = "config.txt"
device = "/dev/ttyUSB0"
manager_pw = "managerpw"
operator_pw = "operatorpw"
debug_mode = True

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

ser = serial.Serial(device)
child = fdpexpect.fdspawn(ser, encoding='utf-8')
child.logfile = stdout
wait_for_boot(child)

child.send("\r")
child.expect(".*#", timeout=3)
gen_ssh_keys(child)
apply_config(child, config)
set_passwords(child, manager_pw, operator_pw)
write_memory(child)
