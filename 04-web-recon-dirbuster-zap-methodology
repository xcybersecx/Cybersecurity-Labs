# Web Reconnaissance and Proxy Analysis Using Photon, DirBuster and OWASP ZAP

**Completed:** 22 August 2026  
**Environment:** Kali Linux and Metasploitable 2  
**Tools:** Photon, DirBuster, SecLists, OWASP ZAP

## Overview

This practical brought together several web-security tools as part of one reconnaissance and analysis workflow.

Rather than treating each tool independently, I worked through the following sequence:

**Target identification → connectivity check → Photon reconnaissance → application analysis → technology identification → DirBuster content discovery → false-positive management → OWASP ZAP proxy analysis**

The main objective was to understand how information gathered during one stage of reconnaissance can guide the next stage.

Testing was limited to the authorised Metasploitable 2 laboratory target.

---

# 1. Confirming the Target

Before carrying out web reconnaissance, I confirmed that the Metasploitable machine was reachable from Kali Linux.

```bash
ping -c 3 <TARGET_IP>
```

Three packets were transmitted and three responses were received, with no packet loss.

## What I Learned

It is useful to confirm basic connectivity before beginning more detailed testing.

If the target cannot be reached, there is little value troubleshooting application tools before checking the underlying network connection.

---

# 2. Photon Reconnaissance

Photon was used to crawl several web applications hosted on the Metasploitable machine.

The purpose was to identify discoverable resources and build an initial picture of each application's web attack surface.

## Results

| Application | Internal URLs | External URLs | Fuzzable URLs | Observation |
|---|---:|---:|---:|---|
| DVWA | 1 | 0 | 0 | Crawl began at the login page |
| Mutillidae | 1 | 0 | 0 | Only one internal URL discovered |
| phpMyAdmin | 2 | 2 | 0 | One URL retrieved from `robots.txt` |
| TWiki | 6 | 0 | 0 | One Level 1 and five Level 2 URLs |
| DAV | 16 | 0 | 4 | More content discovered than appeared in the browser |

The DAV result was particularly useful.

Although little appeared to be present when the application was viewed normally, Photon discovered:

- 16 internal URLs
- 4 fuzzable URLs

This demonstrated that what is visible through the browser does not necessarily represent everything available for discovery.

---

# 3. Understanding the Photon Results

Photon helped reinforce several reconnaissance concepts.

## Internal URLs

Internal URLs belong to the target being crawled.

They can reveal additional pages and resources within the same application.

## External URLs

External URLs point to resources outside the target.

## Fuzzable URLs

A fuzzable URL contains an input location that may be suitable for later testing.

A fuzzable result does **not** mean that a vulnerability has been confirmed.

It identifies an area that may warrant further investigation.

---

# 4. Authentication and Reconnaissance

DVWA presented a login page.

The unauthenticated Photon crawl discovered only one internal URL.

This demonstrated that a crawler can only discover resources available within its current access and session context.

Authentication can therefore significantly change the amount of an application that a reconnaissance tool is able to map.

---

# 5. robots.txt

During the phpMyAdmin crawl, Photon retrieved information from `robots.txt`.

This demonstrated that `robots.txt` can be useful during reconnaissance because it may reveal application paths.

However, `robots.txt` is not an access-control mechanism.

Resources listed within it may still be directly accessible.

---

# 6. Moving from Crawling to Content Discovery

The next stage introduced DirBuster and SecLists.

This helped clarify an important difference between crawling and content discovery.

### Photon

Photon follows what the application exposes through links and other references.

**Photon follows what it can discover.**

### DirBuster

DirBuster takes candidate resource names and asks the server whether they exist.

**DirBuster tests what might exist.**

The two techniques therefore complement each other:

**Photon reconnaissance → understand the application → DirBuster content discovery**

---

# 7. Identifying the Relevant File Extension

Before configuring DirBuster, I manually inspected the Mutillidae application.

While navigating through different parts of the site, I observed that application pages repeatedly used the `.php` extension.

This provided evidence that PHP was relevant to the target.

I therefore configured DirBuster to test PHP files rather than selecting a file extension arbitrarily.

## What I Learned

Reconnaissance can help reduce the search space.

The process became:

**Observe target → identify technology → configure later testing accordingly**

---

# 8. Selecting a SecLists Wordlist

For the first DirBuster run, I used:

```text
/usr/share/seclists/Discovery/Web-Content/common.txt
```

I also learned an important distinction about wordlists.

The wordlist is not a program.

It is a text file containing candidate names that another tool reads.

Attempting to enter the wordlist path directly into the terminal resulted in a permission error because the shell interpreted the file as something to execute.

Instead, the wordlist had to be supplied to DirBuster as input.

---

# 9. Configuring DirBuster

DirBuster was configured using information gathered during earlier reconnaissance.

The configuration included:

- list-based brute force;
- SecLists `common.txt`;
- directory testing;
- file testing;
- recursive scanning;
- PHP as the file extension.

In this context, **brute force did not mean password cracking**.

DirBuster systematically tested candidate directory and file names from the supplied wordlist.

For example:

```text
/admin/
```

or:

```text
/admin.php
```

Recursive scanning allowed DirBuster to continue searching inside directories that it discovered.

---

# 10. Interpreting DirBuster Responses

DirBuster returned a variety of HTTP responses, including:

- `200` - successful response
- `302` - redirection
- `403` - forbidden

These status codes provided information about how the server responded to particular resources.

A `403` response, for example, can still be interesting because it suggests that the server recognised the requested location even though access was denied.

However, a status code or discovered resource does not automatically prove that a vulnerability exists.

---

# 11. Inconsistent Failure Responses

During recursive discovery, DirBuster displayed the warning:

```text
Warning unable to determine consistent fail response.
```

This occurred while testing TWiki.

The application returned different-looking responses when nonexistent resources were requested.

This created a problem because a content-discovery tool must be able to distinguish:

**real resource**

from:

**response generated for a nonexistent resource**

If that distinction cannot be made reliably, large numbers of false positives can be produced.

---

# 12. Investigating the Failure Responses

DirBuster provided several example failure responses.

Although parts of the responses differed, each contained the same message:

```text
This Wiki topic does not exist
```

This provided a stable characteristic that could be used to identify failed requests.

I entered the phrase into DirBuster's failure-matching field and tested it against the example responses.

All three passed the test.

DirBuster reported that the expression should work.

## What I Learned

This was an important example of why automated tools still require human interpretation.

The process became:

**Tool detects ambiguity → inspect responses → identify common failure indicator → test indicator → reduce false positives**

---

# 13. DirBuster Scan Performance

After configuring the failure-matching rule, DirBuster continued recursive enumeration.

However, the scan progressed extremely slowly.

Progress remained around 3 to 5%, while the estimated completion time eventually increased to approximately nine days.

Waiting for the complete scan was not practical for the exercise.

However, the DirBuster stage had already demonstrated:

- list-based directory discovery;
- file discovery;
- recursive enumeration;
- HTTP response interpretation; and
- false-positive management.

The exercise therefore moved to OWASP ZAP for manual application analysis.

---

# 14. Introducing OWASP ZAP

OWASP ZAP was used to examine communication between the browser and the Mutillidae application.

I selected **Manual Explore** and launched Firefox through ZAP.

As I interacted with the application, browser requests and server responses appeared within ZAP's History.

This demonstrated the role of a web proxy.

ZAP sits between the browser and the web application and allows HTTP traffic to be observed and analysed.

---

# 15. Examining a GET Request

The first request examined was a GET request for the Mutillidae application.

It followed the general form:

```http
GET http://<TARGET_IP>/mutillidae/ HTTP/1.1
Host: <TARGET_IP>
```

Other headers contained information such as:

- browser User-Agent;
- accepted content types;
- connection information.

At this point, there was no parameter-value pair associated with the resource.

The browser was simply requesting the application page.

## What I Learned

The request helped separate several parts of an HTTP request:

- method;
- host;
- requested resource;
- headers;
- parameters.

---

# 16. Examining the Server Response

The corresponding server response returned:

```http
HTTP/1.1 200 OK
```

Response headers also disclosed information about the server technology:

```text
Server: Apache/2.2.8 (Ubuntu) DAV/2
```

and:

```text
X-Powered-By: PHP/5.2.4-2ubuntu5.10
```

The response also contained a `PHPSESSID` cookie.

## What I Learned

HTTP responses can reveal information about the technology running behind an application.

I also began to understand the role of session identifiers.

`PHPSESSID` allows the application to associate later requests with an existing PHP session.

The exercise also helped distinguish:

