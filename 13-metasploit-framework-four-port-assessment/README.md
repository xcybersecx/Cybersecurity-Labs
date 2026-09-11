# Metasploit Framework: Four-Port Assessment

**Completed:** 11 September 2026  
**Environment:** Kali Linux and Metasploitable 2 in my authorised VirtualBox lab  
**Assignment requirement:** investigate at least four exposed ports/services and document the practical work  
**Evidence style:** chronological learning record

## Overview

This exercise was part of my hands-on cybersecurity training. The assignment required me to investigate at least four ports on Metasploitable 2, but I ended up exploring several additional services while trying to understand how reconnaissance, enumeration, authentication testing, Metasploit modules, troubleshooting and validation fit together.

I have written this README in the order I actually worked. I kept screenshots that show a **new step, new result, error, decision, pivot or validation**, and removed only screenshots that repeated the same information.

The four ports I ultimately used as the main assignment findings were:

| Port | Service | What I confirmed |
|---:|---|---|
| **3632/tcp** | distccd | Remote command execution, shell opened as `daemon` |
| **139/tcp** | Samba 3.0.20-Debian | Remote command execution, shell confirmed as `root` |
| **3306/tcp** | MySQL 5.0.51a | Remote root database login with a blank password |
| **5900/tcp** | VNC | Weak password identified and remote desktop access confirmed |

I also investigated SSH, Telnet, SMTP, DNS/BIND, HTTP/WebDAV, NFS and UnrealIRCd. I have kept those parts because they were useful to my learning, even where they did not become one of the four final ports.

## Lab scope

| Item | Value |
|---|---|
| Attacking machine | Kali Linux |
| Target | Metasploitable 2 |
| Network | Private local VirtualBox lab |
| Main tools | Nmap, Metasploit Framework, Searchsploit/Exploit-DB, MySQL client, NFS tools, TightVNC Viewer |
| Authorisation | My own intentionally vulnerable training environment |

The IP addresses visible in the screenshots are private lab addresses. No public or third-party systems were tested.

---

# Chronological practical record


## 1. Initial connectivity and first service scan

I started by checking that the Metasploitable 2 VM was reachable, then ran an Nmap service/version scan. This gave me my first picture of the target and showed how many services were exposed.

```bash
ping <TARGET_IP>
sudo nmap -sV <TARGET_IP>
```

The scan showed services including FTP, SSH, Telnet, SMTP, DNS, HTTP, Samba, NFS, MySQL, PostgreSQL, distccd, VNC, IRC and Tomcat.

At this stage, these were only **services and leads**. I had not proved that any particular service was vulnerable.


![Figure 1 - Baseline connectivity and service-version scan](Metasploit%2011-09-26/Screenshot%202026-09-10%20215434.png)

*Figure 1. Ping to the Metasploitable 2 host succeeded, followed by an Nmap service/version scan that exposed a large intentionally vulnerable attack surface.*


## 2. SSH: successful login, then an enumeration problem

The first service I explored further was SSH. I used the SSH login scanner with the known Metasploitable training credentials. Authentication succeeded and a session was opened.

This was useful because it helped me separate **valid credentials** from **software exploitation**. I had accessed SSH, but I had not exploited OpenSSH itself.


![Figure 2 - SSH login scanner and successful session](Metasploit%2011-09-26/Screenshot%202026-09-10%20230829.png)

*Figure 2. Metasploit's SSH login scanner was configured with the lab's known training credentials. Authentication succeeded and an SSH session was opened.*


I then tried SSH user enumeration. My first problem was not the target, it was my own module configuration. The enumeration module needed a valid username list, so I checked the available Metasploit wordlists and corrected the setting.


![Figure 3 - SSH enumeration troubleshooting](Metasploit%2011-09-26/Screenshot%202026-09-10%20231702.png)

*Figure 3. The SSH user-enumeration module initially needed a valid username list. The Metasploit wordlist directory was inspected and a suitable list was selected.*


## 3. Returning to reconnaissance with a full TCP scan

After the early SSH work, I went back to reconnaissance and started a broader Nmap scan so I had a better service baseline before continuing.

