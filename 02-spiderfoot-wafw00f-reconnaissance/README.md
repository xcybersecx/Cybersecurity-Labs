# SpiderFoot and WAFW00F Reconnaissance Practical

**Completed:** 4 August 2026  
**Environment:** Kali Linux and Metasploitable 2  
**Tools:** MySQL Client, SpiderFoot, WAFW00F, nslookup, dig, dnsrecon, dnsenum

## Overview

This practical expanded on my earlier Nmap reconnaissance work by introducing additional tools for service enumeration, OSINT, web application firewall detection and DNS reconnaissance.

The exercise helped me understand that reconnaissance is not performed using a single tool.

Different tools answer different questions.

For example:

- **Nmap:** What ports and services are exposed?
- **MySQL client:** What information can be obtained directly from an exposed database service?
- **SpiderFoot:** What information can be gathered and correlated automatically?
- **WAFW00F:** Is a web application protected by a recognised Web Application Firewall?
- **nslookup / dig:** What DNS information can be queried?
- **dnsrecon / dnsenum:** What additional DNS infrastructure can be enumerated?

The Metasploitable 2 machine was used as the authorised laboratory target.

For privacy, its original local IP address has been replaced with `<TARGET_IP>` in this public write-up.

---

# 1. MySQL Enumeration

Nmap had previously identified MySQL running on TCP port 3306.

The objective was to determine whether the database service was accessible and what information could be obtained from it.

## Initial Connection

An initial connection attempt produced a TLS/SSL compatibility error:

```text
ERROR 2026 (HY000):
TLS/SSL error: wrong version number
```

Because Metasploitable contains an old MySQL implementation, I retried the connection without SSL:

```bash
mysql --skip-ssl -h <TARGET_IP> -u root
```

The connection succeeded.

## Enumerating Databases

I listed the available databases using:

```sql
SHOW DATABASES;
```

Databases returned included:

```text
information_schema
dvwa
metasploit
mysql
owasp10
tikiwiki
tikiwiki195
```

This showed that several deliberately vulnerable applications on the machine were backed by databases accessible through the MySQL service.

---

# 2. Identifying the Database User

I checked how the client was connected using:

```sql
SELECT USER();
```

The result identified the connecting user and source host.

I then checked the account MySQL was actually using for privilege evaluation:

```sql
SELECT CURRENT_USER();
```

The result was:

```text
root@%
```

## Interpretation

The `%` host component indicates that this MySQL account was configured to match connections from any host rather than being limited to a specific machine.

Combined with use of the `root` account, this represented an unnecessarily permissive database configuration within the intentionally vulnerable lab environment.

## What I Learned

`USER()` and `CURRENT_USER()` are related but not identical.

- `USER()` shows how the client presented itself to MySQL.
- `CURRENT_USER()` shows the account MySQL matched for authentication and privilege purposes.

This was my first practical introduction to the difference.

---

# 3. Exiting MySQL

The session could be closed using:

```sql
exit;
```

or:

```sql
quit;
```

---

# 4. SpiderFoot Reconnaissance

SpiderFoot is an automated reconnaissance and OSINT framework.

It can collect and correlate information from many different sources, including information relating to:

- IP addresses
- domains
- DNS
- open ports
- service banners
- WHOIS data
- email addresses
- co-hosted domains
- internet exposure
- technology information

## Starting SpiderFoot

I first reviewed the available options:

```bash
spiderfoot -h
```

I then started the local SpiderFoot web interface:

```bash
spiderfoot -l 127.0.0.1:5001
```

The interface was accessed in the browser at:

```text
http://127.0.0.1:5001
```

A scan was created against the authorised Metasploitable target.

---

# 5. SpiderFoot Results

SpiderFoot identified several open TCP ports that had previously been discovered using Nmap.

Examples included:

| Port | Service |
|---:|---|
| 21 | FTP |
| 22 | SSH |
| 23 | Telnet |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 111 | rpcbind |
| 139 | NetBIOS / SMB |
| 445 | SMB |
| 512 | rexec / rsh |
| 513 | rlogin |
| 3306 | MySQL |
| 5432 | PostgreSQL |
| 5900 | VNC |

## Corroborating Findings

