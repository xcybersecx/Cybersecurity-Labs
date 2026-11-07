# Assignment 19: Evilginx2, YAML and Cookie Management (Authorized Lab)

**Student:** xcybersecx  
**Date:** 7 November 2026  
**Environment:** Kali Linux, Oracle VirtualBox, Metasploitable2, Firefox, Code - OSS  
**Evidence:** 43 screenshots presented below in the order captured

## Aim

The assignment was to study YAML syntax and Evilginx2 phishlet configuration in an authorized environment, examine a different website template such as Facebook, install a cookie-management extension, and use VS Code or Code - OSS to inspect configuration files.

This report records the practical session as it happened. The screenshots show both progress and problems encountered. The Facebook-style YAML was examined as a learning example; this report does not claim a functioning live phishlet or interception of third-party accounts. The browser and cookie exercises used the local DVWA/Metasploitable training environment.

## Practical procedure and screenshot evidence

### 1. Preparing Kali and investigating Code - OSS

**01. Updating the Kali package index.** I ran `sudo apt update` and then checked `apt-cache policy code-oss`. This established that Code - OSS was already installed and showed the available package version.

![Screenshot 01](screenshots/01.png)

**02. Attempting to open the code editor.** The Kali VM displayed Code - OSS beside terminal error output. This was an early check of whether the editor could be used for the YAML exercise.

![Screenshot 02](screenshots/02.png)

**03. Trying to open the GitHub example phishlet.** In the terminal I attempted to launch a YAML file from the Evilginx2 phishlets directory using Code - OSS. The terminal reported a missing `libnode.so.115` shared library, so the attempt was not cleanly successful.

![Screenshot 03](screenshots/03.png)

**04. Inspecting the Code - OSS window.** The editor's welcome screen appeared while the earlier terminal errors remained visible. I continued exploring the editor despite the launch warning.

![Screenshot 04](screenshots/04.png)

**05. Opening the editor's file chooser.** I tried to browse the filesystem through Code - OSS to locate the relevant YAML file.

![Screenshot 05](screenshots/05.png)

**06. Continuing file navigation.** I remained in the editor's file picker while the terminal displayed the library error. This documents the difficulty accessing the file by the first route.

![Screenshot 06](screenshots/06.png)

**07. Viewing a YAML file in Code - OSS.** The editor eventually displayed YAML-style configuration content alongside the terminal, allowing inspection of the file structure.

![Screenshot 07](screenshots/07.png)

### 2. Creating and reviewing a Facebook-style YAML example

**08. Copying the example into a lab working file.** I copied the bundled `example.yaml` to a `facebook_lab.yaml` file. My first editor command contained a leading `!`, which Zsh interpreted as history expansion and returned `event not found`.

![Screenshot 08](screenshots/08.png)

**09. Correcting the editor command.** I retried with the filename rather than the leading exclamation mark, and the Code - OSS interface opened.

![Screenshot 09](screenshots/09.png)

**10. Using Open File.** I browsed files from the editor to select the lab YAML document for study.

![Screenshot 10](screenshots/10.png)

**11. Inspecting configuration keys.** The `facebook_lab.yaml` document showed sections including `min_ver`, `proxy_hosts`, `sub_filters`, `auth_tokens` and `credentials`. I examined how a YAML mapping and list are structured.

![Screenshot 11](screenshots/11.png)

**12. Reviewing host and filter entries.** I focused on the indentation and list entries in the example. The visible Facebook domain references were part of the template being studied, not evidence of a working deployment.

![Screenshot 12](screenshots/12.png)

**13. Continuing the YAML review.** I inspected the host and token sections, paying attention to syntax, nesting and field names.

![Screenshot 13](screenshots/13.png)

**14. Examining a later edit.** The configuration displayed further changes in the token section. This screenshot documents exploration of a phishlet template, not proof that the file was validated or deployed.

![Screenshot 14](screenshots/14.png)

### 3. Installing Cookie-Editor and checking VM network settings

**15. Opening Firefox Add-ons Manager.** I navigated to Firefox extensions to locate a cookie-management tool for the assignment.

![Screenshot 15](screenshots/15.png)

**16. Encountering a connection failure.** Firefox could not reach Mozilla's add-ons site. I recorded the error before troubleshooting network connectivity.

![Screenshot 16](screenshots/16.png)

**17. Opening VirtualBox network settings.** I examined the virtual machine's network adapters to investigate why the lab browser could not connect.

![Screenshot 17](screenshots/17.png)

**18. Comparing adapter settings.** I inspected additional VirtualBox network configuration options before retrying the browser.

![Screenshot 18](screenshots/18.png)

**19. Finding Cookie-Editor.** Firefox reached Mozilla's add-ons search results and displayed Cookie-Editor among the results.

![Screenshot 19](screenshots/19.png)

**20. Opening the extension page.** I reviewed the Cookie-Editor listing and its description before installation.

![Screenshot 20](screenshots/20.png)

**21. Confirming installation.** Firefox displayed the message that Cookie-Editor was added, and the extension panel became available. This is direct evidence of successful installation.

![Screenshot 21](screenshots/21.png)

**22. Inspecting the newly installed extension.** I viewed Cookie-Editor's panel and available options after installation.

![Screenshot 22](screenshots/22.png)

