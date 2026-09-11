# Metasploit Framework: Four-Port Assessment

**Completed:** 11 September 2026  
**Lab:** Kali Linux against Metasploitable 2 in my authorised VirtualBox training environment  
**Primary requirement:** investigate at least four exposed ports/services and document the practical process  
**Evidence:** 61 chronological screenshots retained in `Metasploit 11-09-26/`

## Overview

This exercise was completed as part of my hands-on cybersecurity training. The assignment developed from an earlier Metasploit exercise in which I had followed one known vulnerable service. This time I was expected to work more independently: begin with reconnaissance, choose services from the target's exposed ports, investigate them, troubleshoot problems, and distinguish between a service that merely looked interesting and a weakness I could actually validate.

I deliberately kept the unsuccessful attempts as well as the successful ones. That matters because one of the biggest lessons from this exercise was that **an open port is not a vulnerability, a version match is not proof of exploitation, a Metasploit module existing is not proof that it applies, and even a module saying a target appears vulnerable is not the same as obtaining a working session**.

The four ports I use as the core assessment are:

| Port | Service | Validation obtained | Final classification |
|---:|---|---|---|
| **3632/tcp** | distccd | Remote command shell opened; `whoami` returned `daemon` | **Confirmed remote command execution** |
| **139/tcp** | Samba 3.0.20-Debian | Command shell opened; `whoami` returned `root` | **Confirmed root-level remote command execution** |
| **3306/tcp** | MySQL 5.0.51a | Metasploit found blank root credentials; manual client login confirmed root access | **Confirmed authentication weakness** |
| **5900/tcp** | VNC 3.3 | Weak password identified; TightVNC connection manually confirmed | **Confirmed weak authentication and remote desktop exposure** |

I also investigated SSH, Telnet, SMTP, DNS/BIND, HTTP/WebDAV, NFS and UnrealIRCd. Those additional tests are included because they taught me different things about default credentials, enumeration, information disclosure, misconfiguration, module selection, manual validation and unsuccessful exploitation attempts.

## Objectives

- Confirm the target and establish a service baseline before selecting anything to investigate.
- Use service/version information to decide which exposed ports deserved further research.
- Work through Metasploit's normal module workflow instead of treating it as a one-click exploitation tool.
- Validate successful findings where possible with a second method or by checking the privileges of the resulting session.
- Record failed attempts, incorrect assumptions and troubleshooting rather than deleting them from the final story.
- Separate **confirmed vulnerabilities**, **weak/default credentials**, **enumeration/information disclosure**, **misconfiguration**, and **unconfirmed leads**.
- Finish with remediation ideas and a reflection on what I actually learned.

## Scope and lab environment

| Item | Value |
|---|---|
| Attacking system | Kali Linux |
| Target | Metasploitable 2 |
| Target lab IP | `192.168.1.114` |
| Kali lab IP used for callbacks | `192.168.1.113` |
| Nmap | 7.99 visible in evidence |
| Metasploit Framework | v6.5.3-dev visible in evidence |
| Additional tools | Searchsploit, Exploit-DB, `dig`, MySQL/MariaDB client, `rpcinfo`, `showmount`, NFS mount utilities, TightVNC Viewer |
| Authorisation | Local intentionally vulnerable training VM only |

The IP addresses shown in this report are RFC1918 private lab addresses. I did not test public systems or systems belonging to anyone else.

---

# 1. Reconnaissance and building the target picture

I began by confirming that the Metasploitable 2 VM was reachable and then ran a service/version scan. The first scan immediately showed why Metasploitable is useful for training: the machine exposed many old and intentionally vulnerable services. Instead of choosing a port at random, I used this first pass as a map of the target.

```bash
ping <TARGET_IP>
sudo nmap -sV <TARGET_IP>
```

![Figure 1 - Baseline connectivity and service-version scan](Metasploit%2011-09-26/Screenshot%202026-09-10%20215434.png)

*Figure 1. Ping to the Metasploitable 2 host succeeded, followed by an Nmap service/version scan that exposed a large intentionally vulnerable attack surface.*

![Figure 2 - Repeated baseline capture](Metasploit%2011-09-26/Screenshot%202026-09-10%20215505.png)

*Figure 2. A second capture preserves the same first-pass service inventory for evidence continuity.*

![Figure 3 - Baseline scan retained in full](Metasploit%2011-09-26/Screenshot%202026-09-10%20215526.png)

*Figure 3. A third capture preserves the complete first-pass service list and the private lab addressing visible in the terminal.*


The first service scan exposed FTP, SSH, Telnet, SMTP, DNS, HTTP, Samba, NFS, MySQL, PostgreSQL, distccd, VNC, IRC/TCP 6667, Tomcat and other services. I then performed a deeper full TCP scan and saved the results so I had a more complete basis for later decisions.

```bash
nmap -p- -sV -sC -O -v -oA initial_scan <TARGET_IP>
```

The flags mattered to my learning:

- `-p-` scanned all 65,535 TCP ports rather than only the most common ports.
- `-sV` attempted service/version detection.
- `-sC` ran Nmap's default script set.
- `-O` attempted operating-system detection.
- `-v` increased output detail while the scan was running.
- `-oA initial_scan` saved the scan in Nmap's main output formats for later review.

