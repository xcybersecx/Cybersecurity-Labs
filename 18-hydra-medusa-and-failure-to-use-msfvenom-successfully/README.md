# 18. Hydra and Medusa Credential Auditing and an Unsuccessful msfvenom Exercise

**Dates:** 30 September, 6 October and 7 October 2026  
**Status:** Valid lab credentials reported for FTP and SSH; payload generation and transfer documented, but no successful payload session demonstrated  
**Evidence:** All 46 original screenshots in capture order  
**Scope:** My personally controlled Kali Linux and deliberately vulnerable Metasploitable 2 virtual machines

## Overview

This exercise had two distinct outcomes. Hydra and Medusa identified the deliberately weak training credentials on reachable services. However, my later attempt to generate, transfer and run a payload did not produce a successful session. I kept both outcomes and the failed attempts because this repository is my revision notebook, not a reconstruction that makes every step look successful.

The sequence begins with tool checks on 30 September, continues with service enumeration and credential auditing on 6 October, and ends with transfer and execution troubleshooting on 7 October. The payload generator did produce files, and some transfers completed. Those milestones did not establish successful execution: the target displayed HTML parsing errors, path errors and segmentation faults.

Framework and payload screenshots document work I performed independently. The narrative records observations and outcomes without adding operational exploitation instructions.

## Objectives

- Check the installed tools and establish the current VM addresses.
- Locate candidate lists, then prepare a small list for a controlled training exercise.
- Compare Hydra and Medusa results across FTP, SSH and Telnet.
- Distinguish a valid credential result from a connection or protocol-negotiation failure.
- Document file generation, transfer and execution as separate checkpoints.
- Preserve mistakes, repeated attempts and unresolved results in chronological order.

## Environment and tools

| Component | Evidence in this exercise |
| --- | --- |
| Hypervisor | Oracle VirtualBox |
| Testing machine | Kali Linux |
| Target | Metasploitable 2; console confirms the current target address on 6 October |
| Address changes | Earlier work used different lab addresses; later generation and transfer captures use updated Kali and target addresses |
| Enumeration | Nmap 7.99 and local interface checks |
| Credential auditing | Hydra 9.7; Medusa 2.3; FTP, SSH and Telnet modules |
| Candidate lists and editors | SecLists, RockYou search results, Weakpass browsing, nano and GVim |
| Local custom input | `weakpassword.txt`, used for both username and password candidates |
| Host-list input | `protocol.txt`, despite its name, contains IP addresses |
| Package and tool checks | Package-index refresh, package-policy query and installed-version query |
| File-transfer evidence | Local Python HTTP server, SCP, SSH and wget |
| Independent payload work | msfvenom and framework console, documented as outcomes only |

The host list included the current target and two earlier lab addresses. Only the current target has a valid credential result in these captures. Connection failures against the other addresses do not prove that their credentials were secure or that earlier hardening caused the failure.

## Chronological practical stages

### 1. Initial tool checks, 30 September

I began by checking whether the payload generator was installed. Its path was found and its help output worked, but its version query returned **unknown**. That inconsistency prompted package checks; it was not proof that the executable was missing.

![Figure 01: Executable found, help displayed and version reported as unknown.](Screenshot%202026-09-30%20170444.png)

*Figure 01 (2026-09-30, 17:04:44). Executable found, help displayed and version reported as unknown.*

I refreshed the package indexes, checked the framework package policy and queried the installed package version. The installed and candidate package versions matched in this capture. Refreshing indexes did not itself reinstall or upgrade the package.

![Figure 02: Package-index refresh and installed framework version checks.](Screenshot%202026-09-30%20175553.png)

*Figure 02 (2026-09-30, 17:55:53). Package-index refresh and installed framework version checks.*

An initial generation attempt reported an invalid payload name. A later attempt in the same terminal produced output with a final file size of **207 bytes**. This established generation output, not successful target execution.

![Figure 03: Initial generation error followed by file-generation output.](Screenshot%202026-09-30%20180207.png)

*Figure 03 (2026-09-30, 18:02:07). Initial generation error followed by file-generation output.*

I started a local HTTP server on port **8085**. This capture shows the server listening, but contains no request log establishing a target download at this stage.

![Figure 04: Initial local file-serving setup.](Screenshot%202026-09-30%20180748.png)

