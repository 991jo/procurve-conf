# procurve-conf
A little python3 script to configure HP ProCurve switches based on pyserial and pexpect.

This script is intended to be used with a resetted switch via serial.
It was tested only with a ProCurve 2824 and on Linux and on Linux.

# How to use:
1. setup your config.py
2. Power on the switch
3. plug in serial cable
4. reset switch (often something with pressing the "reset" and "clear" buttons,
take a look into your manual)
5. start script
'''
python3 procurve.conf <switch_name>
'''
6. be happy and repeat ;)

todo:
- [x] clean up the code 
- [x] add some documentation
- [x] add password setting method
- [x] write example config
- [x] requirements.txt
- [x] Jinja2 Template Support
- [x] easier configuration for multiple switches
- [x] config file instead of changing values in the script directly