![Figure 6 - Full TCP scan in progress](Metasploit%2011-09-26/Screenshot%202026-09-10%20232629.png)

*Figure 6. A full-port Nmap scan with service detection, default scripts, OS detection and output logging was started to build a broader evidence base.*

![Figure 7 - Detailed Nmap results, early services](Metasploit%2011-09-26/Screenshot%202026-09-10%20233602.png)

*Figure 7. The detailed scan recorded FTP, SSH, Telnet and SMTP information, including service banners and script output.*

![Figure 8 - Detailed Nmap results, DNS/HTTP/SMB/MySQL](Metasploit%2011-09-26/Screenshot%202026-09-10%20233643.png)

*Figure 8. The scan continued through DNS, HTTP, RPC, Samba and MySQL, giving service versions and protocol details used later in the assessment.*

![Figure 9 - Detailed Nmap results, later services](Metasploit%2011-09-26/Screenshot%202026-09-10%20233945.png)

*Figure 9. The scan identified distccd, VNC, UnrealIRCd, Tomcat and additional RPC services, expanding the shortlist of services worth investigating.*

![Figure 10 - Operating-system and SMB host-script results](Metasploit%2011-09-26/Screenshot%202026-09-10%20234120.png)

*Figure 10. Nmap's OS and SMB scripts reported Linux 2.6.x characteristics, Samba 3.0.20-Debian and SMB security details.*

![Figure 11 - Detailed scan completion](Metasploit%2011-09-26/Screenshot%202026-09-10%20234147.png)

*Figure 11. The full scan completed successfully and produced the baseline from which later service-specific testing was selected.*


### Reconnaissance observations

The detailed scan gave me several important leads:

- Samba was reported as **3.0.20-Debian**.
- MySQL was reported as **5.0.51a-3ubuntu5**.
- distccd was exposed on **3632/tcp**.
- VNC was exposed on **5900/tcp**, protocol 3.3.
- UnrealIRCd was exposed on **6667/tcp**.
- BIND was reported as **9.4.2**.
- Apache was **2.2.8 (Ubuntu) DAV/2**.
- NFS/RPC services were present.
- SMB script output showed message signing disabled and identified the target as `metasploitable`.

At this point these were **leads**, not confirmed vulnerabilities.

---

# 2. SSH: authentication and user enumeration

Before moving into the four core ports, I tested SSH because it gave me a useful comparison between **valid credentials** and **software exploitation**.

I used the Metasploit SSH login scanner with the known Metasploitable training credentials. Authentication succeeded and Metasploit opened an SSH session.

![Figure 4 - SSH login scanner and successful session](Metasploit%2011-09-26/Screenshot%202026-09-10%20230829.png)

*Figure 4. Metasploit's SSH login scanner was configured with the lab's known training credentials. Authentication succeeded and an SSH session was opened.*


That was a real security weakness in the training machine, but the nature of the weakness matters: I had not exploited OpenSSH itself. I had authenticated with weak/default credentials.

I then tried SSH user enumeration. My first configuration referenced a username source incorrectly, so the module aborted. I inspected the installed Metasploit wordlists, selected a valid username list, and reran the test.

![Figure 5 - SSH enumeration troubleshooting](Metasploit%2011-09-26/Screenshot%202026-09-10%20231702.png)

*Figure 5. The SSH user-enumeration module initially needed a valid username list. The Metasploit wordlist directory was inspected and a suitable list was selected.*

![Figure 12 - SSH user enumeration completed](Metasploit%2011-09-26/Screenshot%202026-09-11%20001440.png)

*Figure 12. After correcting the wordlist setting, the SSH enumeration module identified multiple valid-looking local usernames. This was recorded as enumeration, not compromise.*


The corrected enumeration returned multiple candidate/valid usernames. I recorded this as **enumeration/information disclosure**, not account compromise.

### Lesson from SSH

This section taught me not to flatten everything into the word "exploit":

- **Successful login with known credentials** = authentication weakness.
- **User enumeration** = information disclosure/reconnaissance.
- **A genuine software exploit** would require evidence that a flaw in the SSH software itself had been triggered.

---

# 3. Telnet: old protocol plus weak credentials

I researched Telnet using both Searchsploit and Metasploit. I first looked at Telnet-related exploit results, then narrowed the workflow to service/version and login-scanner modules.

![Figure 13 - Telnet research and module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20002704.png)

*Figure 13. Searchsploit and Metasploit searches were used to investigate Telnet-related possibilities rather than assuming the service banner alone proved a vulnerability.*

![Figure 14 - Telnet-version module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20003254.png)

*Figure 14. A Metasploit search narrowed the work toward Telnet service-identification and authentication modules.*

![Figure 15 - Telnet version module options](Metasploit%2011-09-26/Screenshot%202026-09-11%20003508.png)

*Figure 15. The Telnet version scanner was reviewed to understand the target and port settings before use.*

![Figure 16 - Telnet login scanner selected](Metasploit%2011-09-26/Screenshot%202026-09-11%20004509.png)

*Figure 16. The Telnet authentication scanner was selected and its required options reviewed.*


I configured the Telnet login scanner with the known Metasploitable training credentials. The login succeeded and a command session was created.

![Figure 17 - Telnet training credentials accepted](Metasploit%2011-09-26/Screenshot%202026-09-11%20004634.png)

