# Status Page Templates per Failure Class

Every template names: product impact, mitigation in progress, next update time. All times in UTC. No speculation on cause. No provider names unless required.

## Universal Shape

```
Title:   <short, accurate, ≤ 8 words>
Status:  Investigating | Identified | Monitoring | Resolved
Body:
<one short paragraph: what we observed, what users may see>
<one short paragraph: what we are doing>
Next update by: <HH:MM UTC>
```

## hallucination-spike

**Title:** Reduced answer accuracy on <feature>

**Investigating:**
> We are investigating a temporary reduction in answer quality on <feature>. Users may see more "I don't know" responses than usual or, in a small number of cases, answers that are less accurate than our standard. We have raised the conservative-answer threshold to err on the side of refusing rather than answering incorrectly while we investigate.
>
> Next update by HH:MM UTC.

**Identified / Monitoring:**
> We have identified the change that caused the quality drop and have rolled back the affected configuration. Quality metrics are recovering. We will continue to monitor before declaring resolved.
>
> Next update by HH:MM UTC.

**Resolved:**
> Quality on <feature> has returned to our service level for the last <window>. A postmortem will be available by <date>.

## prompt-drift

**Title:** Configuration rollback on <feature>

**Investigating:**
> A recent configuration change on <feature> reduced answer quality. We have rolled the configuration back to the previous known-good version. You may see some answers reload as we re-process.
>
> Next update by HH:MM UTC.

## model-regression

**Title:** Underlying AI model degradation on <feature>

**Investigating:**
> An underlying AI model used by <feature> is producing lower-quality answers than expected. We have pinned to the previous model version for affected requests while we investigate.
>
> Next update by HH:MM UTC.

## jailbreak (PUBLIC; no operational detail; coordinate with security)

**Title:** Temporary safety enhancement on <feature>

**Investigating:**
> We have temporarily tightened safety controls on <feature> to address an attempted abuse of the system. Some prompts that previously succeeded may now be refused. We are restoring normal behaviour as quickly as we can while keeping the protections in place.
>
> Next update by HH:MM UTC.

If data exfiltration is confirmed, **do not** post a status page entry without legal review. Use direct tenant notification instead; status-page entry follows after legal sign-off.

## cost-runaway (usually invisible to most customers)

Typically no public status page entry. Direct tenant notification to the single affected tenant if isolated. Public entry only if customers see degraded latency from quota caps.

**Title (only if public):** Temporary capacity limits on <feature>

**Body:**
> To protect platform stability, we have temporarily limited high-volume requests on <feature>. Most users will not notice; some heavy-usage workflows may see slower responses or queue. Next update by HH:MM UTC.

## agent-action

**Title:** Agent actions paused on <feature>

**Investigating:**
> We have paused agent-driven actions on <feature> while we review recent activity. AI suggestions remain available but the AI will not take actions on your behalf for the moment.
>
> Next update by HH:MM UTC.

## retrieval-drift

**Title:** Reduced source-citation quality on <feature>

**Investigating:**
> <feature> is currently retrieving fewer relevant sources than expected, which is reducing answer quality. We have reverted to the previous knowledge-base snapshot while we investigate.
>
> Next update by HH:MM UTC.

## provider-incident

**Title:** Slower or degraded AI responses on <feature>

**Investigating:**
> An underlying AI service is experiencing problems. We have switched <feature> to a backup service and you may notice slightly slower or differently-styled responses while this continues.
>
> Next update by HH:MM UTC.

## tool-vendor-outage / schema-change

**Title:** Limited integration on <feature>

**Investigating:**
> An external integration used by <feature> is currently unavailable. <feature> remains available for tasks that do not require that integration; affected actions are paused.
>
> Next update by HH:MM UTC.

## training-data-shift / data-evolution

Usually invisible to most customers; per-tenant DM is typically the correct surface. Public entry only if multiple tenants affected.

**Title (if public):** Accuracy issue on <feature> for some workflows

**Body:**
> Some <feature> queries are returning lower-quality answers than expected. We have narrowed the issue to a specific workflow type and are deploying a fix. Affected users will be notified directly.
>
> Next update by HH:MM UTC.

## Language Pattern Library

Phrasings approved by legal/comms:

| Avoid | Use |
|---|---|
| "Our model hallucinated" | "Some answers were less accurate than our service level" |
| "OpenAI is down" | "An underlying AI service is experiencing problems" |
| "We were hacked" | "We are investigating an attempted abuse of the system" |
| "Customer data leaked" | "We are investigating whether information from some accounts was disclosed in an unintended way" (only with legal sign-off; usually direct tenant comms instead) |
| "We've fixed it" (before recovery confirmed) | "We have applied a mitigation and are monitoring" |
| "Should be back soon" | "Next update by HH:MM UTC" |