- **response headers**, which provide protocol and metadata information;
- **response body**, which contains the actual content returned to the browser.

---

# 17. Identifying a GET Parameter

I then navigated to the Mutillidae login functionality.

This generated a request containing:

```text
index.php?page=login.php
```

The request therefore contained:

```text
Parameter: page
Value: login.php
```

This provided a practical example of information being supplied to an application through a URL.

Instead of seeing the whole URL as one piece of text, I could now separate:

- the requested script: `index.php`
- the parameter: `page`
- the value: `login.php`

---

# 18. Observing a POST Request

I entered test credentials into the Mutillidae login form and submitted it.

ZAP captured the resulting POST request.

Unlike the earlier GET request, the submitted form data appeared in the request body.

This demonstrated that browser form fields are converted into HTTP request data and sent to the server.

## Difference Observed

### GET

The parameter was visible in the URL:

```text
page=login.php
```

### POST

The submitted login data appeared within the request body.

This helped make the practical difference between GET and POST much clearer.

---

# 19. HTTP Success vs Application Success

The unsuccessful login attempt returned:

```http
HTTP/1.1 200 OK
```

At first glance, `200 OK` could appear to indicate that the login was successful.

However, the response body contained an application-level error indicating that authentication had failed.

## What I Learned

`200 OK` means that the server successfully processed the HTTP request and returned a valid HTTP response.

It does **not** mean that the action the user attempted was successful.

For example:

```text
HTTP request successful ≠ login successful
```

Application behaviour and response content must also be examined.

---

# 20. Lessons from Manual Proxy Analysis

Using ZAP made the request-response process much easier to understand.

A normal browser interaction hides much of the underlying communication.

ZAP allowed me to see the sequence:

**Browser action → HTTP request → method and parameters → server processing → HTTP response → headers and body → application result**

This also demonstrated why both headers and bodies matter.

Headers provide information about the communication and environment.

The body often contains the information required to understand what actually happened at the application level.

---

# What I Learned

This practical helped connect several different tools into one methodology.

Instead of seeing Photon, DirBuster, SecLists and ZAP as unrelated applications, I began to understand how information gathered by one tool can guide the next stage.

The main lessons were:

- Confirm connectivity before troubleshooting application tools.
- Photon discovers resources by following available references.
- DirBuster searches for resources that may exist even when they are not linked.
- SecLists supplies candidate names for content discovery.
- Manual inspection can reveal technology information that helps configure later testing.
- HTTP status codes must be interpreted rather than accepted blindly.
- Automated tools can generate false positives.
- Failure responses can sometimes be analysed and filtered.
- Long automated scans are not always the most useful use of time.
- ZAP makes browser-to-server communication visible.
- GET and POST requests carry information differently.
- HTTP headers can disclose server and application technologies.
- Session cookies help applications maintain state.
- An HTTP `200 OK` response does not mean the requested application action succeeded.
- Reconnaissance is most useful when each stage informs the next.

---

# Methodology Developed

By the end of the exercise, the practical workflow had become:

**Target identification**

↓

**Connectivity check**

↓

**Photon crawl**

↓

**Analyse discovered resources**

↓

**Manual application inspection**

↓

**Identify PHP technology**

↓

**Select SecLists wordlist**

↓

**Configure DirBuster**

↓

**Directory and file discovery**

↓

**Interpret HTTP responses**

↓

**Identify inconsistent failure behaviour**

↓

**Create and validate failure signature**

↓

**Assess scan performance**

↓

**Move to OWASP ZAP**

↓

**Proxy Mutillidae traffic**

↓

**Inspect GET request**

↓

**Analyse response headers and technology disclosure**

↓

**Identify GET parameter and value**

↓

**Submit login form**

↓

**Inspect POST request**

↓

**Analyse response body**

↓

**Distinguish HTTP success from application success**

---

# Conclusion

This practical marked a shift from using individual security tools to thinking about reconnaissance as a connected process.

Photon helped identify resources already exposed by the application.

DirBuster used a wordlist to search for additional resources that might not be linked.

SecLists supplied the candidate names for that discovery.

When DirBuster produced unreliable results, the responses had to be interpreted and filtered rather than accepted automatically.

OWASP ZAP then exposed the HTTP communication behind ordinary browser interactions.

The most important lesson was that the tools themselves are only part of the process.

The value comes from understanding:

**what information