*Figure 17. The known Metasploitable training credentials authenticated successfully and opened a Telnet session.*


I then listed active Metasploit sessions, entered the Telnet session, checked the current user, and reviewed network information. `whoami` returned `msfadmin`.

![Figure 18 - Telnet session validation](Metasploit%2011-09-26/Screenshot%202026-09-11%20005111.png)

*Figure 18. The active sessions list was inspected, the Telnet session was entered, and `whoami` returned the `msfadmin` user. Network information was also checked from the session.*


### Interpretation

This was again primarily a **credential and protocol weakness**, not proof that I had exploited the Telnet daemon's code. Telnet is also inherently unsuitable for secure modern remote administration because it does not provide the encrypted session protection expected from SSH.

---

# 4. SMTP: version detection and username enumeration

I next investigated TCP/25. Metasploit's SMTP version scanner confirmed the Postfix service, after which I selected the SMTP user-enumeration module.

![Figure 19 - SMTP module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20005324.png)

*Figure 19. The SMTP service was investigated by searching for version and enumeration modules.*

![Figure 20 - SMTP version confirmed](Metasploit%2011-09-26/Screenshot%202026-09-11%20010031.png)

*Figure 20. The SMTP version scanner identified Postfix on the target, after which the SMTP user-enumeration module was selected.*


The enumeration completed and returned a list of local usernames. I also searched available SMTP exploit modules to understand what other classes of issue existed, but I did not treat the search results themselves as evidence against this target.

![Figure 21 - SMTP user enumeration](Metasploit%2011-09-26/Screenshot%202026-09-11%20010611.png)

*Figure 21. The SMTP enumeration module completed and returned a set of local usernames. This was treated as information disclosure and reconnaissance evidence, not account compromise.*

![Figure 22 - SMTP exploit search](Metasploit%2011-09-26/Screenshot%202026-09-11%20011122.png)

*Figure 22. A wider Metasploit search for SMTP-related exploit modules was performed for research. No exploit was claimed solely because modules existed.*


### Interpretation

The SMTP result was useful because local usernames can support later authentication testing. However, finding usernames is not the same as authenticating as those users. I therefore classified this as **information disclosure / account enumeration**.

---

# 5. Core Port 1: 3632/tcp, distccd remote command execution

## Why I selected it

The detailed Nmap scan showed `distccd` on TCP/3632. Metasploit contained a module specifically associated with remote command execution through distcc, so I selected it and reviewed the options rather than immediately running it.

![Figure 23 - distcc module selected](Metasploit%2011-09-26/Screenshot%202026-09-11%20014731.png)

*Figure 23. The distcc command-execution module was selected after the service was identified on TCP/3632. Required host and payload settings were reviewed.*

![Figure 24 - distcc options verified](Metasploit%2011-09-26/Screenshot%202026-09-11%20014825.png)

*Figure 24. The distcc module configuration was checked before execution, including the target host, target port and local callback settings.*


## First attempt: failure

My first run used the initial payload configuration and failed with a bad file descriptor error. No usable session was created.

![Figure 25 - First distcc attempt failed](Metasploit%2011-09-26/Screenshot%202026-09-11%20015136.png)

*Figure 25. The initial distcc attempt produced a bad file descriptor error and did not create a usable session. The failure was retained as troubleshooting evidence.*


I kept this screenshot because it is part of the actual learning process. A failed run does not automatically mean the target is safe. It can also mean the module, payload or callback configuration is not working as expected.

## Troubleshooting and successful validation

I changed the payload configuration and reran the module. This time Metasploit opened a command-shell session.

![Figure 26 - distcc retry opened a shell](Metasploit%2011-09-26/Screenshot%202026-09-11%20015507.png)

*Figure 26. After changing the payload configuration, the distcc attempt opened a command-shell session. This converted a version-based lead into validated command execution.*


I then checked which user context the shell had received:

```bash
whoami
```

The result was:

```text
daemon
```

![Figure 27 - distcc privilege level checked](Metasploit%2011-09-26/Screenshot%202026-09-11%20015742.png)

*Figure 27. Inside the distcc-created shell, `whoami` returned `daemon`, showing that remote command execution was confirmed but the initial session was not root.*


## Finding

**Confirmed remote command execution on TCP/3632.**

The successful shell was stronger evidence than a version match because I demonstrated command execution on the target. The session was initially running as `daemon`, which also reinforced an important distinction: gaining code execution does not automatically mean gaining root privileges.

### Risk

Remote command execution can allow an attacker to run commands on the affected host and can become a starting point for further local enumeration or privilege escalation.

### Remediation

- Remove distcc if it is not required.
- Upgrade unsupported/vulnerable implementations.
- Restrict the service to explicitly trusted build hosts.
- Do not expose the service to untrusted networks.
- Use firewall rules and network segmentation to limit access.

---

# 6. DNS/BIND: corroborating a service version without overclaiming

The initial scan reported ISC BIND 9.4.2. I independently queried the version using a CHAOS TXT request and received `9.4.2`, which corroborated the Nmap fingerprint.

![Figure 28 - BIND version independently queried](Metasploit%2011-09-26/Screenshot%202026-09-11%20020720.png)

*Figure 28. A CHAOS TXT `version.bind` query returned BIND 9.4.2, independently corroborating Nmap's DNS service fingerprint.*


