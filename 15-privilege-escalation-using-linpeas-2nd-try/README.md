# Privilege Escalation Using LinPEAS: Second Try

| **Date** | 24 September 2026 |
|---|---|
| **Environment** | Kali Linux and Metasploitable 2 virtual machines in Oracle VirtualBox |
| **Tools** | Metasploit Framework, LinPEAS, OpenSSH/Linux shell commands, `wget`, `curl`, `ss`, `ping` |
| **Kali VM** | `192.168.1.115` |
| **Target VM** | `192.168.1.116` |
| **Scope** | My own deliberately vulnerable home-lab virtual machine |
| **Evidence** | 43 original screenshots in `images/`, ordered by capture time |

**Purpose: authorised cybersecurity training, Linux enumeration and privilege-escalation assessment in a controlled home lab.**

## 1. Overview

This was my **second attempt at using LinPEAS on Metasploitable 2**, and this time I wanted to go further than simply getting a session and running a script. I tried several service routes, used the access I gained to run LinPEAS, and paid attention to which account each session gave me.

I had several successful results in one lab: **a root shell through Samba**, Meterpreter sessions through VSFTPD, Tomcat, PostgreSQL and Java RMI, and a command shell through DistCC after my first payload failed. The Samba result was particularly satisfying because I checked it myself with `whoami`, and the terminal returned `root`.

The session was also messy in a very real way. I had a broken `locate` database, tried normal Linux commands at a Meterpreter prompt, changed routes when sessions closed, corrected settings and restarted LinPEAS under different accounts. Those moments are staying in this record because they show how I actually worked through the lab.

My overall aim was to become more confident with **initial access, shell handling, Linux enumeration and recognising possible privilege-escalation paths**. I was able to compare a root shell with sessions under service accounts such as `tomcat5`, `postgres` and `daemon`. I also began to understand why LinPEAS gives me leads to investigate rather than a one-click answer.

---

## 2. Objectives

For this exercise, I wanted to:

- gain access to the lab VM through different vulnerable services;
- transfer LinPEAS and run it from the access I had obtained;
- practise moving between Meterpreter and a regular Linux shell;
- check the user context of each session where possible;
- explore permissions, cron jobs, processes, environment variables and kernel-related leads;
- learn from failed commands and payloads, not just the successful ones; and
- keep a screenshot trail that would let me explain my steps afterwards.

---

## 3. Scope and Lab Environment

I carried out the exercise against **my own deliberately vulnerable Metasploitable 2 VM**. My Kali and target machines were on the same private lab network:

`Kali Linux (192.168.1.115) → Metasploitable 2 (192.168.1.116)`

I had already assessed this machine in earlier projects, so I carried that context into this attempt rather than starting the write-up with a scan I did not perform during this particular session.

---

## 4. Locating LinPEAS and a Misleading Download

I started by looking for `linpeas.sh`, but `locate` gave me a short-read error suggesting its database was damaged. I went into `~/Downloads` and tried `wget` with the GitHub homepage. That saved `index.html`, which was not what I wanted. It was a useful little reminder to check what actually arrived after a download.

Luckily, `ls` showed that `linpeas.sh` was already sitting in `~/Downloads`, so I had the file I needed for the next stage.

![Figure 1: My initial file-location problem, the GitHub homepage download, and the existing LinPEAS script in Downloads.](images/01-locate-database-error-and-github-test.png)

*Figure 1. My initial file-location problem, the GitHub homepage download, and the existing LinPEAS script in Downloads.*

### What I learned

I learned not to confuse a successful download with downloading the correct file. I also learned that a broken `locate` database says more about the index than about whether my file is present.

---

## 5. Initial VSFTPD Session and LinPEAS Transfer

I began with the VSFTPD backdoor, which opened a Meterpreter session on Metasploitable 2. I checked the connections from Kali while it was open.

![Figure 2: The VSFTPD-based session and an accompanying socket check.](images/02-vsftpd-session-and-socket-check.png)

*Figure 2. The VSFTPD-based session and an accompanying socket check.*

