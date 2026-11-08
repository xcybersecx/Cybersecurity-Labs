# Lab 20: AI-Assisted Network Reconnaissance with PentAGI, Dahl (Gonka Network) and Nmap

**Lab date:** 8 November 2026  
**Environment:** Kali Linux (VirtualBox), Docker, PentAGI v2.2.0-ce, Metasploitable 2  
**AI inference gateway:** Dahl, backed by the Gonka network  
**Target:** `192.168.1.119` (personally controlled, deliberately vulnerable training VM)  
**Scope:** Configuration, provider troubleshooting, controlled service discovery, interpretation and performance observations

> **Scope and safety:** This is an authorised lab using a Metasploitable 2 virtual machine. The scan was restricted to seven explicitly selected TCP ports. No exploitation, password attacks or unrelated host scanning were part of the final assessment. The target address is an example of the lab's address on the day of testing, not a reusable target for other networks.

## Executive summary

I integrated a fresh Dahl inference account into an existing PentAGI installation running inside Kali Linux, configured model assignments for PentAGI's agent roles, diagnosed API errors and tested actual tool execution. The first Assistant workflow generated a partial response but subsequently failed with HTTP **502**, empty responses and reflector retries. A model availability check showed **83.33% reported one-hour uptime** for MiniMax M2.7, compared with 100% for GLM-5.3 Flash and DeepSeek V4 Flash during that snapshot. This was evidence of instability, but not proof of the precise cause of the failures.

I changed the saved PentAGI **Assistant** role to GLM-5.3 Flash and tested direct answers separately from the much heavier Automation mode. Direct Assistant requests were responsive. The final controlled assessment successfully executed Nmap from PentAGI's container against my Metasploitable 2 VM. All seven requested ports were open, and **the Nmap command itself reported 11.39 seconds**. This figure is *not* the complete AI workflow duration.

## Learning objectives

- Identify the location and running state of an existing PentAGI installation rather than reinstalling it.
- Understand the difference between Kali, Docker containers, a model provider and PentAGI's saved provider profile.
- Add an external inference gateway without deleting existing Gemini or Ollama providers.
- Diagnose a provider that can answer intermittently but fails under repeated agent requests.
- Distinguish model-response latency from multi-agent automation overhead.
- Validate practical tool execution with `pwd` and a scoped Nmap service scan.
- Produce a defensible record of the process, evidence, findings and limitations.

## Environment and configuration overview

| Component | Configuration observed |
|---|---|
| Kali user / home | `x` / `/home/x` |
| PentAGI installation | `/home/x/pentagi` |
| Application | PentAGI v2.2.0-ce at `https://localhost:8443` |
| Container engine | Docker 28.5.2 reported by `docker --version` |
| Inference endpoint | `https://inference.dahl.global/v1` |
| Named provider profile | `Dahl Gonka 50M` |
| Account allocation | 50 million tokens allocated to the selected API key, **not** a consumption figure |
| Saved existing providers | `Gemini Cyber Lab`, `Local Llama 3.1` |
| Final direct Assistant role | `zai-org/GLM-5.3-Flash` |
| Specialist roles configured | DeepSeek V4 Flash for Primary Agent, Adviser and Pentester |
| Other supporting roles | MiniMax M2.7 in the documented initial configuration |
| Scan host | Metasploitable 2, `192.168.1.119` |

**Important:** Model names and prices appearing in PentAGI's downloaded example YAML were configuration defaults, not verified Dahl billing rates. Actual account usage and billing need to be checked in Dahl.

---

## 1. Preparing the Dahl account and key allocation

I started with a new Dahl account on my cybersecurity laptop. After creating the API key, the account screen showed the key as **Exhausted** with **0/0** tokens assigned. That meant the key had no usable allocation, not necessarily that the account's overall token pool had been consumed.

![Dahl key initially showing no allocation](screenshots/01-dahl-key-allocation.png)

*Figure 1.* Dahl's API-key panel before allocation. The key displayed no allocated tokens. I subsequently assigned **50 million tokens** from the available pool to the key used for the PentAGI provider. The full API key and its fingerprint are intentionally excluded from this report.

### Why the allocation matters

A provider's API key handles authentication. The allocated token allowance governs account-side use. Neither proves the model is reachable or has free inference capacity. Therefore, later tests checked the model catalogue and service status independently.

