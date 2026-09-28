# Metasploitable 2: vsFTPd 2.3.4 Backdoor Investigation and Containment

**Date:** 28 September 2026  
**Status:** Completed, documented lab investigation  
**Scope:** My own Kali and deliberately vulnerable Metasploitable 2 virtual machines  
**Evidence:** All **39 original screenshots** already uploaded to the nested screenshot folder, referenced below by their original timestamped filenames. No screenshots were removed or renamed for this README.

> This repository is my practical revision notebook, not a polished reconstruction that hides the mistakes. I kept the commands, errors, corrections, intermediate states, and results in the order they happened so that I can retrace the lab later. This is a *containment* exercise, not proof that I patched the compromised software. It is separate from my six-port configuration-hardening homework.

## Contents

1. [Purpose, environment and baseline](#1-purpose-environment-and-baseline)
2. [Initial access and ordinary FTP connection](#2-initial-access-and-ordinary-ftp-connection)
3. [Inspecting and editing vsFTPd](#3-inspecting-and-editing-vsftpd)
4. [Why the first edits were not enough](#4-why-the-first-edits-were-not-enough)
5. [Following the legacy xinetd service](#5-following-the-legacy-xinetd-service)
6. [Containing FTP and its remaining listener](#6-containing-ftp-and-its-remaining-listener)
7. [Verifying and restoring the baseline](#7-verifying-and-restoring-the-baseline)
8. [Findings, limits and lessons](#8-findings-limits-and-lessons)

## 1. Purpose, environment and baseline

My original plan was to inspect the insecure FTP configuration on Metasploitable 2, change the relevant options and test whether the original access path still worked. The exercise expanded when the first configuration-only changes did not produce the expected result. I decided to keep the whole sequence because knowing *why* a change failed is part of my learning.

| Component | What I used |
| --- | --- |
| Hypervisor | Oracle VirtualBox, with a saved baseline snapshot |
| Testing VM | Kali Linux, observed lab address `192.168.1.115` |
| Target VM | Metasploitable 2, observed lab address `192.168.1.116` |
| Service in scope | FTP on TCP/21, reported as `vsFTPd 2.3.4` |
| Additional listener | TCP/6200, found later during investigation |
| Verification and inspection | Nmap, FTP client, SSH, terminal, nano, shell utilities, xinetd, VirtualBox snapshots and independent framework tests |

The screenshots are stored in the nested `16-vsftpd-backdoor-investigation-and-containment/` directory in this GitHub folder. The image links are relative to this README.

All activity was inside my personally controlled training environment. These private IP addresses are lab-only observations, not universal settings. Metasploitable is intentionally insecure and should remain isolated from untrusted networks.

I began with a full TCP service-detection scan. The output identified vsFTPd 2.3.4 on TCP/21 alongside many other deliberately exposed services. I chose to focus this separate report on FTP, rather than turn the whole service scan into a report about every port.

![Figure 01: Initial Nmap scan of the deliberately vulnerable target shows TCP/21 open and the vsFTPd 2.3.4 banner.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20050337.png)

*Figure 01 (05:03:37). Initial Nmap scan of the deliberately vulnerable target shows TCP/21 open and the vsFTPd 2.3.4 banner.*

**Revision note:** Enumeration tells me what is visible, not whether a particular remediation has worked.

Before I edited anything, I opened the VirtualBox snapshot dialogue and named the restore point **Before Security Hardening**. I included a description explaining that it preserved the original vulnerable configuration.

![Figure 02: Creating the Before Security Hardening restore point while the target is running.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20051158.png)

*Figure 02 (05:11:58). Creating the Before Security Hardening restore point while the target is running.*

**Revision note:** A snapshot is the rollback point for the VM state. A Windows + Shift + S capture is only documentary evidence; it cannot restore a machine.

I checked VirtualBox Manager to confirm the snapshot actually appeared in the snapshot tree. It was not enough merely to open the naming dialogue; I wanted evidence that the restore point had been created.

![Figure 03: VirtualBox Manager lists the baseline snapshot and the current VM state.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20051356.png)

*Figure 03 (05:13:56). VirtualBox Manager lists the baseline snapshot and the current VM state.*

**Revision note:** The snapshot tree and the screenshot are different things: one provides recovery, the other proves what I did.

## 2. Initial access and ordinary FTP connection

I then established the original test result before making changes. My point of comparison was whether a remote session could be opened on the original vulnerable VM. I also checked an ordinary FTP login separately, because FTP authentication and the software backdoor are not the same security issue.

The initial independent test reported that the backdoor had been spawned and a Meterpreter session opened. I recorded this as the **before** result.

![Figure 04: Initial independent test opens a Meterpreter session against the lab target.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20051804.png)

*Figure 04 (05:18:04). Initial independent test opens a Meterpreter session against the lab target.*

**Revision note:** This is evidence about this controlled VM at this moment, not about any other host displaying the same version string.

Inside that session, I checked the working directory and listed the filesystem. That confirmed I had an interactive remote session, rather than relying on a banner or success message alone.

![Figure 05: Working-directory and file-listing checks within the initial session.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20052222.png)

*Figure 05 (05:22:22). Working-directory and file-listing checks within the initial session.*

**Revision note:** A directory listing demonstrates access; it does not, on its own, establish every possible privilege or persistence capability.

In a separate Kali terminal, I connected to the FTP service with the normal lab account. I received `230 Login successful`, then used `pwd` and `ls` to inspect the account directory. This gave me a baseline for ordinary authenticated FTP access.

![Figure 06: Successful normal FTP login and directory listing with the lab account.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20052932.png)

*Figure 06 (05:29:32). Successful normal FTP login and directory listing with the lab account.*

**Revision note:** Do not conflate a successful normal FTP login with successful exploitation of the backdoor.

## 3. Inspecting and editing vsFTPd

To find the settings, I moved from my Kali testing terminal to an SSH connection to Metasploitable 2. I needed to inspect the **target** configuration under `/etc`, not edit Kali's own FTP settings.

The modern SSH client initially refused to negotiate with the old target because of its legacy host-key algorithms. I used a host-specific compatibility option for this isolated training machine and logged in successfully, confirming the `msfadmin` user with `whoami`.

![Figure 07: Resolving the legacy SSH host-key negotiation error and confirming the remote account.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20053334.png)

*Figure 07 (05:33:34). Resolving the legacy SSH host-key negotiation error and confirming the remote account.*

**Revision note:** A compatibility exception for an obsolete VM is not a general recommendation for production SSH connections.

I switched to root on the target and tried to read the FTP configuration. My first path was mistyped; the corrected `/etc/vsftpd.conf` command showed the original file. The active settings included `anonymous_enable=YES` and `local_enable=YES`.

![Figure 08: Root shell and the beginning of the original /etc/vsftpd.conf file.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20053703.png)

*Figure 08 (05:37:03). Root shell and the beginning of the original /etc/vsftpd.conf file.*

**Revision note:** Linux paths and filenames must be exact. The `v` in `vsftpd` became a recurring typing problem during this session.

I reached the later part of the configuration and attempted a backup. The first copy command omitted a space after `cp` and failed. I corrected it to create `/etc/vsftpd.conf.bak`, then listed the two files to verify the backup.

![Figure 09: End of the original configuration, a mistyped copy command, and the corrected backup command.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20054714.png)

*Figure 09 (05:47:14). End of the original configuration, a mistyped copy command, and the corrected backup command.*

**Revision note:** A failed command is not evidence of a completed backup. Check the resulting files.

I tried filtering comments out of the configuration with `grep`, but the pipeline was incomplete and printed usage information. I then used a simpler command to view the active directives. They showed anonymous login and anonymous write-related options enabled.

![Figure 10: The configuration backup is present; the first grep pipeline fails and a simpler command shows active directives.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20055157.png)

*Figure 10 (05:51:57). The configuration backup is present; the first grep pipeline fails and a simpler command shows active directives.*

**Revision note:** If a filter fails, check its syntax and fall back to a readable inspection before editing.

The first nano view documented the original values before editing. I kept `local_enable=YES` in view because I did not intend to remove legitimate local-account FTP access during this initial configuration attempt.

![Figure 11: Opening the unmodified vsFTPd configuration in nano.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20055515.png)

*Figure 11 (05:55:15). Opening the unmodified vsFTPd configuration in nano.*

**Revision note:** Read the existing file before changing values; do not make a blind assumption about defaults.

In nano I changed `anonymous_enable`, `anon_upload_enable`, and `anon_mkdir_write_enable` from `YES` to `NO`. The screen showed the buffer marked Modified.

![Figure 12: Changing the anonymous-access and anonymous-write settings in nano.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20055802.png)

*Figure 12 (05:58:02). Changing the anonymous-access and anonymous-write settings in nano.*

**Revision note:** Changing three anonymous-access options is a configuration hardening attempt; it does not replace compromised software.

I exited nano and displayed the active directives again to verify the values were saved: `anonymous_enable=NO`, `anon_upload_enable=NO`, and `anon_mkdir_write_enable=NO`, while `local_enable=YES` remained in place.

![Figure 13: Confirming the edited values in the file from the shell.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20060206.png)

*Figure 13 (06:02:06). Confirming the edited values in the file from the shell.*

**Revision note:** A saved file is a separate milestone from applying the service configuration and checking its effects.

## 4. Why the first edits were not enough

The next check mattered more than the edited text: what did the service actually allow? I did not want to describe a setting as effective just because the file contained `NO`.

Back in Kali, I again connected to the FTP service. The normal training account worked, and then a test using `anonymous` still returned `230 Login successful`. That contradicted the restriction I thought I had made.

![Figure 14: Direct FTP testing shows that anonymous login still succeeds.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20060510.png)

*Figure 14 (06:05:10). Direct FTP testing shows that anonymous login still succeeds.*

**Revision note:** The observation is that anonymous access still succeeded. At this point I had not established precisely why the change was not effective in the running service.

I returned to the target, confirmed the edited directives were still saved, and checked for `vsftpd` processes. The mismatch between the file and the observed login made me look at the service execution path rather than editing more settings at random.

![Figure 15: Re-checking the changed directives and looking for the running vsftpd process.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20061013.png)

*Figure 15 (06:10:13). Re-checking the changed directives and looking for the running vsftpd process.*

**Revision note:** Separate the file on disk, the running process and the behaviour observed from another machine.

I examined the parent process and saw `/usr/sbin/xinetd`. My first recursive search also contained a redirection typo (`/de/null` instead of `/dev/null`), which I corrected. The successful search identified the xinetd service entry.

![Figure 16: Inspecting the FTP process parent and identifying xinetd as the service supervisor.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20061145.png)

*Figure 16 (06:11:45). Inspecting the FTP process parent and identifying xinetd as the service supervisor.*

**Revision note:** These older Linux systems can use xinetd to start services on demand, unlike the systemd workflows I am more likely to see on modern machines.

## 5. Following the legacy xinetd service

I now had a more specific question: what service definition was actually launching FTP, and would a change to that entry alter the observed behaviour? This was troubleshooting, not my original simple configuration-hardening plan.

I used `cat /etc/xinetd.d/vsftpd` to read the actual service entry. It pointed to `/usr/sbin/vsftpd` and showed `disable = no`. It was important to read the file rather than assume that a command from a modern Linux tutorial applied unchanged.

![Figure 17: Reading the original /etc/xinetd.d/vsftpd service definition.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20061559.png)

*Figure 17 (06:15:59). Reading the original /etc/xinetd.d/vsftpd service definition.*

**Revision note:** `disable = no` means xinetd is configured to provide this service. The presence of a service definition does not prove that another independently running listener has disappeared.

I explored the xinetd configuration, restarted the superserver, and checked where the FTP executable expected its configuration. The terminal also records unsuccessful path guesses. I retained them because they explain why the next step was to inspect the original file again.

![Figure 18: Exploring the legacy service entry, restarting xinetd, and trying to locate the active FTP config.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20062008.png)

*Figure 18 (06:20:08). Exploring the legacy service entry, restarting xinetd, and trying to locate the active FTP config.*

**Revision note:** A process may read a different configuration path from the one I have edited; verify assumptions rather than forcing a conclusion.

I reopened the real xinetd service definition after several mistaken path variants. The output shows that the working filename was `/etc/xinetd.d/vsftpd`, not a nested path such as `/etc/xinetd.d/vsftpd.d/...`.

![Figure 19: Correcting mistaken paths and re-reading the actual xinetd FTP service definition.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20062921.png)

*Figure 19 (06:29:21). Correcting mistaken paths and re-reading the actual xinetd FTP service definition.*

**Revision note:** Directory and filename are distinct. One wrong slash can turn an otherwise reasonable check into `No such file or directory`.

I viewed the xinetd entry in nano before the experimental edit. Its `server` field pointed to the vsftpd executable and the service was still enabled.

![Figure 20: Viewing the xinetd entry in nano before the configuration-path experiment.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20063041.png)

*Figure 20 (06:30:41). Viewing the xinetd entry in nano before the configuration-path experiment.*

**Revision note:** Capture the pre-change state so that the following screenshot has an actual comparison.

I temporarily added a `server_args` entry pointing to `/etc/vsftpd.conf`, trying to make the configuration path explicit. This was an exploratory change, not the final containment action.

![Figure 21: Trial addition of server_args pointing to /etc/vsftpd.conf.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20063222.png)

*Figure 21 (06:32:22). Trial addition of server_args pointing to /etc/vsftpd.conf.*

**Revision note:** Do not report an experiment as a fix before testing the resulting behaviour.

I restarted xinetd and followed up with checks of the executable and file paths. Some candidate paths did not exist. The investigation still had not established that the simple configuration edit had removed the original vulnerability.

![Figure 22: Restarting xinetd and following up on the configuration-path investigation.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20063511.png)

*Figure 22 (06:35:11). Restarting xinetd and following up on the configuration-path investigation.*

**Revision note:** A clean restart message confirms that the supervisor restarted; it does not certify that the vulnerable software is safe.

A later independent test still opened a Meterpreter session. This was the decisive evidence that the intermediate configuration-path experiment had not contained the backdoor.

![Figure 23: Independent test still opens a session after the intermediate service-file experiment.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20064323.png)

*Figure 23 (06:43:23). Independent test still opens a session after the intermediate service-file experiment.*

**Revision note:** When reality contradicts the change I expected to work, record the result and change the investigation, not the wording of the report.

I returned to the xinetd service entry and reviewed the values again before moving to a containment approach. In particular, the `disable` directive was still set to `no`.

![Figure 24: Reviewing the xinetd FTP entry before the containment change.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20064939.png)

*Figure 24 (06:49:39). Reviewing the xinetd FTP entry before the containment change.*

**Revision note:** A controlled before/after report needs to show precisely which switch I changed next.

## 6. Containing FTP and its remaining listener

At this stage I moved from trying to preserve the FTP service to **containing** the compromised service. This is deliberately a different outcome from my later homework, where I need to focus on the particular assigned configuration weaknesses.

In `/etc/xinetd.d/vsftpd`, I changed `disable = no` to `disable = yes` and saved the file. This instructed xinetd not to offer its FTP service.

![Figure 25: Editing the xinetd service entry from disable = no to disable = yes.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20065017.png)

*Figure 25 (06:50:17). Editing the xinetd service entry from disable = no to disable = yes.*

**Revision note:** Disabling the service is containment, not an update of the compromised `/usr/sbin/vsftpd` executable.

I restarted xinetd. The terminal showed its stop and start operations completing successfully.

![Figure 26: Restarting xinetd after disabling its FTP service entry.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20065124.png)

*Figure 26 (06:51:24). Restarting xinetd after disabling its FTP service entry.*

**Revision note:** Apply a service-file change before using an external scan to judge the result.

The next Nmap check showed TCP/21 **closed**, but TCP/6200 **open**. This was the key unexpected result. Although the primary FTP service was no longer available, another listener remained.

![Figure 27: Independent scan shows TCP/21 closed while TCP/6200 is still open.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20065256.png)

*Figure 27 (06:52:56). Independent scan shows TCP/21 closed while TCP/6200 is still open.*

**Revision note:** Never treat a closed main service port as proof that every related process or connection is gone.

From the target, I inspected the TCP/6200 listener with `netstat` and looked up its process. In this lab run the listener was associated with PID `5087` and a short executable name. That PID was transient, not a number to reuse in another session.

![Figure 28: Local socket and process inspection associates the remaining TCP/6200 listener with PID 5087.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20065747.png)

*Figure 28 (06:57:47). Local socket and process inspection associates the remaining TCP/6200 listener with PID 5087.*

**Revision note:** Identify the live process before deciding what to do with it; the port number alone is not a process identity.

I terminated the identified process in this lab and repeated the socket check. The command no longer listed a listener on TCP/6200.

![Figure 29: Terminating that observed lab process and checking that the port-6200 listener is no longer listed.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20065953.png)

*Figure 29 (06:59:53). Terminating that observed lab process and checking that the port-6200 listener is no longer listed.*

**Revision note:** Local socket inspection shows the host-side state. I still needed an independent check from Kali.

I scanned both relevant ports again from Kali. The result showed TCP/21 **closed** and TCP/6200 **closed**. This was stronger evidence for the containment state than either the configuration text or the local process check alone.

![Figure 30: Independent Nmap check shows TCP/21 and TCP/6200 closed.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20070117.png)

*Figure 30 (07:01:17). Independent Nmap check shows TCP/21 and TCP/6200 closed.*

**Revision note:** Compare external before and after states using the same target and port set.

I repeated the independent test. Its output showed a refused connection on port 21, followed by **"Exploit completed, but no session was created."** I captured this result for the standalone report.

![Figure 31: The repeat independent test is refused on TCP/21 and creates no session.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20070626.png)

*Figure 31 (07:06:26). The repeat independent test is refused on TCP/21 and creates no session.*

**Revision note:** No session in this test supports the observed containment outcome. It does not prove the compromised binary was patched or that all possible attack paths are gone.

## 7. Verifying and restoring the baseline

I wanted to keep this investigation separate from the six-port homework. I had already saved the screenshots in Windows, so I could roll the VM back without losing the documentation. I also learned that preserving a modified VM state is optional when the saved screenshots are sufficient for my revision record.

VirtualBox Manager showed **Before Security Hardening** as the saved baseline. I selected this restore point, not a screenshot and not Kali.

![Figure 32: VirtualBox Manager shows the saved Before Security Hardening restore point.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20071041.png)

*Figure 32 (07:10:41). VirtualBox Manager shows the saved Before Security Hardening restore point.*

**Revision note:** The VM snapshot is what reverses disk and machine state. Windows screenshots remain documentation outside the VM.

When I first issued `shutdown -h now` from the ordinary `msfadmin` account, the VM responded that the operation needed root privileges.

![Figure 33: The first shutdown request reports that root privileges are required.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20071219.png)

*Figure 33 (07:12:19). The first shutdown request reports that root privileges are required.*

**Revision note:** When Linux says an administrative operation needs root, the failure is expected; it does not mean the VM is damaged.

I elevated on the target and reissued the shutdown command so that I could restore the powered-off VM cleanly.

![Figure 34: Elevating on the target VM and issuing the shutdown command again.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20071322.png)

*Figure 34 (07:13:22). Elevating on the target VM and issuing the shutdown command again.*

**Revision note:** Shut down the target VM, not the Kali tester or Windows host.

I selected **Restore** for **Before Security Hardening** in VirtualBox Manager. This was the original vulnerable baseline saved before the FTP changes.

![Figure 35: Selecting Restore for Before Security Hardening in VirtualBox Manager.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20071511.png)

*Figure 35 (07:15:11). Selecting Restore for Before Security Hardening in VirtualBox Manager.*

**Revision note:** Check the selected snapshot by name before confirming.

An attempt to preserve the modified current state during restoration produced a VirtualBox snapshot-state error. The original snapshot remained visible. I did not treat a 100% progress indicator as proof of a successful restore until I inspected the snapshot tree and booted the target.

![Figure 36: VirtualBox reports a snapshot-state error while preserving the changed machine state.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20071710.png)

*Figure 36 (07:17:10). VirtualBox reports a snapshot-state error while preserving the changed machine state.*

**Revision note:** A restore notification and the actual VM state can disagree. Verify the machine after the operation settles.

After the restoration completed, I started Metasploitable 2 and used `ip a` to confirm the target was again at `192.168.1.116`.

![Figure 37: The restored target boots and shows its original private lab address.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20072500.png)

*Figure 37 (07:25:00). The restored target boots and shows its original private lab address.*

**Revision note:** The IP address is a useful check, but it does not by itself show that the vulnerable service has returned.

From Kali, I checked the FTP port again. TCP/21 was **open**, unlike the contained state. That confirmed the service had returned after restoration.

![Figure 38: Nmap confirms TCP/21 is open again after restoring the original snapshot.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20072629.png)

*Figure 38 (07:26:29). Nmap confirms TCP/21 is open again after restoring the original snapshot.*

**Revision note:** This scan shows restored reachability; a separate test is needed to check that the original session result is reproducible.

Finally, I repeated my independent original test and the backdoor again spawned a Meterpreter session. That completed the before, containment and restoration comparison.

![Figure 39: A final independent test opens a Meterpreter session again after snapshot restoration.](16-vsftpd-backdoor-investigation-and-containment/Screenshot%202026-09-28%20072844.png)

*Figure 39 (07:28:44). A final independent test opens a Meterpreter session again after snapshot restoration.*

**Revision note:** Restoration returning the original vulnerability is expected here. It does not mean the containment had persisted across rollback.

## 8. Findings, limits and lessons

### What the evidence actually supports

| Observation in this lab | Supported interpretation | Limit |
| --- | --- | --- |
| Original vsFTPd 2.3.4 service and a successful session | The intentionally vulnerable target exhibited the tested backdoor behaviour. | Banner information alone is not proof about another host. |
| Edited anonymous settings, followed by a successful anonymous FTP login | The configuration-only attempt did not demonstrate an effective access restriction. | The precise reason it remained effective was not isolated conclusively. |
| FTP disabled in xinetd; port 21 closed, but 6200 open | The primary FTP service stopped being reachable while a separate listener remained. | Closing port 21 alone was not complete containment of the observed path. |
| Remaining listener terminated; both relevant ports closed; no session created | The observed access path was contained at the time of verification. | No vulnerable executable was patched or replaced. |
| Snapshot restored; FTP opened again; session opened again | The saved original vulnerable state was recovered and reproduced in the same lab. | Containment changes were rolled back, not retained. |

### What I want to remember when revising

1. **Separate the target and tester.** Kali checks and reports the result; Metasploitable holds the configuration being changed.
2. **Back up first and verify the backup.** A mistyped `cp` command is not a backup.
3. **Saved does not mean applied.** Check the running service and then test independently.
4. **Configuration weakness and compromised software are different.** Setting anonymous access to `NO` does not repair the vsFTPd 2.3.4 backdoor.
5. **Service management depends on the system.** Here, xinetd was relevant; a modern systemd walkthrough would not map one-for-one.
6. **A service can be closed while a different listener survives.** TCP/6200 required separate local and external checks.
7. **Do not hide failed commands.** The incorrect paths, typos, restart attempts and negative results explain the actual investigation.
8. **Use snapshots deliberately.** The saved baseline let me document containment and still restore a clean starting point for new coursework.

### Limitations

This is a time-bounded observation on a deliberately vulnerable legacy VM. I did not replace or repair the compromised binary, check every possible access path, or claim that the entire host was secure. Process IDs and lab IP addresses are details of this run. The next six-port coursework exercise is separate and should follow the specific configuration change required for each service rather than automatically disabling every service.

### Evidence handling

The `images/` folder contains every original PNG provided for this package, copied byte-for-byte at its supplied resolution. Images are numbered in **capture order**, not reordered to make the story look cleaner. Each image is embedded at the corresponding point above, not relegated to an unstructured supplement. The visible private IPs and user names refer to the lab. I should still review any public repository for passwords, tokens, external hosts or personal information before publication.

---

**Conclusion:** My initial attempt to change anonymous FTP settings did not establish a fix. I then traced the legacy service, disabled FTP through xinetd, identified and terminated a remaining listener, and confirmed the relevant ports were closed and the original test no longer produced a session. Restoring the baseline returned the original vulnerable state and reproduced the initial result. I have kept the full chronology here so I can revise what happened, including the detours, rather than just remember the final outcome.

