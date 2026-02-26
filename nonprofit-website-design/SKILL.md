---
name: nonprofit-website-design
description: "Design system and visual strategy for NGO, nonprofit, and charity websites. Covers emotional storytelling through design, trust-building visual patterns, donation conversion optimization, impact-driven layouts, nonprofit color psychology, accessibility-first design, and sector-specific patterns (environment, health, education, humanitarian, research). Use when building or reviewing any nonprofit, NGO, charity, social enterprise, or mission-driven organization website."
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline.

**Frontend Design plugin (`webapp-gui-design`):** MUST be active for all visual output. Nonprofit sites demand even MORE intentional design than commercial sites --- generic templates signal inauthenticity. Apply the interface-design exploration workflow (domain, color world, signature, defaults-to-reject) with the nonprofit sector additions below.

# Nonprofit Website Design

Nonprofit websites serve a fundamentally different purpose from commercial sites. Visitors arrive with empathy, not purchase intent. The design must channel that empathy into action --- donate, volunteer, partner, share. Every visual decision either builds trust or breaks it.

## Sections

1. [Color Psychology for Nonprofits](./references/color-psychology.md)
2. [Storytelling Through Design](./references/storytelling-design.md)
3. [Sector-Specific Patterns](./references/sector-patterns.md)

## Core Principles

### 1. Mission-First Hierarchy

The mission statement is the product. It occupies the hero. Not a tagline --- the actual human problem being solved, in language a supporter can feel.

**Hero pattern:** Emotion-first, not organization-first.
- Lead with the IMPACT: "Transforming banana farming communities" not "Welcome to BIRDC"
- Full-bleed authentic photography (never stock)
- Single primary CTA above the fold
- Statistics as social proof: "20+ years | 5,000+ farmers trained | 3 districts served"

### 2. Trust Architecture

Nonprofits must earn trust faster than commercial sites. 61% of visitors refuse online transactions when trust signals are absent.

**Trust signals (deploy all):**
- Transparent financials: link to annual reports, impact metrics
- Partner/funder logos in a trust bar
- Real team photos with names and roles
- Physical addresses and phone numbers visible (not buried)
- SSL badge near donation forms
- Awards, certifications, affiliations
- Testimonials from beneficiaries with photos

**Trust-destroying patterns (avoid):**
- Stock photography of generic "diverse hands"
- Vague impact claims without numbers
- Hidden contact information
- Outdated content (old dates, dead events)
- Broken donation flows
- Missing privacy/security indicators near forms

### 3. Emotional Design Without Manipulation

Stories are remembered 22x more than facts alone. Design must create emotional connection without exploiting suffering.

**The dignity principle:** Show people as empowered agents, not helpless victims. Before/after framing should emphasize transformation and capability, not pity.

**Visual storytelling hierarchy:**
1. Hero: one powerful image + mission statement
2. Impact numbers: concrete, specific, recent
3. Stories: 2-3 beneficiary narratives with photos
4. How it works: simple 3-step visual process
5. CTA: tied to a specific outcome ("Your $25 feeds a family for a week")

### 4. Donation Conversion Design

Optimized donation design increases conversions by up to 54%.

**Donation page rules:**
- Impact-tied amounts: "$50 provides seed stock for one farmer" not just "$50"
- Suggested amounts with one pre-selected (middle option)
- Recurring giving toggle prominent, not hidden
- Minimal form fields (name, email, card --- nothing else required)
- Progress indicator for multi-step forms
- Security badges adjacent to payment fields
- Thank-you page with share buttons and next engagement step

**CTA design:**
- High-contrast color distinct from body palette (accent color)
- Action verb + outcome: "Feed a Family" not "Donate"
- Always visible: sticky header CTA on scroll
- Multiple CTAs per long page (top, mid-story, bottom)
- Button size: minimum 44x44px touch target, visually prominent

### 5. Accessibility as Mission Alignment

Nonprofits serve everyone. Inaccessible design contradicts the mission. Target WCAG 2.2 AA minimum.

**Required:**
- Color contrast: 4.5:1 for body text, 3:1 for large text
- Alt text on every image (descriptive, not decorative labels)
- Keyboard navigation for all interactive elements
- Logical heading hierarchy (h1 > h2 > h3, no skips)
- Form labels explicitly associated with inputs
- Focus indicators visible on all interactive elements
- Captions on all video content
- Responsive: 52% of nonprofit traffic is mobile

**Color blindness safeguard:** Never convey meaning through color alone. 1 in 12 men have color vision deficiency. Use icons, text labels, or patterns alongside color.

### 6. Navigation for Multiple Audiences

Nonprofit visitors fall into distinct groups with different needs:

| Audience | Primary goal | Design response |
|----------|-------------|-----------------|
| Donors | Give money | Prominent donate button, impact proof |
| Volunteers | Give time | Events calendar, signup forms |
| Beneficiaries | Access services | Program info, contact details |
| Partners | Collaborate | About, reports, contact |
| Media | Get information | Press kit, leadership bios, photos |
| Researchers | Find data | Publications, methodology, data |

**Navigation pattern:** Max 6-7 top-level items. "Donate" gets its own CTA-styled button in the header, not a regular nav link. Consider audience-based entry points on the homepage: "I want to donate / volunteer / learn more / partner with us."

## Color Strategy for Nonprofits

See [full reference](./references/color-psychology.md) for detailed color psychology.

**Quick guide by sector:**