I then searched Metasploit for DNS and BIND-related modules, including exploit results.

![Figure 29 - DNS version-module research](Metasploit%2011-09-26/Screenshot%202026-09-11%20020938.png)

*Figure 29. Metasploit was searched for DNS version-related modules to understand what could be enumerated or checked next.*

![Figure 30 - ISC BIND research](Metasploit%2011-09-26/Screenshot%202026-09-11%20021452.png)

*Figure 30. A search for ISC BIND-related modules was performed using the exact service family identified during reconnaissance.*

![Figure 31 - BIND search results continued](Metasploit%2011-09-26/Screenshot%202026-09-11%20021702.png)

*Figure 31. The module list was reviewed further. The existence of modules was treated as research only, not proof that the target matched a specific vulnerability.*

![Figure 32 - Exploit search for BIND](Metasploit%2011-09-26/Screenshot%202026-09-11%20021820.png)

*Figure 32. The search was narrowed to exploit modules associated with BIND.*

![Figure 33 - BIND exploit results reviewed](Metasploit%2011-09-26/Screenshot%202026-09-11%20021841.png)

*Figure 33. Additional BIND-related results were reviewed, but no successful exploit validation was obtained during this stage.*


### Interpretation

This was useful research, but I did **not** obtain a confirmed BIND exploit. I therefore recorded the result as **service fingerprinting and vulnerability research**, not successful exploitation.

This became one of the clearest examples in the exercise of why "I found an old version" is not enough for a vulnerability claim.

---

# 7. Core Port 2: 139/tcp, Samba 3.0.20-Debian

## Why I selected it

Nmap identified Samba 3.0.20-Debian. I searched Metasploit for Samba modules and found the `usermap_script` command-execution module among the results.

![Figure 34 - Samba module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20023051.png)

*Figure 34. A Metasploit search for Samba showed several modules, including the `usermap_script` command-execution module relevant to the target's Samba 3.0.20 service.*

![Figure 35 - Samba search results continued](Metasploit%2011-09-26/Screenshot%202026-09-11%20023109.png)

*Figure 35. The remaining Samba results were reviewed to compare alternatives before selecting the module that best matched the observed version and configuration.*


I did not rely only on the module name. I researched the issue separately and checked Exploit-DB. The research linked the vulnerable Samba range to the username-map-script command-execution issue and CVE-2007-2447.

![Figure 36 - Independent Samba vulnerability research](Metasploit%2011-09-26/Screenshot%202026-09-11%20023416.png)

*Figure 36. Browser research was used to understand the Samba username-map-script issue and its conditions rather than relying on a module name alone.*

![Figure 37 - Exploit-DB corroboration for Samba](Metasploit%2011-09-26/Screenshot%202026-09-11%20024021.png)

*Figure 37. Exploit-DB documented Samba 3.0.20 through 3.0.25rc3 username-map-script command execution and linked it to CVE-2007-2447.*


## Validation and troubleshooting

The first module run opened a command shell. I later closed that session while adjusting the payload/session behavior and repeated the test.

![Figure 38 - First Samba command-shell run](Metasploit%2011-09-26/Screenshot%202026-09-11%20030047.png)

*Figure 38. The Samba usermap module opened a command shell. That session was later closed while the payload and session behavior were being adjusted.*


A subsequent run again produced a command-shell session.

![Figure 39 - Samba retry and session behavior](Metasploit%2011-09-26/Screenshot%202026-09-11%20030739.png)

*Figure 39. A later run again opened a command shell. The repeated result increased confidence that the finding was reproducible within the lab.*


I repeated the process and then interacted with the active session. This time I checked the execution context directly:

```bash
whoami
```

The result was:

```text
root
```

![Figure 40 - Samba root-level command execution confirmed](Metasploit%2011-09-26/Screenshot%202026-09-11%20032259.png)

*Figure 40. A subsequent Samba session was entered and `whoami` returned `root`, confirming root-level remote command execution in the Metasploitable lab.*


## Finding

**Confirmed root-level remote command execution through Samba on TCP/139.**

This was the strongest finding of the exercise because I did not merely identify an old Samba version or a matching CVE. I obtained a shell and verified that the shell was running as root.

### Risk

Root-level remote command execution can provide complete control over the host, including access to files, system configuration, accounts and locally running services.

### Remediation

- Upgrade Samba to a supported patched release.
- Remove or disable unsafe legacy configuration such as vulnerable username-map behavior.
- Restrict SMB to trusted networks and hosts.
- Do not expose legacy SMB services beyond the administrative or internal network segments that genuinely need them.
- Apply least privilege to service accounts and file shares.

---

# 8. HTTP/Apache: testing an assumption, getting a negative result, and pivoting

Apache 2.2.8 with DAV/2 appeared in the initial scan. I researched the banner and then searched Metasploit for WebDAV-related scanners and modules.

![Figure 41 - Apache/WebDAV research](Metasploit%2011-09-26/Screenshot%202026-09-11%20033844.png)

*Figure 41. The Apache 2.2.8 DAV/2 banner was researched to identify likely configuration and WebDAV questions to test rather than jumping directly to an exploit claim.*

![Figure 42 - WebDAV module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20034506.png)

*Figure 42. Metasploit was searched for WebDAV-related scanners and modules that could test whether DAV functionality was actually enabled.*


