# Lab 20: Password Hash Cracking with John the Ripper

**Date:** 14 November 2026  
**Environment:** Kali Linux in Oracle VirtualBox  
**Tool:** John the Ripper (JtR), with `office2john` and `pdf2john`  
**Scope:** Tutor-provided password-protected Word and PDF assignment files, tested in my own lab.

## Objective

For this assignment, I practised extracting password hashes from protected documents and using John the Ripper with wordlists to test whether their passwords could be recovered. I also worked through file-transfer, permissions and command-line errors encountered along the way.

## My workflow

### 1. Move the assignment files into Kali

I used VirtualBox shared folders to access the assignment files from my host desktop, then copied them to my Kali `~/Downloads` directory.

```bash
sudo cp /media/sf_Desktop/*assignment* ~/Downloads/
ls ~/Downloads
```

The screenshots show the Word and PDF assignment files in `~/Downloads`.

### 2. Check my available wordlists

I checked the available wordlists under:

```bash
ls /usr/share/seclists/Passwords/Common-Credentials
```

I later used two lists from this directory, beginning with a smaller list and then a larger one.

### 3. Troubleshoot Word document file permissions

My first attempt to extract the Word document hash returned `PermissionError: [Errno 13] Permission denied`. I then changed ownership of the files copied into `~/Downloads`.

```bash
office2john "assignment john 1.docx" > docx_hash.txt
sudo chown -R x:x ~/Downloads
```

**What I learned:** Copying files from a VirtualBox shared folder can leave ownership or permissions that interfere with processing them as my regular Kali user. I needed to resolve that before continuing.

### 4. Extract and test the Word document hash

I used `office2john` to prepare the Word document hash for John the Ripper. The screenshots then show John reading one Office password hash.

```bash
office2john "assignment john 1.docx" > docx_hash.txt
john --wordlist=/usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt docx_hash.txt
```

The smaller wordlist completed without recovering a password. I tried a larger list:

```bash
john --wordlist=/usr/share/seclists/Passwords/Common-Credentials/Pwdb_top-1000000.txt docx_hash.txt
```

**Result:** John recovered `password123` for `assignment john 1.docx`.

### 5. Extract and test the PDF hash

I used `pdf2john` to extract the PDF hash:

```bash
pdf2john "assignment john 1 pdf.pdf" > pdf_hash.txt
```

I initially made a filename mistake, typing `doc_hash.txt` instead of `docx_hash.txt` in a John command. The terminal reported that the file did not exist, which prompted me to correct the filename.

I then tested the PDF hash with the larger wordlist:

```bash
john --wordlist=/usr/share/seclists/Passwords/Common-Credentials/Pwdb_top-1000000.txt pdf_hash.txt
```

**Result:** John recovered `williamsburg` for `assignment john 1 pdf.pdf`.

## Results

| File | Hash preparation | Password recovered | Outcome |
| --- | --- | --- | --- |
| Tutor's Word document (`.docx`) | `office2john` | `password123` | Successful |
| Tutor's PDF (`.pdf`) | `pdf2john` | `williamsburg` | Successful |

These are the passwords visible in my screenshots for the tutor's exercise files. The protected documents and hash files are not uploaded to this public repository.

## Screenshots

The screenshots are preserved in chronological order, including my mistakes and corrections.

1. [01: Reviewing Kali file paths](screenshots/01-kali-file-paths.png)
2. [02: Checking the environment](screenshots/02-kali-terminal-check.png)
3. [03: VirtualBox shared-folder settings](screenshots/03-virtualbox-shared-folder.png)
4. [04: Copying the supplied assignment files](screenshots/04-copy-assignment-files.png)
5. [05: Word hash extraction permission error](screenshots/05-docx-permissions-troubleshooting.png)
6. [06: Word password recovered](screenshots/06-docx-password-recovered.png)
7. [07: PDF password recovered](screenshots/07-pdf-password-recovered.png)

## What I learned

- `office2john` and `pdf2john` prepare protected documents for John the Ripper; they do not, by themselves, recover the password.
- Wordlist choice matters. The smaller list did not recover my Word document password, but the larger list did.
- File names, file locations and Linux permissions matter when running terminal commands.
- A hash-cracking result needs to be confirmed against the corresponding file, rather than assumed from the tool's status alone.
- This was an **offline, authorised training exercise**, not an attempt to access someone else's files.

## Notes

This README is based on my lab screenshots from 14 November 2026. The screenshots provide the evidence for the recorded results. I used AI assistance to organise the notes into a readable GitHub write-up, but the terminal work and screenshots are from my own exercise.
