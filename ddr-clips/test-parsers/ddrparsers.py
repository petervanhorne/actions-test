import re
import sys
from lxml import etree
import xml.dom.minidom
import xml.etree.ElementTree as ET

def genie_str_to_class(classname):
    try:
        module = getattr(sys.modules[__name__], classname)
        return module()
    except Exception as e:
        return None

# ================================
# Parser for 'show l2route evpn mac-ip all'
# ================================

class NXShowL2RouteEvpnMacIpAll():
    """Parser for 'show l2route evpn mac-ip all'

       The response from the show command is passed as an argument
       to the cli method which generates a Python dictionary containing the
       The selected parsed fields from the show command.
       

    Sample Show Command Output:

Flags -(Rmac):Router MAC (Stt):Static (L):Local (R):Remote (V):vPC link 
(Dup):Duplicate (Spl):Split (Rcv):Recv(D):Del Pending (S):Stale (C):Clear
(Ps):Peer Sync (Ro):Re-Originated (Orp):Orphan 
Topology    Mac Address    Host IP                                 Prod   Flags         Seq No     Next-Hops                              
----------- -------------- --------------------------------------- ------ ---------- ---------- ---------------------------------------
1001        0001.abba.edda 5.1.1.1                                 BGP    --            0         204.1.1.1 (Label: 1001)   
1001        0002.abba.edda 2.2.2.2                                 BGP    --            0         201.1.1.1 (Label: 1001)   


(R):Remote (V):vPC link 
(Dup):Duplicate (Spl):Split (Rcv):Recv(D):Del Pending (S):Stale (C):Clear
(Ps):Peer Sync (Ro):Re-Originated (Orp):Orphan 
Topology    Mac Address    Host IP                                 Prod   Flags         Seq No     Next-Hops
----------- -------------- --------------------------------------- ------ ---------- ----------  ------------
1001        0001.abba.edda 5.1.1.1                                 BGP    --            0         204.1.1.1 (Label: 1001)

Topology    Mac Address    Host IP                                 Prod   Flags         Seq No     Next-Hops                            
----------- -------------- --------------------------------------- ------ ---------- ---------- -----------------------------------
1001        0001.abba.edda 5.1.1.1                                 HMM    L,            0         Local                               
    
    Sample parser_dict{} returned by parser:

    {'nve_peer_mac_ip': {'204.1.1.1': {'nve-peer': '204.1.1.1', 'topology': 1001, 'mac': '0001.abba.edda', 'type': 'MACIP', 'producer': 'BGP', 'host-ip': '5.1.1.1'}}}
        
    Sample ddr-fact definition:
    
    Sample FACT template from ddr-rules:
    
    (deftemplate nve-peer-mac-ip
      (slot device (type STRING)) ; Device running the show command
      (slot peer-ip (type STRING)) ; ip address of the peering device
      (slot vni (type INTEGER)) ; Topology value from show command
      (slot mac (type STRING)) ; peer MAC address
      (slot host-ip (type STRING)) ; ip address of the host device
      (slot type (type STRING)) ; peer type "MACIP"
      (slot producer (type STRING)) ; Infrastructure that produced the l2route "VXLAN" or "IMET"
      (slot flags (type STRING)) ; Flags from the show command
    )      

    Sample DDR function call from ddr-rules:
    
    (run_show_parameter 0 0 "show l2route evpn mac all" 0 none none none none none)
    
      Where: the 1st 0 is the index into the 'show_parameter_fact_list' in ddr-facts
      The 2nd 0 is the index into the  devices list selecting run command on 1st device
      Show command string is the template for execution. 
      
    Sample CLIPs FACT generated:    
      
    (nve-peer-mac-ip (device "leafdummy-1") (peer-ip "201.1.1.1") (vni 1001) (mac "0001.abba.edda") 
      (host-ip "") (type "MACIP") (producer "HMM") (flags ""))

    """
    def parse(self, output=None, pversion=None, debug=None):
        out = output

        # Init dictionary
        parsed_dict = {} # Contains the parsed Python dictionary
        af_dict = {} # Used as intermediate dictionary to build instances
     
        #
        # Precompile the regular expressions used to select data from specific lines
        # These definitions started with the genie_parser "ShowBgpL2vpnEvpn"
        
        p1 = re.compile(r'Topology    Mac Address    Host IP                                 Prod   Flags         Seq No     Next-Hops.*')
        p2 = re.compile(r'^(?P<topology>\d+)\s+(?P<mac>\S+)\s+(?P<host_ip>\S+)\s+(?P<producer>\S+)\s+(?P<flags>\S+)\s+(?P<sequence>\d+)\s+(?P<peer>\S+)\s+.*')
       
        found_line = False  
        found_count = 0         
        for line in out.splitlines():
            line = line.strip()
            if found_line:
                if found_count == 0:
                    found_count = found_count + 1 # skip one line
                    continue
                    
            # Look for line defined in p1 as a marker to find peers learned using BGP
            m = p1.match(line)
            if m:
                # Marker line found
                found_line = True
                continue
          
            m = p2.match(line)
            if m:
                af_dict = parsed_dict.setdefault('nve_peer_mac_ip', {}).setdefault(m.groupdict()['mac'], {})
                af_dict['peer-ip'] = str(m.groupdict()['peer'])
                af_dict['vni'] = int(m.groupdict()['topology'])
                af_dict['mac'] = str(m.groupdict()['mac'])
                af_dict['host-ip'] = str(m.groupdict()['host_ip'])
                af_dict['type'] = 'MACIP'
                af_dict['producer'] = str(m.groupdict()['producer'])
                af_dict['flags'] = str(m.groupdict()['flags'])
            continue
        return parsed_dict
# ================================
# Parser for 'show l2route evpn imet all'
# ================================

