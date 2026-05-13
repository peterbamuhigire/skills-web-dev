# Discovery Interview Patterns

Interviews fail in predictable ways: leading questions, hypothetical futures, polite participants, scripts so long the interviewer cannot listen. This reference encodes patterns that produce *behavioural* signal — what the person actually did, not what they say they would do.

## Recruitment Rules

- Recruit from the *segment under hypothesis*, not from convenience pools. Friends-of-the-team and power users have already learned the product's logic and cannot reproduce a beginner's confusion.
- Compensate participants. Unpaid participants over-select for opinionated outliers and the lonely.
- Track who declined and why; the no-shows often carry the disconfirming signal — they are the people who do not have the problem you are testing for.
- Five participants per actor per cycle is the working minimum; expect 15–20 across a hypothesis if the actor is heterogeneous, with the milestone of *seeing patterns by interview ten* and *no surprises by interview fifteen to twenty*.
- For existing-customer research, recruit deliberately across light/heavy users and recent/long-tenure users. Heavy long-tenure users will dominate if recruitment is left to convenience.

## Pre-Interview Setup

- Write the hypothesis at the top of the interview guide. The interviewer must know what would falsify it before the conversation starts.
- Decide one *behaviour-of-the-past* anchor per cycle: a recent, specific event you will probe in detail.
- Keep the *scripted* portion to a handful of prompts — typically the same handful you reuse across projects. The interviewer is the instrument; long scripts produce shallow probing because the interviewer is steering instead of listening.
- Use a notes template with eight to ten blank lines under each scripted question so notes go directly into the structure during the call.
- Two interviewers when feasible: one leads, one notes verbatim quotes and cues. Switch roles between sessions to avoid one person becoming the team's only interviewer.

## The Five Reusable Question Patterns

Adapt the wording, but every cycle should include these five patterns:

1. **Procedural ("Tell me about how you ...")** — opens with a current activity, not the proposed solution. *"Tell me about how you handle expense reports today."* Forces the participant to reconstruct steps and reveals the real workflow, including its workarounds.
2. **Recent-event ("Tell me about the last time you ...")** — anchors a specific episode. *"Tell me about the last time you needed feedback on a document from a coworker."* Specific events produce concrete detail; abstract questions produce platitudes.
3. **Workaround probe** — *"What were you doing before that, and why did you switch?"* Reveals the cost of the existing solution and the trigger that made the customer act.
4. **Magic-wand ("If you could wave a magic wand and change anything ...")** — frees the participant from feasibility constraints. The literal answer is rarely buildable, but the answer reveals the underlying frustration. Use late in the interview, after the participant has already described actual behaviour.
5. **Generic-parts** — break a familiar activity into smaller pieces and ask whether each piece could be done differently. Defamiliarises taken-for-granted steps that the participant otherwise would not mention because "that's just how it is."

Aim for one custom question per project layered on top of these five; resist the urge to build a brand-new script.

## Open the Interview, Then Shut Up

After the framing and the first procedural question, stop talking. Look at the clock and wait the full sixty seconds before saying another word. The pause is uncomfortable, which is exactly why it works; participants fill silence with the detail you wanted. Most under-performing interviews are interviewers who could not tolerate a ten-second pause.

After the participant has answered, respond with conversational prompts rather than fresh questions: *"Tell me more about that," "What happened next," "Why did you do it that way?"* These do not steer; they keep the participant talking.

## Listen for Five Decision Factors

When the participant is talking, the interviewer's mental checklist is not "have I asked all my questions" but "do I have evidence on each of these factors?":

- **Behaviour** — what they actually did, with sequence and frequency.
- **Constraints** — what they cannot change (budget, policy, hierarchy, taken-for-granted limits).
- **Workarounds** — what they did instead, and at what cost in time, money, and effort.
- **Triggers** — the event that made this matter now rather than last month.
- **Adjacent factors** — the *how, why, when, and with whom* surrounding the action. These are the root causes that ultimately make or break a deliverable.

## Questions to Avoid

- *"Would you use a feature that ..."* — produces optimism, no behavioural signal.
- *"Would you pay for ..."* — produces stated willingness, not commitment.
- Asking about hypothetical future situations the participant has not actually experienced.
- Asking the participant to design the product. They will, and the answer will be misleading.
- Compound questions — *"Tell me about how you do X and what you wish was different about it."* Split into two.

## Steering Without Leading

You are guiding the conversation; you are not interrogating. Phrase questions as objectively as possible and prompt for personal, subjective responses. *"How did that go?"* is better than *"Was that frustrating?"* (which plants the answer).

When the participant veers off-topic, do not yank them back; bridge: *"Earlier you mentioned X — can we go back to that?"* This preserves rapport and surfaces topics they care about that the script missed.

## Recognising Validation In Real Time

A hypothesis is moving toward validation when, across multiple interviews, you hear unprompted descriptions of:

- The same problem, in the participants' own words.
- Concrete workarounds (often the same two or three).
- Money or time already spent attempting to fix it.
- A specific recent trigger that made it acute.

You should know after roughly five interviews whether at least one participant is genuinely excited; if no one is excited by interview five, the hypothesis is likely already invalidated. After ten interviews, patterns should be visible. After fifteen to twenty, surprises stop arriving and the cycle is done.

## Capturing What You Heard

- Verbatim quotes anchor later debriefs more reliably than paraphrased summaries.
- Tag each note with the participant's segment, the question pattern that elicited it, and whether it is *behavioural* or *stated* signal.
- Within an hour of each interview, write a one-paragraph synthesis: pattern observed, signal class, surprises, candidate threshold movements.
- After every cycle, share back what you heard with existing customers when the segment allows it — closing that loop produces correction signal that the interview itself missed.

## Source Grounding

- Alvarez's reusable five-question script (Tell me about how, Tell me about the last time you, magic wand, etc.) and the deliberate sixty-second pause.
- The decision-factor checklist (constraints, workarounds, triggers, adjacent factors) used to steer probing.
- Taken-for-granted (sociological) assumptions and McCaffrey's generic-parts technique to surface them.
- Behaviour-of-the-past anchoring instead of hypothetical future questioning.
- The 5/10/15-20 cadence for excitement, patterns, and saturation.
- Closing the loop by summarising findings back to existing customers.
