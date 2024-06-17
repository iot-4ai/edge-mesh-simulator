### Basic requirements
- fixed position node instances using a 6-vector x, y, z and orientation x', y', z'
- node radio type (BLE, 5G, others)
- node power source
- manage a fleet of nodes
- manage communications between nodes (A, B) and (B, A)
- log communication data by transmitter, receiver (power output, angle of departure, angle of arrival, RSSI)
- fleet will have at least 2 gateway nodes which are not transient part of fleet
- variable node positon & orientation
- manage a fleet of moving nodes (which are observed by the fixed nodes)
- node attenuation relative to default
- chaos
- each message between nodes can be altered by noise and attentuation
	- material properties: absorption, reflection, refraction?
- extra nodes may be injected and try to particpate in the networking protocols—should get rejected
- each fixed node instance needs to recognize packets for:
	- provisioning at "factory"
	- re-provisioning via OTA update
- using zero trust
- nodes need to be able to save state to "get smarter" over time by 1:1 routing instead of broadcast
- nodes to to specify "angle of departure" when hardware is available
- broadcast with TTL in hops or seconds
- nodes need to provide 6 or more "sensors" and 6 or more "control settings"
- over time, network traffic varies
- (re)provisioning OTA
- mesh discovery
- beamforming
- sensor telemetry
- node status
- control data to "control settings"
- responses to "moving nodes"