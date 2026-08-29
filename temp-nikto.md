# Nikto Vulnerability Assessment of Metasploitable Web Applications

**Completed:** 19 August 2026  
**Environment:** Kali Linux and Metasploitable 2  
**Tool:** Nikto v2.6.0

## Overview

This exercise focused on using Nikto to assess several web applications hosted on Metasploitable 2.

The purpose was to identify potential vulnerabilities, insecure configurations, exposed resources and outdated software, and then interpret what the scanner results actually meant.

The applications assessed were:

- DVWA
- Mutillidae
- phpMyAdmin
- WebDAV

A major part of the exercise was learning that automated vulnerability scanners provide **leads**, not automatic proof that every reported item is exploitable.

Testing was limited to the authorised Metasploitable 2 laboratory target.

---

# 1. DVWA Vulnerability Assessment

**Target:** `http://<TARGET_IP>/dvwa/`  
**Tool:** Nikto v2.6.0  
**Scan result:** 8,238 requests, 26 items reported, 16 errors

## Findings

| Finding | Security Significance | Follow-up | Recommendation |
|---|---|---|---|
| `CHANGELOG.txt` exposed | Public application information may reveal useful version or development details for reconnaissance. | Inspect with browser or `curl`. If a version is identified, research relevant CVEs or Searchsploit results. | Remove unnecessary public documentation or restrict access. |
| `login.php` discovered | Exposes an authentication and user-input surface. Its presence alone is not a vulnerability. | OWASP ZAP or manual testing. If a specific injection weakness is later confirmed, more specialised tools may be appropriate. | Apply secure input handling, authentication controls and session management. |
| Clickjacking protection weakness | Inadequate framing restrictions may allow the application to be loaded within another site. | Verify response headers with ZAP or `curl`. | Configure an appropriate Content Security Policy using `frame-ancestors`. |
| `X-Content-Type-Options` missing | Reduces browser-side protection against MIME-type sniffing. | Verify response headers with ZAP or `curl`. | Configure `X-Content-Type-Options: nosniff`. |

## Assessment

The Nikto scan identified information disclosure, an exposed authentication surface and HTTP security-header weaknesses.

These findings increased the visible attack surface, but they did not all represent confirmed vulnerabilities.

The main lesson was that Nikto provides areas for further investigation.

For example:

- an exposed changelog can lead to version research;
- a login page can lead to authentication and input testing;
- a confirmed injection weakness might justify more specialised testing;
- a missing security header is primarily a configuration issue.

Different findings require different follow-up actions.

---

# 2. Mutillidae Vulnerability Assessment

**Target:** `http://<TARGET_IP>/mutillidae/`  
**Tool:** Nikto v2.6.0  
**Web server:** Apache/2.2.8 (Ubuntu) DAV/2  
**Scan result:** 8,208 requests, 57 items reported, 16 errors  
**Scan duration:** Approximately 370 seconds

## Findings

### Potential Remote File Inclusion

Nikto reported numerous potential Remote File Inclusion tests against `index.php`, involving parameters such as:

- `page`
- `path`
- `template`
- `theme`
- `url`
- `site`
- `root_prefix`

### Interpretation

If an application accepts a user-controlled location and includes its contents without adequate validation, an attacker may potentially cause unintended files or remote content to be processed.

However, an automated scanner result is not enough to confirm Remote File Inclusion.

This was therefore treated as a **potential vulnerability requiring validation**.

### Follow-up

Controlled request manipulation using a tool such as Burp Suite or OWASP ZAP could be used to investigate whether user-controlled input actually reaches an unsafe file-inclusion mechanism.

### Recommendation

Do not construct file paths directly from user input.

Use server-side validation and allowlists for permitted files and resources.

---

## Outdated Apache Version

Nikto identified:

**Apache/2.2.8**

The version was obsolete.

An old software version can be associated with publicly documented vulnerabilities, but the version number alone does not prove that every vulnerability affecting that release is exploitable.

### Recommendation

Upgrade Apache to a supported release and maintain an appropriate patch-management process.

---

## Outdated PHP and Version Disclosure

The `X-Powered-By` response disclosed:

**PHP/5.2.4-2ubuntu5.10**

This revealed both the technology in use and an obsolete software version.

Such information assists fingerprinting and may help identify relevant known vulnerabilities.

### Recommendation

Upgrade PHP to a supported release and reduce unnecessary version disclosure.

---

## Exposed `phpinfo.php`

