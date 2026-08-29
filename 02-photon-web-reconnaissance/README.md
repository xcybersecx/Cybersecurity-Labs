# Photon Web Reconnaissance Against Metasploitable Applications

**Completed:** 12 August 2026  
**Environment:** Kali Linux and Metasploitable 2  
**Tools:** Photon, DirBuster, SecLists

## Overview

This exercise focused on web reconnaissance against applications hosted on the Metasploitable 2 virtual machine.

The main objective was to use **Photon** from Kali Linux to crawl several web applications, identify discoverable URLs, and understand how automated reconnaissance can reveal resources that are not immediately obvious from simply viewing a page in a browser.

I also carried out additional practical work using **DirBuster** and **SecLists** to understand the difference between web crawling and wordlist-based content discovery.

Testing was limited to the authorised Metasploitable 2 laboratory target.

---

# 1. Objective

The objectives were to:

1. Confirm that the Metasploitable target was reachable.
2. Identify web applications hosted on the target.
3. Use Photon to crawl each application individually.
4. Compare internal, external and fuzzable URLs discovered.
5. Observe how authentication affected crawling.
6. Understand the role of `robots.txt` during reconnaissance.
7. Compare crawling with wordlist-based directory and file discovery.

---

# 2. Photon Reconnaissance

Photon is a web crawler used for reconnaissance and attack-surface mapping.

It begins with a supplied URL and follows links and other references that it can discover.

The basic format used during the exercise was:

```bash
python3 photon.py -u http://<TARGET_IP>/<APPLICATION>
```

Each application was opened in the browser first so that I could identify its location before crawling it individually.

---

# 3. Results

| Application | Internal URLs | External URLs | Fuzzable URLs | Observation |
|---|---:|---:|---:|---|
| DVWA | 1 | 0 | 0 | Crawl began at the login page |
| Mutillidae | 1 | 0 | 0 | Only one internal URL discovered |
| phpMyAdmin | 2 | 2 | 0 | One URL retrieved from `robots.txt` |
| TWiki | 6 | 0 | 0 | One URL found at Level 1 and five at Level 2 |
| DAV | 16 | 0 | 4 | Considerably more content discovered than was visible in the browser |

---

# 4. Understanding the Results

## Internal URLs

An internal URL belongs to the target being crawled.

These URLs help map additional pages and resources within the same web application or host.

## External URLs

An external URL points away from the target to another domain or external resource.

These can help show how an application interacts with resources outside the target environment.

## Fuzzable URLs

Photon identifies some URLs or parameters as potentially suitable for further input testing.

A fuzzable URL is **not evidence of a vulnerability**.

It simply identifies an input location that may warrant further investigation.

This distinction was important because reconnaissance identifies areas of interest, while additional testing is required before a vulnerability can be confirmed.

---

# 5. DAV Discovery

The DAV application produced the most interesting Photon result.

When viewed normally in the browser, the page appeared to contain very little content.

However, Photon discovered:

- **16 internal URLs**
- **4 fuzzable URLs**

This demonstrated that the amount of content visible to a normal browser user does not necessarily represent the full attack surface that can be discovered through automated reconnaissance.

---

# 6. Authentication and DVWA

Photon discovered only one internal URL when crawling DVWA.

DVWA presented a login page, which prevented the unauthenticated crawler from accessing resources that required an authenticated session.

This demonstrated an important limitation of automated crawling:

> A crawler can only map resources that it can reach within its current access and session context.

If an application requires authentication, an unauthenticated reconnaissance tool may only see a small part of the available application.

---

# 7. robots.txt and phpMyAdmin

During the phpMyAdmin crawl, Photon retrieved a URL from `robots.txt`.

This helped demonstrate the reconnaissance value of the file.

`robots.txt` is designed to provide instructions to compliant web crawlers about paths that should or should not be crawled.

However, it is **not an access-control mechanism**.

A path listed in `robots.txt` may still be directly accessible.

For this reason, the file can sometimes reveal useful information about the structure of a website or application.

---

# 8. Additional Practical Work: DirBuster and SecLists

I also used **DirBuster** with a **SecLists web-content wordlist** to understand how content discovery differs from crawling.

Photon and DirBuster approach reconnaissance differently.

### Photon

Photon follows resources that it can discover from an initial URL.

In simple terms:

**Photon follows what it can find.**

### DirBuster

DirBuster uses candidate names from a wordlist and sends requests to determine whether directories or files exist.

In simple terms:

**DirBuster tests what might exist.**

### SecLists

SecLists provides collections of candidate directory names, filenames and other values that can be supplied to discovery tools.

In this exercise, it provided candidate web-content names for DirBuster to test.

---

# 9. Directory and File Discovery

I learned the difference between several DirBuster options.

## Brute Force Dirs

This tests candidate directory names.

For example:

```text
/admin/
```

## Brute Force Files

This can test candidate filenames.

When combined with a PHP extension, for example:

```text
/admin.php
```

## Recursive Scanning

If DirBuster discovers a directory, recursive scanning allows it to continue looking for additional resources inside that directory.

For example:

```text
/admin/
```

might then be searched for additional files or subdirectories.

## Threads

Threads control how many requests the tool can make concurrently.

Increasing the number of threads may make discovery faster, but it also:

- generates more traffic;
- increases load on the target;
- may cause instability; and
- may make results more difficult to interpret if the server behaves inconsistently.

---

# 10. Inconsistent Fail Responses

During the exercise, DirBuster produced an **inconsistent fail-response warning**.

This showed why content-discovery tools need to understand what a normal response for a nonexistent resource looks like.

If the target returns unusual or inconsistent responses for invalid paths, a discovery tool may incorrectly treat nonexistent resources as valid.

This can produce **false positives**.

The result reinforced the importance of interpreting automated tool output rather than assuming that every result represents a genuine resource.

---

# What I Learned

This exercise helped me understand that web reconnaissance involves more than looking at what is visible in a browser.

Different tools discover information in different ways.

I learned that:

- Photon follows links and discoverable references from a starting URL.
- DirBuster tests possible directory and filename combinations.
- SecLists provides candidate names for content-discovery testing.
- Authentication can limit what an unauthenticated crawler can discover.
- `robots.txt` may reveal useful structural information but does not provide access control.
- A fuzzable URL is an area for further testing, not proof of a vulnerability.
- Automated tools can generate false positives.
- Tool output must be interpreted in context.
- Different reconnaissance techniques can reveal different parts of the same attack surface.

The clearest example was DAV.

Very little appeared to be present when viewing the application normally, but Photon discovered **16 internal URLs and 4 fuzzable URLs**.

This demonstrated why automated reconnaissance can reveal considerably more information than manual browsing alone.

---

# Conclusion

The exercise introduced me to two different approaches to web reconnaissance.

**Photon follows what it can discover.**

**DirBuster tests what might exist.**

**SecLists supplies candidate names for those tests.**

Together, these techniques demonstrated that attack-surface mapping involves combining different forms of reconnaissance rather than relying on a single tool.

Most importantly, the exercise reinforced that discovering a URL, directory, parameter or fuzzable input does not automatically mean a vulnerability exists.

Reconnaissance identifies areas that may deserve further investigation. Additional testing and evidence are required before making a vulnerability finding.

---

## Lab Note

This project documents authorised testing performed against Metasploitable 2, an intentionally vulnerable cybersecurity training environment.