## 2. Finding the existing PentAGI installation

I initially worked from my Kali home directory and used the terminal to determine the working path. The initial recursive name search did not reveal the expected folder, so I examined shell history and then verified the previously created installer directory directly.

```bash
pwd
ls -la
history | grep -i pentagi
ls -ld ~/pentagi
ls -la /home/x/pentagi
```

Shell history showed an earlier `mkdir -p ~/pentagi && cd ~/pentagi` and an attempted installer download. The files confirmed an installer-based setup rather than the Git clone I first remembered.

![Kali terminal showing earlier installation investigation](screenshots/02-kali-installation-search.png)

*Figure 2.* Read-only terminal investigation to retrace the existing installation. This avoided assuming that PentAGI needed to be installed again.

![PentAGI installation directory and configuration file listing](screenshots/03-pentagi-directory.png)

*Figure 3.* The installation directory contained `.env`, `docker-compose.yml`, the installer, and example provider files. The `.env` file contained secrets and was inspected only through redacted checks. No credential-bearing configuration file is included in this repository.

I checked that the Docker client was installed and used `sudo docker ps` after receiving a socket-permission error as the ordinary user. Running containers included the main `pentagi` service, `pgvector`, scraper and supporting terminals. The successful command established that the deployment was already running.

```bash
docker --version
sudo docker ps
```

## 3. Backing up and configuring the external provider

Before editing, I made a local copy of the existing environment file:

```bash
cp -p /home/x/pentagi/.env /home/x/pentagi/.env.backup-20261108
```

This file contains credentials and **must remain local**. The report records only the *names* of the relevant settings and their non-secret values:

```dotenv
LLM_SERVER_URL=https://inference.dahl.global/v1
LLM_SERVER_KEY=<REDACTED_DAHL_KEY>
LLM_SERVER_MODEL=deepseek-ai/DeepSeek-V4-Flash-0731
LLM_SERVER_CONFIG_PATH=/opt/pentagi/conf/custom.provider.yml
```

The key entered was the key allocated 50 million tokens, not the fingerprint. I verified the key was nonempty without printing its value. Configuration presence alone is not a connectivity test.

I also inspected how `docker-compose.yml` mounted the custom provider YAML. In this installation the Compose volume mapping exposed the host custom-provider file at `/opt/pentagi/conf/custom.provider.yml`. The underlying Compose substitution used `PENTAGI_LLM_SERVER_CONFIG_PATH`, which is distinct from the `LLM_SERVER_CONFIG_PATH` setting shown above. This distinction matters if the mount source is customized in the future.

The downloaded reference YAML originally listed models such as `gpt-4.1-mini` and `o3-mini`. Those were *template placeholders*, not the models selected for Dahl. I updated the example YAML and reviewed all 13 model assignments before creating the provider.

![Terminal inspection of Compose mount and downloaded example configuration](screenshots/04-compose-and-template.png)

*Figure 4.* The terminal shows the YAML mount, the originally empty custom-provider example, the reference download and model names in the untouched template. This captures why the provider required an explicit model-mapping step rather than merely supplying an API URL.

![Model roles mapped to the Dahl catalogue](screenshots/05-model-roles.png)

*Figure 5.* Command-line verification of the model mapping. The initial design used DeepSeek for the Primary Agent, Adviser and Pentester and MiniMax for the ten remaining roles. Model-role assignments were proposed for testing, not proven performance rankings.

The Dahl public model catalogue returned three exact identifiers:

```text
zai-org/GLM-5.3-Flash
MiniMaxAI/MiniMax-M2.7
deepseek-ai/DeepSeek-V4-Flash-0731
```

A listing at `/v1/models` verifies model names exposed by the gateway, but does not guarantee availability for every request.

## 4. Creating the saved provider in PentAGI

Docker Compose validation completed without errors:

```bash
cd /home/x/pentagi
sudo docker compose config --quiet
sudo docker compose up -d pentagi
```

PentAGI started and the PostgreSQL container was healthy. I opened the application in Kali Firefox at `https://localhost:8443`, navigated to **Settings → Providers**, and created a new **Custom** provider named **Dahl Gonka 50M**.

![Creating a custom provider in PentAGI](screenshots/06-create-custom-provider.png)