One of the most useful lessons from this stage was seeing a second tool independently identify many of the same exposed services that Nmap had already found.

This helped demonstrate the value of corroboration.

A finding observed by more than one reconnaissance method can give greater confidence that the underlying information is accurate.

---

# 6. What SpiderFoot Added

SpiderFoot did more than identify ports.

Depending on the modules and available data sources, it also attempted to gather information such as:

- port banners
- IP information
- geographic information
- WHOIS data
- co-hosted domains
- domain relationships
- email-related information

Some online SpiderFoot modules produced timeout errors during the exercise.

These appeared to be related to internet connectivity or external services rather than failure of the local reconnaissance process.

## What I Learned

Nmap and SpiderFoot overlap in some areas, but they are not the same type of tool.

### Nmap

Primarily focuses on network discovery and service enumeration.

It helps answer:

**What hosts, ports and services are reachable?**

### SpiderFoot

Automates collection and correlation across a much broader range of reconnaissance and OSINT sources.

It helps answer:

**What additional information can be gathered and connected about this target?**

---

# 7. WAFW00F

WAFW00F is a tool used to identify whether a website appears to be protected by a Web Application Firewall.

A Web Application Firewall, or WAF, monitors and filters HTTP/HTTPS traffic reaching web applications.

Depending on the product and configuration, a WAF may help detect or block attacks such as:

- SQL injection
- Cross-Site Scripting
- malicious HTTP requests
- automated abuse
- some application-layer attacks

Examples of WAF providers include:

- Cloudflare
- Akamai
- Imperva
- AWS WAF
- F5
- Sucuri

---

# 8. Using WAFW00F

I first reviewed the available options:

```bash
wafw00f -h
```

During the practical, I tested WAF detection against public websites for identification purposes.

One test against Cloudflare's own website timed out because of connectivity problems.

A later test against Discord returned a result indicating that the site was protected by Cloudflare.

## What I Learned

WAFW00F does not tell me that a website is vulnerable.

Its purpose is fingerprinting.

It attempts to identify whether a web-facing target is using a known WAF technology.

This information can form part of reconnaissance about the application's defensive environment.

---

# 9. DNS Reconnaissance

The next stage introduced DNS reconnaissance.

DNS translates human-readable names such as:

```text
example.com
```

into network addresses used by computers.

Reconnaissance against DNS can reveal information about an organisation's internet-facing infrastructure.

---

# 10. nslookup

`nslookup` can be used to make basic DNS queries.

Example:

```bash
nslookup google.com
```

The result returned DNS information including IPv4 and IPv6 addresses.

During some queries, the local DNS service refused requests and Kali subsequently used an available public DNS resolver.

## What I Learned

`nslookup` provides a relatively simple way to query DNS and obtain basic information about a domain.

---

# 11. dig

`dig` provides more detailed DNS information.

Example:

```bash
dig google.com
```

The output included sections and fields such as:

- Question
- Answer
- flags
- TTL
- DNS server used
- query time
- message size

## Important Fields

### Answer Section

Contains the DNS records returned for the query.

### TTL

TTL means **Time To Live**.

It specifies how long a DNS response may normally remain cached before it should be refreshed.

### Query Time

Shows approximately how long the DNS query took.

### Server

Shows the DNS resolver that answered the request.

## What I Learned

`dig` provides considerably more detail than `nslookup`, making it useful when I need to understand exactly how a DNS query was answered.

---

# 12. dnsrecon

`dnsrecon` automates several types of DNS reconnaissance.

It can be used to investigate information such as:

- DNS records
- name servers
- subdomains
- zone transfers

Example:

```bash
dnsrecon -d google.com
```

During the exercise, the query timed out.

This demonstrated that reconnaissance tools may be affected by:

- internet connectivity;
- target-side restrictions;
- rate limiting; or
- tool timeout settings.

A timeout therefore does not automatically mean that the tool itself is broken.

---

# 13. dnsenum

`dnsenum` provides another method of DNS enumeration.

Example:

```bash
dnsenum google.com
```

The tool returned information relating to the domain's infrastructure.

This included:

- host addresses
- name servers
- mail-server information
- zone-transfer attempts
- subdomain discovery attempts

---

