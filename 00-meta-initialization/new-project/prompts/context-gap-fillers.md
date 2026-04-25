# Context-Gap Fillers

When the validation kernel reports `[CONTEXT-GAP: <topic>]`, paste the matching prompt below into a fresh assistant chat. Edit the placeholders. Drop the result into `_context/<file>.md`.

## stakeholders

> "I am writing the Stakeholders section of an SRS for a {one-line project description}. The deployment is in {country/region} for {industry}. List 6-10 distinct stakeholder roles, each with: a one-sentence role description, the primary outcome they want, and one constraint they impose on the system. Format as a markdown bullet list. Use the **Bold-then-detail** convention."

## features

> "I am writing the Features section of an SRS for {one-line project description}. The Vision is: {paste vision.md content}. List 8-15 features. Each feature: an `F-N` ID, a 4-word name, one driving stakeholder (must match a stakeholder we already wrote), one measurable success outcome. No vague adjectives."

## glossary

> "I am writing the Glossary for an SRS in the {industry} domain operating in {country/region}. Identify every domain-specific term used in the following text and provide an unambiguous, single-sentence definition for each. Use **Term:** definition format. Source: {paste vision.md + features.md}."

## quality-standards

> "Generate the Quality Standards file for an SRS that targets the following compliance frameworks: {list, e.g. Uganda DPPA 2019, PCI-DSS v4.0}. For each framework, list 3-5 measurable quality attributes the system must meet, with the framework clause referenced in brackets. No vague adjectives."

## methodology

> "We are using the {Waterfall|Agile|Hybrid} methodology. The change-control body is {name}. Sprint cadence: {N weeks, or N/A}. Baseline lock cadence: {date or condition}. Generate methodology.md."