*Figure 6.* The new-provider form showed the Custom type and the individual agent roles available for testing and configuration.

![Custom agent mapping displayed within PentAGI](screenshots/07-provider-role-mapping.png)

*Figure 7.* The saved model assignments were visible in PentAGI, confirming that the custom model configuration was recognised by the interface. This was not yet proof of a successful model response.

![Provider configuration details in the list](screenshots/08-provider-list-details.png)

*Figure 8.* The role settings included parameters such as maximum output tokens, temperature and example price values. Such values require provider-specific validation and should not be mistaken for actual Dahl prices.

![Dahl listed alongside Gemini and Llama](screenshots/09-dahl-provider-listed.png)

*Figure 9.* The provider list showed **Gemini Cyber Lab**, **Local Llama 3.1**, and **Dahl Gonka 50M**. This confirms the new provider was added without removing the existing profiles.

## 5. Diagnosing intermittent AI failures

A first Assistant flow was created with Dahl selected. The assistant initially appeared to stall during startup; it eventually returned useful cybersecurity content, but further responses failed. Docker logs captured an Assistant chain failure and repeated retries.

![Assistant flow during initialization](screenshots/10-assistant-initialization.png)

*Figure 10.* The Assistant flow was created under the Dahl provider. The interface initially showed an empty conversation while the assistant was starting.

![Initial response generated by the assistant](screenshots/11-initial-answer.png)

*Figure 11.* The assistant did generate cybersecurity text, demonstrating that some inference requests succeeded. A successful initial answer did not mean the end-to-end flow was stable.

![Initial diagnostic logs](screenshots/12-terminal-error-logs.png)

*Figure 12.* Terminal logs were inspected for requests and failures. HTTP `200` on PentAGI's GraphQL endpoint meant the local web interface was communicating with its backend; it did **not** prove that the remote Dahl model returned usable content.

![Completed portion of initial cybersecurity explanation](screenshots/13-initial-answer-complete.png)

*Figure 13.* The response described cybersecurity concepts and threats. This provides evidence of real model output before the subsequent agent-chain failure.

![PentAGI Assistant failure message](screenshots/14-assistant-failure-message.png)

*Figure 14.* The visible error described **HTTP 502**, exhausted retries, a response with no content or tool calls, and a reflector recursion failure. These errors must be distinguished from an ordinary slow model response.

![Filtered Docker failure logs](screenshots/15-error-diagnostic.png)

*Figure 15.* Filtering Docker logs helped connect the UI failure to agent-chain retries. The diagnostic search used a command of this form:

```bash
sudo docker logs --since 15m pentagi 2>&1 | grep -iE 'error|failed|timeout|rate.limit|429|401|403|provider|assistant'
```

**What could be concluded:** some remote model calls failed with 502, others returned unusable content, and PentAGI's reflector retry path could not recover. **What could not yet be concluded:** that a single model, parameter or internet connection was solely responsible.

Dahl's status endpoint was queried separately:

```bash
curl -s 'https://inference.dahl.global/v1/status?window=1h'
```

At the recorded snapshot, MiniMax's reported uptime was **83.33%** over the preceding hour; DeepSeek and GLM both showed **100%**. This supported testing an alternative model, but was only a short time-window measurement.

## 6. Changing the Assistant role and measuring the right thing

I preserved the existing custom YAML and changed only the Assistant model to `zai-org/GLM-5.3-Flash`. Restarting the Docker container did not change the model displayed in the **saved** provider profile, so I edited **Dahl Gonka 50M** directly in PentAGI's provider interface and saved the change there.

![Available Dahl models in the provider model selector](screenshots/16-model-dropdown.png)

*Figure 16.* The dropdown displayed all three available Dahl model IDs, including GLM. Selecting a model in the saved provider is a separate action from editing a local YAML template.

![Assistant role updated to GLM in saved provider](screenshots/17-glm-assistant-edit.png)

*Figure 17.* The saved Assistant configuration displayed `zai-org/GLM-5.3-Flash`. This was the configuration used for subsequent direct Assistant testing.

I then distinguished two fundamentally different test modes:

- **Assistant:** direct interaction, optionally with tool execution.
- **Automation:** planning, research, tool orchestration, repeated calls and synthesis.