```bash
nmap -p- -sV -sC -O -v -oA initial_scan <TARGET_IP>
```

What I learned from the flags:

- `-p-` scans all TCP ports.
- `-sV` attempts service/version detection.
- `-sC` runs Nmap's default scripts.
- `-O` attempts OS detection.
- `-v` gives more progress/output detail.
- `-oA` saves the scan in several formats.


![Figure 4 - Full TCP scan in progress](Metasploit%2011-09-26/Screenshot%202026-09-10%20232629.png)

*Figure 4. A full-port Nmap scan with service detection, default scripts, OS detection and output logging was started to build a broader evidence base.*


![Figure 5 - Detailed Nmap results, early services](Metasploit%2011-09-26/Screenshot%202026-09-10%20233602.png)

*Figure 5. The detailed scan recorded FTP, SSH, Telnet and SMTP information, including service banners and script output.*


![Figure 6 - Detailed Nmap results, DNS/HTTP/SMB/MySQL](Metasploit%2011-09-26/Screenshot%202026-09-10%20233643.png)

*Figure 6. The scan continued through DNS, HTTP, RPC, Samba and MySQL, giving service versions and protocol details used later in the assessment.*


![Figure 7 - Detailed Nmap results, later services](Metasploit%2011-09-26/Screenshot%202026-09-10%20233945.png)

*Figure 7. The scan identified distccd, VNC, UnrealIRCd, Tomcat and additional RPC services, expanding the shortlist of services worth investigating.*


![Figure 8 - Operating-system and SMB host-script results](Metasploit%2011-09-26/Screenshot%202026-09-10%20234120.png)

*Figure 8. Nmap's OS and SMB scripts reported Linux 2.6.x characteristics, Samba 3.0.20-Debian and SMB security details.*


The fuller scan gave me several services that looked worth investigating, including Samba 3.0.20-Debian, MySQL 5.0.51a, distccd, VNC, UnrealIRCd, BIND and NFS.

Again, I treated the scan as a **map**, not as proof that those services were exploitable.


## 4. SSH enumeration completed

After correcting the username-list setting, I returned to the SSH enumeration module. This time it completed and identified multiple valid-looking usernames.

I recorded this as **enumeration/information disclosure**, not compromise.


![Figure 9 - SSH user enumeration completed](Metasploit%2011-09-26/Screenshot%202026-09-11%20001440.png)

*Figure 9. After correcting the wordlist setting, the SSH enumeration module identified multiple valid-looking local usernames. This was recorded as enumeration, not compromise.*


## 5. Telnet: research, scanner selection and session validation

I moved to Telnet next. I searched the available tools/modules first instead of assuming that an old Telnet service automatically meant a particular exploit applied.


![Figure 10 - Telnet research and module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20002704.png)

*Figure 10. Searchsploit and Metasploit searches were used to investigate Telnet-related possibilities rather than assuming the service banner alone proved a vulnerability.*


I reviewed the Telnet version-scanner options and then the Telnet login scanner. This was useful because I was beginning to understand the difference between modules that identify a service and modules that test authentication.


![Figure 11 - Telnet version module options](Metasploit%2011-09-26/Screenshot%202026-09-11%20003508.png)

*Figure 11. The Telnet version scanner was reviewed to understand the target and port settings before use.*


![Figure 12 - Telnet login scanner selected](Metasploit%2011-09-26/Screenshot%202026-09-11%20004509.png)

*Figure 12. The Telnet authentication scanner was selected and its required options reviewed.*


Using the known Metasploitable training credentials, the Telnet login succeeded and a command session was opened.


![Figure 13 - Telnet training credentials accepted](Metasploit%2011-09-26/Screenshot%202026-09-11%20004634.png)

*Figure 13. The known Metasploitable training credentials authenticated successfully and opened a Telnet session.*


I entered the session and checked the user context. `whoami` returned `msfadmin`.

What this showed me: the service was accessible with weak/default lab credentials, but this was still **credential-based access**, not proof that I had exploited the Telnet software itself.


![Figure 14 - Telnet session validation](Metasploit%2011-09-26/Screenshot%202026-09-11%20005111.png)

