""" Python Interface for nmap 
"""
import shlex
import subprocess

import re

def port_scan(target, scan_type, args = {}):
    """ nmap
    Args:
        target (str): ip/hostname/range/subnet
        scan_type (str): {FAST | RANGE}
        
    Example:
        nmap -F 192.168.1.1
    """
    command = None

    if scan_type == "FAST":
        command = shlex.split("nmap -F {}".format(target))

    p1 = subprocess.Popen(command, stdout=subprocess.PIPE)
    results =  p1.stdout.readlines()

    entries = []
    for line in results:
        if line.startswith("Note: Host seems down."):
            return {"error": line}
       
        m = re.match(r"(\d+\/\w+)\s+(\w+)\s+(\w+)", line)
        if m:
            info  = m.groups()
            entry = {
                "port" : info[0],
                "state": info[1],
                "service": info[2],
            }
            entries.append(entry)
    p1.terminate()
    return entries


if __name__ == "__main__":
    import pprint

    print("nmap -F {}")
    pprint.pprint( port_scan("10.0.0.1", "FAST"))

