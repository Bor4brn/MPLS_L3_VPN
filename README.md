Here is the detailed explanation of the configuration from the NSO's official README file:

== MPLS Layer3 VPN Example

=== Example Overview

This example illustrates Layer3 VPNs in a service provider MPLS
network.

==== Example Network

The example network consists of Cisco ASR 9k and Juniper core
routers (P and PE) and Cisco IOS based CE routers.

image:network.jpg[]

The Layer3 VPN service configures the CE/PE routers for all endpoints
in the VPN with BGP as the CE/PE routing protocol. Layer2 connectivity
between CE and PE routers are expected to be done through a Layer2
ethernet access network, which is out of scope for this example.

The Layer3 VPN service includes VPN connectivity as well as bandwidth
and QOS parameters.

=== External Policies

This example makes use of two different external policies. The
external policies in this example are modelled in YANG and
stored in NCS but not as a part of the actual service data model.

Having policy information that can be referenced by many service
instances can be very powerful. Changes in the network topology or in
a QOS policy could now be done in one place. NCS can then redeploy all
affected service instances and reconfigure the network. This will be
shown later in this example.


==== Topology

The service configuration only has references to CE devices for the
end-points in the VPN. The service mapping logic reads from a simple
topology model that is configuration data in NCS, outside the
actual service model, and derives what other network devices to
configure.

The topology information has two parts. The first part lists
connections in the network and is used by the service mapping logic to
find out which PE router to configure for an endpoint.

The snippets below show the configuration output in the Cisco style
NCS CLI.

----
topology connection c0
 endpoint-1 device ce0 interface GigabitEthernet0/8 ip-address 192.168.1.1/30
 endpoint-2 device pe0 interface GigabitEthernet0/0/0/3 ip-address 192.168.1.2/30
 link-vlan 88
!
topology connection c1
 endpoint-1 device ce1 interface GigabitEthernet0/1 ip-address 192.168.1.5/30
 endpoint-2 device pe1 interface GigabitEthernet0/0/0/3 ip-address 192.168.1.6/30
 link-vlan 77
!
----

The second part lists devices for each role in the network and is in
this example only used to dynamically render a network map in the
Web UI.

----
topology role ce
 device [ ce0 ce1 ce2 ce3 ce4 ce5 ]
!
topology role pe
 device [ pe0 pe1 pe2 pe3 ]
!
----

==== QOS
QOS configuration in service provider networks is complex, and often
require a lot of different variations. It is also often desirable to be
able to deliver different levels of QOS. This example shows how a QOS
policy configuration can be stored in NCS and be referenced from VPN
service instances.

Three different levels of QOS policies are defined; GOLD, SILVER and
BRONZE with different queueing parameters.

----
qos qos-policy GOLD
 class BUSINESS-CRITICAL
  bandwidth-percentage 20
 !
 class MISSION-CRITICAL
  bandwidth-percentage 20
 !
 class REALTIME
  bandwidth-percentage 20
  priority
 !
!
qos qos-policy SILVER
 class BUSINESS-CRITICAL
  bandwidth-percentage 25
 !
 class MISSION-CRITICAL
  bandwidth-percentage 25
 !
 class REALTIME
  bandwidth-percentage 10
 !
----

Three different traffic classes are also defined with a DSCP value
that will be used inside the MPLS core network as well as default
rules that will match traffic to a class.

----
qos qos-class BUSINESS-CRITICAL
 dscp-value af21
 match-traffic ssh
  source-ip      any
  destination-ip any
  port-start     22
  port-end       22
  protocol       tcp
 !
!
qos qos-class MISSION-CRITICAL
 dscp-value af31
 match-traffic call-signaling
  source-ip      any
  destination-ip any
  port-start     5060
  port-end       5061
  protocol       tcp
 !
!
----

=== Running The Example in the CLI

Make sure you start clean, i.e. no old configuration data is present.
If you have been running this or some other example before, make sure
to stop any NCS or simulated network nodes (ncs-netsim) that you may have
running.  Output like 'connection refused (stop)' means no previous
NCS was running and 'DEVICE ce0 connection refused (stop)...' no
simulated network was running, which is good.

----
make stop clean all start
ncs_cli -u admin -C
----

This will setup the environment and start the simulated network.

==== VPN Service Configuration in the CLI

Before creating a new L3VPN service we must sync the configuration
from all network devices and then enter config mode.

----
devices sync-from
----

Lets start by configuring a VPN network.

----
config
top
!
vpn l3vpn volvo
 as-number 65101
 endpoint main-office
  ce-device    ce0
  ce-interface GigabitEthernet0/11
  ip-network   10.10.1.0/24
  bandwidth    12000000
 !
 endpoint branch-office1
  ce-device    ce1
  ce-interface GigabitEthernet0/11
  ip-network   10.7.7.0/24
  bandwidth    6000000
 !
 endpoint branch-office2
  ce-device    ce4
  ce-interface GigabitEthernet0/18
  ip-network   10.8.8.0/24
  bandwidth    300000
 !
 qos qos-policy GOLD
!
----

Before we send anything to the network, lets see what would be sent if
we committed.
----
commit dry-run outformat native
----

The output is too large to include here but as you can see each CE
device and the PE router it is connected to will be configured.

You can give the CLI pipe flag 'debug template' to get detailed
information on what configuration the output will effect, and how, the
result of XPath evaluations etc. A good way to figure out if the
template is doing something wrong:

----
commit dry-run | debug template
----

Lets commit the configuration to the network

----
commit
----