I ran the WebDAV scanner. The result reported that WebDAV was disabled.

![Figure 43 - WebDAV disabled](Metasploit%2011-09-26/Screenshot%202026-09-11%20034801.png)

*Figure 43. The WebDAV scanner reported that WebDAV was disabled on the target. This negative result was preserved because it ruled out one assumed attack path.*


That negative result was useful: the presence of `DAV/2` in a server banner did not mean that a writable WebDAV attack path was actually available.

Instead of forcing the same idea, I pivoted to directory enumeration.

![Figure 44 - HTTP troubleshooting and pivot](Metasploit%2011-09-26/Screenshot%202026-09-11%20035257.png)

*Figure 44. After WebDAV produced no useful path, the workflow pivoted to HTTP directory enumeration and the directory-scanner options were reviewed.*


The directory scan found several accessible paths:

- `/cgi-bin/`
- `/doc/`
- `/icons/`
- `/phpMyAdmin/`
- `/test/`

![Figure 45 - HTTP directory enumeration](Metasploit%2011-09-26/Screenshot%202026-09-11%20035348.png)

*Figure 45. The directory scan identified exposed paths including `/cgi-bin/`, `/doc/`, `/icons/`, `/phpMyAdmin/` and `/test/`. These were recorded as exposed attack surface, not proof of compromise.*


I then examined the generic HTTP login module and tried it against the phpMyAdmin path.

![Figure 46 - HTTP login-scanner options](Metasploit%2011-09-26/Screenshot%202026-09-11%20035728.png)

*Figure 46. The generic HTTP login scanner was reviewed to see whether an exposed web path used HTTP authentication.*

![Figure 47 - phpMyAdmin did not present HTTP auth](Metasploit%2011-09-26/Screenshot%202026-09-11%20040138.png)

*Figure 47. Testing `/phpMyAdmin/` with the generic HTTP login module returned that no URI was found requesting HTTP authentication. The module therefore did not fit the application's authentication mechanism.*


The module reported that no URI was found asking for HTTP authentication. This made sense in hindsight: phpMyAdmin's application login is not the same thing as browser HTTP Basic authentication.

### Interpretation

The HTTP work produced **attack-surface discovery**, not a confirmed Apache/phpMyAdmin compromise. More importantly, it taught me to match the scanner to the authentication mechanism actually in use.

---

# 9. Core Port 3: 3306/tcp, MySQL 5.0.51a

## Metasploit authentication test

After the HTTP work, I moved to MySQL. The Metasploit MySQL login scanner identified the old server version and reported a successful `root` login with a blank password.

![Figure 48 - MySQL blank-root authentication found](Metasploit%2011-09-26/Screenshot%202026-09-11%20040547.png)

*Figure 48. The MySQL login scanner identified MySQL 5.0.51a and successfully authenticated the `root` database account with a blank password.*


That was already a serious finding, but I wanted to validate it outside the scanner.

## Manual validation and SSL troubleshooting

My first direct MySQL client attempt failed with a TLS/SSL compatibility error. A second syntax attempt also did not match the client's supported options. I then used the client's `--skip-ssl` option and successfully reached the MariaDB/MySQL monitor as root.

![Figure 49 - MySQL manually validated](Metasploit%2011-09-26/Screenshot%202026-09-11%20041142.png)

*Figure 49. Manual client testing initially hit SSL compatibility errors. Using the client's non-SSL option allowed entry to the MariaDB/MySQL monitor as root, independently confirming the authentication weakness.*


## Finding

**Confirmed remote root database access with a blank password on TCP/3306.**

This was not primarily a memory-corruption or command-execution exploit. The weakness was authentication and configuration: a privileged database account was remotely accessible without a password.

### Risk

An unauthorised root database session could expose or modify application data, users, schemas and configuration. Depending on server privileges and integration with applications, database compromise can also become part of a wider host compromise.

### Remediation

- Set a strong unique password for the database root account.
- Disable remote root login unless there is an unavoidable administrative requirement.
- Restrict database access by host/network.
- Bind the service only where necessary.
- Upgrade the unsupported MySQL version.
- Use separate, least-privileged application accounts rather than root.

---

# 10. NFS: a serious additional misconfiguration

Although NFS was not one of my final four, it produced one of the more significant additional findings.

I used `rpcinfo` to review the target's RPC services and `showmount -e` to inspect exported filesystems. The target exported the root filesystem `/` to `*`, meaning any host allowed by the surrounding network could request the export.

![Figure 50 - NFS services and exports enumerated](Metasploit%2011-09-26/Screenshot%202026-09-11%20043857.png)

*Figure 50. `rpcinfo` enumerated RPC/NFS services and `showmount -e` revealed that the target exported `/` to any host (`*`).*


My first mount attempt failed because I had not created the local mount-point directory. After creating the mount point, the NFS export mounted successfully and I could list the target filesystem from Kali.

![Figure 51 - NFS mount troubleshooting and success](Metasploit%2011-09-26/Screenshot%202026-09-11%20044444.png)

*Figure 51. The first mount attempt failed because the local mount-point directory did not exist. After creating it, the target's exported root filesystem mounted successfully and could be listed.*

![Figure 52 - Mounted NFS root filesystem](Metasploit%2011-09-26/Screenshot%202026-09-11%20044458.png)