Nikto identified an accessible `phpinfo.php` page.

`phpinfo()` can expose detailed information about:

- PHP configuration;
- installed modules;
- filesystem paths;
- server settings; and
- environment information.

This information can be valuable during reconnaissance.

### Recommendation

Remove `phpinfo.php` from production systems or restrict it to authorised administrators.

---

## HTTP TRACE Enabled

Nikto reported that the HTTP TRACE method was enabled.

TRACE is a diagnostic HTTP method that can echo information from requests.

Although its presence does not automatically mean the server is compromised, it exposes unnecessary functionality and increases the attack surface.

### Recommendation

Disable TRACE unless it is specifically required.

---

## Missing Security Headers

Nikto identified several missing response headers, including:

- `X-Content-Type-Options`
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `Permissions-Policy`
- `Referrer-Policy`

These headers provide different browser-side security protections.

Their absence should be treated as a **defence-in-depth configuration weakness**, rather than one single exploitable vulnerability.

### Recommendation

Configure security headers appropriate to the application and deployment environment.

---

## `robots.txt` Information Exposure

Nikto found six entries in `robots.txt` requiring manual review.

`robots.txt` can reveal application paths to anyone who requests the file.

It is designed to give instructions to compliant crawlers and is not an access-control mechanism.

### Recommendation

Do not rely on `robots.txt` to hide sensitive resources.

Protect restricted content using proper authentication and authorisation.

---

## PHP Information Disclosure

Nikto detected responses associated with PHP information or Easter Egg functionality.

These responses can assist technology fingerprinting by confirming information about the underlying PHP environment.

### Recommendation

Upgrade the PHP environment and disable unnecessary information exposure where appropriate.

---

## Apache MultiViews

Nikto reported that Apache MultiViews was enabled.

MultiViews can cause Apache to perform content negotiation and may make alternative resource names easier to discover.

### Recommendation

Disable MultiViews where the application does not require it.

---

## Mutillidae Assessment Summary

The most significant Nikto output was the group of potential Remote File Inclusion findings.

Because automated scanners can produce false positives, these results required further validation before being described as confirmed vulnerabilities.

The scan also identified several weaknesses within the supporting web-server environment:

- obsolete Apache;
- obsolete PHP;
- PHP version disclosure;
- exposed `phpinfo.php`;
- HTTP TRACE;
- missing security headers;
- exposed `robots.txt` information; and
- Apache MultiViews.

This reinforced an important lesson:

**Nikto identifies attack surface and possible weaknesses. Further investigation is required to determine which findings are genuinely exploitable.**

---

# 3. phpMyAdmin Vulnerability Assessment

**Target:** `http://<TARGET_IP>/phpMyAdmin/`  
**Tool:** Nikto v2.6.0  
**Web server:** Apache/2.2.8 (Ubuntu) DAV/2  
**Scan result:** 8,268 requests, 28 items reported, 16 errors  
**Scan duration:** Approximately 376 seconds

## Outdated phpMyAdmin Installation

Nikto identified:

**phpMyAdmin 2.11.8.1**

Because phpMyAdmin provides database-administration functionality, an outdated version is particularly important to investigate.

Publicly documented vulnerabilities affecting the identified release could potentially affect database confidentiality, integrity or availability.

### Follow-up

Version research using vulnerability databases, CVE information or Searchsploit can identify known issues affecting the detected release.

### Recommendation

Upgrade phpMyAdmin to a supported version and restrict administrative access.

---

## Outdated Apache Web Server

Nikto reported:

**Apache/2.2.8**

The server version was obsolete and could therefore be associated with publicly documented security weaknesses.

### Recommendation

Upgrade Apache and apply current security patches.

---

## Outdated PHP and Version Disclosure

The server disclosed:

**PHP/5.2.4-2ubuntu5.10**

The exposed version information assists fingerprinting, while the obsolete PHP release may contain vulnerabilities corrected in later versions.

### Recommendation

Upgrade PHP and suppress unnecessary PHP version disclosure.

---

## Exposed phpMyAdmin Resources

Nikto identified several potentially interesting locations:

- `/phpMyAdmin/import/`
- `/phpMyAdmin/readme`
- `/phpMyAdmin/setup/`
- `/phpMyAdmin/test/`

Administrative, setup, test and documentation resources can expose information or functionality that should not normally remain publicly accessible.

The setup interface was particularly noteworthy because installation or configuration functionality should generally be restricted after deployment.