*Figure 04 (2026-09-30, 18:07:48). Initial local file-serving setup.*

### 2. Updated target address and candidate-list preparation, 6 October

On 6 October, I checked the target console with `ip a`. It now showed the current target address, so the earlier target address could no longer be assumed.

![Figure 05: Target console confirms the updated private address.](Screenshot%202026-10-06%20081057.png)

*Figure 05 (2026-10-06, 08:10:57). Target console confirms the updated private address.*

A scan of the earlier target address reported the host down. I then inspected Kali interfaces and began a scan of the current target. The address correction was necessary before interpreting later authentication results.

![Figure 06: Old-address scan fails; local interfaces and new target are checked.](Screenshot%202026-10-06%20081157.png)

*Figure 06 (2026-10-06, 08:11:57). Old-address scan fails; local interfaces and new target are checked.*

The scan of the current target completed and identified FTP, SSH, Telnet and many other exposed services. This inventory showed service reachability; it did not establish valid credentials by itself.

![Figure 07: Service inventory on the current Metasploitable target.](Screenshot%202026-10-06%20081420.png)

*Figure 07 (2026-10-06, 08:14:20). Service inventory on the current Metasploitable target.*

I searched the installed system for SecLists. The long list of paths confirmed available resources, but also showed why finding the collection was different from selecting a manageable file for this exercise.

![Figure 08: Locating installed SecLists resources.](Screenshot%202026-10-06%20081622.png)

*Figure 08 (2026-10-06, 08:16:22). Locating installed SecLists resources.*

I browsed Weakpass while exploring candidate-list sources. This screenshot documents resource exploration, not use of a downloaded corpus in the later tests.

![Figure 09: Weakpass resource browsing.](Screenshot%202026-10-06%20082006.png)

*Figure 09 (2026-10-06, 08:20:06). Weakpass resource browsing.*

I opened the all-in-one list page and began downloading its archive. The page advertised a very large compressed archive and a much larger extracted corpus. The capture shows a download in progress, with no evidence that it completed or became the list used later.

![Figure 10: Large candidate-list archive download in progress.](Screenshot%202026-10-06%20082543.png)

*Figure 10 (2026-10-06, 08:25:43). Large candidate-list archive download in progress.*

I returned to the terminal and opened a local file named `weakpassword.txt` on the Desktop. The earlier SecLists search output remains visible above the editor command.

![Figure 11: Beginning preparation of a local custom candidate list.](Screenshot%202026-10-06%20082856.png)

*Figure 11 (2026-10-06, 08:28:56). Beginning preparation of a local custom candidate list.*

I searched for RockYou and found several related paths, including a text list and other resources with similar names. The search result did not mean every returned file was interchangeable.

![Figure 12: RockYou-related list and resource locations.](Screenshot%202026-10-06%20083128.png)

*Figure 12 (2026-10-06, 08:31:28). RockYou-related list and resource locations.*

I navigated to the directory containing the located RockYou text file, listed its contents and opened the file in nano. This was exploration before returning to the smaller custom list.

![Figure 13: Located RockYou text file opened for inspection.](Screenshot%202026-10-06%20083530.png)

*Figure 13 (2026-10-06, 08:35:30). Located RockYou text file opened for inspection.*

Nano displayed the RockYou list and reported over fourteen million lines. This illustrated the difference in scale between a large existing corpus and a short list suited to the immediate classroom exercise.

![Figure 14: Large RockYou list viewed in nano.](Screenshot%202026-10-06%20083616.png)

*Figure 14 (2026-10-06, 08:36:16). Large RockYou list viewed in nano.*

I returned to editing `weakpassword.txt`. This intermediate capture preserves the preparation sequence, without showing a completed audit result.

![Figure 15: Further editing of the local custom list.](Screenshot%202026-10-06%20084158.png)

*Figure 15 (2026-10-06, 08:41:58). Further editing of the local custom list.*

### 3. Hydra attempts and the FTP result

I opened Hydra help to review its inputs and supported services. I needed to distinguish account candidates, password candidates and target addresses before interpreting a run.

![Figure 16: Hydra help and supported-service information.](Screenshot%202026-10-06%20084252.png)

*Figure 16 (2026-10-06, 08:42:52). Hydra help and supported-service information.*