**23. Checking a bridged network adapter.** In VirtualBox I inspected an adapter attached in Bridged Adapter mode, with the physical Wi-Fi interface selected.

![Screenshot 23](screenshots/23.png)

**24. Testing access to the lab target.** Firefox could not reach the Metasploitable host at the local IP address, and Cookie-Editor reported no cookies for that unreachable page. More network work was needed.

![Screenshot 24](screenshots/24.png)

### 4. Troubleshooting the Kali and Metasploitable connection

**25. Checking networking commands in Kali.** I tried DHCP-related commands, restarted NetworkManager and inspected interfaces. One attempt failed because `dhclient` was not found.

![Screenshot 25](screenshots/25.png)

**26. Inspecting interface output.** I used terminal output to assess the Kali VM's network state and connectivity to the target.

![Screenshot 26](screenshots/26.png)

**27. Checking Metasploitable's interface.** Inside the Metasploitable2 VM, I viewed `ifconfig` output and investigated the target VM's address.

![Screenshot 27](screenshots/27.png)

**28. Assigning the target's lab IP.** I used `ifconfig` on Metasploitable to set its local IPv4 address and verified that it appeared on the interface. This was a lab-network setting.

![Screenshot 28](screenshots/28.png)

**29. Testing connectivity from Kali.** The terminal showed `Network is unreachable` errors. I attempted to bring up or configure Kali's interface, but connectivity was not yet restored.

![Screenshot 29](screenshots/29.png)

**30. Continuing the Kali IP configuration.** I tried `ip addr` and `ifconfig` commands to assign Kali an address on the same lab subnet, followed by repeat pings.

![Screenshot 30](screenshots/30.png)

**31. Restarting the web service.** Back in Metasploitable, I used the Apache restart command after checking the configured address, preparing the vulnerable training service for browser access.

![Screenshot 31](screenshots/31.png)

### 5. Accessing DVWA and observing test cookies

**32. Reaching the training VM.** Firefox successfully loaded the Metasploitable landing page. Cookie-Editor showed no cookies for this landing view.

![Screenshot 32](screenshots/32.png)

**33. Opening the DVWA login page.** I navigated to Damn Vulnerable Web Application (DVWA). Cookie-Editor displayed entries such as `PHPSESSID` and `security` in the local training context.

![Screenshot 33](screenshots/33.png)

**34. Loading the DVWA application.** The DVWA welcome page appeared, including its warning that the deliberately vulnerable app should be used only in a safe lab environment.

![Screenshot 34](screenshots/34.png)

**35. Inspecting the DVWA menu.** I viewed available practice areas, including command execution, file inclusion and SQL injection, without claiming that these exercises were performed.

![Screenshot 35](screenshots/35.png)

**36. Reviewing the DVWA home screen.** I checked that the application and Cookie-Editor were both available in Firefox.

![Screenshot 36](screenshots/36.png)

**37. Continuing cookie inspection.** The Cookie-Editor panel remained open over DVWA, showing the lab's cookie names and allowing observation of their presence.

![Screenshot 37](screenshots/37.png)

**38. Opening Cookie-Editor's import view.** I explored the extension's import functionality while the DVWA login form remained visible.

![Screenshot 38](screenshots/38.png)

**39. Inspecting cookie JSON structure.** The import view showed JSON-like fields such as cookie name, value, domain and session attributes. This was a structure-inspection exercise with local test data.

![Screenshot 39](screenshots/39.png)

**40. Continuing the JSON review.** I examined another view of the cookie fields, noting how a browser cookie is represented by properties and values.

![Screenshot 40](screenshots/40.png)

**41. Reviewing the DVWA page and lab navigation.** I inspected the local login page and browser history suggestions while Cookie-Editor remained available.

![Screenshot 41](screenshots/41.png)

**42. Viewing the DVWA login form.** The lab login form was populated with test credentials. This screenshot demonstrates use of the local training application, not a third-party account.

![Screenshot 42](screenshots/42.png)

**43. Returning to the DVWA home page.** The final screenshot shows the vulnerable training application loading, confirming the lab browser could reach the local web service.

![Screenshot 43](screenshots/43.png)

## Results and reflection

- **Code - OSS:** Installed and opened, although the terminal also exposed a shared-library launch error.
- **YAML study:** Examined an example configuration and a Facebook-style lab document, focusing on syntax and section structure. The screenshots do not establish successful validation or deployment.
- **Cookie-Editor:** Successfully installed in Firefox and used to inspect local DVWA cookie entries and the import interface.
- **Networking:** Diagnosed unreachable-host errors, reviewed VirtualBox adapter settings, configured lab IP addresses and restarted the target web service.
- **DVWA:** Ultimately reached the deliberately vulnerable application and viewed its login and home pages.

The main practical lesson was that a successful lab depends as much on basic system preparation and network troubleshooting as on understanding security-tool configuration. The work remained focused on the authorized training environment.

## Ethical scope

Evilginx2 can be used for authentication interception, so this repository provides **learning evidence, not a deployable phishing configuration**. No real-account credentials, exported browser cookies or session tokens are supplied as separate files. Screenshots showing cookie fields are from the local training context and should not be reused as live credentials.

> **Submission note:** This is a screenshot-based account of the work performed on 7 November 2026. It documents failed attempts honestly and does not claim outcomes not demonstrated by the images.
