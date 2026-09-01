# Photon Web Reconnaissance Against Metasploitable Applications

**Completed:** 12 August 2026  
**Environment:** Kali Linux and Metasploitable 2  
**Tools:** Photon, DirBuster, SecLists

## Overview

This exercise focused on web reconnaissance against applications hosted on the Metasploitable 2 virtual machine.

I used **Photon** to crawl several applications and see what URLs and resources could be discovered automatically. I then used **DirBuster** and **SecLists** to explore a different type of content discovery.

This helped me understand that web reconnaissance is not simply running one tool. A crawler follows resources it can find, while a wordlist-based tool can test for resources that may exist even when they are not linked from the page.

Testing was limited to the authorised Metasploitable 2 laboratory target.

For privacy, the original local IP address has been replaced with `<TARGET_IP>`.

---

## 1. Photon Reconnaissance

Photon is a web crawler used for reconnaissance and attack-surface mapping.

It begins with a supplied URL and follows links and other references it can discover.

The basic format I used was:

```bash
python3 photon.py -u http://<TARGET_IP>/<APPLICATION>
```

I opened each application in the browser first so I could identify its location and then crawled the applications individually.

### Following the trail to other resources

One of the things I learned about Photon was that the starting URL was only the beginning of the crawl.

Photon could follow the trail of references it discovered from that starting point into other URLs and resources. This meant it could lead me to parts of the application that were not obvious from simply viewing the original page and were not necessarily links I would have noticed or followed manually.

That changed how I understood crawling. I was not just giving Photon a page and asking it to list what was visibly on that page. I was giving it a starting point from which it could continue discovering other reachable resources.

This became especially clear when I compared the browser view with the results from DAV later in the exercise.

---

## 2. Photon Results

| Application | Internal URLs | External URLs | Fuzzable URLs | Observation |
| --- | ---: | ---: | ---: | --- |
| DVWA | 1 | 0 | 0 | Crawl began at the login page |
| Mutillidae | 1 | 0 | 0 | Only one internal URL discovered |
| phpMyAdmin | 2 | 2 | 0 | One URL retrieved from `robots.txt` |
| TWiki | 6 | 0 | 0 | One URL found at Level 1 and five at Level 2 |
| DAV | 16 | 0 | 4 | Considerably more content discovered than was visible in the browser |

### Internal URLs

An internal URL belongs to the target being crawled. These help map additional pages and resources within the same application or host.

### External URLs

An external URL points away from the target to another domain or external resource.

### Fuzzable URLs

Photon can identify some URLs or parameters as potentially suitable for further input testing.

A fuzzable URL is **not proof of a vulnerability**. It tells me that there is an input location that may be worth investigating further.

This was an important distinction: reconnaissance identifies possible areas of interest, but further testing is needed before calling something a vulnerability.

---

## 3. DAV Discovery

DAV produced the most interesting Photon result.

When I viewed the application normally in the browser, there appeared to be very little content. Photon discovered:

- **16 internal URLs**
- **4 fuzzable URLs**

This showed me why following the trail from a starting URL can be useful. What was immediately visible in the browser was not necessarily everything Photon could reach and discover during the crawl.

---

## 4. Authentication and DVWA

Photon discovered only one internal URL when crawling DVWA.

DVWA presented a login page, which limited what the unauthenticated crawler could reach.

This helped me understand that a crawler can only map resources available within its current access and session. If authentication is required, an unauthenticated crawl may only reveal a small part of the application.

---

## 5. robots.txt and phpMyAdmin

During the phpMyAdmin crawl, Photon retrieved a URL from `robots.txt`.

I learned that `robots.txt` gives instructions to compliant crawlers about paths that should or should not be crawled, but it is **not an access-control mechanism**.

A listed path may still be directly accessible.

From a reconnaissance point of view, this means `robots.txt` can sometimes provide clues about a website's structure or paths that may be worth examining.

---

## 6. Moving from Crawling to Content Discovery

I then used **DirBuster** with **SecLists**.

This was where the difference between crawling and content discovery became clearer to me.

### Photon

Photon follows resources that it can discover from a starting URL.

**Photon follows what it can find.**

### DirBuster

DirBuster takes candidate directory or file names and sends requests to see whether those resources exist.

**DirBuster tests what might exist.**

This means DirBuster can potentially find content that is not linked from the pages a crawler can see.

### SecLists

SecLists is a collection of different wordlists used for security testing.

For web discovery I could use lists from its web-content collections, but I also learned that SecLists is much broader than one directory. Different lists exist for different types of enumeration and testing, so choosing a list should depend on what I am actually trying to discover.

This was more useful than treating a wordlist as a random file to load into a tool.

---

## 7. Choosing What to Search For