*Figure 14. The active sessions list was inspected, the Telnet session was entered, and `whoami` returned the `msfadmin` user. Network information was also checked from the session.*


## 6. SMTP: version detection and username enumeration

I then investigated SMTP. I first searched for relevant SMTP modules, then used the version scanner to confirm the Postfix service.


![Figure 15 - SMTP module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20005324.png)

*Figure 15. The SMTP service was investigated by searching for version and enumeration modules.*


![Figure 16 - SMTP version confirmed](Metasploit%2011-09-26/Screenshot%202026-09-11%20010031.png)

*Figure 16. The SMTP version scanner identified Postfix on the target, after which the SMTP user-enumeration module was selected.*


I ran SMTP user enumeration and obtained a list of local usernames. I treated this as **information disclosure** rather than account compromise.


![Figure 17 - SMTP user enumeration](Metasploit%2011-09-26/Screenshot%202026-09-11%20010611.png)

*Figure 17. The SMTP enumeration module completed and returned a set of local usernames. This was treated as information disclosure and reconnaissance evidence, not account compromise.*


I also looked through SMTP exploit modules for research. The existence of an exploit module was not enough for me to claim that the target was vulnerable to it.


![Figure 18 - SMTP exploit search](Metasploit%2011-09-26/Screenshot%202026-09-11%20011122.png)

*Figure 18. A wider Metasploit search for SMTP-related exploit modules was performed for research. No exploit was claimed solely because modules existed.*


## 7. Port 3632, distccd: first required-port finding

The full scan had identified distccd on TCP/3632. I selected the relevant Metasploit module and reviewed its required options before running it.


![Figure 19 - distcc module selected](Metasploit%2011-09-26/Screenshot%202026-09-11%20014731.png)

*Figure 19. The distcc command-execution module was selected after the service was identified on TCP/3632. Required host and payload settings were reviewed.*


![Figure 20 - distcc options verified](Metasploit%2011-09-26/Screenshot%202026-09-11%20014825.png)

*Figure 20. The distcc module configuration was checked before execution, including the target host, target port and local callback settings.*


### First attempt

My first run failed with a bad file descriptor error and did not give me a usable session. I kept this screenshot because it was part of the actual troubleshooting, not something I wanted to hide from the final write-up.


![Figure 21 - First distcc attempt failed](Metasploit%2011-09-26/Screenshot%202026-09-11%20015136.png)

*Figure 21. The initial distcc attempt produced a bad file descriptor error and did not create a usable session. The failure was retained as troubleshooting evidence.*


### Retry and validation

After changing the payload configuration, I retried the test and a command shell opened.


![Figure 22 - distcc retry opened a shell](Metasploit%2011-09-26/Screenshot%202026-09-11%20015507.png)

*Figure 22. After changing the payload configuration, the distcc attempt opened a command-shell session. This converted a version-based lead into validated command execution.*


I checked the account context with `whoami`, which returned `daemon`.

**What I confirmed:** remote command execution worked, but the initial shell was not root.


![Figure 23 - distcc privilege level checked](Metasploit%2011-09-26/Screenshot%202026-09-11%20015742.png)

*Figure 23. Inside the distcc-created shell, `whoami` returned `daemon`, showing that remote command execution was confirmed but the initial session was not root.*


## 8. DNS/BIND: confirming a version without overclaiming

Next I looked at the DNS service. I queried `version.bind` and independently confirmed BIND 9.4.2.


![Figure 24 - BIND version independently queried](Metasploit%2011-09-26/Screenshot%202026-09-11%20020720.png)

*Figure 24. A CHAOS TXT `version.bind` query returned BIND 9.4.2, independently corroborating Nmap's DNS service fingerprint.*


I then searched Metasploit for DNS/BIND-related modules and narrowed the research toward the exact service family seen during reconnaissance.


![Figure 25 - DNS version-module research](Metasploit%2011-09-26/Screenshot%202026-09-11%20020938.png)

*Figure 25. Metasploit was searched for DNS version-related modules to understand what could be enumerated or checked next.*