The Automation flow tasked with explaining cybersecurity launched several searches of standards and definitions. It was considerably slower than a direct Assistant answer, but that does not establish a model-to-model speed ranking, because the workflows were different.

![PentAGI planning and search workflow](screenshots/18-automation-research.png)

*Figure 18.* Automation generated an explicit research plan, then searched sources such as NIST and ISO. The additional steps explain why it can be much slower than simply answering a short question.

![Repeated research queries during automation](screenshots/19-automation-search-overhead.png)

*Figure 19.* The automation issued several similar queries about cybersecurity definitions. I stopped the workflow rather than allowing an overly elaborate test to continue. This revealed a practical optimisation target: better task scoping and appropriate use of Assistant mode.

![Direct Assistant flow after switching model](screenshots/20-glm-direct-assistant.png)

*Figure 20.* A short Assistant question was answered promptly. This is qualitative evidence of responsiveness; no precise latency measurement was recorded for that request.

## 7. Verifying real tool execution

To test more than conversational ability, I prompted the Assistant, with agent/tool use enabled, to run `pwd` and report the exact result, without running other commands.

```text
Use your terminal tool to run the command `pwd` in your execution environment.
Report the exact output and explain what directory it identifies.
Do not run any other commands, install anything, or perform research.
```

![Scoped execution test request](screenshots/21-agent-tool-test.png)

*Figure 21.* The narrow tool-execution prompt was designed to separate genuine command execution from a generic AI explanation.

![pwd response from execution environment](screenshots/22-pwd-execution-report.png)

*Figure 22.* PentAGI reported `/work` and exit code `0`. The path refers to PentAGI's **container** environment, not Kali's `/home/x` directory.

![Terminal tool record for command execution](screenshots/23-pwd-tool-log.png)

*Figure 23.* The execution record provides stronger evidence than the assistant's prose alone. Tool logs and exit status should be checked before claiming a real command ran.

## 8. Authorised Nmap service discovery

The final practical task used my intentionally vulnerable Metasploitable 2 VM at `192.168.1.119`. I explicitly restricted the task to seven TCP ports and prohibited exploitation, credential attempts, other-device scans and web research.

### Task submitted

```text
Perform a basic, non-intrusive Nmap service discovery scan against my authorised
Metasploitable 2 training VM at 192.168.1.119.

First, verify that the target is reachable. If reachable, scan TCP ports
21, 22, 23, 80, 139, 445 and 3306 using Nmap service detection.

Report the open ports, detected services and versions, and briefly explain
security significance. Do not exploit vulnerabilities, attempt passwords,
scan other devices or perform web research.

If the target is unreachable, stop and report the error.
```

PentAGI's execution container initially lacked Nmap. It installed Nmap, verified the installation, and executed the targeted scan. The command visible in the tool record was equivalent to:

```bash
nmap -Pn -sT -sV -p 21,22,23,80,139,445,3306 --open 192.168.1.119 -oN /work/nmap_metasploitable_scan.txt
```

**Command explanation:** `-Pn` skips Nmap host discovery; `-sT` uses TCP connect scanning; `-sV` attempts service/version detection; `-p` limits the scan to the authorised seven ports; `--open` displays open ports; and `-oN` saves ordinary text output in the execution environment. Because `-Pn` treats the target as online for scanning purposes, the separate preceding connectivity checks and subsequent actual scan results are important evidence.

![PentAGI installing and running Nmap](screenshots/24-nmap-live-tool-execution.png)

*Figure 24.* The terminal shows Nmap was missing, was installed in the execution container, and then ran against the single authorised IP address. A network-reachable execution container was necessary; Kali's connectivity alone would not guarantee the same for Docker.

### Findings

| TCP port | State | Identified service | Version / details |
|---:|---|---|---|
| 21 | open | FTP | vsftpd 2.3.4 |
| 22 | open | SSH | OpenSSH 4.7p1 Debian 8ubuntu1 |
| 23 | open | Telnet | Linux telnetd |
| 80 | open | HTTP | Apache httpd 2.2.8 (Ubuntu), DAV/2 |
| 139 | open | NetBIOS-SSN | Samba smbd 3.X–4.X |
| 445 | open | NetBIOS-SSN | Samba smbd 3.X–4.X |
| 3306 | open | MySQL | MySQL 5.0.51a-3ubuntu5 |

