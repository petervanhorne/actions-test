(deftemplate evpn-log-event ; FACTs created from evpn event-logs
;
;  show nve internal event-history events;
;
  (slot timestamp (type STRING)) ; timestamp generated when the fact is created
  (slot device (type STRING)) ; Device collecting the data  
  (slot component (type STRING)) ; Component parsed from the show command 
  (slot type (type STRING)) ; Type of event log fact "event" 
  (slot function (type STRING)) ; Feature code function that generated the log message 
  (slot line-num (type INTEGER)) ; Line number in the feature module 
  (slot message (type STRING)) ; Text message in log which may be used to extract additional data 
  (slot version (type STRING)) ; OS Version on the device used to select options for parsing different log formats 
)
