'''
    test_ddr_nx_evpn_parsers.py
    
    Function:: Test automation for ddrparsers used to implement the ddr_nx_evpn_consist usecase
              This script is run using pytest and verifies that the text parsers correctly parse and assert the
              expected clips facts
              
    Usage::
            Run tests from the /test_parsers directory for the usecase
              pytest --full-trace --disable-pytest-warnings -vv test*.py -s (print debugging info)
              pytest --full-trace --disable-pytest-warnings -v test*.py (normal execution)
'''
#
from ddrparsers import *
from ddrparserlib import *
from ddrclass import *
from io import StringIO
import pytest
import threading
import os
import sys
sys.path.insert(0, '../')

def test_NXShowL2RouteEvpnImetAll():

    test_message = '''
Flags- (F): Originated From Fabric, (W): Originated from WAN

Topology ID VNI         Prod  IP Addr                                 Flags  
----------- ----------- ----- --------------------------------------- -------
1002        1002        BGP   204.1.1.1                               -                                  -        
1001        1001        VXLAN 201.1.1.1                               -                                  -        
    '''

    instance_example='''{'nve_peer_l2vpn': {'204.1.1.1': {'type': 'IMET', 'topology_id': 1002, 'vni': 1002, 'producer': 'BGP'}}}'''

    fact_list = [
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "NXShowL2RouteEvpnImetAll",
     "assert_fact_for_each_item_in": "nve_peer_l2vpn",
     "protofact": {"template": "nve-peer-imet",
                                "slots": {"nve-peer": "$",
                                          "vni": "$+vni",
                                          "type": "$+type",
                                          "producer": "$+producer"
                                          },
                                "types": {"nve-peer": "str",                                
                                          "vni": "int",
                                          "type": "str",
                                          "producer": "str" 
                                          }
                  }
    }    ]

#
# Initialize the CLIPS environment and load the FACT templates for the test
#
    try:
        env = clips.Environment()
        env.load("NXShowL2RouteEvpnImetAll_rules.clp")
    except Exception as e:
        print("&&&& Exception loading CLIPS: " + str(e))

    for version in ['9.3(6)', '9.3(12)', '10.2(1)', '10.4(1)']:
        print("***** Test NXShowL2RouteEvpnImetAll Parser OS version: ", version)

        test1=NXShowL2RouteEvpnImetAll() # create instance of parser class
        result = test1.parse(output=test_message, pversion=version)
#
# Verify parser dictionary generated
#
        print("\n%%% Parser result:\n", result)
        assert (result) == {'nve_peer_l2vpn': {'201.1.1.1': {'nve-peer': '201.1.1.1', 'producer': 'VXLAN', 'type': 'IMET', 'vni': 1001}, '204.1.1.1': {'nve-peer': '204.1.1.1', 'producer': 'BGP', 'type': 'IMET', 'vni': 1002}}}

#
# Create CLIPs facts to verify that the ddr-facts definition for the parser works correctly
#
        show_and_assert_fact(env, "nve-peer-l2vpn", fact_list[0], result)
        print("\n*********************** CLIPs FACTs *****************************")

        expected_facts = ['(nve-peer-imet (device "") (nve-peer "204.1.1.1") (type "IMET") (vni 1002) (producer "BGP"))\n',
                      '(nve-peer-imet (device "") (nve-peer "201.1.1.1") (type "IMET") (vni 1001) (producer "VXLAN"))\n']
        i = 0
#
# Redirect sys.stdout to convert the clips fact object to a string
# Verify that the expected facts are present in the clips knowledge base
#
        for fact in env.facts():
            buffer = StringIO()
            sys.stdout = buffer
            print(fact)
            fact_read = buffer.getvalue()
            sys.stdout = sys.__stdout__
            print("fact_read: ", fact_read)
            assert fact_read == expected_facts[i]
            i = i + 1        
        
