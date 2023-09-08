(deftemplate evpn-log-vni ; FACTs created from evpn event vni logs
;
;  show nve internal event-history vni
;
;  2023 Jun 15 19:35:47.086062: E_DEBUG    nve [5050]: [VNI: 1002] [nve_l2rib_message_cb:504] Received IMET notification for peerIP: 204.1.1.1, BD: 1002 Operation: ADD, imetFlag: NVE_CP_PEER_FLAGS_FABRIC_SIDE_PEER, multisiteVNIState: 0, egressVNI: 1002 
;
;    (evpn-log-vni (timestamp "2023 Jul 03 15:23:38.165449") (device "leaf1") (component "nve") (vni 1002) (type "vni") (function "nve_l2rib_message_cb") (line-num 505) (message "Received IMET notification for peerIP: 204.1.1.1, BD: 1002 Operation: ADD, imetFlag: NVE_CP_PEER_FLAGS_FABRIC_SIDE_PEER, multisiteVNIState: 0, egressVNI: 1002") (version "10.2(1)"))
;
  (slot timestamp (type STRING)) ; timestamp generated when the fact is created
  (slot device (type STRING)) ; Device collecting the data  
  (slot component (type STRING)) ; Component parsed from the show command
  (slot vni (type INTEGER)) ; vni id in the log message
  (slot type (type STRING)) ; Type of event log fact "vni" 
  (slot function (type STRING)) ; Feature code function that generated the log message 
  (slot line-num (type INTEGER)) ; Line number in the feature module 
  (slot message (type STRING)) ; Text message in log which may be used to extract additional data 
  (slot version (type STRING))) ; OS Version on the device used to select options for parsing different log formats

