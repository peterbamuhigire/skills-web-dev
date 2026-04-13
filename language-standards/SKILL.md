---
name: language-standards
description: Language and tone standards for all written content across 3 languages
  — English (British, East African), French (Francophone African), and Kiswahili (East
  African standard). Enforces authentic, culturally appropriate, professional communication...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Language Standards — Multi-Language Tone & Grammar

<!-- dual-compat-start -->
## Use When

- Language and tone standards for all written content across 3 languages — English (British, East African), French (Francophone African), and Kiswahili (East African standard). Enforces authentic, culturally appropriate, professional communication...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `language-standards` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
All website copy, headings, CTAs, descriptions, and microcopy must follow this style guide for their respective language. Cross-cutting standard — applied throughout every content-writing step.

## Core Principles (All Languages)

1. **Clear and direct.** Sentences are straightforward, grammatically careful, logically structured.
2. **Formal and respectful.** Politeness is essential. Communication shows courtesy and humility.
3. **No excessive marketing language.** Avoid drama, exaggeration, slang.
4. **Professionally indirect.** Soften directives with courteous phrasing.
5. **Measured confidence.** Confident without arrogance.
6. **Culturally authentic.** Respect regional norms, preferences, sensitivities.

---

# ENGLISH (en) — British English, East African Professional Standard

## Core Characteristics

1. **British English spelling** throughout.
2. **East African tone** — formal, respectful, professionally courteous (Uganda, Kenya, Tanzania blend).
3. **Measured and confident** without arrogance or dramatic language.
4. **Logical sentence structure** — no fragments or telegram-style copy.
5. **Progressive tense preference** — use simple present or past over continuous tenses. "The company plans to expand" not "The company is planning to expand." Simple tenses are more direct and authoritative.
6. **Consistent verb tense** — do not switch tenses within a section. If you begin in present, stay present throughout that block. Mixing past and present within the same thought signals uncertainty.

## British English Spelling

Always use British spelling:

| Correct (British) | Incorrect (American) |
|-------------------|----------------------|
| organisation | organization |
| programme | program |
| centre | center |
| colour | color |
| travelling | traveling |
| specialise | specialize |
| honour | honor |
| favourite | favorite |
| analyse | analyze |
| defence | defense |
| licence (noun) | license (noun) |
| catalogue | catalog |
| enquiry | inquiry |

## Dates and Numbers

- **Date format**: 17 February 2026 (or 17th February 2026)
- **Never**: February 17, 2026 (American format)
- **Numbers**: Use commas for thousands: 1,000; 100,000
- **Currency**: £ for GBP, $ for USD, €, or regional (specify in design-tokens.md)

## Tone by East African Country Context

Adjust tone slightly based on client location. Use Neutral East African when no country is specified.

| Country | Tone | Key marker |
|---------|------|------------|
| **Uganda** | Warm, relational, appreciative | Frequent "kindly", emphasis on harmony: "We highly appreciate your support. Kindly be informed…" |
| **Kenya** | Confident, business-oriented, efficient | Clear timelines, professional firmness: "Please share the signed agreement by Friday, 21 February 2026." |
| **Tanzania** | Calm, measured, conservative | Patient rhythm, influenced by Kiswahili patterns: "We kindly request your guidance. We shall revert shortly." |
| **Neutral (default)** | Balanced blend | Use when no country is specified |

## Courteous Phrases (English)

Natural and expected in East African business English:

- Kindly find attached…
- We kindly request…
- Please be advised that…
- We would like to inform you…
- Thank you for your continued support.
- We look forward to your response.
- We appreciate your partnership.
- Should you require any further clarification, please do not hesitate to contact us.
- Yours faithfully, / Yours sincerely,

## Vocabulary Standards (English)

### Preferred Professional Words
- facilitate, implement, undertake, liaise, coordinate
- engage, support, enhance, review, confirm
- advise, revert (widely accepted in East Africa, meaning "respond")
- significant, important, strategic, beneficial, valuable

### Words to Avoid
Never use exaggerated marketing language:

| Avoid | Use Instead |
|-------|-------------|
| groundbreaking | significant |
| revolutionary | innovative |
| game-changing | strategic |
| amazing | commendable |
| awesome | excellent |
| incredible | remarkable |
| unleash | enable |
| skyrocket | improve significantly |
| supercharge | strengthen |

Also avoid: American slang (FYI, ASAP, BTW), dramatic emotional tone, excessive exclamation marks.

Instead of abbreviations, write in full: "Please respond as soon as possible."

