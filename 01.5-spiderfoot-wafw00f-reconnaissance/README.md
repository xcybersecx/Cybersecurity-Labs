# SpiderFoot and WAFW00F Reconnaissance Practical

**Completed:** 4 August 2026  
**Environment:** Kali Linux and Metasploitable 2  
**Tools:** MySQL Client, SpiderFoot, WAFW00F, nslookup, dig, dnsrecon, dnsenum

## Overview

This practical expanded on my earlier Nmap work by introducing me to several other reconnaissance tools.

The main thing I was beginning to understand was that reconnaissance is not performed with one tool. Different tools can answer different questions.

For example:

- **Nmap:** What ports and services are exposed?
- **MySQL client:** What can I learn by interacting directly with an exposed database service?
- **SpiderFoot:** What information can be gathered and brought together automatically?
- **WAFW00F:** Does a website appear to use a recognised Web Application Firewall?
- **nslookup / dig:** What DNS information can I query?
- **dnsrecon / dnsenum:** What additional DNS information can be enumerated?

Metasploitable 2 was used as the authorised laboratory target.

For privacy, its original local IP address has been replaced with `<TARGET_IP>` in this public write-up.

---

## 1. MySQL Enumeration

Nmap had previously identified MySQL running on TCP port 3306.

I wanted to see whether I could connect to the database service directly and what information it would expose.

### Initial connection

My first connection attempt produced a TLS/SSL compatibility error:

```text
ERROR 2026 (HY000):
TLS/SSL error: wrong version number
```

Because Metasploitable uses an old MySQL implementation, I retried the connection without SSL:

```bash
mysql --skip-ssl -h <TARGET_IP> -u root
```

The connection succeeded.

### Enumerating databases

I listed the available databases using:

```sql
SHOW DATABASES;
```

The databases returned included:

```text
information_schema
dvwa
metasploit
mysql
owasp10
tikiwiki
tikiwiki195
```

This showed that several of the deliberately vulnerable applications on the machine had databases accessible through the MySQL service.

---

## 2. Identifying the Database User

I checked how the client was connected using:

```sql
SELECT USER();
```

I then checked the account MySQL was actually using for privilege evaluation:

```sql
SELECT CURRENT_USER();
```

The result was:

```text
root@%
```

### Interpretation

The `%` host component indicated that the MySQL account could match connections from any host rather than being limited to one specific machine.

Together with the `root` account, this showed how permissive the database configuration was in the intentionally vulnerable lab.

### What I learned

`USER()` and `CURRENT_USER()` are related but are not exactly the same.

- `USER()` shows how the client presented itself to MySQL.
- `CURRENT_USER()` shows the account MySQL matched for authentication and privileges.

This was my first practical introduction to the difference.

The MySQL session could then be closed using:

```sql
exit;
```

or:

```sql
quit;
```

---

## 3. SpiderFoot Reconnaissance

SpiderFoot is an automated reconnaissance and OSINT framework.

I first reviewed the available options:

```bash
spiderfoot -h
```

I then started its local web interface:

```bash
spiderfoot -l 127.0.0.1:5001
```

The interface was available locally at:

```text
http://127.0.0.1:5001
```

I created a scan against the authorised Metasploitable target.

### SpiderFoot results

SpiderFoot identified several open TCP ports that had already been discovered using Nmap.

Examples included:

| Port | Service |
| ---: | --- |
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

One of the useful things about this was seeing a second tool identify many of the same exposed services that Nmap had already found.

It helped me understand the value of checking findings using more than one source or method rather than relying completely on one tool.

### What SpiderFoot added

SpiderFoot did more than identify ports. Depending on the modules and available data, it could also attempt to gather information such as:

- port banners;
- IP information;
- geographic information;
- WHOIS data;
- co-hosted domains;
- domain relationships; and
- email-related information.

Some online SpiderFoot modules produced timeout errors during the exercise.

The important distinction for me was that Nmap and SpiderFoot overlap in some areas, but they are not the same type of tool. Nmap primarily helped me discover reachable hosts, ports and services, while SpiderFoot automated collection from a wider range of reconnaissance and OSINT sources.

---

## 4. WAFW00F

WAFW00F is used to identify whether a website appears to be protected by a Web Application Firewall (WAF).