![Figure 26 - ISC BIND research](Metasploit%2011-09-26/Screenshot%202026-09-11%20021452.png)

*Figure 26. A search for ISC BIND-related modules was performed using the exact service family identified during reconnaissance.*


![Figure 27 - BIND exploit results reviewed](Metasploit%2011-09-26/Screenshot%202026-09-11%20021841.png)

*Figure 27. Additional BIND-related results were reviewed, but no successful exploit validation was obtained during this stage.*


I did not obtain a confirmed exploit from this part of the exercise. I therefore left it as **service fingerprinting and research** rather than turning the version number into a vulnerability claim.


## 9. Port 139, Samba: second required-port finding

I moved to Samba after the scan identified Samba 3.0.20-Debian. I searched Metasploit for Samba modules and found the `usermap_script` command-execution module among the results.


![Figure 28 - Samba module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20023051.png)

*Figure 28. A Metasploit search for Samba showed several modules, including the `usermap_script` command-execution module relevant to the target's Samba 3.0.20 service.*


I also checked independent vulnerability information in Exploit-DB so I could understand why that module was relevant to the version I had observed.


![Figure 29 - Exploit-DB corroboration for Samba](Metasploit%2011-09-26/Screenshot%202026-09-11%20024021.png)

*Figure 29. Exploit-DB documented Samba 3.0.20 through 3.0.25rc3 username-map-script command execution and linked it to CVE-2007-2447.*


### First successful shell

The first run opened a command shell. I later closed/adjusted sessions while trying to understand the session behaviour.


![Figure 30 - First Samba command-shell run](Metasploit%2011-09-26/Screenshot%202026-09-11%20030047.png)

*Figure 30. The Samba usermap module opened a command shell. That session was later closed while the payload and session behavior were being adjusted.*


A later run opened another shell, which made the result more reproducible rather than being a one-off.


![Figure 31 - Samba retry and session behavior](Metasploit%2011-09-26/Screenshot%202026-09-11%20030739.png)

*Figure 31. A later run again opened a command shell. The repeated result increased confidence that the finding was reproducible within the lab.*


I entered the session and checked the user context. `whoami` returned `root`.

**What I confirmed:** remote command execution through Samba, with root-level privileges in the Metasploitable 2 lab.


![Figure 32 - Samba root-level command execution confirmed](Metasploit%2011-09-26/Screenshot%202026-09-11%20032259.png)

*Figure 32. A subsequent Samba session was entered and `whoami` returned `root`, confirming root-level remote command execution in the Metasploitable lab.*


## 10. HTTP/Apache: testing an assumption and changing direction

The Apache banner included DAV/2, so I researched WebDAV first. I did not assume the banner meant WebDAV was actually enabled in a useful way.


![Figure 33 - Apache/WebDAV research](Metasploit%2011-09-26/Screenshot%202026-09-11%20033844.png)

*Figure 33. The Apache 2.2.8 DAV/2 banner was researched to identify likely configuration and WebDAV questions to test rather than jumping directly to an exploit claim.*


I searched for WebDAV-related scanners/modules and then tested the service.


![Figure 34 - WebDAV module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20034506.png)

*Figure 34. Metasploit was searched for WebDAV-related scanners and modules that could test whether DAV functionality was actually enabled.*


The WebDAV scanner reported that WebDAV was disabled. This was a useful **negative result** because it stopped me following the wrong path.


![Figure 35 - WebDAV disabled](Metasploit%2011-09-26/Screenshot%202026-09-11%20034801.png)

*Figure 35. The WebDAV scanner reported that WebDAV was disabled on the target. This negative result was preserved because it ruled out one assumed attack path.*


I then pivoted to HTTP directory enumeration.


![Figure 36 - HTTP troubleshooting and pivot](Metasploit%2011-09-26/Screenshot%202026-09-11%20035257.png)

*Figure 36. After WebDAV produced no useful path, the workflow pivoted to HTTP directory enumeration and the directory-scanner options were reviewed.*


The directory scan identified paths including `/cgi-bin/`, `/doc/`, `/icons/`, `/phpMyAdmin/` and `/test/`.