class NXShowL2RouteEvpnImetAll():
    """Parser for 'show l2route evpn imet all'
      
    Sample Show Command Output:

    Flags- (F): Originated From Fabric, (W): Originated from WAN

    Topology ID VNI         Prod  IP Addr                                 Flags  
    ----------- ----------- ----- --------------------------------------- -------
    1002        1002        BGP   204.1.1.1                               -      
    1002        1002        VXLAN 201.1.1.1                               -      
   
    
    Sample parser_dict{} returned by parser:

    {'nve_peer_l2vpn': {'201.1.1.1': {'nve-peer': '201.1.1.1', 'topology': 1002, 'vni': '1002', 'type': 'IMET', 'producer': 'BGP'}}}
        
    Sample ddr-fact definition:
    
    Sample FACT template from ddr-rules:
    
    (deftemplate nve-peer-l2vpn
      (slot device (type STRING))
      (slot nve-peer (type STRING))
      (slot type (type STRING))
      (slot topology (type INTEGER))
      (slot vni (type INTEGER))
      (slot producer (type STRING))
    )      

    Sample DDR function call from ddr-rules:
    
    (run_show_parameter 0 0 "show bgp l2vpn evpn {0}" 1 ?peer-ip none none none none)
    
      Where: the 1st 0 is the index into the 'show_parameter_fact_list' in ddr-facts
      The 2nd 0 is the index into the  devices list selecting run command on 1st device
      Show command string is the template for execution.  {0} has the value of the variable
      ?peer-ip substituted when the show command is executed.
      The 1 indicates one parameter (out of three maximum) will be used.
      The last two 'none' values could defined FACTs to assert before and after running the
      rule function.
      
    Sample CLIPs FACT generated:    
      
    (evpn-routes (rd "201.1.1.1:33769") (route "[3]:[0]:[32]:[204.1.1.1]/88") 
                 (imported "204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88") 
                 (direction "internal") (path "path_sourced_internal_to_AS") (destinations 0))

    """
    def parse(self, output=None, pversion=None, debug=None):
        out = output
        # Init dictionary
        parsed_dict = {} # Contains the parsed Python dictionary
        af_dict = {} # Used as intermediate dictionary to build instances
    
        #
        # Precompile the regular expressions used to select data from specific lines
        # These definitions started with the genie_parser "ShowBgpL2vpnEvpn"
        
        p1 = re.compile(r'^Topology ID VNI         Prod  IP Addr.*')
        p2 = re.compile(r'^(?P<topology>\d+)\s+(?P<vni>\d+)\s+(?P<producer>\S+)\s+(?P<peer>\S+).*')
        
        found_line = False  
        found_count = 0         
        for line in out.splitlines():
            line = line.strip()
            if found_line:
                if found_count == 0:
                    found_count = found_count + 1 # skip one line
                    continue
                    
            # Look for line defined in p1 as a marker to find peers learned using BGP
            m = p1.match(line)
            if m:
                # Marker line found
                found_line = True
                continue

            m = p2.match(line)
            if m:
                af_dict = parsed_dict.setdefault('nve_peer_l2vpn', {}).setdefault(m.groupdict()['peer'], {})
                af_dict['producer'] = (m.groupdict()['producer'])
                af_dict['nve-peer'] = str(m.groupdict()['peer'])
                af_dict['vni'] = int(m.groupdict()['vni'])
                af_dict['type'] = 'IMET'
                af_dict['producer'] = str(m.groupdict()['producer'])
            continue

        return parsed_dict
        
# ================================
# Parser for 'show l2route evpn mac all'
# ================================

class NXShowL2RouteEvpnMacAll():
    """Parser for 'show l2route evpn mac all'

       The response from the show command is passed as an argument
       to the cli method which generates a Python dictionary containing the
       The selected parsed fields from the show command.
       

    Sample Show Command Output:

Flags -(Rmac):Router MAC (Stt):Static (L):Local (R):Remote (V):vPC link 
(Dup):Duplicate (Spl):Split (Rcv):Recv (AD):Auto-Delete (D):Del Pending
(S):Stale (C):Clear, (Ps):Peer Sync (O):Re-Originated (Nho):NH-Override
(Pf):Permanently-Frozen, (Orp): Orphan

Topology    Mac Address    Prod   Flags         Seq No     Next-Hops                              
----------- -------------- ------ ------------- ---------- ---------------------------------------
1001        0001.abba.edda BGP    Stt,SplRcv    0          204.1.1.1 (Label: 1001)                
1001        0002.abba.edda BGP    Stt,SplRcv    0          201.1.1.1 (Label: 1001)
    
    Sample parser_dict{} returned by parser:

    {'nve_peer_mac': {'204.1.1.1': {'type': 'MAC', 'topology': 1001, 'producer': 'BGP', 'flags': 'SplRcv', 'peer_ip': '5.1.1.1', 'mac': '0001.abba.edda'}}, {'201.1.1.1': {'type': 'MAC', 'topology': 1001, 'producer': 'BGP', 'flags': 'SplRcv', 'peer_ip': '2.2.2.2', 'mac': '0002.abba.edda'}}}
        
    Sample ddr-fact definition:
    
    Sample FACT template from ddr-rules:
    
    (deftemplate nve-peer-mac
      (slot device (type STRING))
      (slot peer-ip (type STRING))
      (slot mac (type STRING))
      (slot type (type STRING))
      (slot vni (type INTEGER))
      (slot producer (type STRING))
      (slot flags (type STRING))
    )      

    Sample DDR function call from ddr-rules:
    
    (run_show_parameter 0 0 "show l2route evpn mac all" 0 none none none none none)
    
      Where: the 1st 0 is the index into the 'show_parameter_fact_list' in ddr-facts
      The 2nd 0 is the index into the  devices list selecting run command on 1st device
      Show command string is the template for execution. 
      
    Sample CLIPs FACT generated:    
      
    (nve-peer-mac (peer-ip "5.1.1.1") (mac '0002.abba.edda') (type "MAC") 
                 (topology 1001) (producer "BGP"))
    """
    def parse(self, output=None, pversion=None, debug=None):
        out = output

        # Init dictionary
        parsed_dict = {} # Contains the parsed Python dictionary
        af_dict = {} # Used as intermediate dictionary to build instances
     
        #
        # Precompile the regular expressions used to select data from specific lines
        # These definitions started with the genie_parser "ShowBgpL2vpnEvpn"
        
        p1 = re.compile(r'Topology    Mac Address    Prod   Flags         Seq No     Next-Hops.*')
        p2 = re.compile(r'(?P<topology>\d+)\s+(?P<mac>\S+)\s+(?P<producer>\S+)\s+(?P<flags>\S+)\s+(?P<sequence>\d+)\s+(?P<peer_ip>\S+).*')
       
        found_line = False  
        found_count = 0         
        for line in out.splitlines():
            line = line.strip()
            if found_line:
                if found_count == 0:
                    found_count = found_count + 1 # skip one line
                    continue
                    
            # Look for line defined in p1 as a marker to find peers learned using BGP
            m = p1.match(line)
            if m:
                # Marker line found
                found_line = True
                continue

            # Check for peers learned using BGP
           
            m = p2.match(line)
            if m:
                af_dict = parsed_dict.setdefault('nve_peer_mac', {}).setdefault(m.groupdict()['mac'], {})
                af_dict['vni'] = int(m.groupdict()['topology'])
                af_dict['peer-ip'] = str(m.groupdict()['peer_ip'])
                af_dict['type'] = 'MAC'
                af_dict['producer'] = str(m.groupdict()['producer'])
                af_dict['flags'] = str(m.groupdict()['flags'])
                af_dict['mac'] = str(m.groupdict()['mac'])
            continue
        return parsed_dict

