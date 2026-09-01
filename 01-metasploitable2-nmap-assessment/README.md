# Metasploitable 2 Vulnerability Assessment Using Nmap and NSE

**Completed:** 29 July 2026  
**Environment:** Kali Linux, Metasploitable 2, Oracle VirtualBox  
**Tools:** Nmap and Nmap Scripting Engine (NSE)

## Overview

This was one of my early practical cybersecurity exercises.

The aim was to carry out an authorised vulnerability assessment against Metasploitable 2, an intentionally vulnerable Linux virtual machine designed for security training.

I used Nmap to work through the main stages of the assessment:

1. identify the target;
2. discover open TCP ports;
3. identify the services and software versions behind those ports;
4. find relevant Nmap NSE scripts;
5. investigate selected services; and
6. document what the results actually showed.

One of the main things I learned was that an open port or an old software version does not automatically prove that a vulnerability exists.

## Scope

Testing was limited to the Metasploitable 2 virtual machine.

Other devices were visible during host discovery, but they were outside the scope of the exercise and were not tested further.

For privacy, the original local IP addresses used during the lab have been replaced with placeholders in this public write-up.

## Lab Environment

Two virtual machines were used:

| System | Purpose |
| --- | --- |
| Kali Linux | Security testing machine |
| Metasploitable 2 | Authorised vulnerable target |

At the time of the exercise, both virtual machines were connected using VirtualBox Bridged Adapter networking so they could communicate on the same local network.

---

## 1. Host Discovery

The first task was to locate the Metasploitable 2 machine on the network.

```bash
sudo nmap -sn <LAB_SUBNET>
```

### What the command does

- `sudo` runs the command with administrative privileges.
- `nmap` launches Nmap.
- `-sn` performs host discovery without carrying out a port scan.
- `<LAB_SUBNET>` represents the local subnet being checked.

The scan identified several active devices. Once the Metasploitable 2 machine had been identified, all further testing was restricted to that target.

### What I learned

Host discovery is useful because it confirms which systems are reachable before more detailed scanning begins.

It also reinforced the importance of scope. Seeing another device on a network does not mean it is authorised for testing.

---

## 2. Full TCP Port Scan

The next stage was to find out which TCP ports were open on the target.

```bash
sudo nmap -p- <TARGET_IP>
```

The `-p-` option tells Nmap to scan all 65,535 TCP ports rather than only its default selection of common ports.

The scan identified **30 open TCP ports**.

Some of the notable services included:

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
| 512 | exec |
| 513 | login |
| 514 | shell |
| 1099 | Java RMI |
| 1524 | bindshell |
| 2049 | NFS |
| 2121 | FTP |
| 3306 | MySQL |
| 3632 | distccd |
| 5432 | PostgreSQL |
| 5900 | VNC |
| 6000 | X11 |
| 6667 | IRC |
| 8009 | AJP13 |
| 8180 | HTTP / Apache Tomcat |

### What I learned

An open port shows that a network service is accessible, but an open port by itself does **not** prove that the service is vulnerable.

The next step was therefore to identify what software was running behind the open ports.

---

## 3. Service and Version Detection

I used Nmap service and version detection:

```bash
sudo nmap -sV <TARGET_IP>
```

The `-sV` option probes open ports to identify the services and software versions in use.

Some of the results were:

| Port | Service | Version |
| ---: | --- | --- |
| 21 | FTP | vsftpd 2.3.4 |
| 22 | SSH | OpenSSH 4.7p1 Debian 8ubuntu1 |
| 23 | Telnet | Linux telnetd |
| 25 | SMTP | Postfix smtpd |
| 53 | DNS | ISC BIND 9.4.2 |
| 80 | HTTP | Apache HTTP Server 2.2.8 |
| 139 / 445 | SMB | Samba 3.0.20 |
| 2121 | FTP | ProFTPD 1.3.1 |
| 3306 | MySQL | MySQL 5.0.51a |
| 5432 | PostgreSQL | PostgreSQL 8.3.x |
| 6667 | IRC | UnrealIRCd |
| 8009 | AJP13 | Apache JServ Protocol |
| 8180 | HTTP | Apache Tomcat |