I began an FTP credential-audit attempt against the current target using the local candidate file for both account and password inputs. This capture records the start of the attempt rather than a valid credential finding.

![Figure 17: Initial Hydra FTP audit setup.](Screenshot%202026-10-06%20084814.png)

*Figure 17 (2026-10-06, 08:48:14). Initial Hydra FTP audit setup.*

The FTP audit printed progress and was interrupted. Hydra wrote a restore file. I recorded it as an incomplete run, not evidence that all candidates had failed.

![Figure 18: Interrupted Hydra FTP attempt and saved restore state.](Screenshot%202026-10-06%20085704.png)

*Figure 18 (2026-10-06, 08:57:04). Interrupted Hydra FTP attempt and saved restore state.*

I edited the custom candidate file in GVim. The capture shows INSERT mode and the end of the list, including an added service-name entry. Its presence in a list does not make it an actual account on the target.

![Figure 19: Custom candidate list edited in GVim.](Screenshot%202026-10-06%20093232.png)

*Figure 19 (2026-10-06, 09:32:32). Custom candidate list edited in GVim.*

I tried Telnet and SSH after further interrupted Telnet attempts. The SSH output reported a negotiation failure involving incompatible MAC algorithms, so authentication could not proceed in that attempt. A protocol error is different from an incorrect password result.

![Figure 20: Telnet interruptions and Hydra SSH negotiation failure.](Screenshot%202026-10-06%20100845.png)

*Figure 20 (2026-10-06, 10:08:45). Telnet interruptions and Hydra SSH negotiation failure.*

I repeated SSH attempts with different candidate inputs, but the same MAC-negotiation failure appeared. The captures contain no Hydra SSH credential success, and reducing or changing candidates did not resolve the observed protocol issue.

![Figure 21: Repeated Hydra SSH attempts remain blocked by negotiation errors.](Screenshot%202026-10-06%20100908.png)

*Figure 21 (2026-10-06, 10:09:08). Repeated Hydra SSH attempts remain blocked by negotiation errors.*

I shortened the custom list in GVim. The visible entries included the training account and a few other candidates. Later tool output shows that the lists changed during preparation, so I do not assign one fixed line count to every run.

![Figure 22: Short custom username and password candidate list.](Screenshot%202026-10-06%20101156.png)

*Figure 22 (2026-10-06, 10:11:56). Short custom username and password candidate list.*

I created `protocol.txt` containing three private IP addresses: the current target and two earlier lab addresses. Despite the filename, it was a host list, not a list of protocols or services.

![Figure 23: Three-address target file prepared in nano.](Screenshot%202026-10-06%20102022.png)

*Figure 23 (2026-10-06, 10:20:22). Three-address target file prepared in nano.*

Hydra reported a valid FTP login on the current target using the default training account and password. It also reported connection errors and that only **one of three targets** completed successfully. I kept the credential success and incomplete host coverage as separate findings.

![Figure 24: Hydra reports valid FTP lab credentials with connection errors elsewhere.](Screenshot%202026-10-06%20102330.png)

*Figure 24 (2026-10-06, 10:23:30). Hydra reports valid FTP lab credentials with connection errors elsewhere.*

### 4. Medusa results for FTP, SSH and Telnet

I opened Medusa help. Its option layout differed from Hydra, so I reviewed how it accepts account, password, host and service inputs rather than assume the two interfaces were identical.

![Figure 25: Medusa help and input options.](Screenshot%202026-10-06%20102546.png)

*Figure 25 (2026-10-06, 10:25:46). Medusa help and input options.*

Medusa reported **ACCOUNT FOUND** and **SUCCESS** for FTP on the current target, using the same default lab pair. Attempts against an earlier target address and another earlier lab address failed to connect. This corroborated the FTP credential finding on the reachable target without demonstrating full coverage of the host list.

![Figure 26: Medusa confirms the FTP credential result on the reachable target.](Screenshot%202026-10-06%20102911.png)

*Figure 26 (2026-10-06, 10:29:11). Medusa confirms the FTP credential result on the reachable target.*

Medusa then reported the same pair as valid for SSH on the current target. The remaining addresses again produced connection errors. This tool-level success contrasts with Hydra failing at SSH negotiation, although the screenshots do not isolate the library or protocol difference responsible.