def test_NXShowL2RouteEvpnMacIpAll():

    test_message = '''
Flags -(Rmac):Router MAC (Stt):Static (L):Local (R):Remote (V):vPC link 
(Dup):Duplicate (Spl):Split (Rcv):Recv(D):Del Pending (S):Stale (C):Clear
(Ps):Peer Sync (Ro):Re-Originated (Orp):Orphan 
Topology    Mac Address    Host IP                                 Prod   Flags         Seq No     Next-Hops                              
----------- -------------- --------------------------------------- ------ ---------- ---------- ---------------------------------------
1001        0001.abba.edda 5.1.1.1                                 BGP    --            0         204.1.1.1 (Label: 1001)  
1001        0002.abba.edda 2.2.2.2                                 BGP    --            0         201.1.1.1 (Label: 1001)
    '''

    fact_list = [
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "NXShowL2RouteEvpnMacIpAll",
     "assert_fact_for_each_item_in": "nve_peer_mac_ip",
     "protofact": {"template": "nve-peer-mac-ip",
                                "slots": {"mac": "$",
                                          "peer-ip": "$+peer-ip",
                                          "vni": "$+vni",
                                          "type": "$+type",
                                          "host-ip": "$+host-ip",
                                          "producer": "$+producer",
                                          "flags": "$+flags"
                                          },
                                "types": {"peer-ip": "str",
                                          "vni": "int",
                                          "mac": "str",
                                          "type": "str",
                                          "host-ip": "str",
                                          "producer": "str",
                                          "flags": "str"
                                          }
                  }
    }]
#
# Initialize the CLIPS environment and load the FACT templates for the test
#
    try:
        env = clips.Environment()
        env.load("NXShowL2RouteEvpnMacIpAll_rules.clp")
    except Exception as e:
        print("&&&& Exception loading CLIPS: " + str(e))

    for version in ['9.3(6)', '9.3(12)', '10.2(1)', '10.4(1)']:
        print("***** Test NXShowL2RouteEvpnMacIpAll Parser OS version: ", version)

        test1=NXShowL2RouteEvpnMacIpAll() # create instance of parser class
        result = test1.parse(output=test_message, pversion=version)
#
# Verify parser dictionary generated
#
        print("\n%%% Parser result:\n", result)

        assert (result) == {'nve_peer_mac_ip': {'0001.abba.edda': {'peer-ip': '204.1.1.1', 'vni': 1001, 'mac': '0001.abba.edda', 'host-ip': '5.1.1.1', 'type': 'MACIP', 'producer': 'BGP', 'flags': '--'}, '0002.abba.edda': {'peer-ip': '201.1.1.1', 'vni': 1001, 'mac': '0002.abba.edda', 'host-ip': '2.2.2.2', 'type': 'MACIP', 'producer': 'BGP', 'flags': '--'}}}

    
#
# Create CLIPs facts to verify that the ddr-facts definition for the parser works correctly
#
        show_and_assert_fact(env, "nve-peer-mac-ip", fact_list[0], result)
        print("\n*********************** CLIPs FACTs *****************************")

        expected_facts = [
    '(nve-peer-mac-ip (device "") (peer-ip "204.1.1.1") (vni 1001) (mac "0001.abba.edda") (host-ip "5.1.1.1") (type "MACIP") (producer "BGP") (flags "--"))\n', 
    '(nve-peer-mac-ip (device "") (peer-ip "201.1.1.1") (vni 1001) (mac "0002.abba.edda") (host-ip "2.2.2.2") (type "MACIP") (producer "BGP") (flags "--"))\n']
        i = 0
#
# Redirect sys.stdout to convert the clips fact object to a string
# Verify that the expected facts are present in the clips knowledge base
#
        for fact in env.facts():
            buffer = StringIO()
            sys.stdout = buffer
            print(fact)
            fact_read = buffer.getvalue()
            sys.stdout = sys.__stdout__
            print("fact_read: ", fact_read)
            assert fact_read == expected_facts[i]
            i = i + 1