### Assertive Language (All Languages)

Hedging language communicates uncertainty. If you're not sure you're any good, how can prospects be? Replace weak phrasing with confident, assertive alternatives:

| Hedging (weak) | Assertive (strong) |
|---------------|-------------------|
| Feel free to reach out | Contact me / Get in touch |
| In case you're interested | Interested? Contact me |
| Perhaps we can work together | Let's work together |
| Maybe we're a good fit | Add a "Who is this for?" section |
| We might be able to help | We can help |
| It could potentially improve | It improves |

Additional: cut qualifiers before statements — "We believe this will…" → "This will…", "This could help…" → "This helps…", "You might want to consider…" → [give the recommendation directly].

This applies across all three languages. In French: "N'hésitez pas à nous contacter" is acceptable (culturally standard), but avoid excessive hedging like "Il serait éventuellement possible de...". In Kiswahili: use direct invitations ("Wasiliana nasi" not "Labda unaweza kuwasiliana nasi").

### Condescending Phrases Ban (All Languages)

Never use these patterns in any language:
- **"Research suggests that..."** — Which research? What niche? What size businesses? Too vague to be credible. Only cite research if it features your target audience and their specific problems.
- **"If you're a business owner..."** / "Si vous êtes un entrepreneur..." / "Kama wewe ni mfanyabiashara..." — If you know your audience IS business owners, address them directly. Don't do the "if" dance.

### AI Language Avoidance (All Languages)

AI-generated text has recognisable vocabulary and patterns. Every piece of content must pass as entirely human-written.

**Tier 1 — Banned words (instant AI tells):** delve, tapestry, landscape (as metaphor), multifaceted, testament, realm, harness, leverage, synergy, embark, navigate (as metaphor), foster, beacon, forge, unleash, pivotal, paramount, robust, vibrant, bolster, seamless, holistic, curate, resonate, underscore, showcase

**Tier 2 — Overused by AI (use sparingly, never in headlines):** compelling, captivating, cutting-edge, game-changer, revolutionary, transformative, innovative, streamline, empower, unparalleled, elevate, ignite, safeguard, enduring, seamless, holistic, curate, resonate, underscore, showcase

**Tier 3 — Flagged in combination (fine alone, AI-tell together):** crucial, facilitate, enhance, ensure, enable, encourage, essential, navigate, compelling, drive, embodies, emphasises. Rule: no more than one Tier 3 word per paragraph.

**Banned phrases:** "In today's fast-paced world", "It's important to note", "In the realm of", "Embark on a journey", "Game-changer", "Treasure trove", "Digital landscape", "Ever-evolving", "Not only X but also Y" (overused), "X isn't just Y; it's Z", "From X to Y, [subject] has..." (listicle pattern), "Whether you're [X] or [Y]..." (false inclusivity)

**Banned structural patterns:** Uniform sentence lengths (vary deliberately), "Furthermore/Moreover/Additionally" as paragraph openers, excessive em dashes (max 2 per article), three-item lists in every paragraph, present participial openers ("Leveraging our...", "Fostering an environment...")

**Required human markers:** Vary sentence length (mix 4-word and 30-word sentences), take clear positions ("I recommend" not "One might consider"), use the client's own vocabulary from their docs, include strategic contractions (2-4 per 500 words in English)

See `blog-writer/references/human-voice-standards.md` for the full blacklist with replacements, detailed techniques, and Voice DNA extraction process.

---

## Redundant Phrases (All Languages)

Delete constructions where one word does the full job: *close proximity* → proximity, *consensus of opinion* → consensus, *free gift* → gift, *end result* → result, *future plans* → plans, *past history* → history, *refer back* → refer, *revert back* → revert, *advance warning* → warning, *repeat again* → repeat, *exact same* → same. Full list in `blog-writer/references/editorial-standards.md`.

---

## The "Because" Principle (All Languages)

"Because" is the most persuasive connector in professional writing (Cialdini research: giving any reason after "because" dramatically increases reader compliance). Apply in CTAs, headlines, and persuasive paragraphs: "Register today — because the first cohort fills fast." In French: *parce que* or *car*. In Kiswahili: *kwa sababu*. Full guidance in `content-writing/SKILL.md`.

## English CTAs and Button Text

Apply respectful tone to buttons and UI text:

| Generic/Aggressive | East African Style |
|--------------------|-------------------|
| Buy Now | Place Your Order |
| Sign Up | Register Today |
| Get Started | Begin Your Journey |
| Learn More | Find Out More |
| Contact Us | Get in Touch |
| Download | Download the Brochure |