I looked around the filesystem and moved into `/tmp`. Then I tried `wget` and `nc` at the Meterpreter prompt. Neither worked. I was still slipping between thinking of Meterpreter as a normal Linux shell and remembering that it has its own command set.

I changed approach and used Meterpreter's `upload` command. That successfully transferred my local `linpeas.sh` into `/tmp` on the target.

![Figure 3: The unsuccessful Meterpreter `wget`/`nc` attempts followed by a successful `upload` of `linpeas.sh`.](images/03-meterpreter-upload-after-unsupported-commands.png)

*Figure 3. The unsuccessful Meterpreter `wget`/`nc` attempts followed by a successful `upload` of `linpeas.sh`.*

I opened a system shell, changed to `/tmp`, made the script executable, and ran it:

```sh
cd /tmp
chmod +x linpeas.sh
./linpeas.sh
```

![Figure 4: The switch from Meterpreter to a normal shell and the first LinPEAS execution.](images/04-local-shell-and-first-linpeas-launch.png)

*Figure 4. The switch from Meterpreter to a normal shell and the first LinPEAS execution.*

![Figure 5: The first LinPEAS banner and colour legend.](images/05-first-linpeas-banner.png)

*Figure 5. The first LinPEAS banner and colour legend.*

### What I understood

I now understood the difference between getting a file onto the machine and actually running it. Once I entered a system shell, I could use `chmod`, execute the script, and see the LinPEAS banner appear.

---

## 6. Exploring the First LinPEAS Results

The first LinPEAS run gave me plenty to look at. I spent time on the scheduled-task section, where it highlighted cron paths, showed the hourly/daily/weekly/monthly jobs, and marked several cron directories as writable.

That caught my attention as something to investigate further, especially in a lower-privileged account. The output told me where to look; I had not yet tried changing a job or observing it run.

![Figure 6: LinPEAS checks of cron directories and scheduled-task entries.](images/06-first-linpeas-cron-permission-flags.png)

*Figure 6. LinPEAS checks of cron directories and scheduled-task entries.*

The output also displayed service/configuration text, including Postfix-related settings. I later interrupted the output and backgrounded the shell channel rather than keeping this long run open indefinitely.

![Figure 7: Configuration output and backgrounding the first shell channel.](images/07-first-linpeas-output-and-background.png)

*Figure 7. Configuration output and backgrounding the first shell channel.*

---

## 7. Checking the Session and Trying Samba

After leaving that run, I checked my listener and used `ping` to make sure Metasploitable 2 was still reachable. It replied without packet loss, although the previous Metasploit session was no longer active. I decided to try another service and searched for Samba modules.

![Figure 8: A listener check on Kali.](images/08-kali-listener-check.png)

*Figure 8. A listener check on Kali.*

![Figure 9: The target responding to three ICMP echo requests.](images/09-kali-target-ping.png)

*Figure 9. The target responding to three ICMP echo requests.*

![Figure 10: The previous session was no longer active; I searched for Samba-related modules.](images/10-vsftpd-session-closed-samba-search.png)

*Figure 10. The previous session was no longer active; I searched for Samba-related modules.*

---

## 8. Samba: My Root Shell

I selected the module:

```text
exploit/multi/samba/usermap_script
```

The options showed `RHOSTS` set to `192.168.1.116`, the Samba service on port `139`, and the reverse-shell listener on `192.168.1.115:4444`.

![Figure 11: Selection of the Samba username-map script module.](images/11-samba-module-selected.png)

*Figure 11. Selection of the Samba username-map script module.*

![Figure 12: Module options showing the target and reverse connection settings.](images/12-samba-options-configured.png)

*Figure 12. Module options showing the target and reverse connection settings.*

![Figure 13: A contemporaneous socket check while I was working through the Samba attempt.](images/13-socket-check-before-samba-result.png)

*Figure 13. A contemporaneous socket check while I was working through the Samba attempt.*

**This one worked.** Metasploit opened a command shell, and I immediately ran `whoami` to see who I was. The answer was **`root`**. I had root access through the Samba route, and I could now run LinPEAS from that shell.