def test_NXShowL2RouteEvpnMacAll():
    test_message = '''
Flags -(Rmac):Router MAC (Stt):Static (L):Local (R):Remote (V):vPC link 
(Dup):Duplicate (Spl):Split (Rcv):Recv(D):Del Pending (S):Stale (C):Clear
(Ps):Peer Sync (Ro):Re-Originated (Orp):Orphan 
Topology    Mac Address    Prod   Flags         Seq No     Next-Hops                              
----------- -------------- ------ ------------- ---------- ---------------------------------------
1001        0001.abba.edda BGP    Stt,SplRcv    0          204.1.1.1 (Label: 1001)                
1001        0002.abba.edda BGP    Stt,SplRcv    0          201.1.1.1 (Label: 1001)
    '''

    fact_list = [
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "NXShowL2RouteEvpnMacAll",
     "assert_fact_for_each_item_in": "nve_peer_mac",
     "protofact": {"template": "nve-peer-mac",
                                "slots": {"mac": "$",
                                          "peer-ip": "$+peer-ip",
                                          "type": "$+type",
                                          "vni": "$+vni",
                                          "producer": "$+producer",
                                          "flags": "$+flags"
                                          },
                                "types": {"mac": "str",
                                          "peer-ip": "str",
                                          "type": "str",                                
                                          "vni": "int",
                                          "producer": "str",
                                          "flags": "str"                                           
                                          }
                  }
    }]
#
# Initialize the CLIPS environment and load the FACT templates for the test
#
    try:
        env = clips.Environment()
        env.load("NXShowL2RouteEvpnMacAll_rules.clp")
    except Exception as e:
        print("&&&& Exception loading CLIPS: " + str(e))

    for version in ['9.3(6)', '9.3(12)', '10.2(1)', '10.4(1)']:
        print("***** Test NXShowL2RouteEvpnMacAll Parser OS version: ", version)

        test1=NXShowL2RouteEvpnMacAll() # create instance of parser class
        result = test1.parse(output=test_message)
#
# Verify parser dictionary generated
#
        print("\n%%% Parser result:\n", result)

        assert (result) == {'nve_peer_mac': {'0001.abba.edda': {'vni': 1001, 'peer-ip': '204.1.1.1', 'type': 'MAC', 'producer': 'BGP', 'flags': 'Stt,SplRcv', 'mac': '0001.abba.edda'}, '0002.abba.edda': {'vni': 1001, 'peer-ip': '201.1.1.1', 'type': 'MAC', 'producer': 'BGP', 'flags': 'Stt,SplRcv', 'mac': '0002.abba.edda'}}}   
#
# Create CLIPs facts to verify that the ddr-facts definition for the parser works correctly
#
        show_and_assert_fact(env, "nve-peer-mac", fact_list[0], result)
        print("\n*********************** CLIPs FACTs *****************************")

        expected_facts = ['(nve-peer-mac (device "") (peer-ip "204.1.1.1") (mac "0001.abba.edda") (type "MAC") (vni 1001) (producer "BGP") (flags "Stt,SplRcv"))\n', '(nve-peer-mac (device "") (peer-ip "201.1.1.1") (mac "0002.abba.edda") (type "MAC") (vni 1001) (producer "BGP") (flags "Stt,SplRcv"))\n']
        i = 0
#
# Redirect sys.stdout to convert the clips fact object to a string
# Verify that the expected facts are present in the clips knowledge base
#
        for fact in env.facts():
            buffer = StringIO()
            sys.stdout = buffer
            print(fact)
            fact_read = buffer.getvalue()
            sys.stdout = sys.__stdout__
            print("fact_read: ", fact_read)
            assert fact_read == expected_facts[i]
            i = i + 1

def test_NXShowBgpL2vpnEvpnRT3():

    test_message = '''
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
    '''

    instance_example='''{'route_distinguisher': {'201.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88', 'imported': '204.1.1.1:33769:[3]:[0]:[32]:[204.1.1.1]/88', 'path': 'path_sourced_internal_to_AS', 'direction': 'internal', 'destinations': 0}, '204.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88', 'imported': '', 'path': 'path_locally_originated', 'direction': 'local', 'destinations': 0}}}'''

    fact_list = [
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "NXShowBgpL2vpnEvpnRT3",
     "assert_fact_for_each_item_in": "route_distinguisher",
     "protofact": {"template": "evpn-routes",
                                "slots": {"rd": "$",
                                          "route": "$+route",
                                          "route-type": "$+route_type",                                
                                          "vni": "$+vni",                                
                                          "imported": "$+imported",
                                          "path-type": "$+path_type",                               
                                          "destinations": "$+destinations" 
                                          },
                                "types": {"rd": "str",
                                          "route": "str",
                                          "route-type": "int",                                
                                          "vni": "int",                                
                                          "imported": "str",
                                          "path-type": "str",                               
                                          "destinations": "int" 
                                          }
                  }
    }]

