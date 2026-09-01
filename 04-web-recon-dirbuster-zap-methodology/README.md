# Web Reconnaissance and Proxy Analysis Using Photon, DirBuster and OWASP ZAP

**Completed:** 22 August 2026  
**Environment:** Kali Linux and Metasploitable 2  
**Tools:** Photon, DirBuster, SecLists, OWASP ZAP

## Overview

This practical brought together several things I had been learning separately and helped me see them as one process.

The general sequence was:

**confirm target → crawl with Photon → inspect the application → use what I found to configure DirBuster → interpret the results → move to ZAP → inspect the actual HTTP traffic**

The main lesson was that information gathered at one stage can help decide what to do at the next stage.

Testing was limited to the authorised Metasploitable 2 laboratory target.

For privacy, the original local IP address has been replaced with `<TARGET_IP>`.

---

## 1. Confirming the Target

Before starting the web reconnaissance, I confirmed that Metasploitable was reachable from Kali:

```bash
ping -c 3 <TARGET_IP>
```

Three packets were transmitted and three responses were received with no packet loss.

This was a simple step, but it reinforced a useful troubleshooting habit: check basic connectivity before assuming an application or security tool is the problem.

---

## 2. Photon Reconnaissance

I used Photon to crawl several applications hosted on Metasploitable.

| Application | Internal URLs | External URLs | Fuzzable URLs | Observation |
| --- | ---: | ---: | ---: | --- |
| DVWA | 1 | 0 | 0 | Crawl began at the login page |
| Mutillidae | 1 | 0 | 0 | Only one internal URL discovered |
| phpMyAdmin | 2 | 2 | 0 | One URL retrieved from `robots.txt` |
| TWiki | 6 | 0 | 0 | One Level 1 and five Level 2 URLs |
| DAV | 16 | 0 | 4 | More content discovered than appeared in the browser |

DAV was again the clearest example of why crawling was useful. Very little appeared to be present when viewed normally, but Photon discovered **16 internal URLs and 4 fuzzable URLs**.

Photon starts with a URL and follows the trail of references it can discover into other reachable resources. The starting page therefore does not necessarily show everything the crawler may eventually reach.

I also reinforced the distinction between:

- **internal URLs** — resources belonging to the target;
- **external URLs** — resources outside the target; and
- **fuzzable URLs** — input locations that may be worth later testing.

A fuzzable URL is not proof of a vulnerability.

### Authentication

DVWA only produced one internal URL because the crawl reached a login page.

This showed me that a crawler is limited by its current access and session. If it is not authenticated, it may only see a small part of an application.

### robots.txt

During the phpMyAdmin crawl, Photon retrieved information from `robots.txt`.

I learned that `robots.txt` may reveal application paths, but it is not an access-control mechanism. A path being listed there does not make it private.

---

## 3. Using Reconnaissance to Configure DirBuster

Before configuring DirBuster, I manually inspected Mutillidae.

While moving through the application, I noticed that pages repeatedly used the `.php` extension.

That gave me a reason to configure DirBuster to test PHP files rather than choosing an extension at random.

The process was becoming:

**observe target → identify clues about the technology → configure the next tool accordingly**

This was an important change for me because I was beginning to understand why I was selecting particular settings rather than simply copying them.

---

## 4. Selecting a SecLists Wordlist

For the first DirBuster run I used:

```text
/usr/share/seclists/Discovery/Web-Content/common.txt
```

I also learned something very basic but useful here: **a wordlist is not a program**.

It is a text file containing candidate values that another program reads.

At one point I entered the wordlist path directly into the terminal and received a permission error because the shell treated it as something I was trying to execute.

The correct approach was to give the wordlist to DirBuster as input.

I also learned that SecLists contains many different collections. `Discovery/Web-Content` was relevant to this task, but the correct list depends on what I am trying to enumerate.

---

## 5. Configuring DirBuster

The configuration included:

- list-based brute force;
- SecLists `common.txt`;
- directory testing;
- file testing;
- recursive scanning; and
- PHP as the file extension.

Here, **brute force did not mean password cracking**.

DirBuster was systematically testing candidate directory and file names from the supplied list.

For example, a directory might look like:

```text
/admin/
```

while a PHP file might look like:

```text
/admin.php
```

Recursive scanning meant that when DirBuster found a directory, it could continue looking for resources inside it.

---

## 6. Interpreting DirBuster Responses

DirBuster returned HTTP responses including:

- `200` — successful response;
- `302` — redirection; and
- `403` — forbidden.

A `403` could still be interesting because the server may recognise the requested location even though access is denied.

But I learned not to equate a status code or discovered path with a vulnerability. It is evidence about how the server responded and still needs interpretation.

---

## 7. Inconsistent Failure Responses

During recursive discovery against TWiki, DirBuster displayed:

```text
Warning unable to determine consistent fail response.
```

This became one of the most useful parts of the exercise.

A content-discovery tool needs to distinguish a real resource from the response returned for something that does not exist.

TWiki was returning different-looking responses for nonexistent resources, which made that distinction difficult and could create large numbers of false positives.

### Investigating the responses

DirBuster showed several example failure responses.

Although other parts differed, I noticed that they all contained:

```text
This Wiki topic does not exist
```

I entered that phrase into DirBuster's failure-matching field and tested it against the examples.

All three passed the test, and DirBuster reported that the expression should work.

The process was:

**tool reports ambiguity → inspect the responses → find a common failure indicator → test it → use it to reduce false positives**

This was a good example of why automated tools still need human interpretation.

---

## 8. The Nine-Day DirBuster Scan

After configuring the failure-matching rule, DirBuster continued recursive enumeration.

It was extremely slow.

Progress remained around **3–5%**, while the estimated completion time eventually reached approximately **nine days**.

Waiting for that was not practical.

By then I had already used the scan to learn:

- list-based directory discovery;
- file discovery;
- recursive enumeration;
- HTTP response interpretation; and
- false-positive management.

Rather than waiting days for the tool to finish, I moved on to OWASP ZAP.

This was also a useful practical lesson: a tool technically running does not necessarily mean that continuing to wait is the best use of the assessment time.

---

## 9. Introducing OWASP ZAP

I used OWASP ZAP to examine the communication between Firefox and Mutillidae.

I selected **Manual Explore** and launched Firefox through ZAP.

As I interacted with the application, requests and responses appeared in ZAP's History.

This made the idea of a web proxy much easier to understand.

In this setup, ZAP sat between the browser and the web application so that I could inspect the HTTP communication.

---

## 10. Examining a GET Request

One of the first requests I examined was a GET request for Mutillidae.

It followed the general form:

```http
GET http://<TARGET_IP>/mutillidae/ HTTP/1.1
Host: <TARGET_IP>
```

Other headers contained information such as the browser User-Agent, accepted content types and connection information.

At this point there was no parameter-value pair associated with the resource. The browser was simply requesting the application page.

This helped me separate parts of an HTTP request:

- method;
- host;
- requested resource;
- headers; and
- parameters.

---

## 11. Examining the Response

The corresponding response returned:

```http
HTTP/1.1 200 OK
```

The response headers also disclosed:

```text
Server: Apache/2.2.8 (Ubuntu) DAV/2
```

and:

```text
X-Powered-By: PHP/5.2.4-2ubuntu5.10
```

This connected back to the earlier reconnaissance work because the response itself gave clues about the technologies in use.

The response also contained a `PHPSESSID` cookie.

I began to understand that a session identifier allows the application to associate later requests with an existing session.

This stage also helped me distinguish between:

- **response headers** — protocol and metadata information; and
- **response body** — the actual content returned to the browser.

---

## 12. Identifying a GET Parameter

I navigated to the Mutillidae login functionality.

ZAP captured a request containing:

```text
index.php?page=login.php
```

I could now break that down into:

```text
Requested script: index.php
Parameter: page
Value: login.php
```

This was useful because I stopped seeing the URL as one long piece of text and began recognising the individual parts that an application receives and processes.

---

## 13. Observing a POST Request

I entered test credentials into the Mutillidae login form and submitted it.

ZAP captured the POST request.

Unlike the earlier GET parameter, the submitted form data appeared in the request body.

The practical difference became much clearer:

### GET

The parameter was visible in the URL:

```text
page=login.php
```

### POST

The submitted login information was carried in the request body.

Seeing the actual requests made this easier to understand than simply memorising the definition of GET and POST.

---

## 14. HTTP Success vs Application Success

The unsuccessful login attempt returned:

```http
HTTP/1.1 200 OK
```

At first, `200 OK` might look as though the login worked.

But the response body contained an application-level error showing that authentication had failed.

This taught me an important distinction:

```text
HTTP request successful ≠ login successful
```

`200 OK` means that the server successfully handled the HTTP request and returned a valid HTTP response.

It does not mean that the action the user wanted the application to perform was successful.

The status code therefore has to be interpreted together with the response content and application behaviour.

---

## 15. How the Stages Connected

By the end of this practical, the workflow made more sense to me as a connected process:

```text
Confirm target connectivity
        ↓
Crawl with Photon
        ↓
Inspect discovered resources
        ↓
Look at the application manually
        ↓
Notice PHP technology
        ↓
Choose a relevant SecLists wordlist and extension
        ↓
Configure DirBuster
        ↓
Interpret HTTP responses
        ↓
Investigate inconsistent failure behaviour
        ↓
Create and test a failure signature
        ↓
Decide whether continuing the scan is practical
        ↓
Move to ZAP
        ↓
Proxy browser traffic
        ↓
Inspect GET request and response
        ↓
Identify parameter and value
        ↓
Inspect POST form submission
        ↓
Compare HTTP status with application result
```

This was the first time the tools started to feel less like separate programs I was learning and more like different parts of the same investigation.

---

## What I Learned

The main things I took from this practical were:

- confirm connectivity before troubleshooting application tools;
- Photon can follow discovered references from a starting URL into other reachable resources;
- authentication affects what a crawler can see;
- `robots.txt` can provide reconnaissance information but is not access control;
- inspect the target before deciding which file extensions or settings make sense;
- a SecLists wordlist is input to another tool, not a program to execute;
- DirBuster can test resources that are not linked from the application;
- recursive scanning can continue discovery inside directories;
- HTTP status codes need interpretation;
- automated discovery can generate false positives;
- inconsistent failure responses can sometimes be filtered by finding a common response characteristic;
- an automated scan taking days may not be useful simply because it is still running;
- ZAP makes the browser/server conversation visible;
- GET parameters can appear in the URL;
- POST form data can appear in the request body;
- response headers can disclose technology information;
- cookies such as `PHPSESSID` help maintain session state; and
- `200 OK` describes the HTTP response, not necessarily success of the application action.

---

## Conclusion

This practical marked a shift from using individual tools to thinking about reconnaissance as a connected process.

Photon helped me discover resources by following references from a starting point.

Manual inspection then gave me clues about the application technology, which helped me configure DirBuster more deliberately.

When DirBuster produced unreliable failure responses, I had to inspect the responses myself and identify a pattern the tool could use to reduce false positives.

When the scan became impractically slow, I moved to ZAP rather than treating completion of the automated scan as the objective.

ZAP then let me see what was happening underneath ordinary browser actions: GET and POST requests, parameters, headers, cookies, response bodies and status codes.

The most important lesson was that the tools themselves were only part of the process.

The value came from understanding **what information each stage gave me, what that information meant, and how it could guide the next step**.

## Lab Note

This project documents authorised testing performed against Metasploitable 2, an intentionally vulnerable cybersecurity training environment.
