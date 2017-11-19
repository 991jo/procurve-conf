#!/usr/bin/env python3

import time

from sys import stdout
from pexpect import fdpexpect
import serial

config = "config.txt"
device = "/dev/ttyUSB0"

def gen_ssh_keys(child):
    child.expect(".*#")
    child.sendline("end")
    child.expect(".*?(?!\(.*?\))#")
    child.sendline("conf term")
    child.expect(".*\(config\)#")
    child.sendline("crypto key generate ssh rsa")
    child.expect("Installing new RSA key", timeout=60)
    child.expect(".*\(config\)#")

def set_passwords(child, manager_pw, operator_pw):
    pass

def wait_for_boot(child):
    print("debug: waiting for boot")
    child.send("\r")
    child.send("\r")
    pattern_list = child.compile_pattern_list(
            [   "Speed Sense.+?<Enter> twice.+continue\.", 
                "Press any key to continue",
                ".+#"   ])
    ptrn_nr = child.expect_list(pattern_list, timeout=400)
    print("debug: I FOUND SOMETHING")
    if ptrn_nr == 0:
        print("debug: case 0")
        child.send("\r")
        child.send("\r")
        time.sleep(1)
        child.send("\r")
        child.send("\r")
        time.sleep(1)
        child.send("\r")
        child.send("\r")
        wait_for_boot(child)
    elif ptrn_nr == 1:
        print("debug: case 1")
        child.sendline("\r")
        child.expect(".#")
    else:
        print("debug: case 2")
        return

def apply_config(child, config):
    child.sendline("end")
    child.expect(".*#")
    child.sendline("configure terminal")
    with open(config) as f:
        for line in f:
            child.sendline(line)
            child.expect(".*#")
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
