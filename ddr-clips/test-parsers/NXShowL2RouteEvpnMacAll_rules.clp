   (deftemplate nve-peer-mac
     (slot device (type STRING)) ; Device running the show command
     (slot peer-ip (type STRING)) ; ip address of the peering device
     (slot mac (type STRING)) ; peer MAC address
     (slot type (type STRING)) ; peer type "MAC"
     (slot vni (type INTEGER)) ; Topology value from show command
     (slot producer (type STRING)) ; Infrastructure that produced the l2route "VXLAN" or "IMET"
     (slot flags (type STRING)) ; Flags from the show command
    )      