*Figure 52. A fuller directory listing of the mounted target root preserved evidence that the export exposed the operating-system filesystem.*


I then unmounted it as part of cleanup.

![Figure 53 - NFS cleanup](Metasploit%2011-09-26/Screenshot%202026-09-11%20044714.png)

*Figure 53. The mounted NFS filesystem was unmounted after validation, documenting cleanup at the end of the test.*


### Finding

**Confirmed NFS export misconfiguration.**

The root filesystem was remotely exported and mountable from my lab machine. This is materially different from merely seeing TCP/2049 open.

### Remediation

- Never export `/` broadly.
- Restrict NFS exports to specific trusted hosts or networks.
- Use the minimum filesystem scope needed.
- Review `root_squash` and related permissions.
- Firewall NFS/RPC services from untrusted networks.

---

# 11. UnrealIRCd: "appears vulnerable" is not the same as "exploited"

Nmap had identified UnrealIRCd on TCP/6667. Metasploit contained a module for the well-known UnrealIRCd 3.2.8.1 backdoor, so I selected it and reviewed the options.

![Figure 54 - UnrealIRCd module selected](Metasploit%2011-09-26/Screenshot%202026-09-11%20045045.png)

*Figure 54. Metasploit located the UnrealIRCd 3.2.8.1 backdoor module associated with the service on TCP/6667, and its options were reviewed.*


When I ran the module, its automatic check reported that the target appeared vulnerable. However, the run completed without creating a session.

![Figure 55 - UnrealIRCd appeared vulnerable but no session](Metasploit%2011-09-26/Screenshot%202026-09-11%20045504.png)

*Figure 55. The module's automatic check reported that the target appeared vulnerable, but the run completed without creating a session. The payload was changed for troubleshooting.*


I tried additional compatible payload configurations. The module continued to report the service as vulnerable, but no session was created.

![Figure 56 - UnrealIRCd troubleshooting retained](Metasploit%2011-09-26/Screenshot%202026-09-11%20050741.png)

*Figure 56. Several additional payload attempts were tried, but no session was obtained. The finding remained unconfirmed despite the positive vulnerability check.*


### Final status

**Not confirmed as successfully exploited in my assessment.**

This is one of the most useful results in the whole exercise. A scanner/module confidence message is evidence, but it is not equivalent to a working session. I therefore did not write "UnrealIRCd exploited" in the findings table.

---

# 12. Core Port 4: 5900/tcp, VNC

## Authentication testing

The initial scan identified VNC protocol 3.3 on TCP/5900. I searched Metasploit for VNC modules and narrowed the results to the VNC login scanner.

![Figure 57 - VNC module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20050904.png)

*Figure 57. Metasploit was searched for VNC modules, exposing scanners and authentication-related options relevant to TCP/5900.*

![Figure 58 - VNC authentication modules identified](Metasploit%2011-09-26/Screenshot%202026-09-11%20050946.png)

*Figure 58. Further VNC search results showed the VNC login scanner among other modules. The authentication scanner was chosen for validation.*

![Figure 59 - VNC login scanner selected](Metasploit%2011-09-26/Screenshot%202026-09-11%20051045.png)

*Figure 59. The VNC login scanner was loaded and prepared for the target service.*


The scanner found a successful login using the password:

```text
password
```

No username was required by the VNC service in this test.

![Figure 60 - Weak VNC password confirmed](Metasploit%2011-09-26/Screenshot%202026-09-11%20051856.png)

*Figure 60. The VNC scanner reported a successful login using the password `password` with no username, confirming a weak authentication control on the lab service.*


## Manual validation

I then connected with TightVNC Viewer using the recovered lab password. Authentication succeeded and the remote desktop was displayed. A root terminal was visible inside the desktop session.

![Figure 61 - VNC access manually validated](Metasploit%2011-09-26/Screenshot%202026-09-11%20051949.png)

*Figure 61. TightVNC Viewer connected successfully using the discovered password and displayed the target desktop, where a root terminal was visible. This manually corroborated the scanner result.*


## Finding

**Confirmed weak VNC authentication and remote graphical access on TCP/5900.**

The important nuance is that the VNC password itself was not a "root password". The VNC service exposed an already-running graphical desktop environment in which a root terminal/session was present. The manual connection proved that the weak VNC password gave interactive access to that desktop.

### Risk

Weak remote-desktop authentication can provide direct interactive access to the machine. The impact depends on the privileges and state of the desktop session exposed through VNC.

### Remediation

- Use a strong unique VNC password.
- Restrict VNC to trusted administrative networks, VPN access or an SSH tunnel.
- Avoid exposing privileged desktop sessions.
- Use modern remote-administration tooling with stronger authentication and encryption where possible.

---

# 13. Findings summary

## Four required ports

| Port | Service | What I actually proved | Category | Severity in this lab |
|---:|---|---|---|---|
| **3632** | distccd | Command shell opened; `whoami` = `daemon` | Remote command execution | High |
| **139** | Samba 3.0.20 | Command shell opened; `whoami` = `root` | Root-level remote command execution | Critical |
| **3306** | MySQL 5.0.51a | Blank-password root login found and manually confirmed | Authentication/configuration weakness | Critical |
| **5900** | VNC 3.3 | Weak password found and graphical connection manually confirmed | Weak authentication / remote access | High |