# ================================
# Parser for 'show bgp l2vpn evpn route-type 3
# ================================
class NXShowBgpL2vpnEvpnRT3():
    """Parser for 'show bgp l2vpn evpn 204.1.1.1'
       Where 204.1.1.1 is the evpn peer identifier

       The response from the show command is passed as an argument
       to the cli method which generates a Python dictionary containing the
       The selected parsed fields from the show command.
       
    The 'parse' method of this class is called from the DDR rule functions in ddrclass.py.
    The rule function, e.g. '(run_show_parameter ...' runs the show command, collects the response
    and calls the parse method with the results read from the device.  The parse
    method generates a Python dictionary containing the fields required to assert a CLIPs FACT.
    The rule function calls the 'assert_template_fact' ddrclass.py function to assert the FACT.

    Sample Show Command Output:
    
    BGP routing table information for VRF default, address family L2VPN EVPN
    Route Distinguisher: 201.1.1.1:33769    (L2VNI 1002)
    BGP routing table entry for [3]:[0]:[32]:[204.1.1.1]/88, version 18
    Paths: (1 available, best #1)
    Flags: (0x000012) (high32 00000000) on xmit-list, is in l2rib/evpn, is not in HW
    Multipath: iBGP

      Advertised path-id 1
      Path type: internal, path is valid, is best path, no labeled nexthop
             Imported from 204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88 
      AS-Path: NONE, path sourced internal to AS
        204.1.1.1 (metric 0) from 204.1.1.2 (204.1.1.2)
      Origin IGP, MED not set, localpref 100, weight 0
      Extcommunity: RT:1000:1002 ENCAP:8
      Originator: 204.1.1.1 Cluster list: 204.1.1.2 
      PMSI Tunnel Attribute:
        flags: 0x00, Tunnel type: Ingress Replication
        Label: 1002, Tunnel Id: 204.1.1.1

    Path-id 1 not advertised to any peer
    
    Sample parser_dict{} returned by parser:
    
    {'route_distinguisher': {'201.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88', 'imported': '204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88', 'path': 'path sourced internal to AS', 'direction': 'internal', 'destinations': 0}, '204.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88', 'imported': '', 'path': 'path sourced internal to AS', 'direction': 'internal', 'destinations': 1}}}

    Sample ddr-fact definition:
    
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "ShowBgpL2EvpnRecv",
     "assert_fact_for_each_item_in": "route_distinguisher",
     "protofact": {"template": "evpn-routes",
                                "slots": {"rd": "$",
                                          "route": "$+route",                                
                                          "imported": "$+imported",
                                          "direction": "$+direction",
                                          "path": "$+path",                                
                                          "destinations": "$+destinations" 
                                          },
                                "types": {"rd": "str",
                                          "route": "str",                                
                                          "imported": "str",
                                          "direction": "str",
                                          "path": "str",                                
                                          "destinations": "int" 
                                          }
                  }
    }

    Sample FACT template from ddr-rules:
    
    (deftemplate evpn-routes
      (slot tname (default evpn-routes))
      (slot device (type STRING))
      (slot rd (type STRING))
      (slot route (type STRING))
      (slot imported (type STRING))
      (slot direction (type STRING))
      (slot path (type STRING))
      (slot destinations (type INTEGER)))
      

    Sample DDR function call from ddr-rules:
    
    (run_show_parameter 0 0 "show bgp l2vpn evpn {0}" 1 ?peer-ip none none none none)
    
      Where: the 1st 0 is the index into the 'show_parameter_fact_list' in ddr-facts
      The 2nd 0 is the index into the  devices list selecting run command on 1st device
      Show command string is the template for execution.  {0} has the value of the variable
      ?peer-ip substituted when the show command is executed.
      The 1 indicates one parameter (out of three maximum) will be used.
      The last two 'none' values could defined FACTs to assert before and after running the
      rule function.
      
    Sample CLIPs FACT generated:    
      
    (evpn-routes (rd "201.1.1.1:33769") (route "[3]:[0]:[32]:[204.1.1.1]/88") 
                 (imported "204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88") 
                 (direction "internal") (path "path_sourced_internal_to_AS") (destinations 0))

    """
    def parse(self, output=None, pversion=None, debug=None):
        out = output

        # Init dictionary
        parsed_dict = {} # Contains the parsed Python dictionary
        af_dict = {} # Used as intermediate dictionary to build instances

        # Initialize variables reused in parser to default values that are used
        # when no data is included in the show response for the data item
        # The ddr-facts processing for the parser output expects that there will\
        # be a dictionary entry for every  field in the FACT definition
        
        vrf_name = 'default'
        route = ""
        vni = 0
        route_distinguisher = ""
        imported_from = ""
        dest_count = 0
        path_type = ""
        
        #
        # Precompile the regular expressions used to select data from specific lines
        # These definitions started with the genie_parser "ShowBgpL2vpnEvpn"
        
        p1 = re.compile(r'^\s*BGP +routing +table +information +for +VRF'
                            ' +(?P<vrf_name>\S+), +address +family'
                            ' +(?P<address_family>[\w\s\-\_]+)$')
        p2 = re.compile(r'^BGP routing table entry for (?P<route>.*?), version (?P<version>\d+)') 
        p3 = re.compile(r'.*Route Distinguisher: (?P<route_distinguisher>(\S+)).*\(L2VNI (?P<vni>\d+).*')
        p4 = re.compile(r'.*Imported from (?P<imported>.*)')
        p5 = re.compile(r'.*Imported to (?P<dest_count>\d+)')
        p6 = re.compile(r'.*Path type: (?P<path_type>.*?),') 
        p7 = re.compile(r'.*AS-Path: .*?, (?P<as_path>.*)') 

        # Iterate through each line in the show command output to select required fields
        # Fields are collected by matching content in multiple show output lines
        # When all required fields are available, a parser sub-dictionary is added to
        # parser_dict {}  
           
        for line in out.splitlines():
            line = line.strip()
            # BGP routing table information for VRF default, address family L2VPN EVPN
            m = p1.match(line)
            if m:
                # Get the vrf_name from the show command
                vrf_name = m.groupdict()['vrf_name']
                continue

            # BGP routing table entry for [3]:[0]:[32]:[204.1.1.1]/88
            m = p2.match(line)
            if m:
                route = m.groupdict()['route']
                continue

            # Route Distinguisher: 201.1.1.1:33769
            m = p3.match(line)
            if m:
                route_distinguisher = m.groupdict()['route_distinguisher']
                vni = int(m.groupdict()['vni'])
                continue

            # Imported from 204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88
            # If the RD "Path Type" section includes "Imported from" generate a dictionary entry
            m = p4.match(line)
            if m:
                imported_from = m.groupdict()['imported']
                continue               

            # Imported to 1 destination(s)
            m = p5.match(line)
            if m:
                dest_count = int(m.groupdict()['dest_count'])
                continue

            # Path type: internal (from routing protocol)       Path type: local (generated by this peer device)
            # If the "Path Type" is not local (this device is a receiver) generate dictionary entry
            # The AS-Path is the last field that needs to be read to complete the FACT
            # af_dict is used to create an instance of the 'route_distinquisher' and the
            # required members are added to the dictionary using the update method.
            #
            # After the parsed_dict is updated, the variables used to collect the fields from
            # the show command are re-initialized

            # {'route_distinguisher': {'201.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88',
            #  'imported': '204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88',
            #  'path-type': 'internal', 
            #  'destinations': 0}}}
            
            m = p6.match(line)
            if m:
                path = m.groupdict()['path_type']
                af_dict = parsed_dict.setdefault('route_distinguisher', {}).setdefault(route_distinguisher, {})
                af_dict.update({'route': route})
                af_dict.update({'vni': vni})
                af_dict.update({'imported': imported_from})
                af_dict.update({'path_type': path})
                af_dict.update({'destinations': dest_count})
                af_dict.update({'route_type': 3})               
                route = ""
                route_distinguisher = ""
                imported_from = ""
                dest_count = 0
                direction = ""
                path = ""
                continue

        return parsed_dict
                        