I treated these as exposed web attack surface, not as proof that the web server had been compromised.


![Figure 37 - HTTP directory enumeration](Metasploit%2011-09-26/Screenshot%202026-09-11%20035348.png)

*Figure 37. The directory scan identified exposed paths including `/cgi-bin/`, `/doc/`, `/icons/`, `/phpMyAdmin/` and `/test/`. These were recorded as exposed attack surface, not proof of compromise.*


I also reviewed the generic HTTP login scanner and tried it against phpMyAdmin.


![Figure 38 - HTTP login-scanner options](Metasploit%2011-09-26/Screenshot%202026-09-11%20035728.png)

*Figure 38. The generic HTTP login scanner was reviewed to see whether an exposed web path used HTTP authentication.*


The result showed that the selected module expected HTTP authentication, while phpMyAdmin was using a different application-level login mechanism. That taught me that choosing a scanner requires understanding **how the authentication actually works**.


![Figure 39 - phpMyAdmin did not present HTTP auth](Metasploit%2011-09-26/Screenshot%202026-09-11%20040138.png)

*Figure 39. Testing `/phpMyAdmin/` with the generic HTTP login module returned that no URI was found requesting HTTP authentication. The module therefore did not fit the application's authentication mechanism.*


## 11. Port 3306, MySQL: third required-port finding

I then tested the MySQL service. The Metasploit login scanner identified the old MySQL version and successfully authenticated the `root` database account with a blank password.


![Figure 40 - MySQL blank-root authentication found](Metasploit%2011-09-26/Screenshot%202026-09-11%20040547.png)

*Figure 40. The MySQL login scanner identified MySQL 5.0.51a and successfully authenticated the `root` database account with a blank password.*


I wanted to verify that result manually rather than relying only on the scanner. My first manual client attempt ran into an SSL/TLS compatibility problem because the client was much newer than the lab server.

After adjusting the client connection for the old lab environment, I successfully entered the MySQL/MariaDB monitor as root.

**What I confirmed:** privileged database access was possible without a root password.


![Figure 41 - MySQL manually validated](Metasploit%2011-09-26/Screenshot%202026-09-11%20041142.png)

*Figure 41. Manual client testing initially hit SSL compatibility errors. Using the client's non-SSL option allowed entry to the MariaDB/MySQL monitor as root, independently confirming the authentication weakness.*


## 12. NFS: an additional configuration weakness

NFS was not one of the four ports I ultimately used for the assignment, but it produced an important additional result.

I used `rpcinfo` and `showmount -e` to inspect the RPC/NFS services and exports. The target exposed the root filesystem `/` to `*`.


![Figure 42 - NFS services and exports enumerated](Metasploit%2011-09-26/Screenshot%202026-09-11%20043857.png)

*Figure 42. `rpcinfo` enumerated RPC/NFS services and `showmount -e` revealed that the target exported `/` to any host (`*`).*


My first mount attempt failed because the local mount-point directory did not exist. I created the directory and tried again. The export then mounted successfully.


![Figure 43 - NFS mount troubleshooting and success](Metasploit%2011-09-26/Screenshot%202026-09-11%20044444.png)

*Figure 43. The first mount attempt failed because the local mount-point directory did not exist. After creating it, the target's exported root filesystem mounted successfully and could be listed.*


I listed the mounted filesystem and could see the target's root filesystem from Kali.

This was a good example of why I should not confuse a Linux error with a security result. The first failure was simply my missing local directory. Once that was fixed, the actual NFS exposure could be validated.


![Figure 44 - Mounted NFS root filesystem](Metasploit%2011-09-26/Screenshot%202026-09-11%20044458.png)

*Figure 44. A fuller directory listing of the mounted target root preserved evidence that the export exposed the operating-system filesystem.*


I unmounted the share afterwards as part of cleanup.


![Figure 45 - NFS cleanup](Metasploit%2011-09-26/Screenshot%202026-09-11%20044714.png)

*Figure 45. The mounted NFS filesystem was unmounted after validation, documenting cleanup at the end of the test.*


## 13. UnrealIRCd: a positive check without a successful session