![Figure 27: Medusa reports valid SSH lab credentials.](Screenshot%202026-10-06%20103101.png)

*Figure 27 (2026-10-06, 10:31:01). Medusa reports valid SSH lab credentials.*

A subsequent Medusa Telnet attempt failed to identify the login prompt on the current target, and the other addresses could not be reached on the expected service port. There is no valid Telnet credential result in this screenshot.

![Figure 28: Medusa Telnet prompt-identification and connection failures.](Screenshot%202026-10-06%20103145.png)

*Figure 28 (2026-10-06, 10:31:45). Medusa Telnet prompt-identification and connection failures.*

### 5. Independent generation, transfer and execution attempts, 6 and 7 October

I returned to independent payload work and displayed the generator’s payload inventory. This demonstrates that the tool could list its supported entries, but does not establish execution on the target.

![Figure 29: Payload inventory displayed during the independent exercise.](Screenshot%202026-10-06%20105335.png)

*Figure 29 (2026-10-06, 10:53:35). Payload inventory displayed during the independent exercise.*

On 7 October, the generator reported that it saved a new ELF file with a final size of **233 bytes**. I recorded generation as its own milestone. The filename `working_shell.elf` expressed my intention, not a verified working result.

![Figure 30: ELF file generated and saved with a reported size of 233 bytes.](Screenshot%202026-10-07%20161607.png)

*Figure 30 (2026-10-07, 16:16:07). ELF file generated and saved with a reported size of 233 bytes.*

I started a local HTTP server from the Downloads directory on port **8080**. This prepared a transfer method; it did not prove that the target had received the file.

![Figure 31: Local HTTP file server started from Downloads.](Screenshot%202026-10-07%20162127.png)

*Figure 31 (2026-10-07, 16:21:27). Local HTTP file server started from Downloads.*

I repeated generation with a different callback address and saved another file under the same name. The changing addresses and overwritten filename make the individual captures important, rather than treating every file bearing that name as identical.

![Figure 32: Regeneration after changing the recorded callback address.](Screenshot%202026-10-07%20162905.png)

*Figure 32 (2026-10-07, 16:29:05). Regeneration after changing the recorded callback address.*

I generated the file again with another port value. The tool again reported a 233-byte result. These parameter changes were independent attempts, with no successful session demonstrated in the capture.

![Figure 33: Further independent generation attempt with changed parameters.](Screenshot%202026-10-07%20163006.png)

*Figure 33 (2026-10-07, 16:30:06). Further independent generation attempt with changed parameters.*

I captured the HTTP server again, listening from Downloads. This is a repeated setup checkpoint, not an additional successful transfer result.

![Figure 34: Repeated local HTTP-server setup capture.](Screenshot%202026-10-07%20163033.png)

*Figure 34 (2026-10-07, 16:30:33). Repeated local HTTP-server setup capture.*

An SCP transfer initially failed because of legacy host-key negotiation. A connection-specific compatibility override allowed the transfer to complete, and the progress output showed **233 bytes** copied. This confirmed the transfer milestone, without validating execution.

![Figure 35: SCP negotiation error followed by a completed 233-byte transfer.](Screenshot%202026-10-07%20164427.png)

*Figure 35 (2026-10-07, 16:44:27). SCP negotiation error followed by a completed 233-byte transfer.*

I logged into the target over SSH after the transfer. The successful administrative session demonstrates account access, not a reverse session from the generated file.

![Figure 36: Administrative SSH login after the SCP transfer.](Screenshot%202026-10-07%20164633.png)

*Figure 36 (2026-10-07, 16:46:33). Administrative SSH login after the SCP transfer.*

The target history contains a malformed path formed by joining two file paths, followed by a corrected permission operation and an execution attempt. The latter ended in **Segmentation fault**. The file had arrived, but the captured execution failed.

![Figure 37: Path mistake followed by a segmentation fault on execution.](Screenshot%202026-10-07%20165110.png)

*Figure 37 (2026-10-07, 16:51:10). Path mistake followed by a segmentation fault on execution.*

I tried another transfer route. The history includes an invalid wget option, then a request to the server without the active HTTP-server port, which returned connection refused. These were syntax and endpoint errors, not evidence of a valid file download.

![Figure 38: Download-option error and connection refusal.](Screenshot%202026-10-07%20170406.png)