---

# FRENCH (fr) — Francophone African Professional Standard

## Core Characteristics

1. **Formal francophone African French** — not Québécois, not Belgian variants.
2. **Respectful and courteous** — professionalism with warmth.
3. **Standard French grammar and conventions**.
4. **Vous (formal)** throughout all professional communication — never "tu".
5. **Culturally appropriate** for Côte d'Ivoire, Cameroon, Senegal, DRC, Gabon.

## French Spelling and Grammar

Use standard French orthography:
- Accent marks required: é, è, ê, ë, à, ù, ç, œ, æ
- Double-check diacritical marks (many African translators omit them)
- UTF-8 encoding mandatory

### Apostrophes in Astro JSX Templates (French, Swahili, all languages)

**CRITICAL:** Single-quoted JS strings inside Astro JSX expressions (`.astro` template section) CANNOT contain straight apostrophes (`'`). This breaks the build because the apostrophe terminates the string early.

**Rules for any text containing apostrophes (e.g. French `d'`, `l'`, `n'`, `qu'`; Swahili `ng'`):**
1. **Use double-quoted strings** for any JS string literal that contains an apostrophe: `"d'excellence"` not `'d\'excellence'`
2. **Never use `\u2019` escape sequences** — Astro's template compiler may not handle them correctly
3. **Never use backslash-escaped apostrophes** (`\'`) in JSX template expressions — they work in frontmatter JS but fail in template JSX
4. **HTML text content is fine** — apostrophes in regular HTML `<p>d'excellence</p>` work without escaping
5. For JSX expression strings that need both `"` and `'`, use template literals: `` `string with ' and "` ``

### Verb Conjugation
- Use **vous** for all formal communication (not tu)
- Example: "Veuillez remplir le formulaire" (not "Remplis le formulaire")
- Imperative form: "Veuillez" + infinitive for politeness

### Gender Agreement
All adjectives and past participles must agree with gender:
- "La page est complétée" (feminine)
- "Le service est complété" (masculine)
- "Les pages sont complétées" (feminine plural)

## French Dates and Numbers

- **Date format**: 17 février 2026 (or 17 février 2026)
- **Month names**: Lowercase (février, not Février)
- **Numbers**: Use space or period for thousands: 1 000 or 1.000 (not 1,000)
- **Decimal separator**: Comma (not period): 3,14 (not 3.14)
- **Currency**: Franc CFA (FCFA), Euro (€), or specified in design-tokens.md

## Formal Registers and Politeness

### Standard Openings
- Madame, Monsieur,
- Chère Madame, Cher Monsieur,
- Greetings,

### Standard Closings
- Cordialement, (warm, professional)
- Respectueusement, (respectful)
- Avec mes meilleures salutations,
- Veuillez agréer l'expression de nos salutations distinguées.

### Courtesy Phrases (French)

- Nous vous prions de…
- Veuillez… (imperative form with "vous")
- Merci de votre attention.
- Nous apprécions votre partenariat.
- N'hésitez pas à nous contacter.
- Nous vous remercions de votre soutien continu.
- Nous attendons avec intérêt votre réponse.
- Si vous avez besoin de précisions supplémentaires, veuillez nous contacter.

## French Vocabulary Standards

### Preferred Professional Terms
- Faciliter, mettre en œuvre, entreprendre, coordonner
- Engager, soutenir, améliorer, examiner, confirmer
- Conseiller, informer, communiquer
- Significatif, important, stratégique, bénéfique, précieux

### Words to Avoid (Marketing Hype)

| Avoid | Use Instead |
|-------|-------------|
| révolutionnaire | innovant |
| "game-changing" | stratégique |
| incroyable | remarquable |
| génial | excellent |
| dingue | étonnant |
| Libérez le pouvoir | Activez la capacité |

### Francophone African Terminology

Use terms understood across francophone Africa (not Canada-specific, not France-specific):
- Budget (not "subvention")
- Entreprise (company, not "compagnie")
- Personnel (staff, not "employés" alone)
- Client (customer/client, standard everywhere)
- Formation (training, widely used)

## French CTAs and Button Text

| English | French (Formal) |
|---------|-----------------|
| Sign Up | S'inscrire |
| Register | Créer un compte |
| Contact Us | Nous contacter |
| Learn More | En savoir plus |
| Submit | Soumettre |
| Download | Télécharger |
| Place Your Order | Passer votre commande |
| Get Started | Commencer maintenant |

## French-Specific Considerations

