# Per-Tenant Notification Templates

Named tenants on the HIGH_RISK_TENANTS list, and all Enterprise tier tenants affected, receive direct notification — not a generic mass email. Sent by the tenant's account manager / CSM with a real human signature.

## Sev-1, Initial DM (within 30 minutes)

**Subject:** Incident affecting <feature> in your account — initial notice (inc-1923)

**Body:**

> Hello <First Name>,
>
> I'm writing to let you know that we are responding to an issue affecting <feature> in your account. Here is what we know so far.
>
> **What we observed.** Starting at HH:MM UTC, <feature> began producing answers that did not meet our normal quality bar / <or> began responding more slowly than usual / <or> took the following action(s) we are investigating: <list>.
>
> **Your account.** Our current estimate is that approximately <N> requests in your account between HH:MM and HH:MM UTC were affected. <If agent-class:> the following actions taken by the AI on your behalf are under review: <list>.
>
> **What we are doing.** We have <named mitigation, e.g. "rolled the affected configuration back" / "paused agent actions" / "switched to a backup model"> and our team is investigating the root cause. <If applicable:> we are not asking you to take any action at this time.
>
> **Next update.** I will send you another note by HH:MM UTC. If you need to reach me directly, this email or <phone>.
>
> Best,
> <Account manager / CSM>

## Sev-1, Update (every 60 minutes for high-risk)

**Subject:** Re: Incident affecting <feature> in your account — update HH:MM UTC

> Hello <First Name>,
>
> A brief update on inc-1923.
>
> **What changed.** <named change in mitigation or understanding>.
>
> **Current state.** Quality / behaviour is now <stable / recovering / still impacted>. Our containment metric for <feature> is at <value> vs our service level of <value>.
>
> **What you might see.** <Plain-language description of current customer experience.>
>
> **Next update.** HH:MM UTC.
>
> <Sig>

## Sev-1 with Data Implications

**Subject:** Important: incident affecting <feature> and review of account data (inc-1923)

(Drafted with legal review. Template paragraphs below — never sent verbatim without legal sign-off.)

> Hello <First Name>,
>
> I am writing to inform you of an incident under investigation that may have affected information in your account. We are taking this seriously and will give you complete information as our review progresses.
>
> **What we are investigating.** At HH:MM UTC, our team detected <description suitable for sharing with legal sign-off>. We are currently investigating whether and to what extent information from your account may have been involved.
>
> **What we have done.** We have <mitigation>. We have preserved the relevant evidence to support a thorough review and, if applicable, regulator notification.
>
> **What we will do next.** Our team will complete an initial determination by HH:MM UTC and contact you again with a more specific update. If our review confirms that account information was disclosed in an unintended way, we will follow up with details of what was involved, the actions we will take, and any actions we recommend you take.
>
> **Your DPO and security contact.** If you would like our DPO / security lead to brief your team, we can arrange a call today.
>
> <Sig + legal CC>

## Sev-2 DM

**Subject:** Issue affecting <feature> in your account (inc-1924)

> Hi <First Name>,
>
> A short note to let you know we are working on an issue with <feature> that has reduced answer quality for a small number of requests since HH:MM UTC. We've <named mitigation> and quality is recovering.
>
> **Your account.** ~<N> requests affected.
>
> **Action needed.** None at this time.
>
> **Resolution.** I expect this to be fully resolved by HH:MM UTC and will confirm.
>
> <Sig>

## Sev-2 Close-Out

**Subject:** Resolved: issue affecting <feature> in your account (inc-1924)

> Hi <First Name>,
>
> The <feature> issue I notified you of earlier today is resolved. Quality has been at our service level for <window> and we are out of the incident state.
>
> **Summary.** <2–3 sentence summary>.
>
> **Postmortem.** A postmortem will be available by <date>. I will send a copy of the customer-facing summary.
>
> Thank you for your patience.
> <Sig>

## Close-Out for Sev-1 (Detailed)

**Subject:** Resolved: incident affecting <feature> (inc-1923) — summary and next steps

> Hello <First Name>,
>
> The incident affecting <feature> is resolved. I want to give you a clear picture of what happened in your account, what we did, and what we are doing to prevent it.
>
> **Timeline (in your time zone).**
> - HH:MM detection.
> - HH:MM containment.
> - HH:MM full resolution.
>
> **Your account.** <Number of requests affected; named actions taken by AI on your behalf if agent-class; any data implications and what we determined>.
>
> **Root cause (preliminary).** <One-sentence factual cause; postmortem will detail>.
>
> **What we did.** <Mitigations applied>.
>
> **What we will do.** <Action items relevant to the customer's account: change in a default, new monitoring, eval-gate change, etc.>.
>
> **Postmortem.** Full postmortem available by <date>; I will send the customer-facing summary.
>
> **Open call.** Happy to schedule a debrief with your team if useful.
>
> Best,
> <Sig>

## Anti-Patterns

- Same template to a regulated bank and a hobbyist; voice and detail level mismatched.
- "Issue resolved" with no timeline, no count of affected requests, no postmortem date.
- Sent at 02:14 UTC to a Tokyo customer who is asleep — coordinate with CSM's time zone for non-sev-1.
- AI-generated tenant comms during an AI incident — tone-deaf, sometimes wrong.
- Legal CC missing on data-implication communications.