#
# Initialize the CLIPS environment and load the FACT templates for the test
#
    try:
        env = clips.Environment()
        env.load("NXShowBgpL2vpnEvpnRT3_rules.clp")
    except Exception as e:
        print("&&&& Exception loading CLIPS: " + str(e))

    for version in ['9.3(6)', '9.3(12)', '10.2(1)', '10.4(1)']:
        print("***** Test NXShowBgpL2vpnEvpnRT3 Parser OS version: ", version)

        test1=NXShowBgpL2vpnEvpnRT3() # create instance of parser class
        result = test1.parse(output=test_message, pversion=version)
#
# Verify parser dictionary generated
#
        print("\n%%% Parser result:\n", result)

        assert (result) == {'route_distinguisher': {'201.1.1.1:33769': {'route': '[3]:[0]:[32]:[204.1.1.1]/88', 'vni': 1002, 'imported': '', 'path_type': 'internal', 'destinations': 0, 'route_type': 3}}}   
#
# Create CLIPs facts to verify that the ddr-facts definition for the parser works correctly
#
        show_and_assert_fact(env, "evpn-foutes", fact_list[0], result)
        print("\n*********************** CLIPs FACTs *****************************")

        expected_facts = ['(evpn-routes (device "") (rd "201.1.1.1:33769") (route "[3]:[0]:[32]:[204.1.1.1]/88") (route-type 3) (vni 1002) (imported "") (path-type "internal") (destinations 0))\n']
        i = 0
#
# Redirect sys.stdout to convert the clips fact object to a string
# Verify that the expected facts are present in the clips knowledge base
#
        for fact in env.facts():
            buffer = StringIO()
            sys.stdout = buffer
            print(fact)
            fact_read = buffer.getvalue()
            sys.stdout = sys.__stdout__
            print("fact_read: ", fact_read)
            assert fact_read == expected_facts[i]
            i = i + 1

def test_NXShowBgpL2vpnEvpnRT2():

    test_message = '''
BGP routing table information for VRF default, address family L2VPN EVPN
Route Distinguisher: 201.1.1.1:33768    (L2VNI 1001)
BGP routing table entry for [2]:[0]:[0]:[48]:[0001.abba.edda]:[32]:[5.1.1.1]/272, version 171
Paths: (1 available, best #1)
Flags: (0x000212) (high32 00000000) on xmit-list, is in l2rib/evpn, is not in HW
Multipath: iBGP

  Advertised path-id 1
  Path type: internal, path is valid, is best path, no labeled nexthop, in rib
             Imported from 204.1.1.1:33768:[2]:[0]:[0]:[48]:[0001.abba.edda]:[32]:[5.1.1.1]/272 
  AS-Path: NONE, path sourced internal to AS
    204.1.1.1 (metric 0) from 204.1.1.2 (204.1.1.2)
      Origin IGP, MED not set, localpref 100, weight 0
      Received label 1001 10001
      Extcommunity: RT:1000:1001 RT:1000:10001 ENCAP:8 Router MAC:88f0.31bf.cbff
      Originator: 204.1.1.1 Cluster list: 204.1.1.2 

  Path-id 1 not advertised to any peer
    '''

    instance_example='''{'route_distinguisher': {'201.1.1.1:33768': {'route': '[2]:[0]:[0]:[48]:[0001.abba.edda]:[0]:[0.0.0.0]/216', 'vni': 1001, 'imported': '', 'path_type': 'internal', 'destinations': 0, 'route_type': 3}}}'''

    fact_list = [
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "NXShowBgpL2vpnEvpnRT2",
     "assert_fact_for_each_item_in": "route_distinguisher",
     "protofact": {"template": "evpn-routes",
                                "slots": {"rd": "$",
                                          "route": "$+route",
                                          "route-type": "$+route_type",                                
                                          "vni": "$+vni",                                
                                          "imported": "$+imported",
                                          "path-type": "$+path_type",                               
                                          "destinations": "$+destinations" 
                                          },
                                "types": {"rd": "str",
                                          "route": "str",
                                          "route-type": "int",                                
                                          "vni": "int",                                
                                          "imported": "str",
                                          "path-type": "str",                               
                                          "destinations": "int" 
                                          }
                  }
    }]