# ================================
# Parser for 'show bgp l2vpn evpn route-type 2
# ================================
class NXShowBgpL2vpnEvpnRT2():
    """Parser for 'show bgp l2vpn evpn route-type 2'

       The response from the show command is passed as an argument
       to the cli method which generates a Python dictionary containing the
       The selected parsed fields from the show command.
       
    The 'parse' method of this class is called from the DDR rule functions in ddrclass.py.
    The rule function, e.g. '(run_show_parameter ...' runs the show command, collects the response
    and calls the parse method with the results read from the device.  The parse
    method generates a Python dictionary containing the fields required to assert a CLIPs FACT.
    The rule function calls the 'assert_template_fact' ddrclass.py function to assert the FACT.

    Sample Show Command Output: See examples below in code

      
    Sample parser_dict{} returned by parser:
    
    {'route_distinguisher': {'201.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88', 'imported': '204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88', 'path': 'path sourced internal to AS', 'direction': 'internal', 'destinations': 0}, '204.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88', 'imported': '', 'path': 'path sourced internal to AS', 'direction': 'internal', 'destinations': 1}}}

    Sample ddr-fact definition:
    
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "ShowBgpL2EvpnRecv",
     "assert_fact_for_each_item_in": "route_distinguisher",
     "protofact": {"template": "evpn-routes",
                                "slots": {"rd": "$",
                                          "route": "$+route",                                
                                          "imported": "$+imported",
                                          "direction": "$+direction",
                                          "path": "$+path",                                
                                          "destinations": "$+destinations" 
                                          },
                                "types": {"rd": "str",
                                          "route": "str",                                
                                          "imported": "str",
                                          "direction": "str",
                                          "path": "str",                                
                                          "destinations": "int" 
                                          }
                  }
    }

    Sample FACT template from ddr-rules:
    
    (deftemplate evpn-routes
      (slot tname (default evpn-routes))
      (slot device (type STRING))
      (slot rd (type STRING))
      (slot route (type STRING))
      (slot imported (type STRING))
      (slot direction (type STRING))
      (slot path (type STRING))
      (slot destinations (type INTEGER)))
      

    Sample DDR function call from ddr-rules:
    
    (run_show_parameter 0 0 "show bgp l2vpn evpn {0}" 1 ?peer-ip none none none none)
    
      Where: the 1st 0 is the index into the 'show_parameter_fact_list' in ddr-facts
      The 2nd 0 is the index into the  devices list selecting run command on 1st device
      Show command string is the template for execution.  {0} has the value of the variable
      ?peer-ip substituted when the show command is executed.
      The 1 indicates one parameter (out of three maximum) will be used.
      The last two 'none' values could defined FACTs to assert before and after running the
      rule function.
      
    Sample CLIPs FACT generated:    
      
    (evpn-routes (rd "201.1.1.1:33769") (route "[3]:[0]:[32]:[204.1.1.1]/88") 
                 (imported "204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88") 
                 (direction "internal") (path "path_sourced_internal_to_AS") (destinations 0))

    """
    def parse(self, output=None, pversion=None, debug=None):
        out = output

        # Init dictionary
        parsed_dict = {} # Contains the parsed Python dictionary
        af_dict = {} # Used as intermediate dictionary to build instances

        # Initialize variables reused in parser to default values that are used
        # when no data is included in the show response for the data item
        # The ddr-facts processing for the parser output expects that there will\
        # be a dictionary entry for every  field in the FACT definition
        
        vrf_name = 'default'
        route = ""
        vni = 0
        route_distinguisher = ""
        imported_from = ""
        dest_count = 0
        path_type = ""

    # Select parser logic based on the NX-OS version
        parsed_dict = {}
        if pversion == None:
            return parsed_dict

    # NX-OS version '9'
    #   Route Distinguisher: 204.1.1.1:33768    (L2VNI 1001)
    #   BGP routing table entry for [2]:[0]:[0]:[48]:[0001.abba.edda]:[32]:[5.1.1.1]/272, version 4
    #   Paths: (1 available, best #1)
    #   Flags: (0x000102) (high32 00000000) on xmit-list, is not in l2rib/evpn
    #   
    #     Advertised path-id 1
    #     Path type: local, path is valid, is best path, no labeled nexthop
    #     AS-Path: NONE, path locally originated
    #       204.1.1.1 (metric 0) from 0.0.0.0 (204.1.1.1)
    #         Origin IGP, MED not set, localpref 100, weight 32768
    #         Received label 1001 10001
    #         Extcommunity: RT:1000:1001 RT:1000:10001 ENCAP:8 Router MAC:88f0.31bf.cbff
    #   
    #     Path-id 1 advertised to peers:
    #       204.1.1.2      
                
        elif pversion in ['9.3(6)', '9.3(12)']:     
        #
        # Precompile the regular expressions used to select data from specific lines
        # These definitions started with the genie_parser "ShowBgpL2vpnEvpn"
        
            p2 = re.compile(r'.*Route Distinguisher: (?P<route_distinguisher>(\S+)).*\(L2VNI (?P<vni>\d+).*')
            p3 = re.compile(r'^BGP routing table entry for (?P<route>.*?), version (?P<version>\d+)') 
            p4 = re.compile(r'.*Imported from (?P<imported>.*)')
            p5 = re.compile(r'.*Imported to (?P<dest_count>\d+)')
            p6 = re.compile(r'.*Path type: (?P<path_type>.*?),') 
            p7 = re.compile(r'.*AS-Path: .*?, (?P<as_path>.*)') 

        # Iterate through each line in the show command output to select required fields
        # Fields are collected by matching content in multiple show output lines
        # When all required fields are available, a parser sub-dictionary is added to
        # parser_dict {}  
           
            for line in out.splitlines():
                line = line.strip()
                # Route Distinguisher: 201.1.1.1:33769
                m = p2.match(line)
                if m:
                    route_distinguisher = m.groupdict()['route_distinguisher']
                    vni = int(m.groupdict()['vni'])
                    continue

                # BGP routing table entry for [3]:[0]:[32]:[204.1.1.1]/88
                m = p3.match(line)
                if m:
                    route = m.groupdict()['route']
                    continue

                # Imported from 204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88
                # If the RD "Path Type" section includes "Imported from" generate a dictionary entry
                m = p4.match(line)
                if m:
                    imported_from = m.groupdict()['imported']
                    continue               

                # Imported to 1 destination(s)
                m = p5.match(line)
                if m:
                    dest_count = int(m.groupdict()['dest_count'])
                    continue

            # Path type: internal (from routing protocol)       Path type: local (generated by this peer device)
            # If the "Path Type" is not local (this device is a receiver) generate dictionary entry
            # The AS-Path is the last field that needs to be read to complete the FACT
            # af_dict is used to create an instance of the 'route_distinquisher' and the
            # required members are added to the dictionary using the update method.
            #
            # After the parsed_dict is updated, the variables used to collect the fields from
            # the show command are re-initialized

            # {'route_distinguisher': {'201.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88',
            #  'imported': '204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88',
            #  'path-type': 'internal', 
            #  'destinations': 0}}}
            
                m = p6.match(line)
                if m:
                    path = m.groupdict()['path_type']
                    af_dict = parsed_dict.setdefault('route_distinguisher', {}).setdefault(route_distinguisher, {})
                    af_dict.update({'route': route})
                    af_dict.update({'vni': vni})
                    af_dict.update({'imported': imported_from})
                    af_dict.update({'path_type': path})
                    af_dict.update({'destinations': dest_count})
                    af_dict.update({'route_type': 2})               
                    route = ""
                    route_distinguisher = ""
                    imported_from = ""
                    dest_count = 0
                    direction = ""
                    path = ""
                    continue
            return parsed_dict