Several services were running old software versions.

At this stage, I did not treat the version numbers themselves as proof of vulnerabilities. Instead, I used them to decide which services should be investigated further.

---

## 4. Finding Relevant NSE Scripts

The next part of the exercise introduced me to the Nmap Scripting Engine.

Rather than trying to memorise vulnerability commands, I searched the NSE scripts already installed with Nmap for scripts that matched the services I had discovered.

For example:

```bash
ls /usr/share/nmap/scripts | grep ftp
```

```bash
ls /usr/share/nmap/scripts | grep http
```

```bash
ls /usr/share/nmap/scripts | grep smb
```

```bash
ls /usr/share/nmap/scripts | grep mysql
```

This gave me a simple process:

1. identify a service;
2. identify its version;
3. search for relevant NSE scripts;
4. run an appropriate script;
5. analyse the result; and
6. decide what the evidence actually supports.

This was an important step in moving from basic port scanning towards vulnerability assessment.

---

## 5. FTP: vsftpd 2.3.4

### Command

```bash
sudo nmap --script ftp-vsftpd-backdoor <TARGET_IP>
```

The FTP service on port 21 was identified as **vsftpd 2.3.4**.

The NSE script detected the known vsftpd 2.3.4 backdoor associated with **CVE-2011-2523**.

The test successfully executed the `id` command and returned:

```text
uid=0(root) gid=0(root)
```

### Interpretation

This was the strongest finding in the assessment because it was not based only on a version number.

The NSE test demonstrated successful command execution with root privileges, so I treated this as a **confirmed vulnerability**.

### Potential impact

Root-level access could allow an attacker to execute commands, access or alter files, create users, install malicious software, change system configuration, and take complete control of the affected machine.

### Recommendation

Remove the vulnerable version of vsftpd and replace it with a supported version.

If FTP is not required, disable the service. If file transfer is needed, use an encrypted alternative such as SFTP.

---

## 6. SSH: OpenSSH 4.7p1

### Command

```bash
sudo nmap --script ssh2-enum-algos <TARGET_IP>
```

The script enumerated the cryptographic algorithms supported by the SSH server.

Legacy algorithms included:

- `diffie-hellman-group1-sha1`
- `ssh-dss`
- `3des-cbc`
- `arcfour`
- `hmac-md5`

### Interpretation

The test did not demonstrate that SSH could be exploited.

Instead, it showed that the server supported several obsolete cryptographic algorithms, so I treated this as a **configuration weakness** rather than a confirmed vulnerability.

### Recommendation

Upgrade OpenSSH and disable obsolete algorithms in favour of modern cryptographic standards.

---

## 7. Telnet

### Command

```bash
sudo nmap --script telnet-encryption <TARGET_IP>
```

The test showed that the Telnet service did not support encrypted communication.

### Interpretation

Telnet transmits information in clear text. This means credentials and commands could potentially be intercepted by somebody able to monitor the network.

The weakness is associated with the protocol itself rather than a particular software vulnerability.

### Recommendation

Disable Telnet and use SSH for encrypted remote administration.

---

## 8. SMTP: Postfix

### Command

```bash
sudo nmap --script smtp-commands <TARGET_IP>
```

The SMTP server advertised several supported commands and capabilities, including:

- `PIPELINING`
- `STARTTLS`
- `VRFY`
- `ETRN`
- `DSN`

The presence of `VRFY` was interesting because it may allow valid user accounts to be identified depending on the server configuration.

### Interpretation

This did not demonstrate a direct compromise of the SMTP server.

However, user-enumeration functionality could provide useful information during reconnaissance and support later password attacks or phishing attempts.

### Recommendation

Disable unnecessary SMTP commands such as `VRFY` and maintain the mail server with current security updates.

---

## 9. DNS: ISC BIND 9.4.2

### Command

