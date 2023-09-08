(deftemplate evpn-routes ; Facts generated from show bgp l2vpn evpn
  (slot device (type STRING)) ; Device executing the show commands
  (slot rd (type STRING)) ; RD received by device receiving the BGP peer advertisement
  (slot route (type STRING)) ; Route information sent or received.  The route can be type [3] or type [2]
  (slot route-type (type INTEGER)) ; 2 or 3 indicating the route type
  (slot vni (type INTEGER)) ; vni id contained in the route message
  (slot imported (type STRING)) ; Route data imported by the receiving peer
  (slot path-type (type STRING)) ; "local" indicates the device originated the route, "internal" indicates received by BGP
  (slot destinations (type INTEGER)) ; Number of destinations in the show command output
)

