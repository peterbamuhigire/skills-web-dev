# How We Handle Data Security in Our Mobile and Web Applications

Your data is not ours to mishandle. Every system we build — whether a mobile app running on an Android phone in Kampala or a web platform accessed from a browser in Nairobi — is designed from the ground up with security as a foundational requirement, not an afterthought.

This article explains, in plain terms, the specific measures we take to protect client data across all our applications.

---

## Why Data Security Cannot Be an Afterthought

Many software teams treat security as something to "add later" — after features are built and the system is running. This is a serious mistake. Vulnerabilities introduced at the architecture stage are extraordinarily difficult to fix once a system is in production.

We take the opposite approach. Before a single line of code is written, our team establishes the security architecture: how data will be stored, how it will travel between systems, who will have access to it, and how the system will respond if something goes wrong.

---

## 1. Encrypted Data in Transit

All data moving between our applications and their servers travels over HTTPS with TLS 1.2 or higher. This means that if someone intercepts the network traffic — through a public Wi-Fi access point, for example — they see only encrypted, unreadable data.

We enforce this without exception. HTTP connections are redirected to HTTPS automatically. Certificate pinning is applied in our Android applications for high-sensitivity endpoints, ensuring the app only communicates with servers presenting the correct, verified certificate.

---

## 2. Encrypted Data at Rest

Sensitive information stored on device — user credentials, session tokens, personal records — is held in encrypted storage.

On Android, we use `EncryptedSharedPreferences` and Room database encryption via SQLCipher for particularly sensitive data. On the server side, sensitive fields such as national identification numbers, financial records, and health data are encrypted at the column level in the database, separate from standard application-level access controls.

Encryption keys are managed through secure key stores and are never embedded in source code.

---

## 3. Authentication and Session Management

We implement authentication carefully, with no shortcuts.

- **Passwords** are never stored in plain text. We use bcrypt with a work factor calibrated to be computationally expensive for attackers whilst remaining fast enough for legitimate users.
- **Sessions** are issued as cryptographically signed tokens with short expiry windows. Idle sessions are invalidated automatically.
- **Multi-factor authentication** is available and recommended for administrative accounts on all our platforms.
- **Role-based access control (RBAC)** ensures that every user — whether a cashier, manager, or system administrator — sees only the data and functions their role permits. A user cannot escalate their own permissions.

---

## 4. Protection Against Common Web Vulnerabilities

Our PHP and JavaScript code is written with OWASP Top 10 vulnerabilities in mind at every step.

**SQL Injection** is prevented through the use of prepared statements and parameterised queries throughout. We do not construct SQL queries by concatenating user-supplied strings.

**Cross-Site Scripting (XSS)** is blocked by escaping all output rendered in the browser. User input is never trusted and is validated at the server boundary before processing.

**Cross-Site Request Forgery (CSRF)** protection is applied to all state-changing requests through synchronised token patterns.

**File uploads** are validated for MIME type, file size, and content. Uploaded files are stored outside the web root and served through controlled handlers, preventing executable uploads from being accessed directly.

---

## 5. Secure API Design

Our REST APIs are designed on the principle of least privilege: every endpoint exposes only what is necessary and nothing more.

API keys and JWT tokens carry expiry claims and scope restrictions. All API requests from mobile applications are authenticated. Rate limiting is applied to sensitive endpoints — authentication, password reset, and data export — to prevent brute force and enumeration attacks.

We log all API activity for audit purposes, recording who accessed what and when, without logging the sensitive data itself.

---

## 6. Multi-Tenant Data Isolation

Several of our platforms serve multiple client organisations from a shared infrastructure. In these environments, strict tenant isolation is non-negotiable.

Every database query is scoped to the authenticated tenant's identifier. It is architecturally impossible for one tenant's query to return another tenant's records — not merely through application logic checks, but through query construction that physically cannot cross tenant boundaries.

Tenant data isolation is verified during code review and tested explicitly before any multi-tenant feature is released.

---

## 7. Dependency and Supply Chain Security

Third-party libraries introduce risk when not managed carefully. We maintain an updated inventory of all dependencies across our projects and monitor for published vulnerabilities. Libraries that are no longer maintained or carry known unpatched vulnerabilities are replaced.

Our servers run minimal operating system installations — only the packages required for the application are present. Unused services, ports, and accounts are removed.

---

## 8. Security in the Development Process

Security is not reviewed only at the end. It is part of every stage of development.

- Code reviews include a security checklist covering input validation, output encoding, authentication flows, and data handling.
- Our team follows a documented set of secure coding standards for PHP, Android/Kotlin, and JavaScript.
- New features that handle personal data are subject to a privacy impact review before implementation begins.
- We conduct periodic security audits of our own platforms using structured checklists covering configuration, authentication, authorisation, and injection vulnerabilities.

---

## 9. Incident Response Readiness

No system is entirely immune to incidents. What matters is how quickly and effectively an incident is contained and resolved.

We maintain documented incident response procedures for our hosted platforms, including:

- Detection through structured application and server logging
- Containment steps for credential compromise, unauthorised access, and data exposure
- Communication protocols for notifying affected clients promptly
- Post-incident review to close the vulnerability and prevent recurrence

Our clients are never left to discover a problem on their own.

---

## What This Means for You as a Client

When you commission a system from us, you are not receiving software that happens to have security features. You are receiving a system built on security principles that protect your customers, your reputation, and your operations.

We document the security measures applied to each system we deliver, so you understand precisely what protections are in place and can answer questions from your own clients and regulators with confidence.

---

**Want to discuss the security requirements for your next project?**

Contact us to arrange a consultation. We are happy to walk through our approach in detail and explain how it applies to your specific context and industry.

---

*Published by the development team. Last reviewed March 2026.*
