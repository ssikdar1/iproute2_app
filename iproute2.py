""" Python Interface for iproute2
"""
import shlex
import subprocess

import re

def neighbors():
    """ ip neigh/ arp
    Example:
        10.0.0.1 dev wlp3s0 lladdr 5c:b0:66:08:dd:ca STALE
        fe80::5eb0:66ff:fe08:ddca dev wlp3s0 lladdr 5c:b0:66:08:dd:ca router REACHABLE
    """
    command = shlex.split("ip neigh show")
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE)
    results =  p1.stdout.readlines()
    entries = []
    for result in results:
        line = result.strip().split()
        entry = {
            "to" : line[0],
            "dev": line[2],
            "lladr": line[4],
            "state": line[5]
        }
        entries.append(entry)
    p1.terminate()
    return entries

def route():
    """ ip route/route
    Example:
        default via 10.0.0.1 dev wlp3s0  proto static  metric 600 
        10.0.0.0/24 dev wlp3s0  proto kernel  scope link  src 10.0.0.102  metric 600 
        169.254.0.0/16 dev wlp3s0  scope link  metric 1000 
    """
    command = shlex.split("ip route")
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE)
    results =  p1.stdout.readlines()
    entries = []
    for result in results:
        line = result.strip().split()
        entry = {
            "to" : line[0],
        }
        for i in xrange(1, len(line), 2):
            key = line[i]
            value = line[i+1]
            if key in ('metric',):
                value = int(value)
            entry[key] = value
            
        entries.append(entry)
    p1.terminate()
    return entries

def link():
    """ ip link
    Example:
	1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1
	    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
	2: enp0s25: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast state DOWN mode DEFAULT group default qlen 1000
	    link/ether 3c:97:0e:7f:f9:a7 brd ff:ff:ff:ff:ff:ff
	3: wlp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DORMANT group default qlen 1000
	    link/ether 3c:a9:f4:00:d9:dc brd ff:ff:ff:ff:ff:ff
    """
    command = shlex.split("ip link show")
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE)
    results =  p1.stdout.readlines()
    entries = []
    entry = None
    for result in results:
        line = result.strip().split()
        m = re.match(r"(\d):", line[0])
        if m:
            entry = {
                "to" : line[0],
            }
            #3: wlp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DORMANT group default qlen 1000
            start_point = 3
            entry["device"] = line[1].replace(":","")
            entry["info"] = line[2]
            for i in xrange(3, len(line), 2):
                key = line[i]
                value = line[i+1]
                entry[key] = value
        else:
            # link/ether 3c:97:0e:7f:f9:a7 brd ff:ff:ff:ff:ff:ff
            if len(line) == 1:
                entry[line[0]] = None
            else:
                for i in xrange(0, len(line), 2):
                    key = line[i]
                    value = line[i+1]
                    entry[key] = value
            
            entries.append(entry)
            entry = None
    p1.terminate()
    return entries
    
def maddr():
    """ ip maddr/ ipmaddr
    Example:

        2:  enp0s25
            link  01:00:5e:00:00:01
            inet  224.0.0.1
            inet6 ff02::1
            inet6 ff01::1
        
    """ 
    command = shlex.split("ip maddr")
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE)
    results =  p1.stdout.readlines()
    entries = []
    entry = {}
    for result in results:
        line = result.strip().split()
        m = re.match(r"(\d):", line[0])
        if m:
            # 1:    lo 
            if int(m.group(1)) == 1:
                entry = {"multicast_addresses": []}
            else:
                # new interface
                entries.append(entry)
                entry = {"multicast_addresses": []}

            entry['interface_index'] = m.group(1)
            entry['interface_name'] = line[1]
        else:
            # link  01:00:5e:00:00:01 users 2 
            multicast_address = {}
            for i in xrange(0, len(line), 2):
                key = line[i]
                value = line[i+1]
                if key in ('users',):
                    value = int(value)
                multicast_address[key] = value
                entry['multicast_addresses'].append(multicast_address)        
    entries.append(entry)
    return entries

def add_tuntap(interface_name, mode):
    """
    ip tuntap add dev tun0 mode tun
    """
    # TODO: what to do about sudo?
    command = shlex.split("sudo ip tuntap add dev {} mode {}".format(interface_name, mode))
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p1.communicate()
    return_code = p1.returncode
    if return_code != 0:
        print "error"
        print stdout
        print stderr
        return False
    return True