![Figure 14: Metasploit reporting the Samba command-shell session.](images/14-samba-command-shell-opened.png)

*Figure 14. Metasploit reporting the Samba command-shell session.*

![Figure 15: `whoami` returned `root`, and I started LinPEAS using the shell.](images/15-samba-root-identity-and-linpeas-start.png)

*Figure 15. `whoami` returned `root`, and I started LinPEAS using the shell.*

LinPEAS started successfully. I worked through its coloured output, which included extensive file listings and system configuration details. There was a lot to take in, and I was beginning to see how much the account I was using could affect what I saw.

![Figure 16: LinPEAS starting in the Samba-derived session.](images/16-samba-linpeas-banner.png)

*Figure 16. LinPEAS starting in the Samba-derived session.*

![Figure 17: A long listing of files and kernel module paths flagged by LinPEAS.](images/17-samba-linpeas-file-listings.png)

*Figure 17. A long listing of files and kernel module paths flagged by LinPEAS.*

![Figure 18: Further configuration output and the attempted closure of the shell channel.](images/18-samba-linpeas-config-and-session-exit.png)

*Figure 18. Further configuration output and the attempted closure of the shell channel.*

![Figure 19: The Samba command-shell session closed after user confirmation.](images/19-samba-session-closure.png)

*Figure 19. The Samba command-shell session closed after user confirmation.*

### What I learned

The big moment here was seeing `root` returned by a command I ran myself. I also got more comfortable distinguishing the access I had gained from the coloured leads LinPEAS was showing me.

---

## 9. Checking the UnrealIRCd Route

I next searched for the UnrealIRCd 3.2.8.1 backdoor module and inspected its payload and connection options. I also made another socket check.

![Figure 20: The UnrealIRCd module search and initial configuration.](images/20-unrealircd-search-and-configuration.png)

*Figure 20. The UnrealIRCd module search and initial configuration.*

![Figure 21: The selected UnrealIRCd module and its payload options.](images/21-unrealircd-payload-options.png)

*Figure 21. The selected UnrealIRCd module and its payload options.*

![Figure 22: Another Kali socket check during the IRC investigation.](images/22-socket-check-after-irc-investigation.png)

*Figure 22. Another Kali socket check during the IRC investigation.*

I researched and configured the route, but moved on without a successful session captured for this attempt.

---

## 10. Tomcat Manager: A New Meterpreter Session

I searched Metasploit for Tomcat-related modules and selected the Manager deployment route (`exploit/multi/http/tomcat_mgr_deploy`).

![Figure 23: Tomcat module search results.](images/23-tomcat-module-search.png)

*Figure 23. Tomcat module search results.*

I set Tomcat's HTTP port to `8180` and my listener to `6666`. I managed to combine the username option and value into `HttpUsertomcat`, which Metasploit rejected. Once I corrected the option names, I entered the known training credentials and continued.

The exploit uploaded and executed a WAR/JSP payload and opened a Meterpreter session.

![Figure 24: The rejected datastore-option typo, corrected Tomcat settings, and successful Meterpreter session.](images/24-tomcat-credentials-and-meterpreter-opened.png)

*Figure 24. The rejected datastore-option typo, corrected Tomcat settings, and successful Meterpreter session.*

I used `getuid`, which returned `tomcat5`. After opening a shell I tried a `curl` command with stray bracket characters in the address and received a globbing error. I then used `wget` to start LinPEAS.

![Figure 25: The `tomcat5` identity, malformed `curl` command, and the subsequent `wget` attempt.](images/25-tomcat-uid-and-malformed-curl.png)

*Figure 25. The `tomcat5` identity, malformed `curl` command, and the subsequent `wget` attempt.*

![Figure 26: LinPEAS banner showing that the Tomcat run started.](images/26-tomcat-linpeas-banner.png)

*Figure 26. LinPEAS banner showing that the Tomcat run started.*