#PVH
    # NX-OS version 10.2(1) or 10.4(1)
    #   Route Distinguisher: 201.1.1.1:33768    (L2VNI 1001)
    #   BGP routing table entry for [2]:[0]:[0]:[48]:[0001.abba.edda]:[32]:[5.1.1.1]/272, version 171
    #   Paths: (1 available, best #1)
    #   Flags: (0x000212) (high32 00000000) on xmit-list, is in l2rib/evpn, is not in HW
    #   Multipath: iBGP
    #   
    #     Advertised path-id 1
    #     Path type: internal, path is valid, is best path, no labeled nexthop, in rib
    #                Imported from 204.1.1.1:33768:[2]:[0]:[0]:[48]:[0001.abba.edda]:[32]:[5.1.1.1]/272 
    #     AS-Path: NONE, path sourced internal to AS
    #       204.1.1.1 (metric 0) from 204.1.1.2 (204.1.1.2)
    #         Origin IGP, MED not set, localpref 100, weight 0
    #         Received label 1001 10001
    #         Extcommunity: RT:1000:1001 RT:1000:10001 ENCAP:8 Router MAC:88f0.31bf.cbff
    #         Originator: 204.1.1.1 Cluster list: 204.1.1.2 
    #   
    #     Path-id 1 not advertised to any peer

        elif pversion in ['10.2(1)', '10.4(1)']:
        #
        # Precompile the regular expressions used to select data from specific lines
        # These definitions started with the genie_parser "ShowBgpL2vpnEvpn"
        
            p1 = re.compile(r'^\s*BGP +routing +table +information +for +VRF'
                            ' +(?P<vrf_name>\S+), +address +family'
                            ' +(?P<address_family>[\w\s\-\_]+)$')
            p2 = re.compile(r'^BGP routing table entry for (?P<route>.*?), version (?P<version>\d+)') 
            p3 = re.compile(r'.*Route Distinguisher: (?P<route_distinguisher>(\S+)).*\(L2VNI (?P<vni>\d+).*')
            p4 = re.compile(r'.*Imported from (?P<imported>.*)')
            p5 = re.compile(r'.*Imported to (?P<dest_count>\d+)')
            p6 = re.compile(r'.*Path type: (?P<path_type>.*?),') 
            p7 = re.compile(r'.*AS-Path: .*?, (?P<as_path>.*)') 

        # Iterate through each line in the show command output to select required fields
        # Fields are collected by matching content in multiple show output lines
        # When all required fields are available, a parser sub-dictionary is added to
        # parser_dict {}  
           
            for line in out.splitlines():
                line = line.strip()
                # BGP routing table information for VRF default, address family L2VPN EVPN
                m = p1.match(line)
                if m:
                # Get the vrf_name from the show command
                    vrf_name = m.groupdict()['vrf_name']
                    continue

                # BGP routing table entry for [3]:[0]:[32]:[204.1.1.1]/88
                m = p2.match(line)
                if m:
                    route = m.groupdict()['route']
                    continue

                # Route Distinguisher: 201.1.1.1:33769
                m = p3.match(line)
                if m:
                    route_distinguisher = m.groupdict()['route_distinguisher']
                    vni = int(m.groupdict()['vni'])
                    continue

                # Imported from 204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88
                # If the RD "Path Type" section includes "Imported from" generate a dictionary entry
                m = p4.match(line)
                if m:
                    imported_from = m.groupdict()['imported']
                    continue               

                # Imported to 1 destination(s)
                m = p5.match(line)
                if m:
                    dest_count = int(m.groupdict()['dest_count'])
                    continue

            # Path type: internal (from routing protocol)       Path type: local (generated by this peer device)
            # If the "Path Type" is not local (this device is a receiver) generate dictionary entry
            # The AS-Path is the last field that needs to be read to complete the FACT
            # af_dict is used to create an instance of the 'route_distinquisher' and the
            # required members are added to the dictionary using the update method.
            #
            # After the parsed_dict is updated, the variables used to collect the fields from
            # the show command are re-initialized

            # {'route_distinguisher': {'201.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88',
            #  'imported': '204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88',
            #  'path-type': 'internal', 
            #  'destinations': 0}}}
            
                m = p6.match(line)
                if m:
                    path = m.groupdict()['path_type']
                    af_dict = parsed_dict.setdefault('route_distinguisher', {}).setdefault(route_distinguisher, {})
                    af_dict.update({'route': route})
                    af_dict.update({'vni': vni})
                    af_dict.update({'imported': imported_from})
                    af_dict.update({'path_type': path})
                    af_dict.update({'destinations': dest_count})
                    af_dict.update({'route_type': 2})               
                    route = ""
                    route_distinguisher = ""
                    imported_from = ""
                    dest_count = 0
                    direction = ""
                    path = ""
                    continue
            return parsed_dict
            
        else:
            print("%%%% DDR-error: NXShowBgpL2vpnEvpnRT2: Unsupported Version: " + str(pversion))
            return {}
        