I next investigated the IRC service on TCP/6667. Metasploit contained a module for the UnrealIRCd 3.2.8.1 backdoor, so I selected it and reviewed its options.


![Figure 46 - UnrealIRCd module selected](Metasploit%2011-09-26/Screenshot%202026-09-11%20045045.png)

*Figure 46. Metasploit located the UnrealIRCd 3.2.8.1 backdoor module associated with the service on TCP/6667, and its options were reviewed.*


The module's automatic check reported that the target appeared vulnerable, but the run completed without creating a session.


![Figure 47 - UnrealIRCd appeared vulnerable but no session](Metasploit%2011-09-26/Screenshot%202026-09-11%20045504.png)

*Figure 47. The module's automatic check reported that the target appeared vulnerable, but the run completed without creating a session. The payload was changed for troubleshooting.*


I tried additional compatible payload configurations, but I still did not obtain a session.

**Final status:** I did **not** record this as successfully exploited. This became one of the clearest lessons from the assignment: *appears vulnerable* is not the same as *I proved successful exploitation*.


![Figure 48 - UnrealIRCd troubleshooting retained](Metasploit%2011-09-26/Screenshot%202026-09-11%20050741.png)

*Figure 48. Several additional payload attempts were tried, but no session was obtained. The finding remained unconfirmed despite the positive vulnerability check.*


## 14. Port 5900, VNC: fourth required-port finding

Finally, I investigated VNC. I searched the available VNC modules and selected the login scanner.


![Figure 49 - VNC module search](Metasploit%2011-09-26/Screenshot%202026-09-11%20050904.png)

*Figure 49. Metasploit was searched for VNC modules, exposing scanners and authentication-related options relevant to TCP/5900.*


![Figure 50 - VNC login scanner selected](Metasploit%2011-09-26/Screenshot%202026-09-11%20051045.png)

*Figure 50. The VNC login scanner was loaded and prepared for the target service.*


The scanner identified a working VNC password: `password`.


![Figure 51 - Weak VNC password confirmed](Metasploit%2011-09-26/Screenshot%202026-09-11%20051856.png)

*Figure 51. The VNC scanner reported a successful login using the password `password` with no username, confirming a weak authentication control on the lab service.*


I then used TightVNC Viewer to verify the result manually. The connection succeeded and displayed the Metasploitable desktop.

A root terminal was visible inside that already-running desktop session. I therefore describe the finding carefully: the weak VNC password gave me access to the graphical session, it was **not** a recovered root password.

**What I confirmed:** weak VNC authentication and working remote desktop access.


![Figure 52 - VNC access manually validated](Metasploit%2011-09-26/Screenshot%202026-09-11%20051949.png)

*Figure 52. TightVNC Viewer connected successfully using the discovered password and displayed the target desktop, where a root terminal was visible. This manually corroborated the scanner result.*


---

# Findings summary

## Four ports used for the assignment

| Port | Service | What I actually proved | Type of result |
|---:|---|---|---|
| **3632** | distccd | Command shell opened; `whoami` returned `daemon` | Remote command execution |
| **139** | Samba 3.0.20 | Command shell opened; `whoami` returned `root` | Root-level remote command execution |
| **3306** | MySQL 5.0.51a | Root login worked with a blank password and was manually verified | Authentication/configuration weakness |
| **5900** | VNC | Weak password worked and remote desktop access was manually verified | Weak authentication / remote access |

## Other services I investigated

| Service | What happened | How I classified it |
|---|---|---|
| SSH | Known lab credentials worked; usernames were also enumerated | Weak credentials + enumeration |
| Telnet | Known lab credentials worked; session opened as `msfadmin` | Weak credentials / insecure legacy protocol |
| SMTP | Local usernames were enumerated | Information disclosure |
| DNS/BIND | Version independently confirmed; exploit research did not lead to a validated session | Fingerprinting / research |
| HTTP/WebDAV | WebDAV disabled; directories enumerated; phpMyAdmin auth module did not match | Negative result + enumeration |
| NFS | Root filesystem export could be mounted | Confirmed configuration weakness |
| UnrealIRCd | Module said target appeared vulnerable, but no session was created | Unconfirmed candidate |

