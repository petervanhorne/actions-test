(deftemplate evpn-log-trigger ; FACTs created from evpn event trigger logs
;
;  show nve internal event-history triggers
;
;  2023 Jun 15 19:35:00.528915: E_DEBUG    nve [5050]: nve_populate_urib_update_rnh_batch: ADD peer:204.1.1.1 vrf:1
;
;    (evpn-log-trigger (timestamp "2023 Jul 03 15:23:38.180349") (device "leaf1") (component "nve") (type "trigger") (function "nve_populate_urib_update_rnh_batch") (line-num 436) (message "nve_populate_urib_update_rnh_batch: ADD peer:204.1.1.1 vrf:1") (version "10.2(1)"))
;
  (slot timestamp (type STRING)) ; timestamp generated when the fact is created
  (slot device (type STRING)) ; Device collecting the data  
  (slot component (type STRING)) ; Component parsed from the show command
  (slot type (type STRING)) ; Type of event log fact "trigger" 
  (slot function (type STRING)) ; Feature code function that generated the log message 
  (slot line-num (type INTEGER)) ; Line number in the feature module 
  (slot message (type STRING)) ; Text message in log which may be used to extract additional data 
  (slot version (type STRING)) ; OS Version on the device used to select options for parsing different log formats 
)