# ==================================================
# Parser for 'show nve internal event-history peer'
# ==================================================
class NXShowNveInternalPeer():

    def parse(self, output=None, pversion=None, debug=None):
    #
    # Sample log messages NX-OS version '9.3'
    #
        '''2023 Feb 13 17:54:49.625302: E_DEBUG    nve [5065]: [Peer: 204.1.1.1] [nve_process_peer_add_req:692] Peer add request on VNI: 1002, egressVni: 1002 rnhMAC: 00:00:00:00:00:00 learnSrc: BGP flags: FABRIC  nveIf: nve1 tunnelID: 0x0 

          2023 Feb 13 17:54:49.625088: E_DEBUG    nve [5065]: [Peer: 204.1.1.1] [nve_handle_bgp_peer_msg:5701] ADD peer, VNI: 1002 MAC: 00:00:00:00:00:00 underlayVRF: 1 encap: 1 flags: 0 tunnelID: 0x0 egressVNI: 1002 peerNode: no ifNode: yes vniReady: yes [L2-vni-rep-mode-ready] ''' 
    #
    # Sample log messages NX-OS version '10.4(1)'
    #
        '''2023-03-30T14:07:01.292307000+00:00 [M 27] [nve] E_DEBUG [nve_cmn_l2rib_send_all_peer_obj:675] Replaying all peer objects to L2RIB
        
           2023-03-30T14:08:39.035656000+00:00 [M 27] [nve] E_DEBUG [Interface: port-channel213] [nve_handle_l3_proto_state_change:3816] L3 protocol state change portState: up'''    
    #
    # Sample log messages NX-OS version '10.2(1)'
    #
        '''[26] 2023 Jul 03 15:23:38.165984 [nve] E_DEBUG    [23936]:[Peer: 204.1.1.1] [nve_process_peer_add_req:696] Peer add request on VNI: 1002, egressVni: 1002 rnhMAC: 00:00:00:00:00:00 learnSrc: BGP-IMET flags: FABRIC  nveIf: nve1 tunnelID: 0x0'''    
    #
    # Sample parser output
    #
        '''{'event_record': {'2023 Jun 15 19:35:47.087249': {'component': 'nve', 'type': 'peer', 'peer': '204.1.1.1', 'interface': 'none', 'function': 'nve_peer_info_update', 'line_num': 3237, 'message': 'Filled in delPeerTree', 'version': '9.3(6)'}, '2023 Jun 15 19:35:47.086464': {'component': 'nve', 'type': 'peer', 'peer': '204.1.1.1', 'interface': 'none', 'function': 'nve_peer_process_transition_values', 'line_num': 2090, 'message': 'Peer is in state: peer-add-complete, not processing transition values', 'version': '9.3(6)'}}}'''

    # Select parser logic based on the NX-OS version
        parsed_dict = {}
        if pversion == None:
            return parsed_dict

    # NX-OS version '9.3(6)'
                
        elif pversion in ['9.3(6)', '9.3(12)']:     

            p1 = re.compile(r'(?P<timestamp>([^E]*))E_DEBUG\s+(?P<component>(\S+))[^\]]*\]: \[(?P<tag>([^:]*)): (?P<peer>([^]]*))] \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))](?P<message>(.*))')
            p2 = re.compile(r'(?P<timestamp>([^E]*))E_DEBUG\s+(?P<component>(\S+))[^\]]*\]: \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))] (?P<message>(.*))')

            for line in output.splitlines():
                line = line.strip()
    #
    #    2023 Feb 13 17:54:49.625302: E_DEBUG    nve [5065]: [Peer: 204.1.1.1] [nve_process_peer_add_req:692] Peer add request on VNI: 1002, egressVni: 1002 rnhMAC: 00:00:00:00:00:00 learnSrc: BGP flags: FABRIC  nveIf: nve1 tunnelID: 0x0
    # 
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    timestamp = m.groupdict()['timestamp'].rstrip().rstrip(':')
                    message_string = m.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m.groupdict()['component']})
                    af_dict.update({'type': 'peer'})
                    af_dict.update({'peer': m.groupdict()['peer']})
                    af_dict.update({'interface': 'none'})
                    af_dict.update({'function': m.groupdict()['function']})
                    af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
    #
    #     2023 Feb 13 17:54:49.624801: E_DEBUG    nve [5065]: [nve_handle_bgp_peer_msg:5579] 1 peers TXID: 1 flags: 0
    #
                m2 = p2.match(line)
                if m2:
                    group = m2.groupdict()
                    timestamp = m2.groupdict()['timestamp'].rstrip().rstrip(':')
                    message_string = m2.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m2.groupdict()['component']})
                    af_dict.update({'type': 'peer'})
                    af_dict.update({'peer': 'none'})
                    af_dict.update({'interface': 'none'})
                    af_dict.update({'function': m2.groupdict()['function']})
                    af_dict.update({'line_num': int(m2.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
            return parsed_dict

#PVH
    # NX-OS version 10.2(1) or 10.4(1)

        elif pversion in ['10.2(1)', '10.4(1)']:
            if pversion == '10.4(1)':
                p1 = re.compile(r'(?P<timestamp>(\S+)) \[[^\]]*\].\[(?P<component>([^\]]*))\] E_DEBUG \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))](?P<message>(.*))')
                p2 = re.compile(r'(?P<timestamp>(\S+)) \[[^\]]*\].\[(?P<component>([^\]]*))\] E_DEBUG \[[^:]*: (?P<interface>([^]]\S+))] \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))] (?P<message>(.*))')
            elif pversion == '10.2(1)':
                p1 = re.compile(r'\[\d+\] (?P<timestamp>([^\[]*)).\[(?P<component>([^\]]*))\] E_DEBUG\s+\[\d+\]:\[Peer: (?P<peer>([^]]\S+))] \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))] (?P<message>(.*))')
                p2 = re.compile(r'(?P<timestamp>(\S+)) \[[^\]]*\].\[(?P<component>([^\]]*))\] E_DEBUG \[[^:]*: (?P<interface>([^]]\S+))] \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))] (?P<message>(.*))')
            else:
                print("%%%% DDR-error: NXShowNveInternalPeer: Unsupported Version: " + str(pversion))
                return {}

            for line in output.splitlines():
                line = line.strip()
    #
    # 2023-03-30T14:07:01.292307000+00:00 [M 27] [nve] E_DEBUG [nve_cmn_l2rib_send_all_peer_obj:675] Replaying all peer objects to L2RIB
    # 
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    timestamp = m.groupdict()['timestamp'].rstrip().rstrip('+00:00')
                    message_string = m.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m.groupdict()['component']})
                    af_dict.update({'type': 'peer'})
                    af_dict.update({'peer':  m.groupdict()['peer']})
                    af_dict.update({'interface': 'none'})
                    af_dict.update({'function': m.groupdict()['function']})
                    af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
    #
    # 2023-03-30T14:08:39.035656000+00:00 [M 27] [nve] E_DEBUG [Interface: port-channel213] [nve_handle_l3_proto_state_change:3816] L3 protocol state change portState: up
    #
                m2 = p2.match(line)
                if m2:
                    group = m2.groupdict()
                    timestamp = m2.groupdict()['timestamp'].rstrip().rstrip('+00:00')
                    message_string = m2.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m2.groupdict()['component']})
                    af_dict.update({'type': 'peer'})
                    af_dict.update({'peer': 'none'})
                    af_dict.update({'interface': m2.groupdict()['interface']})
                    af_dict.update({'function': m2.groupdict()['function']})
                    af_dict.update({'line_num': int(m2.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
            return parsed_dict

    # Unsupported OS version
    
        else:
            print("%%%% DDR-error: NXShowNveInternalPeer: Unsupported Version: " + str(pversion))
            return {} 
       
# ==================================================
# Parser for 'show nve internal event-history multicast'
# ==================================================
class NXShowNveInternalMulticast():

    def parse(self, output=None, pversion=None, debug=None):
    #
    # Sample log messages
    #
        '''2023 Feb 11 00:36:45.431250: E_DEBUG    nve [5065]: [nve_write_mrib_info_to_buffer:180] Filled MRIB buffer with source: 201.1.1.1, group: 225.1.1.1, vrfContext: default nveIOD: 123, srcIOD: 124, vxlanEncap: TRUE, vxlanDecap: FALSE add: TRUE, IOD: 0 

           2023 Feb 11 00:36:45.431227: E_DEBUG    nve [5065]: [nve_write_mrib_info_to_buffer:154] IPv4 multicast group 225.1.1.1 is SSM'''
    # 
    # Sample parser result
    #
        '''{'event_record': {'2023_Feb_11_00:36:45.431250': {'component': 'nve', 'type': 'multicast', 'function': 'nve_write_mrib_info_to_buffer', 'line_num': 180, 'message': 'Filled_MRIB_buffer_with_source:_201.1.1.1,_group:_225.1.1.1,_vrfContext:_default_nveIOD:_123,_srcIOD:_124,_vxlanEncap:_TRUE,_vxlanDecap:_FALSE_add:_TRUE,_IOD:_0'}, '2023_Feb_11_00:36:45.431227': {'component': 'nve', 'type': 'multicast', 'function': 'nve_write_mrib_info_to_buffer', 'line_num': 154, 'message': 'IPv4_multicast_group_225.1.1.1_is_SSM'}}}'''

        # Init vars
        parsed_dict = {}
        p1 = re.compile(r'(?P<timestamp>([^E]*))E_DEBUG\s+(?P<component>(\S+))[^\]]*\]: \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))](?P<message>(.*))')

        for line in output.splitlines():
            line = line.strip()
            m = p1.match(line)

            if m:
                group = m.groupdict()
                timestamp = m.groupdict()['timestamp'].rstrip().rstrip(':')
                message_string = m.groupdict()['message'].lstrip()
                af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                af_dict.update({'component': m.groupdict()['component']})
                af_dict.update({'type': 'multicast'})
                af_dict.update({'function': m.groupdict()['function']})
                af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                af_dict.update({'message': message_string})
                continue
        return parsed_dict

# ==================================================
# Parser for 'show nve internal event-history events'
# ==================================================
class NXShowNveInternalEvents():

    def parse(self, output=None, pversion=None, debug=None):
        if debug == 1:
            print("**** DDR Parser NXShowNveInternalEventsAll Debug: message: " + str(pversion))        
    #
    # Sample log messages
    #
        '''2023 Feb 13 17:54:48.960231: E_DEBUG    nve [5065]: [nve_overlay_peer_vni_add_done_batch_cb:1007] Received peer VNI add callback, numberOfPeerVNIs: 1 

2023 Feb 13 17:54:48.960045: E_DEBUG    nve [5065]: [nve_vni_fl_update_sdb:3926] Existing FL peerIP: 204.1.1.1 for VNI: 1002 

2023 Feb 13 17:54:48.960039: E_DEBUG    nve [5065]: [nve_send_heartbeat:10627] Sending a heartbeat to system manager 

2023 Feb 13 17:54:48.959838: E_DEBUG    nve [5065]: [nve_vni_fl_update_sdb:3987] Adding FL peerIP: 204.1.1.1 in position: 0 to VNI: 1002'''
    #
    # Sample parser output
    #
        '''{'event_record': {'2023_Feb_13_17:54:48.960231': {'component': 'nve', 'type': 'event', 'function': 'nve_overlay_peer_vni_add_done_batch_cb', 'line_num': 1007, 'message': 'Received_peer_VNI_add_callback,_numberOfPeerVNIs:_1'}, '2023_Feb_13_17:54:48.960045': {'component': 'nve', 'type': 'event', 'function': 'nve_vni_fl_update_sdb', 'line_num': 3926, 'message': 'Existing_FL_peerIP:_204.1.1.1_for_VNI:_1002'}, '2023_Feb_13_17:54:48.960039': {'component': 'nve', 'type': 'event', 'function': 'nve_send_heartbeat', 'line_num': 10627, 'message': 'Sending_a_heartbeat_to_system_manager'}, '2023_Feb_13_17:54:48.959838': {'component': 'nve', 'type': 'event', 'function': 'nve_vni_fl_update_sdb', 'line_num': 3987, 'message': 'Adding_FL_peerIP:_204.1.1.1_in_position:_0_to_VNI:_1002'}}}'''

    # Select parser logic based on the NX-OS version
        parsed_dict = {}
        if pversion == None:
            return parsed_dict

    # NX-OS version '9.3(6)'
                
        elif pversion in ['9.3(6)', '9.3(12)']:     
            p1 = re.compile(r'(?P<timestamp>([^E]*))E_DEBUG\s+(?P<component>(\S+))[^\]]*\]: \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))](?P<message>(.*))')
            for line in output.splitlines():
                line = line.strip()
                m = p1.match(line)

                if m:
                    group = m.groupdict()
                    timestamp = m.groupdict()['timestamp'].rstrip().rstrip(':')
                    message_string = m.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m.groupdict()['component']})
                    af_dict.update({'type': 'event'})
                    af_dict.update({'function': m.groupdict()['function']})
                    af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
            return parsed_dict

    # NX-OS version 10.2.(1) or 10.4(1)

        elif pversion in ['10.2(1)', '10.4(1)']:
            if pversion == '10.4(1)':
                p1 = re.compile(r'(?P<timestamp>(\S+)) \[[^\]]*\].\[(?P<component>([^\]]*))\] [^\]]*\[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))](?P<message>(.*))')
            elif pversion == '10.2(1)':
                p1 = re.compile(r'\[\d+\] (?P<timestamp>(.{27})).\[(?P<component>([^\]]*))\] E_DEBUG\s+\[\d+\]:\[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))](?P<message>(.*))')
            else:
                print("%%%% DDR-error: NXShowNveInternalTrigger: Unsupported Version: " + str(pversion))
                return {}

            for line in output.splitlines():
                line = line.strip()
                m = p1.match(line)

                if m:
                    group = m.groupdict()
                    timestamp = m.groupdict()['timestamp'].rstrip('+00:00')
                    message_string = m.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m.groupdict()['component']})
                    af_dict.update({'type': 'event'})
                    af_dict.update({'function': m.groupdict()['function']})
                    af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
            return parsed_dict        

    # Unsupported OS version
    
        else:
            print("%%%% DDR-error: NXShowNveInternalEventsAll: Unsupported Version: " + str(pversion))
            return {} 
                       
