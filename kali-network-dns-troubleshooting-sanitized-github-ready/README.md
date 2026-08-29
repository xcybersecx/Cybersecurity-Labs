# Kali Linux Network & DNS Troubleshooting

## Overview

While attempting to complete a vulnerability-scanning assignment using
OWASP ZAP, I encountered a network connectivity problem that prevented
my Kali Linux virtual machine from reaching external training targets.

The original objective was to use ZAP to examine deliberately vulnerable
applications including OWASP Juice Shop and Acunetix Test ASP.NET. Both
targets failed to load. What first looked like a ZAP or website problem
became a practical troubleshooting exercise involving Kali Linux,
VirtualBox networking, DHCP, routing and DNS.

I have kept the unsuccessful steps in this write-up because they were
part of identifying where the fault actually existed.

## Lab Environment

-   **Host OS:** Windows
-   **Virtualisation:** Oracle VirtualBox
-   **Guest OS:** Kali Linux
-   **Network interface:** `eth0`
-   **Security tool:** OWASP ZAP
-   **Training targets:** OWASP Juice Shop and Acunetix Test ASP.NET
-   **Initial VirtualBox network mode:** Bridged Adapter
-   **Temporary working network mode:** NAT

## 1. Initial ZAP Failure

I launched OWASP Juice Shop through ZAP's **Manual Explore** function
with the HUD enabled. ZAP eventually reported a name-resolution failure.

![ZAP showing the Juice Shop name-resolution
failure](images/01-zap-dns-failure.png)

*Recreated from lab evidence; identifying information sanitised.*

Because more than one remote training target had failed, I did not want
to assume that Juice Shop itself was responsible. I began testing the
network independently of ZAP.

## 2. Checking the Kali Network Interface

I used:

``` bash
ip addr
```

Earlier in the troubleshooting session, `eth0` was UP and had an IPv4
address on the local `192.168.1.x/24` network.

![Kali interface information during
troubleshooting](images/02-interface-ip-before-loss.png)

*Recreated from lab evidence; identifying information sanitised.*

I also used:

``` bash
ip route
```

to inspect the routing table and determine whether Kali had a default
gateway.

I tested the local gateway with:

``` bash
ping -c 4 192.168.1.1
```

and received all four replies. This showed that Kali could communicate
with the local gateway at that stage.

## 3. Separating Host, VM and Internet Problems

I tested the Windows host separately. At one point the Windows browser
also timed out, demonstrating that the initial outage was not specific
to Kali, VirtualBox, Firefox or ZAP.

After restarting the router, the Windows host regained internet access,
but Kali still did not work correctly. This meant there was now a
VM-specific problem to investigate as well.

## 4. NetworkManager Restart and Loss of the Route

I restarted NetworkManager:

``` bash
sudo systemctl restart NetworkManager
```

Afterward, `ip route` no longer showed the previous default route
through `eth0`.

![Routing table after the default route
disappeared](images/03-route-lost.png)

*Recreated from lab evidence; identifying information sanitised.*

I checked the interface again:

``` bash
ip addr
```

`eth0` still existed and was UP, but it no longer had its previous IPv4
address.

![eth0 present but without its previous IPv4
configuration](images/04-eth0-no-ip.png)

*Recreated from lab evidence; identifying information sanitised.*

This demonstrated an important distinction: **an interface can be UP
without having a usable IP configuration.**

## 5. DHCP / NetworkManager Investigation

I first tried:

``` bash
sudo dhclient eth0
```

but the system returned:

``` text
sudo: dhclient: command not found
```

I therefore continued through NetworkManager.

``` bash
nmcli device status
```

`nmcli` is the **NetworkManager Command-Line Interface**. It showed
`eth0` attempting to obtain an IP configuration and later becoming
disconnected.

![NetworkManager showing the Ethernet connection
state](images/05-networkmanager-dhcp.png)

*Recreated from lab evidence; identifying information sanitised.*

I checked the saved connection profiles:

``` bash
nmcli connection show
```

and confirmed that **Wired connection 1** still existed.

I then tried to activate it manually:

``` bash
nmcli connection up "Wired connection 1"
```

NetworkManager returned an IP-configuration failure.

![NetworkManager unable to reserve an IP
configuration](images/06-ip-configuration-failure.png)

*Recreated from lab evidence; identifying information sanitised.*

This pointed toward a DHCP/IP-configuration problem rather than a ZAP
problem.

## 6. Inspecting VirtualBox Networking

The Kali VM was configured with a **Bridged Adapter**.

![VirtualBox network settings showing Bridged Adapter
mode](images/07-virtualbox-bridged.png)

*Recreated from lab evidence; identifying information sanitised.*

In Bridged mode, the VM behaves more like a separate machine attached
directly to the physical LAN. During this session, Kali was failing to
obtain the required IP configuration in that mode.

For troubleshooting and for the immediate internet-based ZAP task, I
temporarily changed the VM from **Bridged Adapter** to **NAT**.

After the change, I ran:

``` bash
nmcli device status
```

and `eth0` showed as connected.