*Figure 38 (2026-10-07, 17:04:06). Download-option error and connection refusal.*

A request to the HTTP server root returned **200 OK**, but the response was **576,656 bytes** of `text/html`. That differed sharply from the generated 233-byte file. The successful HTTP response had retrieved a page, not demonstrated retrieval of the intended ELF.

![Figure 39: HTTP request succeeds but retrieves a large HTML response.](Screenshot%202026-10-07%20170600.png)

*Figure 39 (2026-10-07, 17:06:00). HTTP request succeeds but retrieves a large HTML response.*

I independently started a framework listener. This screenshot shows startup and a listening message, with no session-opened result. A listener running is a separate checkpoint from the target successfully executing a file.

![Figure 40: Independent listener startup without a demonstrated session.](Screenshot%202026-10-07%20170906.png)

*Figure 40 (2026-10-07, 17:09:06). Independent listener startup without a demonstrated session.*

The listener history contains a user interrupt, a mistyped options command and another startup. None of the visible output establishes a successful payload session. I retained these intermediate attempts in order.

![Figure 41: Listener interruption, command typo and restart attempt.](Screenshot%202026-10-07%20171233.png)

*Figure 41 (2026-10-07, 17:12:33). Listener interruption, command typo and restart attempt.*

I regenerated the file again and received a 233-byte output report. This is another generation checkpoint, rather than evidence that the later target-side failure had been resolved.

![Figure 42: Repeated 233-byte file-generation output.](Screenshot%202026-10-07%20171346.png)

*Figure 42 (2026-10-07, 17:13:46). Repeated 233-byte file-generation output.*

The target attempted to execute the previously downloaded file and reported a syntax error showing `<!DOCTYPE html>`. This directly corroborated that the saved file contained HTML. Giving it an `.elf` filename and executable permissions had not changed its contents.

![Figure 43: Execution error exposes HTML in the downloaded file.](Screenshot%202026-10-07%20171749.png)

*Figure 43 (2026-10-07, 17:17:49). Execution error exposes HTML in the downloaded file.*

The HTTP server logs showed requests for `/` returning successful responses. These root-directory requests are consistent with the HTML download seen on the target; they do not demonstrate that the intended file endpoint was requested at this point.

![Figure 44: HTTP request logs show root-directory requests.](Screenshot%202026-10-07%20171926.png)

*Figure 44 (2026-10-07, 17:19:26). HTTP request logs show root-directory requests.*

Further target-side history showed another server-root download, a mistyped address that could not resolve and another large HTML response. I kept the repeated errors because they explain why a successful transfer indicator was misleading.

![Figure 45: Repeated HTML retrieval and an address-resolution error.](Screenshot%202026-10-07%20172306.png)

*Figure 45 (2026-10-07, 17:23:06). Repeated HTML retrieval and an address-resolution error.*

The final capture records another HTML parsing failure, then a request for the actual filename returning **233 bytes** as `application/octet-stream`. The file was saved in the current directory, while subsequent attempts first referred to the old `/tmp` path and failed. Execution from the current location finally ran far enough to report **Segmentation fault**. No successful session is visible, and the precise cause of that crash remains unresolved.

![Figure 46: Actual file downloaded; stale-path errors followed by another segmentation fault.](Screenshot%202026-10-07%20174001.png)

*Figure 46 (2026-10-07, 17:40:01). Actual file downloaded; stale-path errors followed by another segmentation fault.*

## Before I repeat this lab

**Planned repeat, not yet completed.** These are checks I intend to apply next time. They do not change the original results or guarantee that the unresolved crash will disappear.

### 1. Confirm my starting state

- [ ] Record the VirtualBox snapshot and whether earlier hardening has been rolled back.
- [ ] Check the current address on each VM rather than reuse an old screenshot.
- [ ] Record tester and target roles separately in my local notes.
- [ ] Confirm the intended service is reachable before interpreting authentication results.
- [ ] Record installed package versions. Investigate an unknown version display rather than automatically reinstalling a tool whose help and package checks work.

**Revisit Figures 01–07:** the earlier target address was stale, and refreshing package indexes did not demonstrate a reinstall.

### 2. Prepare clear credential-audit inputs