# 14. Name Server Discovery

The DNS enumeration identified authoritative name servers associated with Google, including:

```text
ns1.google.com
ns2.google.com
ns3.google.com
ns4.google.com
```

These systems are responsible for answering authoritative DNS queries for the domain.

---

# 15. Zone Transfer Testing

`dnsenum` also attempted DNS zone transfers using AXFR.

All zone-transfer attempts failed.

## What I Learned

A DNS zone transfer can allow a secondary DNS server to obtain DNS zone information from an authoritative server.

If incorrectly exposed to unauthorised users, this could reveal a large amount of DNS infrastructure information.

For that reason, public zone transfers are normally restricted.

A failed AXFR attempt against a properly configured public domain is therefore expected.

---

# 16. Subdomain Enumeration

`dnsenum` can also attempt to identify common subdomains.

Conceptually, examples might include names such as:

```text
mail.example.com
vpn.example.com
dev.example.com
test.example.com
```

This demonstrated another use of DNS reconnaissance:

**identifying additional hosts or services associated with an organisation.**

---

# 17. How the Tools Fit Together

One of the most useful parts of this practical was understanding how the tools complemented one another.

## Nmap

```text
What ports and services are exposed?
```

## MySQL Client

```text
What can I learn by directly interacting with the exposed database service?
```

## SpiderFoot

```text
What reconnaissance information can be automatically collected and correlated?
```

## WAFW00F

```text
Does this web application appear to use a recognised WAF?
```

## nslookup

```text
What basic DNS information can I retrieve?
```

## dig

```text
What detailed DNS information is returned?
```

## dnsrecon / dnsenum

```text
What additional DNS infrastructure or records can be enumerated automatically?
```

---

# 18. Key Commands Used

## MySQL

```bash
mysql --skip-ssl -h <TARGET_IP> -u root
```

```sql
SHOW DATABASES;
SELECT USER();
SELECT CURRENT_USER();
exit;
```

## SpiderFoot

```bash
spiderfoot -h
spiderfoot -l 127.0.0.1:5001
```

Local interface:

```text
http://127.0.0.1:5001
```

## WAFW00F

```bash
wafw00f -h
```

Example identification query:

```bash
wafw00f https://discord.com
```

## DNS

```bash
nslookup google.com
```

```bash
dig google.com
```

```bash
dnsrecon -d google.com
```

```bash
dnsenum google.com
```

---

# What I Learned

By the end of the practical, I had gained experience with several different forms of reconnaissance.

I learned how to:

- connect to an older MySQL service when modern SSL negotiation caused compatibility problems;
- enumerate databases;
- distinguish `USER()` from `CURRENT_USER()` in MySQL;
- identify an overly permissive database account configuration;
- use SpiderFoot to automate reconnaissance and OSINT collection;
- compare SpiderFoot findings with earlier Nmap results;
- understand the difference between a network scanner and an OSINT automation framework;
- use WAFW00F to fingerprint Web Application Firewall technology;
- use `nslookup` for basic DNS queries;
- use `dig` for more detailed DNS analysis;
- use `dnsrecon` and `dnsenum` for automated DNS reconnaissance;
- understand what DNS zone transfers are and why unrestricted transfers are a security concern; and
- recognise that reconnaissance results should be collected from multiple sources and interpreted together.

The practical reinforced the idea that reconnaissance is not about running one scanner.

It is a process of gathering information from different perspectives and building a more complete picture of the target.

---

# Conclusion

This exercise broadened my understanding of reconnaissance beyond port scanning.

My earlier Nmap work identified exposed network services.

This practical showed how those findings could be expanded through:

**service interaction → automated OSINT → WAF fingerprinting → DNS reconnaissance**

SpiderFoot was particularly useful because it independently identified many of the same services already discovered through Nmap while also attempting to gather additional contextual information.

The overall lesson was that different reconnaissance tools provide different pieces of information.

Used together, they can provide a more complete understanding of a target's exposed attack surface and supporting infrastructure.

---

## Lab Note

Testing against Metasploitable 2 was performed within an authorised cybersecurity laboratory.

Public-domain DNS and WAF examples in this exercise were limited to basic reconnaissance and technology-identification queries.