```bash
sudo nmap --script dns-recursion <TARGET_IP>
```

The purpose of this test was to determine whether the DNS server permitted open recursive queries.

The script produced no positive evidence that open recursion was enabled.

### Interpretation

I did **not** classify this as a vulnerability.

The fact that BIND was an old version could justify further investigation, but the particular weakness being tested was not demonstrated by this NSE result.

This was useful because it reinforced that a test returning no vulnerability is still a valid assessment result.

### Recommendation

Keep DNS software updated and restrict unnecessary recursive-query functionality.

---

## 10. HTTP: Apache 2.2.8

### Command

```bash
sudo nmap --script http-enum <TARGET_IP>
```

The script identified several accessible web resources, including:

- `/phpMyAdmin`
- `/tikiwiki`
- `/test`
- `/doc`
- `/icons`
- `/webdav`

Other application and administrative resources were also exposed.

### Interpretation

The existence of these directories did not mean they were automatically vulnerable.

However, exposing additional applications, management interfaces and directories increases the attack surface and gives an attacker more areas to investigate.

### Recommendation

Remove unnecessary applications and directories, restrict administrative interfaces, and keep the web server and hosted applications updated.

---

## 11. SMB: Samba

### Command

```bash
sudo nmap --script smb-os-discovery <TARGET_IP>
```

The script was able to retrieve information including:

- operating-system information;
- computer name;
- workgroup or domain information;
- fully qualified domain name; and
- system time.

This information was available without authentication.

### Interpretation

The test did not demonstrate exploitation of SMB.

It did demonstrate **information disclosure**.

Information gathered during reconnaissance can help an attacker build a more accurate picture of a target and choose more appropriate attacks.

### Recommendation

Restrict unnecessary SMB information disclosure and limit SMB access to authorised users and systems.

---

## 12. MySQL: MySQL 5.0.51a

### Command

```bash
sudo nmap --script mysql-info <TARGET_IP>
```

The NSE script returned information about the MySQL service, including:

- protocol version;
- server version;
- thread information;
- server capabilities; and
- authentication-related information.

### Interpretation

The script did not demonstrate unauthorised database access.

The main finding was that detailed service information could be obtained without authentication.

This information could help an attacker research vulnerabilities affecting the particular MySQL version or plan further testing.

### Recommendation

Upgrade MySQL to a supported version, restrict database access to authorised systems, and use strong authentication.

---

## Findings Summary

| Finding | Classification |
| --- | --- |
| vsftpd 2.3.4 backdoor with root command execution | **Confirmed vulnerability** |
| Legacy SSH cryptographic algorithms | Configuration weakness |
| Telnet clear-text communication | Insecure protocol |
| SMTP `VRFY` functionality | Potential information disclosure / enumeration |
| Exposed HTTP applications and directories | Increased attack surface |
| SMB system information disclosure | Information disclosure |
| MySQL service information disclosure | Information disclosure |
| DNS open recursion | Not confirmed |

---

## What I Learned

This exercise helped me understand how the stages of a vulnerability assessment connect to one another:

**host discovery → port scanning → service identification → targeted investigation → interpretation → remediation**

The main lessons I took from the exercise were:

- An open port is not automatically a vulnerability.
- An outdated version is not proof that exploitation is possible.
- Enumeration helps determine what should be investigated next.
- NSE scripts can provide additional evidence about individual services.
- Findings should be described according to what the evidence actually demonstrates.
- A confirmed vulnerability is different from a configuration weakness or information-disclosure issue.
- Negative results are also important and should not be exaggerated into vulnerabilities.
- Staying within the authorised scope of an assessment is essential.

The most significant result was the confirmed vsftpd 2.3.4 backdoor, which demonstrated root-level command execution.

More importantly, the exercise helped me understand **why reconnaissance comes before vulnerability assessment** and how information gathered at one stage guides the next.

## Lab Note

This project documents testing performed against **Metasploitable 2, an intentionally vulnerable cybersecurity training machine**, in an authorised lab environment.