![eth0 connected after moving the VM to
NAT](images/08-nat-connected.png)

*Recreated from lab evidence; identifying information sanitised.*

NAT does not make ZAP scan differently. It simply gives the Kali VM an
outbound path through VirtualBox and the host's internet connection.

For local VM-to-VM testing such as Metasploitable, I may use a different
network topology because direct reachability between the laboratory
machines has different requirements.

## 7. Verifying External IP Connectivity

I tested an external IP address:

``` bash
ping -c 4 8.8.8.8
```

This succeeded with:

``` text
4 packets transmitted
4 packets received
0% packet loss
```

![Successful external-IP connectivity
test](images/09-external-ip-success.png)

*Recreated from lab evidence; identifying information sanitised.*

This proved that Kali could now reach an external IP address.

However:

``` bash
ping -c 2 google.com
```

still returned:

``` text
Temporary failure in name resolution
```

This distinction was useful: **IP connectivity had returned, but
hostname resolution had not.**

## 8. Inspecting DNS Under NAT

I inspected the resolver configuration:

``` bash
cat /etc/resolv.conf
```

NetworkManager had generated:

``` text
nameserver 10.0.2.3
```

![Resolver configuration after switching to
NAT](images/10-nat-dns-resolver.png)

*Recreated from lab evidence; identifying information sanitised.*

Because direct external-IP connectivity worked while hostname resolution
failed, I configured the NetworkManager profile to ignore the
automatically supplied DNS setting and use Google's public DNS resolver:

``` bash
nmcli connection modify "Wired connection 1" ipv4.ignore-auto-dns yes ipv4.dns "8.8.8.8"
```

I then reactivated the connection:

``` bash
nmcli connection up "Wired connection 1"
```

NetworkManager reported:

``` text
Connection successfully activated
```

![NetworkManager confirming that the connection was
reactivated](images/11-connection-reactivated.png)

*Recreated from lab evidence; identifying information sanitised.*

## 9. Final DNS Verification

I tested hostname resolution again:

``` bash
ping -c 2 google.com
```

This time Kali resolved `google.com` to an IP address and received both
replies:

``` text
2 packets transmitted
2 packets received
0% packet loss
```

![Successful DNS resolution and connectivity
test](images/12-dns-resolution-success.png)

*Recreated from lab evidence; identifying information sanitised.*

This confirmed that both external IP connectivity and DNS resolution
were functioning again.

## Working Network Path

For the current internet-hosted ZAP task, the path can be represented
approximately as:

``` text
Firefox
   |
   v
OWASP ZAP
   |
   v
Kali Linux
   |
   v
VirtualBox NAT
   |
   v
Host Internet Connection
   |
   v
Internet
   |
   v
Authorised Training Target
```

## Commands Used

  -----------------------------------------------------------------------------
  Command                                   Purpose
  ----------------------------------------- -----------------------------------
  `ip addr`                                 Display interfaces and assigned IP
                                            addresses

  `ip route`                                Display the routing table and
                                            default gateway

  `ping -c 4 <IP>`                          Test network reachability using
                                            four packets

  `ping -c 2 google.com`                    Test hostname resolution and
                                            connectivity

  `cat /etc/resolv.conf`                    Display the current DNS resolver
                                            configuration

  `sudo systemctl restart NetworkManager`   Restart NetworkManager

  `nmcli device status`                     Show NetworkManager's view of
                                            network devices

  `nmcli connection show`                   Show saved NetworkManager
                                            connection profiles

  `nmcli connection up`                     Activate a NetworkManager
                                            connection

  `nmcli connection modify`                 Modify a NetworkManager connection
                                            profile
  -----------------------------------------------------------------------------

## What I Learned

The main lesson from this exercise was that **"the internet is not
working" is not a sufficiently precise diagnosis**.

A machine can have an active interface but no IP address; have an IP
address but no usable default route; reach its local gateway but not the
internet; or reach external IP addresses while still being unable to
resolve domain names.

I also learned why it is useful to test both an IP address and a
hostname:

``` bash
ping 8.8.8.8
```

tests reachability to an external IP without requiring DNS, whereas:

``` bash
ping google.com
```

requires DNS resolution first.

Therefore, a situation where `8.8.8.8` works but `google.com` fails is
useful evidence that DNS should be investigated.

Most importantly, I learned to troubleshoot in stages rather than
assuming that the application displaying the visible error is the source
of the problem. The original symptom appeared while I was using OWASP
ZAP, but ZAP was not ultimately the underlying cause.

## Privacy / Evidence Note

The images in this repository are **recreated evidence illustrations based on the real troubleshooting session**, not untouched screenshots. They preserve the commands, errors, sequence and technical observations needed for the report while removing or replacing identifying information such as device identifiers, MAC addresses, desktop details and other incidental information.

Private RFC1918 laboratory addresses are retained only where they are useful to explain the networking process; they are not public internet addresses.

## Status

**Resolved.**

Kali regained external network connectivity and DNS resolution, allowing
the OWASP ZAP vulnerability-scanning assignment to continue.