## Additional services investigated

| Service/Port | Result | Classification | Confirmation level |
|---|---|---|---|
| SSH/22 | Known lab credentials authenticated; session opened | Weak/default credentials | Confirmed |
| SSH/22 | Usernames enumerated after fixing the user-file setting | Information disclosure | Confirmed enumeration |
| Telnet/23 | Known lab credentials authenticated; session opened as `msfadmin` | Weak credentials + insecure legacy protocol | Confirmed |
| SMTP/25 | Postfix version identified; multiple local usernames enumerated | Information disclosure | Confirmed enumeration |
| DNS/53 | BIND 9.4.2 independently returned by `version.bind` | Service/version disclosure | Confirmed fingerprint |
| HTTP/80 | WebDAV scanner reported disabled | Negative test result | Confirmed negative result |
| HTTP/80 | Multiple accessible directories discovered | Attack-surface exposure | Confirmed enumeration |
| HTTP/80 | Generic HTTP login scanner did not match phpMyAdmin auth | Tool/mechanism mismatch | Confirmed negative result |
| NFS/2049 + RPC | `/` exported to `*`; root filesystem mounted from Kali | Serious misconfiguration | Confirmed |
| IRC/6667 | Module said target appeared vulnerable, but no session was obtained | Candidate vulnerability | **Not confirmed exploited** |

---

# 14. Troubleshooting ledger

This assignment involved much more troubleshooting than the earlier exercises. I kept it because it shows where my understanding changed.

### SSH enumeration: bad username-file configuration

**Problem:** The enumeration module would not run correctly because the username source was not set to a valid file.  
**What I did:** Inspected `/usr/share/wordlists/` and the Metasploit wordlists, then set a valid user list.  
**Result:** Enumeration completed and returned usernames.  
**Lesson:** A module error can be a configuration problem, not a target-security result.

### distcc: bad file descriptor and no session

**Problem:** The first payload/module run produced a bad file descriptor and no working shell.  
**What I did:** Reviewed the module options and changed to another compatible command payload.  
**Result:** A command shell opened.  
**Lesson:** Payload compatibility and callback behavior matter separately from whether the underlying vulnerability exists.

### Samba: sessions opened and were closed while adjusting behavior

**Problem:** Early Samba sessions were opened but then closed/aborted during testing.  
**What I did:** Repeated the validation and checked the final session directly.  
**Result:** Reproducible command execution, with `whoami` returning root.  
**Lesson:** A clean privilege check is stronger evidence than simply seeing "session opened" in the console.

### WebDAV: banner assumption disproved

**Problem:** Apache's `DAV/2` banner suggested WebDAV might be relevant.  
**What I did:** Used a dedicated WebDAV scanner.  
**Result:** WebDAV was reported disabled.  
**Lesson:** Banner information can guide a test, but a feature name in a banner is not proof that a vulnerable configuration is active.

### HTTP login against phpMyAdmin: wrong authentication model

**Problem:** The generic HTTP login scanner did not find a URI requesting HTTP authentication.  
**What I did:** Read the output rather than assuming the credentials had simply failed.  
**Result:** The module was not appropriate for phpMyAdmin's application-level form login.  
**Lesson:** The authentication mechanism matters when choosing a scanner.

### MySQL: SSL/TLS compatibility error

**Problem:** The modern client initially refused the connection because of an SSL/TLS compatibility problem with the old lab server.  
**What I did:** Tried client options and eventually connected using the client's non-SSL mode.  
**Result:** Manual root login succeeded.  
**Lesson:** Manual validation can fail for client/server compatibility reasons even when the credentials are valid.

### NFS: mount point did not exist

**Problem:** The mount command failed because the local mount directory was missing.  
**What I did:** Created the mount point and reran the mount.  
**Result:** The export mounted and the target root filesystem was visible.  
**Lesson:** Not every error is security-related; basic Linux filesystem requirements still matter.

### UnrealIRCd: positive check, no session

**Problem:** The module reported that the target appeared vulnerable, but exploitation produced no session.  
**What I did:** Tried additional payload configurations.  
**Result:** Still no session.  
**Lesson:** I should report **what I proved**, not what I expected or what a module predicted.

---

# 15. Findings versus observations

One of my main learning goals was to stop using "vulnerability" as a catch-all word.

### Confirmed vulnerability or exploitable weakness

I use this label only where I demonstrated the security impact directly, for example:

- distcc produced a command shell.
- Samba produced a root command shell.
- MySQL accepted a remote root login without a password and I manually reproduced it.
- VNC accepted a weak password and I manually connected.
- NFS allowed the exported root filesystem to be mounted.

### Confirmed enumeration / information disclosure

These results exposed useful information but did not themselves grant control:

- SSH usernames.
- SMTP usernames.
- BIND version information.
- HTTP directory discovery.

### Authentication weakness

These involved valid credentials rather than a code-level exploit:

- SSH with the known Metasploitable credentials.
- Telnet with the known Metasploitable credentials.
- MySQL root with a blank password.
- VNC with the weak password `password`.

### Unconfirmed candidate

UnrealIRCd is the clearest example. Metasploit's check said it appeared vulnerable, but I did not obtain a session, so I did not mark exploitation as confirmed.

---

# 16. Remediation summary