#
# Initialize the CLIPS environment and load the FACT templates for the test
#
    try:
        env = clips.Environment()
        env.load("NXShowBgpL2vpnEvpnRT2_rules.clp")
    except Exception as e:
        print("&&&& Exception loading CLIPS: " + str(e))

    for version in ['9.3(6)', '9.3(12)', '10.2(1)', '10.4(1)']:
        print("***** Test NXShowBgpL2vpnEvpnRT2 Parser OS version: ", version)
        test1=NXShowBgpL2vpnEvpnRT2() # create instance of parser class
        result = test1.parse(output=test_message, pversion=version)
#
# Verify parser dictionary generated
#
        print("\n%%% Parser result:\n", result)

        assert (result) == {'route_distinguisher': {'201.1.1.1:33768': {'route': '[2]:[0]:[0]:[48]:[0001.abba.edda]:[32]:[5.1.1.1]/272', 'vni': 1001, 'imported': '', 'path_type': 'internal', 'destinations': 0, 'route_type': 2}}}  
#
# Create CLIPs facts to verify that the ddr-facts definition for the parser works correctly
#
        show_and_assert_fact(env, "evpn-routes", fact_list[0], result)
        print("\n*********************** CLIPs FACTs *****************************")

        expected_facts = ['(evpn-routes (device "") (rd "201.1.1.1:33768") (route "[2]:[0]:[0]:[48]:[0001.abba.edda]:[32]:[5.1.1.1]/272") (route-type 2) (vni 1001) (imported "") (path-type "internal") (destinations 0))\n']
        i = 0
#
# Redirect sys.stdout to convert the clips fact object to a string
# Verify that the expected facts are present in the clips knowledge base
#
        for fact in env.facts():
            buffer = StringIO()
            sys.stdout = buffer
            print(fact)
            fact_read = buffer.getvalue()
            sys.stdout = sys.__stdout__
            print("fact_read: ", fact_read)
            assert fact_read == expected_facts[i]
            i = i + 1
            
def test_NXShowNveInternalPeer():

    test_message_9_3 = '''2023 Feb 13 17:54:49.625302: E_DEBUG    nve [5065]: [Peer: 204.1.1.1] [nve_process_peer_add_req:692] Peer add request on VNI: 1002, egressVni: 1002 rnhMAC: 00:00:00:00:00:00 learnSrc: BGP flags: FABRIC  nveIf: nve1 tunnelID: 0x0 

          2023 Feb 13 17:54:49.625088: E_DEBUG    nve [5065]: [Peer: 204.1.1.1] [nve_handle_bgp_peer_msg:5701] ADD peer, VNI: 1002 MAC: 00:00:00:00:00:00 underlayVRF: 1 encap: 1 flags: 0 tunnelID: 0x0 egressVNI: 1002 peerNode: no ifNode: yes vniReady: yes [L2-vni-rep-mode-ready]
    '''

    test_message_10_4 = '''2023-03-30T14:07:01.292307000+00:00 [M 27] [nve] E_DEBUG [nve_cmn_l2rib_send_all_peer_obj:675] Replaying all peer objects to L2RIB
        
           2023-03-30T14:08:39.035656000+00:00 [M 27] [nve] E_DEBUG [Interface: port-channel213] [nve_handle_l3_proto_state_change:3816] L3 protocol state change portState: up'''
    test_message_10_2 = '''[26] 2023 Jul 03 15:23:38.165984 [nve] E_DEBUG    [23936]:[Peer: 204.1.1.1] [nve_process_peer_add_req:696] Peer add request on VNI: 1002, egressVni: 1002 rnhMAC: 00:00:00:00:00:00 learnSrc: BGP-IMET flags: FABRIC  nveIf: nve1 tunnelID: 0x0'''
        
    fact_list = [
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "NXShowNveInternalPeer",
     "assert_fact_for_each_item_in": "event_record",
     "protofact": {"template": "evpn-log-peer",
                                "slots": {"timestamp": "$",
                                          "component" : "$+component",
                                          "type" : "$+type",
                                          "peer" : "$+peer",
                                          "interface" : "$+interface",
                                          "function" : "$+function",
                                          "line-num" : "$+line_num",
                                          "message" : "$+message",                                        
                                          "version" : "$+version"                                        
                                          },
                                "types": {"timestamp": "str",
                                          "component" : "$str",
                                          "type" : "str",
                                          "peer" : "str",
                                          "interface" : "str",
                                          "function" : "str",
                                          "line-num" : "int",
                                          "message" : "str",                                        
                                          "version" : "str"                                        
                                          }
                  }
    }]