![Figure 27: LinPEAS environment and log output, including the `tomcat5` user context.](images/27-tomcat-linpeas-environment.png)

*Figure 27. LinPEAS environment and log output, including the `tomcat5` user context.*

### What I understood

Another working session, this time as **`tomcat5`**. Comparing its LinPEAS output with the earlier Samba root shell made the account context feel much more concrete.

---

## 11. PostgreSQL Payload and LinPEAS

I next configured the PostgreSQL payload module:

```text
exploit/linux/postgres/postgres_payload
```

The options showed the PostgreSQL service on port `5432`, the target `192.168.1.116`, the training database credentials, and a Linux x86 Meterpreter reverse TCP payload. I changed the local port to `7777` before running it.

![Figure 28: PostgreSQL payload-module settings.](images/28-postgres-module-configured.png)

*Figure 28. PostgreSQL payload-module settings.*

![Figure 29: The listener port changed to `7777` and the options rechecked.](images/29-postgres-listener-reconfigured.png)

*Figure 29. The listener port changed to `7777` and the options rechecked.*

Metasploit identified PostgreSQL **8.3.1**, uploaded a shared object to the target, and opened Meterpreter. `getuid` returned **`postgres`**. I opened a shell and launched LinPEAS.

![Figure 30: PostgreSQL Meterpreter success, `postgres` identity and the LinPEAS launch.](images/30-postgres-meterpreter-and-linpeas-start.png)

*Figure 30. PostgreSQL Meterpreter success, `postgres` identity and the LinPEAS launch.*

![Figure 31: LinPEAS banner from the PostgreSQL-derived shell.](images/31-postgres-linpeas-banner.png)

*Figure 31. LinPEAS banner from the PostgreSQL-derived shell.*

LinPEAS produced a long list of kernel-related CVE candidates and process/file information. I kept those screenshots so I could revisit the leads and understand which ones mattered for this old system.

![Figure 32: Kernel-version-related exploit candidates listed by LinPEAS; these were not validated.](images/32-postgres-linpeas-kernel-cve-candidates.png)

*Figure 32. Kernel-version-related exploit candidates listed by LinPEAS; these were not validated.*

![Figure 33: Process-owned file listings, including PostgreSQL data paths.](images/33-postgres-linpeas-process-files.png)

*Figure 33. Process-owned file listings, including PostgreSQL data paths.*

The environment information showed the PostgreSQL account context (`HOME=/var/lib/postgresql` and `USER=postgres`). I then interrupted and closed the shell channel.

![Figure 34: PostgreSQL environment output followed by termination of the channel.](images/34-postgres-linpeas-environment-and-close.png)

*Figure 34. PostgreSQL environment output followed by termination of the channel.*

### What I understood

I had successfully opened another Meterpreter session, this time as **`postgres`**. Seeing `getuid` return a different user helped me understand why it matters which service I entered through.

---

## 12. DistCC: A Failed Payload and a Working Pivot

I selected the DistCC command-execution module:

```text
exploit/unix/misc/distcc_exec
```

The module targeted port `3632` on `192.168.1.116`.

![Figure 35: DistCC module selected with target and reverse connection settings.](images/35-distcc-module-options.png)

*Figure 35. DistCC module selected with target and reverse connection settings.*

The first run, using the default reverse Bash payload, returned errors including **`bash: 101: Bad file descriptor`** and `/dev/tcp/...: No such file or directory`. Metasploit said the exploit completed but no session was created.

I then changed to the Unix reverse payload and changed the listener port to `8889`. This time Metasploit accepted the connections and opened a command shell.

![Figure 36: The failed first DistCC payload and the subsequent successful command-shell session.](images/36-distcc-payload-failure-and-command-shell.png)

*Figure 36. The failed first DistCC payload and the subsequent successful command-shell session.*

`whoami` returned **`daemon`**. I invoked LinPEAS from that shell and its banner appeared.

![Figure 37: The command shell identified as `daemon` and the LinPEAS command entered.](images/37-distcc-daemon-uid-and-linpeas-command.png)