| Area | Remediation priority |
|---|---|
| Legacy services | Remove services that are not needed and upgrade unsupported software. |
| Samba | Patch/upgrade immediately, remove unsafe legacy configuration and restrict SMB access. |
| distcc | Remove or isolate the service and restrict it to trusted build hosts only. |
| MySQL | Set strong passwords, disable remote root login, restrict network exposure and upgrade. |
| VNC | Replace weak passwords, restrict access and avoid exposing privileged desktop sessions. |
| SSH/Telnet | Eliminate default credentials; disable Telnet and use SSH with strong authentication. |
| NFS | Do not export `/`; restrict exports to explicit trusted hosts and least-required paths. |
| SMTP/DNS | Reduce unnecessary information disclosure and restrict administrative exposure. |
| HTTP | Remove unnecessary directories/apps, patch the web stack and enforce appropriate access controls. |
| Network architecture | Segment legacy services and firewall them from untrusted networks. |

---

# 17. Limitations

- Metasploitable 2 is intentionally vulnerable, so these results are not representative of a normally patched production Linux host.
- I did not attempt stealth, persistence, destructive actions, denial-of-service testing or evasion.
- I did not test any system outside my own authorised lab.
- Some services were taken only as far as enumeration because that was enough to answer the learning question at that point.
- I did not assign formal CVSS scores; the severity labels in this report are qualitative and specific to the demonstrated lab impact.
- Nmap and Metasploit output can contain false positives or imperfect service fingerprints, which is why I tried to validate important findings separately.
- The UnrealIRCd result remained unconfirmed because I did not obtain a working session.
- Screenshots preserve the practical process, but they are not a complete shell history of every command entered during the exercise.

---

# 18. Evidence and privacy

All 61 screenshots are retained in the repository because this project is primarily a **learning record**, not a polished client pentest report. Repeated screenshots and failed attempts therefore have value: they show how the work evolved and allow me to revisit errors later.

The visible target and attacker addresses are private RFC1918 lab IPs. No public target, personal account credential or third-party system was tested as part of this project.

For a professional client report I would normally curate the evidence more aggressively and avoid unnecessary screenshots. For this training portfolio I have intentionally preserved more of the process.

A screenshot-by-screenshot map is available in [`EVIDENCE-INDEX.md`](EVIDENCE-INDEX.md).

---

# 19. What I learned

This was the first exercise in which the practical value came as much from the **failed paths** as from the successful ones.

## Metasploit is a framework, not a magic exploit button

The repeated pattern became clearer:

```text
reconnaissance
    ↓
identify service/version
    ↓
research the service and likely issue
    ↓
search Metasploit
    ↓
select the correct module
    ↓
review required options
    ↓
configure target/callback/authentication inputs
    ↓
run
    ↓
interpret the result
    ↓
validate impact
    ↓
document honestly
```

I became more comfortable with `search`, `use`, `show options`, `set`, `run`, `sessions`, `sessions -i` and checking the resulting shell with commands such as `whoami`.

## Module categories matter

An auxiliary scanner can perform version detection, login testing or enumeration without being an exploit. An exploit module is intended to trigger a vulnerability. A successful login from a scanner is still security-relevant, but it should be described as an authentication weakness rather than pretending software exploitation occurred.

## RHOSTS/RPORT versus LHOST/LPORT

I also reinforced the direction of the connection:

- `RHOSTS` = remote target host(s).
- `RPORT` = remote target service port.
- `LHOST` = my Kali address when a payload needs to connect back.
- `LPORT` = the local listening port used for that callback.

Understanding the direction became particularly important when troubleshooting distcc, Samba and UnrealIRCd sessions.

## A session must still be interpreted

The distcc shell ran as `daemon`, while the Samba shell ran as `root`. Both were successful command execution, but they were not equivalent in impact. Checking the current user turned "session opened" into much more meaningful evidence.

## Manual validation made the report stronger

The MySQL scanner result became more convincing when I manually connected as root. The VNC scanner result became more convincing when TightVNC Viewer opened the remote desktop. This made me appreciate why independent corroboration matters.

## Negative results are still results

WebDAV being disabled, phpMyAdmin not using HTTP Basic authentication, and UnrealIRCd failing to create a session all prevented me from making claims the evidence did not support.

The biggest lesson was therefore not a particular Metasploit command. It was learning to ask:

> **What exactly did this result prove?**

---

# 20. Conclusion

The assignment required four ports, but working independently led me to investigate a broader set of services. The four strongest core findings were distcc remote command execution, Samba root-level command execution, blank-password MySQL root access and weak VNC authentication with confirmed remote desktop access.

The additional services were equally useful for learning because they showed different categories of result: default credentials on SSH and Telnet, account enumeration through SMTP, version disclosure through DNS, exposed web paths, a severe NFS export misconfiguration, and an UnrealIRCd candidate that I deliberately left unconfirmed because no session was created.

The practical exercise moved me away from thinking in terms of "find old version, run exploit" and toward a more disciplined workflow: **discover, research, test, troubleshoot, validate, classify, document**.

That distinction is what I would carry forward into later assessments.

---

## Lab-use statement

This repository documents cybersecurity exercises performed solely against **Metasploitable 2**, an intentionally vulnerable training VM, in my authorised local lab. The material is retained as evidence of my coursework and learning process.