#
# Initialize the CLIPS environment and load the FACT templates for the test
#
    try:
        env = clips.Environment()
        env.load("NXShowNveInternalPeer_rules.clp")
    except Exception as e:
        print("&&&& Exception loading CLIPS: " + str(e))

    for version in ['9.3(6)', '9.3(12)', '10.2(1)']:
        print("***** Test NXShowNveInternalPeer Parser OS version: ", version)
        for version in ['9.3(6)', '9.3(12)']:
            test1=NXShowNveInternalPeer() # create instance of parser class
            result = test1.parse(output=test_message_9_3, pversion=version)
        for version in ['10.2(1)']:
            test1=NXShowNveInternalPeer() # create instance of parser class
            result = test1.parse(output=test_message_10_2, pversion=version)
#PVH        for version in ['10.4(1)']:
#            test1=NXShowNveInternalPeer() # create instance of parser class
#            result = test1.parse(output=test_message_10_4, pversion=version)
#
# Verify parser dictionary generated
#
        print("\n%%% Parser result:\n", result)

        assert (result) == {'event_record': {'2023 Jul 03 15:23:38.165984': {'component': 'nve', 'type': 'peer', 'peer': '204.1.1.1', 'interface': 'none', 'function': 'nve_process_peer_add_req', 'line_num': 696, 'message': 'Peer add request on VNI: 1002, egressVni: 1002 rnhMAC: 00:00:00:00:00:00 learnSrc: BGP-IMET flags: FABRIC  nveIf: nve1 tunnelID: 0x0', 'version': '10.2(1)'}}}  
#
# Create CLIPs facts to verify that the ddr-facts definition for the parser works correctly
#
        show_and_assert_fact(env, "evpn-log-peer", fact_list[0], result)
        print("\n*********************** CLIPs FACTs *****************************")

        expected_facts = ['(evpn-log-peer (timestamp "2023_Jul_03_15:23:38.165984") (device "") (component "nve") (type "peer") (peer "204.1.1.1") (interface "none") (function "nve_process_peer_add_req") (line-num 696) (message "Peer_add_request_on_VNI:_1002,_egressVni:_1002_rnhMAC:_00:00:00:00:00:00_learnSrc:_BGP-IMET_flags:_FABRIC__nveIf:_nve1_tunnelID:_0x0") (version "10.2(1)"))\n']
        i = 0
#
# Redirect sys.stdout to convert the clips fact object to a string
# Verify that the expected facts are present in the clips knowledge base
#
        for fact in env.facts():
            buffer = StringIO()
            sys.stdout = buffer
            print(fact)
            fact_read = buffer.getvalue()
            sys.stdout = sys.__stdout__
            print("fact_read: ", fact_read)
            assert fact_read == expected_facts[i]
            i = i + 1
            