### Recommendation

Remove unnecessary installation, test and documentation resources and restrict administrative functionality.

---

## Directory Indexing

Nikto reported directory indexing under:

`/phpMyAdmin/test/`

Directory indexing can allow users to browse files and directories that might otherwise be less obvious.

This makes reconnaissance easier.

### Recommendation

Disable directory indexing and remove unnecessary test resources.

---

## `robots.txt` and ETag Information

Nikto identified `robots.txt` and reported potential metadata disclosure through ETags.

`robots.txt` may expose application paths, while server metadata can provide additional information during reconnaissance.

### Recommendation

Protect sensitive paths using authentication and authorisation rather than relying on `robots.txt`.

Reduce unnecessary metadata exposure where practical.

---

## HTTP TRACE Enabled

Nikto reported that HTTP TRACE was active.

TRACE is normally unnecessary for production applications and exposes additional functionality.

### Recommendation

Disable TRACE unless specifically required.

---

## Missing HTTP Security Headers

Nikto identified missing:

- `X-Content-Type-Options`
- `Strict-Transport-Security`
- `Referrer-Policy`
- `Permissions-Policy`
- `Content-Security-Policy`

Their absence weakened browser-side defence-in-depth controls.

### Recommendation

Configure appropriate security headers according to the application's requirements.

---

## Apache MultiViews

Apache MultiViews was enabled.

This may assist discovery of alternative filenames or resources during enumeration.

### Recommendation

Disable MultiViews if the application does not require it.

---

## PHP Information Disclosure

Nikto generated several responses revealing characteristics of the PHP environment.

Although these findings did not demonstrate direct compromise, they provided useful fingerprinting information.

### Recommendation

Upgrade PHP and reduce unnecessary information exposure.

---

## Potentially Exposed Administrative Resources

Nikto reported an unusual administrative-style path and application-related downloadable content.

Unexpected administrative resources or application files can warrant further investigation because they may expose:

- internal files;
- configuration information;
- test functionality; or
- administrative interfaces.

### Recommendation

Remove unused resources, restrict required management interfaces and prevent sensitive application files from being publicly served.

---

## phpMyAdmin Assessment Summary

The phpMyAdmin scan identified weaknesses affecting both the application and the supporting web-server environment.

The most important concerns were:

- obsolete phpMyAdmin;
- outdated Apache;
- outdated PHP;
- exposed setup and test resources;
- directory indexing;
- TRACE;
- missing security headers;
- information disclosure; and
- unnecessary administrative resources.

### Overall Risk

**Risk level: High**

The combination of an obsolete database-administration application, outdated supporting software and exposed administrative resources created a broad attack surface.

Priority remediation would include:

1. upgrading phpMyAdmin;
2. upgrading Apache and PHP;
3. removing setup and test content;
4. restricting administrative interfaces;
5. disabling directory indexing; and
6. hardening the web-server configuration.

---

# 4. WebDAV Vulnerability Assessment

**Target:** `http://<TARGET_IP>/dav/`  
**Tool:** Nikto v2.6.0  
**Web server:** Apache/2.2.8 (Ubuntu) DAV/2  
**Scan result:** 8,285 requests, 31 items reported, 16 errors

## WebDAV Enabled

Nikto identified WebDAV functionality and several supported methods, including:

- `LOCK`
- `UNLOCK`
- `PROPFIND`
- `PROPPATCH`
- `COPY`

WebDAV extends HTTP with additional methods used to manage remote web resources.

Its presence is not automatically a vulnerability.

The security concern depends on which operations the server permits and how access to those operations is controlled.

---

## PUT Permitted

Nikto reported that the server permitted the HTTP `PUT` method.

`PUT` can allow a client to store a resource on the server.

### Interpretation

This was an important result because weak access controls could potentially allow unauthorised files to be uploaded.

However, permission to upload a file does not automatically mean that uploaded content can execute.

That would require separate validation.

### Recommendation

Where WebDAV is required:

- restrict access to authorised users;
- limit writable locations;
- restrict permitted file types; and
- ensure uploaded content cannot execute unexpectedly.

---

## DELETE Permitted

The server permitted the `DELETE` method.

If access controls are insufficient, this could potentially allow server resources to be removed.

### Recommendation

Restrict deletion operations to authorised users and disable the method where it is unnecessary.

---

## MOVE Permitted

The server supported `MOVE`.

This could allow server-side resources to be relocated where permissions permit.

