# ORM Leak Exploitation Write-up: PentesterLab CTF - ORM LEAK 02

## Overview

This write-up details the exploitation of an ORM (Object-Relational Mapping) leak vulnerability in the PentesterLab CTF exercise "ORM LEAK 02". This challenge demonstrates how improper handling of user-controlled input within Django ORM queries can lead to the exposure of sensitive database information, specifically a hashed user password.

**Key Learning Points:**

* Identifying ORM injection points in nested/chained lookups (`related_field__another_field__lookup`).
* Establishing "true" and "false" response conditions for blind injection.
* Automating character-by-character data exfiltration using a Python script.
* Leveraging multithreading for faster exploitation.

## What is an ORM Leak?

An ORM acts as a bridge between an application's object-oriented code and its relational database. While convenient, if user input is directly incorporated into ORM queries without proper sanitization, an attacker can manipulate the query using ORM lookup methods (e.g., `__startswith`, `__contains`, `__gt`). This allows for blind data exfiltration, where information is inferred based on subtle differences in the application's responses.

Django's ORM, in particular, offers powerful field lookups. When an application unpacks user-controlled parameters directly into a `filter()` method (e.g., `Model.objects.filter(**user_input_dict)`), it can create a vulnerability.

## Challenge: ORM LEAK 02

### Objective

The goal was to retrieve the hashed password of the `admin` user. The challenge specified that the hash begins with `pbkdf2_` and contains alphanumeric characters, `=`, `/`, `+`, `$`, and `_`. The leaked hash itself was the key to the challenge.

### Initial Reconnaissance & Vulnerability Identification

The new host for ORM LEAK 02 was `https://api-ptl-14ef33012386-0b276d30b296.libcurl.me`. Through initial testing, the `POST /api/articles/` endpoint was identified as a potential target.

A test request was sent to this endpoint with a known ID:

![image](https://github.com/user-attachments/assets/e60b30cc-45b5-4e7d-8971-456332c5ff49)

![image](https://github.com/user-attachments/assets/33b352f0-deab-4656-939e-1179d7a01064)



### Determining True/False Conditions for Blind Injection

With the admin ID (1) identified, the next step was to confirm how `password__startswith` would behave. The full lookup chain for the password field would be `created_by__user__password__startswith`.

**Test Case 1: Incorrect Prefix (`@`)**

![image](https://github.com/user-attachments/assets/e7ae6940-f7c7-4a82-bb8c-8cbe5fd9045c)


![image](https://github.com/user-attachments/assets/760877c5-acbe-49b4-8aa6-4c667f94c4c4)

This was the "false" condition: an empty JSON array `[]`.




**Test Case 2: Correct Prefix (p)**

![image](https://github.com/user-attachments/assets/5d5f9ed9-e08b-4510-97d7-75f740d118a2)


![image](https://github.com/user-attachments/assets/369e08cf-4a04-4d4a-84f9-5d90fae74739)