# ==================================================
# Parser for 'show nve internal event-history triggers'
# ==================================================
class NXShowNveInternalTrigger():

    def parse(self, output=None, pversion=None, debug=None):
    #
    # Sample log messages NX OS 9
    #
        '''2023 Feb 13 17:54:44.468645: E_DEBUG    nve [5065]: [nve_populate_urib_update_rnh_batch:357] nve_populate_urib_update_rnh_batch: ADD peer:204.1.1.1 vrf:1''' 
    #
    # Sample log messages NX OS 10.4(1)
    #
        '''2023-03-30T14:07:01.292434000+00:00 [M 27] [nve] E_DEBUG [nve_l2rib_notify_eoc:1568] Sent EOC for obj: 5
           2023-03-30T14:07:01.292321000+00:00 [M 27] [nve] E_DEBUG [nve_l2rib_send_all_peer_obj:1158] Adding all peer related objects to L2RIB'''
    #
    # Sample log messages NX OS 10.2(1)
    #
        '''[2] 2023 Jul 03 15:23:38.180349 [nve] E_DEBUG    [23936]:[nve_populate_urib_update_rnh_batch:436]  nve_populate_urib_update_rnh_batch: ADD peer:204.1.1.1 vrf:1'''
    #    
    # Sample parser output
    #
        '''{'event_record': {'2023 Jun 15 19:35:00.528915': {'component': 'nve', 'type': 'trigger', 'function': 'nve_populate_urib_update_rnh_batch', 'line_num': 357, 'message': 'nve_populate_urib_update_rnh_batch: ADD peer:204.1.1.1 vrf:1', 'version': '9.3(6)'}}}'''

    # Select parser logic based on the NX-OS version
        parsed_dict = {}
        if pversion == None:
            return parsed_dict

    # NX-OS version '9'
    #  2023 Jul 17 19:58:45.177944: E_DEBUG    nve [24647]: [nve_populate_urib_update_rnh_batch:358] nve_populate_urib_update_rnh_batch: ADD peer:201.1.1.1 vrf:1 

        elif pversion in ['9.3(12)']:
            p1 = re.compile(r'.*(?P<timestamp>(.{27})): E_DEBUG\s+(?P<component>(\S+)) \[\d+\]: \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))] nve_populate_urib_update_rnh_batch:(?P<message>(.*))')
            for line in output.splitlines():
                line = line.strip()
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    timestamp = m.groupdict()['timestamp'].rstrip().rstrip(':')
                    message_string = m.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m.groupdict()['component']})
                    af_dict.update({'type': 'trigger'})
                    af_dict.update({'function': 'nve_populate_urib_update_rnh_batch'})
                    af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
            return parsed_dict           
                
        elif pversion in ['9.3(6)']:     
            p1 = re.compile(r'(?P<timestamp>([^E]*))E_DEBUG\s+(?P<component>(\S+))[^\]]*\]: \[nve_populate_urib_update_rnh_batch:(?P<line_num>([^]]\d+))](?P<message>(.*))')
            for line in output.splitlines():
                line = line.strip()
                m = p1.match(line)
                if m:
                    group = m.groupdict()
                    timestamp = m.groupdict()['timestamp'].rstrip().rstrip(':')
                    message_string = m.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m.groupdict()['component']})
                    af_dict.update({'type': 'trigger'})
                    af_dict.update({'function': 'nve_populate_urib_update_rnh_batch'})
                    af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
            return parsed_dict           