- [ ] Use separate, clearly named files for username candidates, password candidates and lab targets.
- [ ] Start with a small classroom list that I can inspect completely.
- [ ] Check spelling, capitalisation, blank lines and accidental spaces. Save and reopen the file to verify its contents.
- [ ] Include only currently verified, authorised lab targets. Remove stale addresses from the new input.
- [ ] Record which input files were used in each attempt, since I edited them during the original run.
- [ ] Identify whether a run is fresh or resumed so an earlier restore file does not confuse the record.

**Revisit Figures 08–24:** the large corpus was explored, but the successful result used the custom input. The file called `protocol.txt` contained hosts.

### 3. Classify the error before changing anything

| Error or result | My next check |
| --- | --- |
| Connection refused or unreachable host | Recheck the address, VM state and service availability before drawing a password conclusion. |
| SSH MAC or host-key negotiation error | Record a compatibility failure separately from an authentication failure. Keep legacy compatibility work confined to the training VM. |
| Telnet prompt-identification failure | Preserve the actual prompt and error for review; the result remains unresolved. |
| Interrupted audit | Mark it incomplete and preserve its output and resume state. |
| Valid credentials plus other-host errors | Record the successful target separately from targets that were not tested successfully. |

**Revisit Figures 18–28:** Hydra's SSH negotiation failure and Medusa's SSH success were different outcomes. Telnet remained unresolved.

### 4. Verify ordinary file handling

For my independently performed generation and execution work, I intend to record the source file, destination file and each observed result separately.

- [ ] Record the full source path, byte count and identified file type before transfer.
- [ ] Confirm the directory being served and distinguish a directory page from an individual file.
- [ ] Check received content type and byte count. HTTP success alone is insufficient.
- [ ] Identify the received file and compare its checksum with the source before treating them as identical. Matching size alone is insufficient.
- [ ] Record the actual destination directory and use that path consistently in subsequent inspection.
- [ ] Check spaces between commands, options and paths; avoid accidentally joining two full paths.
- [ ] Keep attempts distinguishable in my notes instead of silently overwriting earlier evidence.
- [ ] Stop and investigate unexpected HTML content. A filename extension or executable permission does not establish file type.

**Revisit Figures 35–39 and 43–46:** I encountered HTML saved under an executable filename, and later referred to an old destination after downloading into the current directory.

### 5. Treat the segmentation fault as unresolved

The HTML download explains the parsing errors. It does **not** establish the cause of the segmentation faults. A crash appeared after the SCP transfer and again after the later 233-byte download.

If the crash recurs, I intend to stop repeating the same attempt, preserve the exact error and record file identity, target operating-system and architecture information, and relevant diagnostics for a separate compatibility review. I will change one variable at a time and document why. I have not established a working repair for the crash.

**Revisit Figures 37 and 46.**

### 6. Save evidence for the new attempt

| Checkpoint | What I intend to record |
| --- | --- |
| Starting state | Snapshot, VM roles and service availability |
| Input preparation | Saved input-file descriptions without publishing credential values |
| Credential audit | Exact success, failure, interruption or negotiation result for each service |
| Ordinary transfer | Source and received file type, size, checksum and location |
| Independent execution | Exact observed outcome, including any crash |
| Final assessment | What worked, what remained unresolved and what changed |

I will append the repeat attempt with its own date and figure numbers, preserving the original 46 screenshots for comparison.


## Troubleshooting

| Observation | Interpretation supported by the evidence |
| --- | --- |
| Version query returned unknown, but help and package queries worked | The tool existed; the version display alone did not establish a broken installation. |
| Scan of the earlier target address reported host down | The VM address needed rechecking before testing services. |
| Very large list download was started | No completed download or use of that corpus is demonstrated. Later audits used the custom list. |
| Hydra runs were interrupted | Incomplete runs are not exhaustive negative credential results. |
| Hydra SSH reported incompatible MAC algorithms | The observed attempt failed during negotiation, before a valid credential result. |
| Hydra FTP found a valid pair while other connections failed | A positive result on one reachable host can coexist with incomplete overall coverage. |
| Medusa SSH reported success where Hydra had negotiation errors | Tool-specific results differed; the underlying compatibility cause was not isolated. |
| Medusa Telnet could not identify the prompt | This did not establish successful Telnet authentication or a secure password. |
| SCP initially rejected legacy host keys | A compatibility workaround allowed transfer; it did not upgrade the old server. |
| HTTP returned 200 OK and text/html | Transport success did not establish retrieval of the intended binary. |
| An .elf-named file contained a DOCTYPE line | The wrong content had been saved under the desired filename. |
| Actual file saved in the current directory; old /tmp path still used | The transfer destination and later referenced path differed. |
| Final execution ended in a segmentation fault | Execution remained unsuccessful; the crash cause was not established. |