---

# Troubleshooting I want to remember

This exercise had several problems that were useful to keep:

- **SSH enumeration:** my username-file setting was wrong, so I had to find and use a valid wordlist.
- **distcc:** the first payload attempt failed with a bad file descriptor; a later compatible configuration opened a shell.
- **Samba:** I opened, closed and retried sessions while learning how the session behaviour worked, then validated the final shell with `whoami`.
- **WebDAV:** the Apache banner suggested a direction, but the dedicated scanner showed WebDAV was disabled.
- **phpMyAdmin:** the generic HTTP login scanner was the wrong authentication model for that application.
- **MySQL:** manual validation initially failed because of SSL/TLS compatibility between a modern client and the old lab server.
- **NFS:** the first mount error was caused by a missing local mount-point directory.
- **UnrealIRCd:** the module reported the target appeared vulnerable, but I did not get a session, so I did not claim successful exploitation.

---

# What I learned

The biggest change for me was learning to ask **what a result actually proves**.

I started to separate:

- an open port from a vulnerability;
- a service/version match from a confirmed exploit;
- valid credentials from software exploitation;
- enumeration from compromise;
- a Metasploit `check` result from a working session;
- a shell running as a normal account from a shell running as root.

I also became more comfortable with the basic Metasploit flow:

```text
reconnaissance
→ identify service/version
→ research
→ search for a relevant module
→ review options
→ configure
→ run
→ interpret the result
→ validate
→ document what actually happened
```

I also reinforced the meaning of:

- `RHOSTS` = the remote target.
- `RPORT` = the remote service port.
- `LHOST` = my Kali address when a callback is needed.
- `LPORT` = the local listening port used for that callback.

The manual checks mattered too. MySQL became stronger evidence when I could reproduce the login manually. The VNC result became stronger when I could connect with a separate VNC client. `whoami` helped me understand the difference between the distcc shell running as `daemon` and the Samba shell running as `root`.

---

# Basic security takeaways

I am still learning, so I have kept this section intentionally simple rather than writing recommendations as if this were a professional client report.

- Old or intentionally vulnerable services should be patched, upgraded, removed or isolated when they are not needed.
- Administrative accounts should not use blank or weak passwords.
- Remote services such as SMB, databases, VNC and NFS should be restricted to systems that actually need access.
- NFS should not broadly export sensitive filesystem locations such as `/`.
- Legacy protocols such as Telnet should not be used for secure remote administration.
- A finding should be validated before I describe it as confirmed.

---

# Limitations

- Metasploitable 2 is intentionally vulnerable and is not representative of a normally patched production host.
- I did not test any system outside my authorised lab.
- I did not attempt stealth, persistence, destructive actions, denial-of-service testing or evasion.
- Some services were taken only as far as enumeration because that was enough for the learning goal.
- The UnrealIRCd result remained unconfirmed because I did not obtain a working session.
- The screenshots document the practical sequence but are not a complete shell history of every command I typed.

---

# Evidence note

The repository contains the full original screenshot set in `Metasploit 11-09-26/`.

This README shows the practical work **in chronological order** and omits only near-duplicate captures or repeated screens that did not add a new step or result. The purpose is for me to be able to reopen this project later and follow my own learning from beginning to end without having to jump between separate evidence documents.

---

# Conclusion

The assignment asked for four ports, but the process became a broader lesson in how to investigate services without calling everything an exploit.

The four main results were:

1. distcc remote command execution;
2. Samba root-level remote command execution;
3. blank-password MySQL root access; and
4. weak VNC authentication with confirmed remote desktop access.

The additional SSH, Telnet, SMTP, DNS, HTTP, NFS and UnrealIRCd work was useful because it showed me different kinds of results, including weak credentials, enumeration, configuration weaknesses, negative results and an unconfirmed candidate.

The most important lesson was not a particular Metasploit command. It was learning to document **what I actually proved**, including when something failed.

---

## Lab-use statement

This repository documents cybersecurity exercises performed solely against **Metasploitable 2**, an intentionally vulnerable training VM in my authorised local lab.