### In-Country Reviewer Required
All French content must be reviewed by a native francophone speaker from the target market (Côte d'Ivoire, Cameroon, Senegal, DRC, Gabon). Send for review before publishing.

### Text Expansion
French is typically 20–40% longer than English. Design for 1.3x expansion:
- Buttons must accommodate longer labels
- Navigation items must wrap gracefully
- Form labels must not overlap fields

### Regional Variations
Avoid country-specific terms unless relevant:
- Use neutral francophone African vocabulary
- Avoid France-centric references
- Avoid Canadian (Québécois) terminology

### Francophone Africa Geographic Scope

**CRITICAL RULE:** French content must target Francophone Africa broadly — NOT just East Africa or Uganda.

The French language version of any website should be written and positioned for the entire Francophone African market:

**Target countries (examples, not exhaustive):**
Côte d'Ivoire, Cameroun, Sénégal, RDC (Congo-Kinshasa), Guinée, Mali, Burkina Faso, Gabon, Niger, Bénin, Togo, Madagascar, Mauritanie, Djibouti, Comores

**Financial institutions to reference (where relevant):**
- BCEAO (Banque Centrale des États de l'Afrique de l'Ouest) — West Africa
- BEAC (Banque des États de l'Afrique Centrale) — Central Africa
- Ecobank, BOA (Bank of Africa), UBA, Orabank, BGFI
- BNI (Côte d'Ivoire), Société Générale Afrique
- BOAD (IFD Ouest-africaine), AFC (Africa Finance Corporation)

**Business regulatory frameworks to use:**
- OHADA (Organisation pour l'Harmonisation en Afrique du Droit des Affaires)
- SYSCOHADA (accounting standards)
- FCFA currency (BCEAO/BEAC zone)

**What to AVOID in French content:**
- Ugandan-specific references: UDB, Centenary Bank, Stanbic Uganda, DFCU
- East Africa-only phrasing: "Afrique de l'Est" as the primary qualifier
- Assuming the French reader is in Uganda or East Africa

**What to DO:**
- Use "Afrique francophone" as the geographic qualifier
- Reference institutions and frameworks relevant across West and Central Africa
- Use examples from Côte d'Ivoire, Sénégal, Cameroun, DRC, Guinée
- SEO: target "plan d'affaires Côte d'Ivoire", "consultant Sénégal", "financement entreprise Cameroun", "business plan Afrique francophone"

**When a client is specifically in East Africa:**
If the client is Uganda-based, English pages handle the Ugandan/East African audience. The French pages reach the francophone African audience — these are different markets.

---

# KISWAHILI (sw) — East African Standard

## Core Characteristics

1. **Standard East African Kiswahili** — not regional dialects (Mombasa, Zanzibar variants).
2. **Formal/respectful register** throughout professional communication.
3. **Humble and relationship-focused** — Swahili culture emphasizes harmony.
4. **UTF-8 encoding** for proper character rendering.
5. **Simple sentence structure** — Kiswahili clarity values straightforward expression.

## Kiswahili Grammar and Structure

### Standard Kiswahili Conventions
- **Subject prefixes**: Proper noun classes (m-/ba, ki-/vi, n-, li-)
- **Verb conjugation**: Tense markers (-li-, -na-, -ta-, -ki-, -a)
- **Adjective agreement**: Must agree with noun class
- **No gender distinction** in pronouns (yeye = he/she)

### Formal Register (Habari Rasmi)

Use formal register in all professional communication:
- Avoid slang (sheng, Nairobi street language)
- Use full words (hakuna = do not have, not "hakuna matata")
- Respectful pronouns and address forms

### Tense Selection
- **Present habitual**: -na- (Anataka = He/she wants)
- **Near future**: -ta- (Atakuja = He/she will come)
- **Past completed**: -li- (Alifika = He/she arrived)
- **Conditional**: -ki-, -ngali (Akija = if he/she comes)

## Kiswahili Dates and Numbers

- **Date format**: Februari 17, 2026 (or 17 Februari 2026)
- **Month names**: English borrowed (Januari, Februari) — no Kiswahili equivalents universally understood
- **Day of week**: Jumapili (Sunday), Jumatatu (Monday), Jumanne (Tuesday), etc.
- **Numbers**: Use spaces for thousands: 1 000 (not 1,000)
- **Currency**: Shilingi (Sh, KES for Kenya), or specified in design-tokens.md

## Kiswahili Courtesy and Formality

### Standard Openings (Business)
- Habari yako?  (How are you? — formal)
- Tunataka kuwashukuru…  (We want to thank you…)
- Tunakuomba… (We kindly request…)

### Respectful Phrases (Kiswahili)

- **Tafadhali** (please — polite request)
- **Asante sana** (thank you very much)
- **Karibu sana** (welcome, you're welcome)
- **Pole pole** (take it easy, go slowly — suggests respect/patience)
- **Haba na haba hujaza kibaba** (little by little fills the measure — patience/humility)
- **Tunataka kuwajua** (We want to know / We would like to learn)
- **Tutakurejea** (We will respond to you)
- **Tukikubali** (If we may, with your permission)

### Closings
- **Kwa heshima** (with respect)
- **Wakati mwingine** (another time / we hope to hear from you)
- **Tunatumaini kuongea nayo upya** (We hope to speak with you again)

## Kiswahili Vocabulary Standards

### Preferred Professional Terms
- **Kusimamia** (to manage, oversee)
- **Kutekeleza** (to implement, execute)
- **Kushiriki** (to participate, engage)
- **Kusaada** (to help, support)
- **Kuboresha** (to improve, enhance)
- **Kupatiana** (to agree, coordinate)
- **Kuhakiki** (to verify, confirm)
- **Kuarifu** (to inform, notify)
- **Kujifunza** (to learn)
- **Muhimu** (important, significant)
- **Faida** (benefit, advantage)
- **Lengo** (goal, objective)

### Words to Avoid (Too Colloquial)
- Slang/sheng — use formal Kiswahili
- Hyperbolic marketing words
- English insertions without Kiswahili alternative available

## Kiswahili CTAs and Button Text

| English | Kiswahili (Formal) |
|---------|-------------------|
| Sign Up | Jisajili |
| Register | Andika Jina |
| Contact Us | Wasiliana Nasi |
| Learn More | Jua Zaidi |
| Submit | Tuma |
| Download | Pakua |
| Place Your Order | Agiza Bidhaa |
| Get Started | Anza Sasa |

## Kiswahili-Specific Considerations

### In-Country Reviewer Required
All Kiswahili content must be reviewed by a native Kiswahili speaker from East Africa (Kenya, Tanzania, or Uganda). Regional variants exist; ensure reviewer is from target market.

### Text Expansion
Kiswahili is typically 10–30% longer than English. Design for 1.2x expansion:
- Buttons must flex for longer labels
- Navigation items must wrap gracefully
- Form labels must have clear spacing

### No Dialects
- Use standard East African Kiswahili
- Avoid Mombasa Swahili (maChinwali features)
- Avoid Zanzibari Swahili (historical variants)
- Avoid regional slang or sheng (Nairobi street language)

### Relationships and Harmony
Kiswahili communication culture emphasizes relationships:
- Lead with greetings and acknowledgment
- Use plural forms to show respect (sisi = we, kuambia mtu = speak to a person)
- Avoid direct criticism or bluntness
- Always acknowledge the relationship before asking for action

---

# When This Skill Applies

**Cross-cutting** — applies to all visible website text, meta descriptions, alt text, form labels, error messages, email templates, and microcopy in all enabled languages.

**Extended reference:** `references/business-english-advanced.md` — phrase banks (meetings, presentations, apologies, formal correspondence), 80 ESL grammar rules, register-switching guidance, and anti-jargon rewrites.

## Integration with Other Skills

- **i18n**: Determines which language versions are built
- **page-builder**: Applies language standards when creating content
- **seo**: Uses language standards for meta tags, titles, descriptions
- **sector-strategies**: Industry-specific tone within language standards

---

# Enforcement Checkpoints

Before publishing any page, verify:

- [ ] **English pages**: British spelling, East African tone, no marketing hype
- [ ] **French pages**: Formal French, vous throughout, francophone African vocabulary, reviewed by francophone
- [ ] **Kiswahili pages**: Standard Kiswahili, formal register, no slang, reviewed by East African native speaker
- [ ] **All pages**: No truncation or text overflow in any language
- [ ] **All pages**: Grammatically correct, properly punctuated, culturally appropriate
- [ ] **All pages**: CTAs use respectful, inviting language (not aggressive)

## Language-Specific Reviewers

- **English**: East African professional (optional native review; standards in this guide)
- **French**: Native francophone speaker from Côte d'Ivoire, Cameroon, Senegal, DRC, or Gabon
- **Kiswahili**: Native Kiswahili speaker from Kenya, Tanzania, or Uganda

All translations reviewed by in-country professionals before publishing.