## Findings

| Test or milestone | Observed result | Limit |
| --- | --- | --- |
| Hydra FTP, current target | Valid default lab pair reported | Only one of three listed targets completed successfully. |
| Hydra SSH | MAC-negotiation errors | No valid SSH credential result from Hydra is captured. |
| Medusa FTP, current target | Same lab pair reported as SUCCESS | Other listed hosts produced connection errors. |
| Medusa SSH, current target | Same lab pair reported as SUCCESS | Success is documented in tool output; a separate manual SSH login appears later in the sequence. |
| Telnet attempts | Interruptions, negotiation/prompt difficulties and connection errors | No successful Telnet credential finding is documented. |
| File generation | Output files reported, including a later 233-byte ELF | Generation did not establish successful execution. |
| SCP | Completed 233-byte transfer | Target execution subsequently crashed. |
| HTTP root requests | Large HTML response downloaded | Wrong content for the intended executable. |
| Later filename request | 233-byte application/octet-stream response | File-type verification and byte-for-byte comparison are not captured. |
| Final execution | Segmentation fault | No successful payload session is demonstrated. |

## Defensive significance

The FTP and SSH results illustrate the risk of leaving known training defaults available on reachable services. In a real deployment, service exposure and default account credentials would require remediation and a separate retest. This lab does not show those remediation steps being performed.

The failures against other addresses cannot be treated as proof of password strength, lockout, or successful hardening. A service may be unavailable, the address may be stale, or the tool may fail to negotiate the protocol. I need to establish reachability and protocol compatibility before interpreting a negative credential result.

The file-transfer sequence also illustrates a general validation lesson: a filename, success status or completed progress bar is not enough to establish what was received. Here, the content type, byte count and displayed HTML error exposed the mismatch.

## Limitations

These are observations from deliberately vulnerable training VMs, with changing addresses and several edited input files. The screenshots do not establish complete coverage of every candidate, target or service. They also do not establish comparative tool performance under identical conditions.

I did not demonstrate that refreshing package indexes reinstalled the framework or fixed the unknown version display. I did not demonstrate a completed Weakpass archive download or use of that archive in the audits.

The generation, transfer and listener screenshots do not establish a working payload session. The final correct-looking download still ended in a segmentation fault. Architecture, runtime compatibility, file integrity and other possible crash causes were not isolated, so I do not assign a definitive explanation to the crash.

## Evidence and privacy

All **46 original screenshots** remain under their original timestamped filenames and are embedded once above in chronological order. Repeated terminal histories, editor captures and failed attempts remain visible because they help me retrace my work.

The original screenshots are already present in this repository. The written narrative describes account findings and machine roles without repeating credential values or private IP addresses. Image paths encode spaces and point to the existing PNGs in this folder.

## What I learned

1. A VM address is a current observation, not a permanent property of the lab.
2. List size and list purpose matter; usernames, passwords and target addresses are different inputs even when filenames are misleading.
3. A valid credential result, an interrupted run and a protocol failure need different conclusions.
4. Two tools can produce different outcomes against the same service without establishing that one is universally better.
5. File generation, transfer, execution and session establishment are separate milestones.
6. A successful HTTP response can contain the wrong resource, and changing its extension does not change its type.
7. Current-directory files and absolute paths must be distinguished when reviewing terminal history.
8. An unsuccessful exercise still provides useful evidence if I preserve the failure and state what remains unresolved.

## Conclusion

Hydra reported valid FTP training credentials, and Medusa reported the same pair for both FTP and SSH on the reachable Metasploitable target. Telnet remained unresolved. My independent payload exercise generated and transferred files, but encountered wrong-content downloads, path mistakes and segmentation faults, with no successful session demonstrated. I have retained the full sequence so I can revise both the successful credential-audit results and the unresolved execution failure accurately.
