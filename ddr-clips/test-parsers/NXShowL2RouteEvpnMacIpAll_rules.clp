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

