(deftemplate evpn-log-peer ; FACTs created from evpn event peer logs
;
;  show nve internal event-history peer
;
;  2023 Jun 15 19:35:47.086304: E_DEBUG    nve [5050]: [Peer: 204.1.1.1] [nve_pi_peer_add:138] Peer ADD request - peerID: 1, VNI: 1002, nveIf: nve1, learnSrc: BGP-IMET, disableMacLearning: Yes, flags: NVE_CP_PEER_FLAGS_FABRIC_SIDE_PEER, egressVni: 1002 
;
;    (evpn-log-peer (timestamp "2023 Jul 03 15:23:38.16574") (device "leaf1") (component "nve") (type "peer") (peer "204.1.1.1") (interface "none") (function "nve_pi_peer_add") (line-num 138) (message "Peer ADD request - peerID: 0, VNI: 1002, nveIf: nve1, learnSrc: BGP-IMET, disableMacLearning: Yes, flags: NVE_CP_PEER_FLAGS_FABRIC_SIDE_PEER, egressVni: 1002") (version "10.2(1)"))
;
  (slot timestamp (type STRING)) ; timestamp generated when the fact is created
  (slot device (type STRING)) ; Device collecting the data 
  (slot component (type STRING)) ; Component parsed from the show command
  (slot type (type STRING)) ; Type of event log fact "peer"
  (slot peer (type STRING)) ; Peer ip address
  (slot interface (type STRING)) ; Interface if a port-channel is used
  (slot function (type STRING)) ; Feature code function that generated the log message
  (slot line-num (type INTEGER)) ; Line number in the feature module
  (slot message (type STRING)) ; Text message in log which may be used to extract additional data
  (slot version (type STRING)) ; OS Version on the device used to select options for parsing different log formats
)        