### Recommendation

Restrict the method according to operational requirements and authorisation controls.

---

## COPY Permitted

The server supported `COPY`.

This may allow resources to be duplicated to other locations where WebDAV permissions allow it.

### Recommendation

Disable unnecessary methods and enforce proper authorisation.

---

## PROPFIND and PROPPATCH

These methods support retrieval and modification of WebDAV resource metadata.

Their presence confirmed that broader WebDAV functionality was enabled.

### Recommendation

Expose only the WebDAV functionality required by authorised users.

---

## Directory Indexing

Nikto identified directory indexing.

This can expose files and directories that would otherwise be less obvious to someone browsing the application.

### Recommendation

Disable directory indexing unless specifically required.

---

## HTTP TRACE

TRACE was also enabled on the WebDAV service.

### Recommendation

Disable TRACE where unnecessary.

---

## Outdated Apache

The WebDAV service was hosted on:

**Apache/2.2.8**

The version was obsolete.

### Recommendation

Upgrade Apache to a supported release and maintain current security patches.

---

## Missing Security Headers

Nikto reported missing browser security headers, including:

- Content Security Policy;
- HSTS;
- Referrer Policy;
- Permissions Policy; and
- `X-Content-Type-Options`.

These represent configuration weaknesses that reduce defence-in-depth protection.

### Recommendation

Configure appropriate HTTP security headers.

---

## WebDAV Assessment Summary

The WebDAV scan exposed a broad HTTP attack surface.

The most important relationship identified during this assessment was:

**WebDAV enabled → additional HTTP methods available → PUT permits file storage → validate access controls → determine how uploaded files are handled**

This helped me understand that the security issue is not simply that WebDAV exists.

The actual risk depends on what actions the server permits and whether those actions are properly authenticated and authorised.

Nikto also identified:

- directory indexing;
- TRACE;
- obsolete Apache; and
- several missing security headers.

Together, these findings indicated a deliberately weak web-server configuration requiring further assessment.

### Recommended Remediation

- Disable WebDAV where it is unnecessary.
- Restrict WebDAV access to authorised users.
- Disable unnecessary methods such as `PUT`, `DELETE`, `COPY` and `MOVE`.
- Prevent executable content from being stored or served from writable locations.
- Disable directory indexing.
- Disable TRACE where unnecessary.
- Upgrade Apache.
- Configure appropriate HTTP security headers.

---

# What I Learned

This exercise helped me understand how to interpret automated vulnerability scanner output rather than treating every line as a confirmed exploit.

Nikto was useful for identifying:

- exposed resources;
- outdated software;
- interesting HTTP methods;
- missing security headers;
- information disclosure;
- configuration weaknesses; and
- potential vulnerabilities requiring further investigation.

The most important lessons were:

### A scanner finding is a lead

Nikto tells me where to look next.

It does not automatically prove that a vulnerability is exploitable.

### Different findings require different follow-up techniques

An exposed software version may lead to CVE research.

A potential input vulnerability may require request manipulation and manual validation.

A missing HTTP security header normally requires configuration review rather than exploitation.

### Outdated software is important, but evidence matters

Knowing that software is old helps prioritise research.

It does not mean that every CVE associated with that version applies to the exact deployment.

### WebDAV demonstrated how findings can form an attack path

A single result such as "WebDAV enabled" was less important than understanding how several observations connect:

**WebDAV → additional methods → PUT → potential file upload → access-control testing → handling of uploaded content**

This was a useful step in learning to think beyond individual scanner findings and consider how weaknesses may interact.

### Validation matters

Automated scanners can generate false positives.

A potential vulnerability should therefore be validated before being reported as a confirmed exploit.

---

# Conclusion

The Nikto assessments demonstrated that vulnerability scanning is more useful when the results are interpreted rather than simply collected.

Across DVWA, Mutillidae, phpMyAdmin and WebDAV, Nikto identified a combination of:

- potential vulnerabilities;
- exposed resources;
- obsolete software;
- insecure HTTP methods;
- information disclosure;
- missing security headers; and
- configuration weaknesses.

The exercise helped me move from asking:

**"What did the scanner find?"**

towards asking:

**"What does this result mean, how serious is it, and what would I need to do next to validate it?"**

That distinction was one of the main lessons from the assessment.

---

## Lab Note

This project documents authorised testing performed against Metasploitable 2, an intentionally vulnerable cybersecurity training environment.