| Sector | Primary | Why |
|--------|---------|-----|
| Environment/Agriculture | Forest green, earth tones | Nature, growth, sustainability |
| Healthcare | Blue + white | Trust, calm, clinical competence |
| Education | Blue + warm accent | Reliability + approachability |
| Humanitarian | Warm red/orange + navy | Urgency + stability |
| Arts/Culture | Bold, vibrant, unique | Creativity, community, energy |
| Research/Science | Deep blue/green + gold | Authority, knowledge, excellence |
| Children/Youth | Bright, playful palette | Energy, optimism, safety |

**Competitive differentiation:** Charity: water uses bright yellow in a sector drowning in blue. Susan G. Komen chose pink in healthcare's sea of cool tones. Study what competitors use and consciously diverge.

**The accent color rule:** One dominant brand color + one high-contrast accent for CTAs. The accent appears ONLY on: donate buttons, primary CTAs, key headlines, email action buttons. Everywhere else, let the brand color and neutrals do the work.

## Typography for Nonprofits

**Pairing strategy:** Display font (characterful, mission-aligned) + body font (highly readable, accessible).

| Tone | Display suggestion | Body suggestion |
|------|-------------------|-----------------|
| Authoritative/Research | Slab serif or strong geometric sans | Clean humanist sans |
| Warm/Community | Rounded sans or friendly serif | Open, generous x-height sans |
| Modern/Innovative | Geometric display | Neutral grotesque |
| Traditional/Established | Classic serif | Paired serif or clean sans |
| Urgent/Activist | Bold condensed sans | Readable sans at generous size |

**Minimum sizes:** 16px body text (18px preferred for nonprofit audiences which skew older). 14px absolute minimum for any readable content. Line height 1.5-1.7 for body text.

**Readability over style:** Nonprofits communicate to broad, diverse audiences including ESL speakers. Prioritize clarity. Avoid light font weights, low-contrast text, and decorative scripts for body copy.

## Layout Patterns

### Homepage Structure (Recommended)

```
1. Hero: Full-width image + mission + primary CTA
2. Trust bar: Partner/funder logos (4-6)
3. Impact numbers: 3-4 key statistics with icons
4. Story section: 1-2 beneficiary stories with photos
5. Programs/Services: Card grid (3-4 items)
6. How to help: Donate / Volunteer / Partner paths
7. News/Events: Latest 2-3 items
8. Newsletter signup: Simple email capture
9. Footer: Contact info, social links, legal
```

### Contact Page Pattern

```
1. Hero: Warm, inviting (not corporate)
2. Contact details: Physical addresses with maps
3. Contact form: Name, email, enquiry type, message
4. Alternative contact: Phone, email, social
5. FAQ or "What to expect" section
```

### About/Impact Page Pattern

```
1. Hero: Team or field photo
2. Mission/Vision/Values: Clear, concise
3. Timeline or milestones: Visual history
4. Team section: Real photos, names, brief bios
5. Partners/Funders: Logo grid with links
6. Annual report: Download or embedded highlights
7. CTA: Join the mission
```

## Photography Direction

**Always use authentic photography.** Real people, real locations, real impact.

**Shot types needed:**
- Hero/landscape: Facility, field, or community (wide, atmospheric)
- Portrait: Team members, beneficiaries, partners (warm, dignified)
- Action: Work being done, training in progress, products being made
- Detail: Products, equipment, results (close-up, tactile)
- Event: Community gatherings, ceremonies, achievements

**Treatment:** Consistent editing across all photos. Slight warmth for community-focused orgs. Natural, unforced compositions. Never over-processed or HDR. Dark overlay (10-20% opacity) on hero images for text readability.

**Photo bank workflow:** Source from organizational events. Get permissions. Name files descriptively. Store originals in `photo-bank/`, processed versions in `src/assets/images/`.

## Micro-Interactions

Use sparingly but intentionally:
- Scroll-triggered stat counters (numbers animate up)
- Hover reveals on team/story cards (subtle lift + shadow)
- Progress bars on campaign/fundraising goals
- Parallax on hero images (subtle, 0.3-0.5 factor)
- Staggered fade-in for card grids on scroll

**Performance rule:** No interaction should delay first contentful paint. Use IntersectionObserver for scroll triggers. CSS animations over JS where possible. Respect `prefers-reduced-motion`.

## Multilingual Considerations

Many nonprofits serve multilingual communities:
- Language switcher: visible in header, flag-free (use language names)
- RTL support if serving Arabic/Hebrew communities
- Content parity: all languages get the same quality, not just translated text
- URL structure: `/en/`, `/fr/`, `/sw/` prefixes with hreflang tags
- Cultural sensitivity: imagery and tone appropriate per audience

## Performance

Nonprofit audiences often have slower connections (rural areas, developing countries):
- Target: < 3s first contentful paint on 3G
- Images: WebP/AVIF with responsive `srcset`, lazy loading below fold
- Fonts: `font-display: swap`, subset to used characters
- CSS: Purge unused styles, critical CSS inline
- JS: Minimal, defer non-essential, no heavy frameworks for static content

## The Nonprofit Design Mandate

Before shipping, run these checks:

1. **The empathy test:** Does a first-time visitor understand the mission within 5 seconds?
2. **The trust test:** Would you give this organization your credit card based on the design alone?
3. **The action test:** Is there a clear next step visible without scrolling?
4. **The dignity test:** Are beneficiaries shown as empowered, not pitiful?
5. **The accessibility test:** Can someone with low vision, motor impairment, or a screen reader use every feature?
6. **The mobile test:** Does the donation flow work flawlessly on a phone?
7. **The freshness test:** Does the site feel current, not abandoned?

If any check fails, iterate before deploying.