*Figure 37. The command shell identified as `daemon` and the LinPEAS command entered.*

![Figure 38: LinPEAS starting under the DistCC-derived shell.](images/38-distcc-linpeas-banner.png)

*Figure 38. LinPEAS starting under the DistCC-derived shell.*

### What I learned

This was one of the most useful troubleshooting moments: the first payload failed, I changed the approach, and the next attempt opened a shell. `whoami` returned **`daemon`**. I could see the difference between an exploit running and a payload giving me a usable session.

---

## 13. Java RMI: Another Session and LinPEAS Run

I searched for Java-related Metasploit modules and selected the Java RMI server module:

```text
exploit/multi/misc/java_rmi_server
```

I configured the target on port `1099`, with Kali as the reverse connection host and a local listener on port `9991`.

![Figure 39: Searching the Java/RMI module list.](images/39-java-rmi-module-search.png)

*Figure 39. Searching the Java/RMI module list.*

![Figure 40: Java RMI module and payload options.](images/40-java-rmi-options.png)

*Figure 40. Java RMI module and payload options.*

The module reported that it sent an RMI call and a payload JAR, and then opened a Meterpreter session. I opened a shell and started LinPEAS.

![Figure 41: Java RMI Meterpreter session and the shell-based LinPEAS command.](images/41-java-rmi-meterpreter-and-linpeas-launch.png)

*Figure 41. Java RMI Meterpreter session and the shell-based LinPEAS command.*

![Figure 42: LinPEAS banner during the Java RMI run.](images/42-java-rmi-linpeas-banner.png)

*Figure 42. LinPEAS banner during the Java RMI run.*

The later process list showed services running under several accounts, including `root`, `www-data`, `tomcat55` and `daemon`, alongside a Java/Metasploit payload process. It gave me another view of how much was running on this deliberately vulnerable VM. I did not capture a separate user-identity command for this Java RMI shell.

![Figure 43: Process enumeration under different system accounts during the Java RMI LinPEAS run.](images/43-java-rmi-linpeas-process-list.png)

*Figure 43. Process enumeration under different system accounts during the Java RMI LinPEAS run.*

---

## 14. Results at a Glance

I came away from this session with several working routes into the same training machine, not just one successful screenshot. This is how my attempts turned out:

| Route / activity | My result |
|---|---|
| VSFTPD | Opened Meterpreter and transferred LinPEAS to `/tmp` |
| Samba `usermap_script` | Opened a command shell; **`whoami` returned `root`** |
| UnrealIRCd | Researched and configured the module, then moved on |
| Tomcat Manager | Opened Meterpreter; `getuid` returned **`tomcat5`** |
| PostgreSQL | Opened Meterpreter; `getuid` returned **`postgres`** |
| DistCC | First payload failed; second attempt opened a shell; `whoami` returned **`daemon`** |
| Java RMI | Opened Meterpreter, entered a shell and started LinPEAS |
| LinPEAS | Ran under several sessions and gave me cron, process, configuration and kernel-related leads to study |

I have left the individual screenshots beside each stage above, where they explain what I was doing at that point rather than separating the evidence from the story.

---

## 15. Troubleshooting and Pivots

A surprising amount of this exercise was about recognising what kind of problem I was looking at and knowing when to change direction.

- The `locate` database was broken, but `ls` showed that I already had `linpeas.sh` in Downloads.
- `wget` at the GitHub homepage downloaded `index.html`, which taught me to check the actual file.
- `wget` and `nc` were not available at the Meterpreter prompt, so I used `upload`, then a shell to run the script.
- When a session disappeared, I checked reachability and moved on to another service rather than assuming the whole VM was down.
- In Tomcat, I corrected a datastore-option typo and later switched from a malformed `curl` command to `wget`.
- The DistCC default payload failed; changing it produced a working command shell.
- I interrupted some very long LinPEAS output so I could continue exploring other routes.

The pattern I kept practising was **try → read the output → understand the error → adjust → try again**. I am getting more comfortable doing that without feeling that every failed command means the whole exercise has gone wrong.