A WAF monitors and filters HTTP/HTTPS traffic reaching web applications and may detect or block certain malicious requests.

I first reviewed the available options:

```bash
wafw00f -h
```

During the practical, I used WAFW00F against public websites for basic identification purposes.

One test against Cloudflare's own website timed out because of connectivity problems. A later test against Discord returned a result indicating that the site was protected by Cloudflare.

### What I learned

WAFW00F does **not** tell me that a website is vulnerable.

Its purpose in this exercise was fingerprinting: identifying whether a web-facing target appeared to be using a recognised WAF technology.

---

## 5. DNS Reconnaissance

The next part of the practical introduced DNS reconnaissance.

DNS translates human-readable domain names into network addresses used by computers. DNS queries can also provide information about internet-facing infrastructure.

### nslookup

`nslookup` can be used to make basic DNS queries.

For example:

```bash
nslookup google.com
```

The result returned DNS information including IPv4 and IPv6 addresses.

During some queries, the local DNS service refused requests and Kali subsequently used an available public DNS resolver.

### dig

`dig` provides more detailed DNS information.

For example:

```bash
dig google.com
```

The output included information such as:

- the question and answer sections;
- flags;
- TTL;
- DNS server used;
- query time; and
- message size.

This helped me understand some of the information returned during a DNS query.

**TTL** means **Time To Live** and shows how long a DNS response may normally remain cached before being refreshed.

**Query time** shows approximately how long the DNS query took.

**Server** shows the DNS resolver that answered the request.

I found `dig` more detailed than `nslookup`.

---

## 6. dnsrecon

`dnsrecon` automates several types of DNS reconnaissance.

An example used during the practical was:

```bash
dnsrecon -d google.com
```

The query timed out during the exercise.

This was another useful reminder that a timeout does not automatically mean a tool is broken. Connectivity, the target, rate limiting or timeout settings can all affect the result.

---

## 7. dnsenum

I also used `dnsenum`:

```bash
dnsenum google.com
```

It returned information relating to the domain's infrastructure, including host addresses, name servers and mail-server information. It also attempted zone transfers and subdomain discovery.

### Name server discovery

The enumeration identified authoritative Google name servers including:

```text
ns1.google.com
ns2.google.com
ns3.google.com
ns4.google.com
```

### Zone transfer testing

`dnsenum` attempted DNS zone transfers using AXFR.

The attempts failed.

I learned that zone transfers are used to transfer DNS zone information between DNS servers. If they are incorrectly exposed, they can reveal a large amount of DNS information. A failed AXFR attempt against a properly configured public domain is therefore expected.

### Subdomain enumeration

`dnsenum` can also attempt to identify subdomains associated with a domain.

This helped me understand another purpose of DNS reconnaissance: discovering additional hosts or services associated with an organisation.

---

## Key Commands Used

### MySQL

```bash
mysql --skip-ssl -h <TARGET_IP> -u root
```

```sql
SHOW DATABASES;
SELECT USER();
SELECT CURRENT_USER();
exit;
```

### SpiderFoot

```bash
spiderfoot -h
spiderfoot -l 127.0.0.1:5001
```

### WAFW00F

```bash
wafw00f -h
wafw00f https://discord.com
```

### DNS

```bash
nslookup google.com
dig google.com
dnsrecon -d google.com
dnsenum google.com
```

---

## What I Learned

By the end of the practical, I had used several different forms of reconnaissance.

I learned how to:

- connect to an older MySQL service when SSL negotiation caused a compatibility problem;
- enumerate databases;
- distinguish `USER()` from `CURRENT_USER()` in MySQL;
- recognise a permissive database account configuration;
- use SpiderFoot for automated reconnaissance and OSINT collection;
- compare SpiderFoot results with earlier Nmap findings;
- use WAFW00F to identify WAF technology;
- use `nslookup` and `dig` for DNS queries;
- use `dnsrecon` and `dnsenum` for further DNS reconnaissance; and
- understand what DNS zone transfers are and why unrestricted transfers can be a security concern.

The main lesson for me was that reconnaissance is not about running one scanner. Different tools provide different pieces of information, and those results have to be interpreted together.

## Lab Note

Testing against Metasploitable 2 was performed within an authorised cybersecurity laboratory.

Public-domain DNS and WAF examples in this exercise were limited to basic reconnaissance and technology-identification queries.