One thing I learned during the DirBuster work was that I should not simply select file extensions at random.

Before choosing an extension, I could look at the application for clues about the technology it was using. Existing URLs, filenames and other page clues could suggest what type of files were likely to be present.

For example, if the application was clearly using PHP, searching for `.php` files made sense. If the application showed signs of ASP.NET, an extension such as `.aspx` would be more relevant.

So rather than thinking:

> Pick every extension and hope something appears.

the better approach was:

> Look at the target first, gather clues, and choose options that make sense for that application.

This also showed me that reconnaissance begins before pressing **Start** on a scanner.

---

## 8. Directories, Files and Trailing Slashes

DirBuster also helped me understand the difference between searching for directories and files.

### Directory discovery

A directory might appear as:

```text
/admin/
```

The trailing `/` is a useful clue that the path is being treated as a directory.

### File discovery

A file could instead appear as:

```text
/admin.php
```

or, on a different type of application:

```text
/admin.aspx
```

The extension provides a clue about the type of server-side technology being used.

Learning to notice things such as the **trailing slash**, path structure and file extension made the results easier for me to interpret instead of seeing every URL as essentially the same thing.

---

## 9. Recursive Scanning

If DirBuster discovers a directory, recursive scanning can continue searching inside that directory.

For example, discovering:

```text
/admin/
```

does not necessarily mean the discovery process has finished. That directory may contain additional files or subdirectories.

This helped me understand why content discovery can branch into more paths as new directories are found.

---

## 10. Threads

I also learned what the thread setting was doing.

Threads control how many requests the tool can make concurrently.

Increasing the number can make discovery faster, but it also means more traffic is being sent to the target. It can increase load and, particularly when a target is behaving inconsistently, make the results harder to interpret.

So a higher number is not automatically better.

---

## 11. Inconsistent Fail Responses

During the practical, DirBuster produced an **inconsistent fail-response warning**.

This became one of the more useful parts of the exercise because it forced me to think about what the tool was actually doing.

For directory discovery to work properly, the tool needs some way to distinguish:

```text
A resource exists
```

from:

```text
A resource does not exist
```

If a server responds strangely or inconsistently when a nonexistent path is requested, the tool can mistakenly treat invalid resources as real ones.

That can create **false positives**.

The important lesson was that I could not simply assume that every item shown by DirBuster genuinely existed. The responses still had to be interpreted.

---

## 12. How the Tools Fit Together

By this stage I could see the difference between the tools more clearly.

| Tool | What I was using it for |
| --- | --- |
| Photon | Crawling resources that could be discovered from a starting URL |
| DirBuster | Testing possible directory and file names |
| SecLists | Supplying wordlists appropriate to the type of discovery being performed |

They overlap as reconnaissance tools, but they do not discover information in exactly the same way.

A crawler can miss something because nothing it can reach links to it.

A wordlist-based discovery tool may still find that resource if the relevant name is included in the list being tested.

At the same time, wordlist discovery depends heavily on the choices I make: the list, extensions, recursion, threads and how I interpret the responses.

---

## Key Commands and Examples

### Photon

```bash
python3 photon.py -u http://<TARGET_IP>/<APPLICATION>
```

### Example directory

```text
/admin/
```

### Example PHP file

```text
/admin.php
```

### Example ASP.NET file

```text
/admin.aspx
```

---

## What I Learned

This exercise helped me understand web reconnaissance in more depth than simply looking at what was visible in a browser.

I learned that:

- Photon follows links and other references it can discover.
- Authentication can limit what an unauthenticated crawler sees.
- `robots.txt` can reveal structural information but is not access control.
- A fuzzable URL is an area for further investigation, not proof of a vulnerability.
- DirBuster uses candidate names to test what directories or files might exist.
- SecLists contains different types of wordlists, and the list should be chosen according to the task.
- Looking at the target can give clues about which file extensions are sensible to test.
- `.php` and `.aspx` are examples of extensions that may be relevant depending on the technology being used.
- A trailing slash can help distinguish a directory path from a file path.
- Recursive scanning can continue discovery inside directories that have already been found.
- More threads can increase speed but also increase traffic and load.
- Inconsistent server responses can cause false positives.
- Automated results still have to be interpreted rather than accepted automatically.

The clearest Photon example was DAV. Very little appeared to be present when I viewed it normally, but Photon found **16 internal URLs and 4 fuzzable URLs**.

The DirBuster work added another lesson: before running a discovery tool, I should look at the target and think about what I am asking the tool to search for.

That was probably the biggest change in my understanding during this exercise. I was moving from simply learning commands to beginning to understand why I was choosing particular options.

## Lab Note

This project documents authorised testing performed against Metasploitable 2, an intentionally vulnerable cybersecurity training environment.
