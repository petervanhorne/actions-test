(deftemplate nve-peer-imet ; FACTs created from parsing "show l2route evpn imet all"
;
;  Topology ID VNI         Prod  IP Addr                                 Flags  
;  ----------- ----------- ----- --------------------------------------- -------
;  1002        1002        BGP   204.1.1.1                               -      
;  1002        1002        VXLAN 201.1.1.1                               -      
;
;    (nve-peer-imet (device "leaf1") (nve-peer "201.1.1.1") (type "IMET") (vni 1002) (producer "VXLAN"))
;
  (slot device (type STRING)) ; Device running the show command
  (slot nve-peer (type STRING)) ; ip address of the peering device
  (slot type (type STRING)) ; peer type "IMET"
  (slot vni (type INTEGER)) ; vni id
  (slot producer (type STRING)) ; Infrastructure that produced the l2route "VXLAN" or "IMET"
)