def test_NXShowNveInternalTrigger():

    test_message_9_3 = '''2023 Feb 13 17:54:44.468645: E_DEBUG    nve [5065]: [nve_populate_urib_update_rnh_batch:357] nve_populate_urib_update_rnh_batch: ADD peer:204.1.1.1 vrf:1'''

    test_message_10_4 = '''2023-03-30T14:07:01.292434000+00:00 [M 27] [nve] E_DEBUG [nve_l2rib_notify_eoc:1568] Sent EOC for obj: 5
           2023-03-30T14:07:01.292321000+00:00 [M 27] [nve] E_DEBUG [nve_l2rib_send_all_peer_obj:1158] Adding all peer related objects to L2RIB'''
           
    test_message_10_2 = '''[2] 2023 Jul 03 15:23:38.180349 [nve] E_DEBUG    [23936]:[nve_populate_urib_update_rnh_batch:436]  nve_populate_urib_update_rnh_batch: ADD peer:204.1.1.1 vrf:1'''
        
    fact_list = [
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "NXShowNveInternalTrigger",
     "assert_fact_for_each_item_in": "event_record",
     "protofact": {"template": "evpn-log-trigger",
                                "slots": {"timestamp": "$",
                                          "component" : "$+component",
                                          "type" : "$+type",
                                          "function" : "$+function",
                                          "line-num" : "$+line_num",
                                          "message" : "$+message",                                        
                                          "version" : "$+version"                                        
                                          },
                                "types": {"timestamp": "str",
                                          "component" : "$str",
                                          "type" : "str",
                                          "function" : "str",
                                          "line-num" : "int",
                                          "message" : "str",                                        
                                          "version" : "str"                                        
                                          }
                  }
    }]

#
# Initialize the CLIPS environment and load the FACT templates for the test
#
    try:
        env = clips.Environment()
        env.load("NXShowNveInternalTrigger_rules.clp")
    except Exception as e:
        print("&&&& Exception loading CLIPS: " + str(e))

    for version in ['9.3(6)', '9.3(12)', '10.2(1)']:
        print("***** Test NXShowNveInternalTrigger Parser OS version: ", version)
        for version in ['9.3(6)', '9.3(12)']:
            test1=NXShowNveInternalTrigger() # create instance of parser class
            result = test1.parse(output=test_message_9_3, pversion=version)
        for version in ['10.2(1)']:
            test1=NXShowNveInternalTrigger() # create instance of parser class
            result = test1.parse(output=test_message_10_2, pversion=version)
#PVH        for version in ['10.4(1)']:
#            test1=NXShowNveInternalTrigger() # create instance of parser class
#            result = test1.parse(output=test_message_10_4, pversion=version)
#
# Verify parser dictionary generated
#
        print("\n%%% Parser result:\n", result)

        assert (result) == {'event_record': {'2023 Jul 03 15:23:38.180349': {'component': 'nve', 'type': 'trigger', 'function': 'nve_populate_urib_update_rnh_batch', 'line_num': 436, 'message': 'nve_populate_urib_update_rnh_batch: ADD peer:204.1.1.1 vrf:1', 'version': '10.2(1)'}}}  
#
# Create CLIPs facts to verify that the ddr-facts definition for the parser works correctly
#
        show_and_assert_fact(env, "evpn-log-trigger", fact_list[0], result)
        print("\n*********************** CLIPs FACTs *****************************")

        expected_facts = ['(evpn-log-trigger (timestamp "2023_Jul_03_15:23:38.180349") (device "") (component "nve") (type "trigger") (function "nve_populate_urib_update_rnh_batch") (line-num 436) (message "nve_populate_urib_update_rnh_batch:_ADD_peer:204.1.1.1_vrf:1") (version "10.2(1)"))\n']
        i = 0
#
# Redirect sys.stdout to convert the clips fact object to a string
# Verify that the expected facts are present in the clips knowledge base
#
        for fact in env.facts():
            buffer = StringIO()
            sys.stdout = buffer
            print(fact)
            fact_read = buffer.getvalue()
            sys.stdout = sys.__stdout__
            print("fact_read: ", fact_read)
            assert fact_read == expected_facts[i]
            i = i + 1
            
