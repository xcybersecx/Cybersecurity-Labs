# Learning Notes: Metasploit Four-Port Assessment

These notes sit beside the main report and are deliberately more explanatory. They are based on the commands and decisions visible in my screenshots from this exercise.

## 1. The basic workflow I practised

```text
Nmap / service discovery
        ↓
service and version identification
        ↓
research
        ↓
Metasploit search
        ↓
module selection
        ↓
show options
        ↓
configure required fields
        ↓
run
        ↓
read the output carefully
        ↓
validate the result
```

The last two steps are where much of my learning happened. A tool can run successfully without proving compromise, and a tool can error because I configured it incorrectly.

## 2. Nmap commands used

### Quick service/version baseline

```bash
sudo nmap -sV <TARGET_IP>
```

`-sV` asks Nmap to identify the service and version behind an open port where possible.

### Full TCP assessment scan

```bash
nmap -p- -sV -sC -O -v -oA initial_scan <TARGET_IP>
```

- `-p-` scans all TCP ports.
- `-sV` identifies service/version information.
- `-sC` runs the default NSE script set.
- `-O` attempts OS detection.
- `-v` gives more progress/detail.
- `-oA initial_scan` writes normal, grepable and XML output using the same base filename.

## 3. Metasploit commands that became familiar

```text
search <term>
use <module>
show options
set <OPTION> <value>
run
sessions
sessions -i <id>
```

### `search`
Used to find modules by service or technology, for example SSH, Telnet, SMTP, Samba, VNC, BIND and UnrealIRCd.

### `use`
Loads the selected module so that its options can be inspected and configured.

### `show options`
Shows which values are required, which already have defaults and what each field means. This became important because several of my early errors were configuration errors.

### `set`
Sets one module option for the current module context.

### `run`
Executes the configured scanner or exploit module.

### `sessions`
Lists sessions Metasploit currently knows about.

### `sessions -i <id>`
Interacts with one selected session.

## 4. RHOSTS, RPORT, LHOST and LPORT

These stopped looking like random abbreviations once I understood the direction:

| Option | Meaning |
|---|---|
| `RHOSTS` | Remote host or hosts being tested |
| `RPORT` | Remote service port |
| `LHOST` | My local Kali address used when a callback is required |
| `LPORT` | Local port listening for the callback |

A module can identify the correct target service but still fail to create a session if the payload or callback configuration is unsuitable.

## 5. Scanner versus exploit versus login test

This exercise forced me to separate three things I had previously been tempted to lump together.

### Enumeration scanner
Examples in this exercise included SSH user enumeration, SMTP user enumeration and HTTP directory discovery. These reveal information.

### Login scanner
SSH, Telnet, MySQL and VNC authentication modules test credentials. A successful result proves an authentication weakness if the credentials should not be available/guessable, but it does not automatically mean the service software itself was exploited.

### Exploit module
The distcc and Samba modules actually led to command-shell sessions, so I could validate code execution and then inspect the user context.

## 6. Checking privileges after gaining a shell

```bash
whoami
```

The same command gave two very different results:

- distcc shell: `daemon`
- Samba shell: `root`

That difference changed the impact of the findings. A shell is not a complete description of privilege.

## 7. SSH lesson

I successfully authenticated with the known Metasploitable `msfadmin` training credentials. I also configured SSH user enumeration after first pointing the module at the wrong/non-working username source.

Main lesson: weak credentials and username disclosure are security issues, but they are not the same as exploiting OpenSSH.

## 8. Telnet lesson

Telnet accepted the known training credentials and opened a session. The practical lesson was twofold: weak/default credentials were present, and Telnet is an obsolete plaintext remote-administration protocol compared with SSH.

## 9. SMTP lesson

SMTP version detection found Postfix, and user enumeration returned local usernames. This helped me understand why account names are useful reconnaissance even though they do not prove that the accounts can be logged into.

## 10. distcc lesson

The first module/payload combination failed with a bad file descriptor. A different compatible command payload created a shell. `whoami` returned `daemon`.

Main lesson: module selection, payload behavior and privilege level are separate questions.

## 11. DNS/BIND lesson

I used a `version.bind` CHAOS TXT query to independently confirm BIND 9.4.2. I then researched BIND modules in Metasploit but did not obtain a confirmed exploit.

Main lesson: service fingerprinting can be corroborated manually, but an old version and a matching module list are still only leads until impact is validated.

## 12. Samba lesson

The target's Samba 3.0.20-Debian version matched the historical username-map-script issue. I corroborated the research using Exploit-DB, ran the matching Metasploit module, repeated the test and checked the resulting session with `whoami`.

The final session returned `root`.

Main lesson: this was a much stronger finding because I connected version evidence, external research, repeatable exploitation and privilege validation.

## 13. HTTP/WebDAV lesson

The Apache banner included DAV/2, but the dedicated WebDAV scanner reported that WebDAV was disabled. I then pivoted to directory enumeration, which found `/cgi-bin/`, `/doc/`, `/icons/`, `/phpMyAdmin/` and `/test/`.

The generic HTTP login scanner then reported that phpMyAdmin was not requesting HTTP authentication.

Main lesson: a scanner must match the actual feature and authentication mechanism. Negative results are useful because they tell me to stop forcing the wrong hypothesis.

## 14. MySQL lesson

The MySQL login scanner found a blank password for the remote root account. Manual validation initially failed because of SSL compatibility between a modern client and the old lab server. After using the client's non-SSL option, I reached the database monitor as root.

Main lesson: manual corroboration improved confidence, and troubleshooting client compatibility is different from troubleshooting credentials.

## 15. NFS lesson

`rpcinfo` showed the RPC/NFS services and `showmount -e` revealed that `/` was exported to `*`.

The first mount attempt failed because my local mount-point directory did not exist. After creating it, the export mounted successfully. I later unmounted it.

Main lesson: some serious findings are misconfigurations rather than code exploits, and some errors are just ordinary Linux mistakes.

## 16. UnrealIRCd lesson

The Metasploit module reported that the target appeared vulnerable, but repeated attempts did not create a session.

Main lesson: **"appears vulnerable" is not the same as "I exploited it."** My report should preserve that distinction.

## 17. VNC lesson

The VNC login scanner identified the weak password `password`. TightVNC Viewer then connected successfully and showed the remote desktop.

Main lesson: a second tool can manually validate a scanner result. The VNC password did not itself prove a root credential, but it exposed a desktop in which a root terminal was already open.

## 18. My reporting rule going forward

Before I call something a confirmed vulnerability, I should ask:

1. What did I observe?
2. What did the tool actually test?
3. Did the result create access, reveal information, or merely match a version?
4. Did I independently validate it?
5. What privileges did the resulting access have?
6. What evidence do I have in the screenshots?
7. What would be an accurate, non-inflated finding name?

That is the main skill this exercise added to my earlier scanner-based work.