def delete_tuntap(interface_name, mode):
    """
    ip tuntap del dev {interface_name}
    """
    command = shlex.split(" ip tuntap del dev {} mode {} ".format(interface_name, mode))
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p1.communicate()
    return_code = p1.returncode
    if return_code != 0:
        print "error"
        print stdout
        print stderr
        return False
    return True
 
def tc(tc_object, tc_command, tc_dev = None, tc_options = {}):
    """ 
    Args:
        tc_object (str): {qdisc | class | filter | action | monitor | exec }
        tc_command (str): {add | delete | change | replace | get | show | link } 
        tc_dev (str) : device
        tc_options (dict): option args to pass to tcp
    Returns:
        success (bool), info (list or dict to be turned into json)
    """ 
    args = []
    # parse options
    if 'statistics' in tc_options and tc_options['statistics']:
        args.append(" -s ") 
    if 'details' in tc_options and tc_options['details']:
        args.append(" -d ") 
    if 'raw' in tc_options and tc_options['raw']:
        args.append(" -r ") 
    if 'pretty' in tc_options and tc_options['pretty']:
        args.append(" -p ") 
    if 'batch' in tc_options and tc_options['batch'] is not None:
        args.append(" -b {} ".format(options['batch'])) 
    if 'netns' in tc_options and tc_options['netns'] is not None:
        args.append(" -n {} ".format(options['netns'])) 

    dev = ""
    if tc_dev is not None:
        dev = " dev {} ".format(tc_dev) 
 
    command = shlex.split("tc {} {} {} {}".format(" ".join(args), tc_object, tc_command, dev))
    #print command
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE)

    # look at exit status
    stdout, return_code = p1.communicate()[0], p1.returncode
    
    #print stdout
    #print stdout.split("\n")
    #print return_code

    # Parse output
    retval = parse_tc_output(stdout)

    if return_code == 0:
        success = True
    else:
        success = False 

    return success, retval

def parse_tc_output(stdout):
    retval = []
    ret = None 
    for line in stdout.split("\n"):
        m = re.match(r"(qdisc)\s(.+\d\:)(.+)", line)
        if m:
            if ret is None:
                # first entry
                ret = {}
            else:
                # not first entry, append & reset
                retval.append(ret)
                ret = {}
            #qdisc pfifo_fast 0: parent :1 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
            ret['qdisc'] = []
            vals = m.groups()
            ret = {
               "queue": vals[1].strip(),
            } 
            other_info = vals[2] 
            m2 = re.match(r".+priomap\s*(.+)", other_info)
            if m2:
                ret["priomap"] = m2.group(1)
            m3 = re.match(r".+bands\s*(\d)", other_info)
            if m3:
                ret["bands"] = m3.group(1)
        else:
            m = re.match(r"\s*(Sent)\s*(\d+)\s*(bytes)\s(\d+)\s(pkt)\s\((dropped)\s(\d+),\s*(overlimits)\s(\d+)\s*(requeues)\s(\d+)\)", line)
            if m:
                #  Sent 1429059 bytes 12081 pkt (dropped 0, overlimits 0 requeues 1) 
                ret["statistics"] = {
                    "sent": int(m.group(2)),
                    "bytes": int(m.group(4)),
                    "pkt": {
                        "dropped": int(m.group(7)),
                        "overlimits": int(m.group(9)),
                        "requeues": int(m.group(11))
                        }
                    }
            else:
                m = re.match(r"\s*backlog\s(\d+)b\s*(\d+)p\s*requeues\s(\d+)", line)
                if m:
                    #backlog 0b 0p requeues 0 
                    ret["statistics"]["backlog"] = {
                        "bytes": int(m.group(1)),
                        "packets": int(m.group(2)),
                        "requeues": int(m.group(3))
                    }
                    
    # TODO ERROR CASES
    return retval

if __name__ == "__main__":
    import pprint
    #print("ip neigh show")
    #pprint.pprint( neighbors() )
 
    #print("ip neigh show")
    #pprint.pprint( route() )

    #print("ip maddr")
    #pprint.pprint( maddr() )

    #print("ip link")
    #pprint.pprint( link() )


    #print("ip tuntap")
    #pprint.pprint( tuntap("tun1", "tun") )

    #print("ip tuntap")
    #pprint.pprint( delete_tuntap("tun1", "tun") )
    #print("tc -s -d  qdisc ls dev wlp3s0")
    #pprint.pprint( tc("qdisc", "ls", "wlp3s0", {'statistics' : True, 'details': True}) )