def test_NXShowNveInternalVni():

    test_message_9_3 = '''2023 Jun 15 19:35:47.086062: E_DEBUG    nve [5050]: [VNI: 1002] [nve_l2rib_message_cb:504] Received IMET notification for peerIP: 204.1.1.1, BD: 1002 Operation: ADD, imetFlag: NVE_CP_PEER_FLAGS_FABRIC_SIDE_PEER, multisiteVNIState: 0, egressVNI: 1002'''

    test_message_10_4 = '''  '''
           
    test_message_10_2 = '''[14] 2023 Jul 03 15:23:38.165449 [nve] E_DEBUG    [23936]:[VNI: 1002] [nve_l2rib_message_cb:505] Received IMET notification for peerIP: 204.1.1.1, BD: 1002 Operation'''
        
    fact_list = [
    {"fact_type": "show_and_assert",
     "device": "DUMMY",
     "genie_parser": "NXShowNveInternalVni",
     "assert_fact_for_each_item_in": "event_record",
     "protofact": {"template": "evpn-log-vni",
                                "slots": {"timestamp": "$",
                                          "component" : "$+component",
                                          "type" : "$+type",
                                          "function" : "$+function",
                                          "vni" : "$+vni",
                                          "line-num" : "$+line_num",
                                          "message" : "$+message",                                        
                                          "version" : "$+version"                                        
                                          },
                                "types": {"timestamp": "str",
                                          "component" : "$str",
                                          "type" : "str",
                                          "vni" : "int",
                                          "function" : "str",
                                          "line-num" : "int",
                                          "message" : "str",                                        
                                          "version" : "str"                                        
                                          }
                  }
    }]

#
# Initialize the CLIPS environment and load the FACT templates for the test
#ls
    try:
        env = clips.Environment()
        env.load("NXShowNveInternalVni_rules.clp")
    except Exception as e:
        print("&&&& Exception loading CLIPS: " + str(e))

    for version in ['9.3(6)', '9.3(12)', '10.2(1)']:
        print("***** Test NXShowNveInternalVni Parser OS version: ", version)
        for version in ['9.3(6)', '9.3(12)']:
            test1=NXShowNveInternalVni() # create instance of parser class
            result = test1.parse(output=test_message_9_3, pversion=version)
        for version in ['10.2(1)']:
            test1=NXShowNveInternalVni() # create instance of parser class
            result = test1.parse(output=test_message_10_2, pversion=version)
#PVH        for version in ['10.4(1)']:
#            test1=NXShowNveInternalVni() # create instance of parser class
#            result = test1.parse(output=test_message_10_4, pversion=version)
#
# Verify parser dictionary generated
#
        print("\n%%% Parser result:\n", result)

        assert (result) == {'event_record': {'2023 Jul 03 15:23:38.165449': {'component': 'nve', 'type': 'vni', 'vni': 1002, 'function': 'nve_l2rib_message_cb', 'line_num': 505, 'message': 'Received IMET notification for peerIP: 204.1.1.1, BD: 1002 Operation', 'version': '10.2(1)'}}}  
#
# Create CLIPs facts to verify that the ddr-facts definition for the parser works correctly
#
        show_and_assert_fact(env, "evpn-log-vni", fact_list[0], result)
        print("\n*********************** CLIPs FACTs *****************************")

        expected_facts = ['(evpn-log-vni (timestamp "2023_Jul_03_15:23:38.165449") (device "") (component "nve") (vni 1002) (type "vni") (function "nve_l2rib_message_cb") (line-num 505) (message "Received_IMET_notification_for_peerIP:_204.1.1.1,_BD:_1002_Operation") (version "10.2(1)"))\n']
        i = 0
#
# Redirect sys.stdout to convert the clips fact object to a string
# Verify that the expected facts are present in the clips knowledge base
#
        for fact in env.facts():
            buffer = StringIO()
            sys.stdout = buffer
            print(fact)
            fact_read = buffer.getvalue()
            sys.stdout = sys.__stdout__
            print("fact_read: ", fact_read)
            assert fact_read == expected_facts[i]
            i = i + 1