#PVH
    # NX-OS version 10.2(1) or 10.4(1)

        elif pversion in ['10.2(1)', '10.4(1)']:
            if pversion == '10.4(1)':
                p1 = re.compile(r'(?P<timestamp>(\S+)) \[[^\]]*\].\[(?P<component>([^\]]*))\] E_DEBUG \[[^V](?P<function>([^:]*)):(?P<line_num>([^]]\d+))] (?P<message>(.*))')
            elif pversion == '10.2(1)':
                p1 = re.compile(r'\[\d+\] (?P<timestamp>([^\[]*)).\[(?P<component>([^\]]*))\] E_DEBUG\s+\[\d+\]:\[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))] (?P<message>(.*))')
            else:
                print("%%%% DDR-error: NXShowNveInternalTrigger: Unsupported Version: " + str(pversion))
                return {}

            for line in output.splitlines():
                line = line.strip()
                m = p1.match(line)

                if m:
                    group = m.groupdict()
                    timestamp = m.groupdict()['timestamp'].rstrip().rstrip(':').rstrip('+00:00')
                    message_string = m.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m.groupdict()['component']})
                    af_dict.update({'type': 'trigger'})
                    af_dict.update({'function': m.groupdict()['function']})
                    af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
            return parsed_dict           

    # Unsupported OS version
    
        else:
            print("%%%% DDR-error: NXShowNveInternalTrigger: Unsupported Version: " + str(pversion))
            return {} 
                   
# ==================================================
# Parser for 'show nve internal event-history vni'
# ==================================================
class NXShowNveInternalVni():

    def parse(self, output=None, pversion=None, debug=None):
    #
    # Sample log messages NX OX version 9
    #
        '''2023 May 04 19:07:23.114968: E_DEBUG    nve [5065]: [nve_vni_to_sw_bd:2075] Before update SW BD: 0, xconnect FALSE:  

           2023 May 04 19:02:00.522951: E_DEBUG    nve [5065]: [nve_vni_to_sw_bd:2075] Before update SW BD: 0, xconnect FALSE: '''
    #
    # Sample log messages NX OS version 10.4(1)
    #
        '''2023-03-30T14:07:01.487350000+00:00 [M 27] [nve] E_DEBUG [VNI: 11000] [nve_vrf_vni_handle_l3vm_vni_msg:420] VRF: EVPN-VRF-1, ID: 4, RC: -1 - ok'''
    #
    # Sample log messages NX OS version 10.2(1)
    #
        '''[14] 2023 Jul 03 15:23:38.165449 [nve] E_DEBUG    [23936]:[VNI: 1002] [nve_l2rib_message_cb:505] Received IMET notification for peerIP: 204.1.1.1, BD: 1002 Operation'''
    # 
    # Sample parser result
    #
        '''{'event_record': {'2023_May_04_19:07:23.114968': {'component': 'nve', 'type': 'vni', 'function': 'nve_vni_to_sw_bd', 'line_num': 2075, 'message': 'Before_update_SW_BD:_0,_xconnect_FALSE:'}, '2023_May_04_19:02:00.522951': {'component': 'nve', 'type': 'vni', 'function': 'nve_vni_to_sw_bd', 'line_num': 2075, 'message': 'Before_update_SW_BD:_0,_xconnect_FALSE:'}}}'''

    # Select parser logic based on the NX-OS version
        parsed_dict = {}
        if pversion == None:
            return parsed_dict

    # NX-OS version '9.3(6)'
                
        elif pversion in ['9.3(6)', '9.3(12)']:     
            p1 = re.compile(r'(?P<timestamp>([^+]*)).*VNI: (?P<vni>(\d+))\] \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))](?P<message>(.*))')

            for line in output.splitlines():
                line = line.strip()
                m = p1.match(line)

                if m:
                    group = m.groupdict()
                    timestamp = m.groupdict()['timestamp'].rstrip().rstrip(':')
                    message_string = m.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': 'nve'})
                    af_dict.update({'type': 'vni'})
                    af_dict.update({'vni': m.groupdict()['vni']})
                    af_dict.update({'function': m.groupdict()['function']})
                    af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue
            return parsed_dict                
#PVH
    # NX-OS version 10.2(1) or 10.4(1)

        elif pversion in ['10.2(1)', '10.4(1)']:
            if pversion == '10.4(1)':
                p2 = re.compile(r'(?P<timestamp>(\S+)) \[[^\]]*\].\[(?P<component>([^\]]*))\] E_DEBUG \[[^:]*: (?P<vni>([^]]\d+))] \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))] (?P<message>(.*))')
            elif pversion == '10.2(1)':
                p2 = re.compile(r'\[\d+\] (?P<timestamp>([^\[]*)).\[(?P<component>([^\]]*))\] E_DEBUG\s+\[\d+\]:\[VNI\: (?P<vni>([^]]\d+))] \[(?P<function>([^:]*)):(?P<line_num>([^]]\d+))] (?P<message>(.*))')
            else:
                print("%%%% DDR-error: NXShowNveInternalVni: Unsupported Version: " + str(pversion))
                return {}
    #
    # Process show command output
    #
            for line in output.splitlines():
                line = line.strip()

                m = p2.match(line)

                if m:
                    group = m.groupdict()
                    timestamp = m.groupdict()['timestamp'].rstrip().rstrip(':').rstrip('+00:00')
                    message_string = m.groupdict()['message'].lstrip()
                    af_dict = parsed_dict.setdefault('event_record', {}).setdefault(timestamp, {})
                    af_dict.update({'component': m.groupdict()['component']})
                    af_dict.update({'type': 'vni'})
                    af_dict.update({'vni': int(m.groupdict()['vni'])})
                    af_dict.update({'function': m.groupdict()['function']})
                    af_dict.update({'line_num': int(m.groupdict()['line_num'])})
                    af_dict.update({'message': message_string})
                    af_dict.update({'version': pversion})
                    continue

            return parsed_dict                

    # Unsupported OS version
    
        else:
            print("%%%% DDR-error: NXShowNveInternalVni: Unsupported Version: " + str(pversion))
            return {}