![Completed Nmap output and PentAGI interpretation](screenshots/25-nmap-final-results.png)

*Figure 25.* The terminal recorded **1 host up**, all seven requested TCP ports open, and **Nmap done: 1 IP address (1 host up) scanned in 11.39 seconds**. PentAGI also produced explanatory security notes in the conversation pane. These scan results establish the exposed services, not successful exploitation.

### Security interpretation

- **FTP (21):** The reported vsftpd 2.3.4 build is historically associated with a deliberately backdoored distribution, highly relevant in this Metasploitable training image. A version string alone does not establish compromise of an arbitrary real-world host.
- **SSH (22):** The identified OpenSSH build is very old; real risk requires configuration and patch-level verification.
- **Telnet (23):** Telnet provides no encryption for session traffic and is unsuitable for real-world remote administration across untrusted networks.
- **HTTP (80):** The old Apache version and WebDAV functionality are exposure indicators requiring scoped follow-up checks.
- **SMB (139/445):** Samba services expose file-sharing functionality. Nmap's broad version family does not, by itself, prove a specific Samba vulnerability.
- **MySQL (3306):** An exposed, old database service is a significant configuration and maintenance concern, but access and authentication were not tested.

## 9. Performance, limitations and lessons learned

| Observation | Interpretation |
|---|---|
| Initial Dahl Assistant returned some text, then 502 failures | Partial connectivity succeeded, but reliability failed under repeated requests |
| MiniMax reported 83.33% uptime in a one-hour snapshot | A plausible service-side contributor; not definitive root-cause proof |
| GLM direct answers were described as fast | Promising, but qualitative rather than instrumented benchmark data |
| Full Automation launched repeated searches | Orchestration can dominate duration and token use for simple questions |
| `pwd` executed and returned `/work` | Evidence of real container tool access |
| Nmap itself took 11.39 seconds | Demonstrates fast underlying scan; excludes AI planning and report time |
| Nmap installed during a task | Execution environment was not pre-provisioned with that tool |
| Existing Gemini and Ollama providers remained listed | Integration was additive, not a replacement |

**Key lessons:**

1. **A valid provider configuration is not the same as a reliable provider.** Verify actual requests and error handling.
2. **Saved provider profiles and YAML templates can diverge.** Changes to the template may not automatically update existing records in the application.
3. **A short, constrained Assistant prompt is often more efficient than a full Automation workflow.** Use the heavier mode only when its extra tools and planning are justified.
4. **Check actual execution logs.** A plausible AI answer is not enough to prove a command ran.
5. **Separate Nmap runtime from AI overhead.** The recorded 11.39 seconds is a tool benchmark, not an end-to-end agent benchmark.
6. **Treat scan observations as observations.** Open ports and version fingerprints are not proof of exploitability.

## 10. Follow-up work

- Record end-to-end time, token usage, request count and retries across identical Assistant tasks for GLM, MiniMax and DeepSeek.
- Test the saved PentAGI role profiles individually, especially the DeepSeek Primary Agent and Pentester, rather than assuming they perform identically.
- Verify parameter compatibility for each model, particularly reasoning controls and JSON/tool-call output.
- Evaluate reproducible tool provisioning for ephemeral execution containers, without weakening the sandbox boundary.
- Repeat scoped network discovery in the lab and save a checksum and machine-readable Nmap result, if appropriate.
- Confirm that any ongoing provider errors are observed at the Dahl API boundary and not only inside PentAGI's retries.

## Evidence handling and repository hygiene

- No `.env` file, API key, fingerprint, bearer token or private credential is intentionally included.
- Screenshots were selected to document actions and outcomes, not to publish unrelated local files.
- `192.168.1.119` was a personally controlled training VM at the time of the scan. Future tests should re-verify the target IP and authorisation.
- Dahl's 50M number denotes an **allocated allowance**, not demonstrated consumption or guaranteed throughput.
- These observations are specific to the software, network and provider conditions on **8 November 2026**.

---

**Outcome:** A working, additive Dahl integration in PentAGI, with a demonstrated container command, a completed seven-port Metasploitable 2 service scan, and a documented troubleshooting path for unreliable model requests and excessive automation overhead.