---

## 16. Terms I Learned

**Meterpreter:** The interactive Metasploit environment I was using after several successful exploits. Its commands are not identical to an ordinary Linux shell.

**System shell:** The environment in which I could run regular Linux commands such as `cd`, `chmod`, `wget` and `whoami`.

**RHOSTS / RPORT:** The target machine and service port.

**LHOST / LPORT:** My Kali address and listening port for a reverse connection.

**Foothold:** My initial access through a service, associated with a particular account.

**Privilege escalation:** Increasing the privileges available to an existing lower-privileged session. In this exercise I was exploring possible paths with LinPEAS and also obtained root directly through Samba.

**LinPEAS:** A Linux enumeration script that highlights areas such as permissions, processes, services, scheduled tasks and possible escalation leads.

**CVE candidate:** A known vulnerability entry to research against the target's actual software and configuration.

---

## 17. What I Learned

I went into this second attempt wanting to get better at using LinPEAS. I came out of it understanding much more about **sessions, users and why the route I used matters**.

I successfully transferred and ran the script, became more comfortable moving between Meterpreter and a system shell, and learned to check identity with `getuid` or `whoami`. The Samba shell returning **root** was a real milestone for me. I could also compare that experience with Tomcat as `tomcat5`, PostgreSQL as `postgres`, and DistCC as `daemon`.

The DistCC pivot was another highlight. I saw an error that initially seemed like the end of the attempt, changed the payload, and got a shell on the next run. That is the kind of practical troubleshooting I want to become more confident with.

LinPEAS gave me more information than I could sensibly investigate in one session. The cron permissions, process lists, environment details and kernel CVE suggestions are things I now know to examine more carefully. I understand that finding an interesting lead and verifying it are separate stages, and I want to practise that next.

---

## 18. Security Takeaways

The lab showed me how much exposure can come from old services and weak/default configurations. On a normal system, I would be thinking about retiring unsupported software, restricting unnecessary services, changing default credentials, running services with the privileges they actually need, and reviewing the permissions on files and scheduled tasks.

The exercise also made me appreciate why enumeration matters after getting access: the same machine looks different depending on the account and service context.

---

## 19. Scope and Next Steps

This was one practical learning session, not an attempt to exhaust every possible route on Metasploitable 2. I explored several services and ran LinPEAS under different sessions, but did not pursue every result it highlighted. I did not complete a separate low-privilege-to-root escalation chain from the `tomcat5`, `postgres` or `daemon` accounts during this attempt. My confirmed root shell came through the Samba service.

For the next exercise I want to select a smaller number of LinPEAS leads, check their permissions and prerequisites, and follow them more deliberately. I also want to keep checking the current user before and after each important step.

---

## 20. Evidence and Privacy

The **43 screenshots** are my original captures from 24 September 2026, arranged by their timestamps and given clearer filenames for GitHub. I have kept the unsuccessful attempts alongside the working ones because they form part of the session.

My terminal used a translucent background, so some older text can be seen faintly behind the active output. The foreground commands and results are what I used when describing each stage. The private `192.168.1.x` addresses belong to my home lab. The images are otherwise unchanged from my originals.

---

## Conclusion

This second try felt much more like a real hands-on session. I opened access through several different services, got a **root shell through Samba and verified it with `whoami`**, recovered from a failed DistCC payload, and used LinPEAS under different user accounts to understand what each session could see.

The errors were frustrating in the moment, but they are also where a lot of the learning happened. I am leaving this exercise with a clearer picture of how initial access, shell identity, enumeration and privilege escalation fit together, and a better idea of what I want to investigate next.

---

## Lab Note

This is my student record of authorised practice on my own deliberately vulnerable Metasploitable 2 VM.

## References

- [PEASS-ng / LinPEAS, official project](https://github.com/peass-ng/PEASS-ng)
- [Metasploit Framework documentation](https://docs.metasploit.com/)
- [Rapid7 Metasploitable 2 introduction](https://docs.rapid7.com/metasploit/metasploitable-2/)
