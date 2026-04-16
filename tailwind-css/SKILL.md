---
name: tailwind-css
description: Tailwind CSS v3 utility-first styling — setup, responsive design, dark
  mode, event/state modifiers, tailwind.config.js customization (colors, spacing,
  screens, plugins), @apply and @layer directives, flexbox/grid classes, and best
  practices. Use...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Tailwind CSS

<!-- dual-compat-start -->
## Use When

- Tailwind CSS v3 utility-first styling — setup, responsive design, dark mode, event/state modifiers, tailwind.config.js customization (colors, spacing, screens, plugins), @apply and @layer directives, flexbox/grid classes, and best practices. Use...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `tailwind-css` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Theme + responsive audit | Markdown doc reviewing tokens, breakpoint coverage, and dark-mode parity | `docs/web/tailwind-theme-audit.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Utility-first CSS framework. Style in HTML — no custom CSS required.

## Setup

```bash
# Next.js (includes Tailwind automatically)
npx create-next-app@latest my-app --typescript --tailwind

# Standalone (any project)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**tailwind.config.js** (minimum):

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,jsx,ts,tsx}'],
  theme: { extend: {} },
  plugins: [],
};
```

**input.css**:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**CDN (prototyping only):**

```html
<script src="https://cdn.tailwindcss.com"></script>
```

---

## Core Philosophy

Tailwind replaces custom CSS with composable utility classes directly on elements.

```html
<!-- Traditional CSS approach -->
<div class="mainBlock">…</div>

<!-- Tailwind utility-first approach -->
<div class="bg-gray-500 p-2 w-72 rounded border border-gray-900 flex">…</div>
```

**Utility classes vs inline styles:**
- Utility classes are part of a design system — reusable, consistent
- Utility classes support responsive breakpoints and state variants
- Utility classes handle hover, focus, dark mode — inline styles cannot

---

## Responsive Design

Mobile-first breakpoints. Apply a prefix to target that breakpoint **and above**.

| Prefix | Min-width | Equivalent CSS |
|--------|-----------|----------------|
| (none) | 0px | Always applies |
| `sm:`  | 640px | `@media (min-width: 640px)` |
| `md:`  | 768px | `@media (min-width: 768px)` |
| `lg:`  | 1024px | `@media (min-width: 1024px)` |
| `xl:`  | 1280px | `@media (min-width: 1280px)` |
| `2xl:` | 1536px | `@media (min-width: 1536px)` |

```html
<!-- Pink on mobile, red sm+, green md+, gray lg+, blue xl+ -->
<div class="bg-pink-500 sm:bg-red-500 md:bg-green-500 lg:bg-gray-500 xl:bg-blue-500">
```

**Target a range** (apply only between breakpoints):

```html
<div class="sm:max-lg:bg-red-500">  <!-- only sm to lg -->
<div class="sm:max-md:flex">        <!-- flex only at sm width -->
```

---

## Event and State Modifiers

Format: `{modifier}:{utility-class}`

```html
<!-- hover, active, focus -->
<button class="bg-green-300 hover:bg-blue-400 active:bg-red-500">Click</button>

<!-- Multiple on same event -->
<button class="hover:bg-green-500 hover:text-white">Hover me</button>

<!-- focus -->
<input class="focus:outline-none focus:ring-2 focus:ring-blue-500" />

<!-- disabled -->
<input disabled class="disabled:bg-gray-200 disabled:cursor-not-allowed" />

<!-- required / invalid -->
<input required class="required:bg-red-50 invalid:border-red-500" />

<!-- first-child / last-child -->
<div class="first:font-bold last:italic">…</div>

<!-- odd / even children -->
<div class="odd:bg-green-100 even:bg-blue-100">…</div>

<!-- group — parent hover affects children -->
<div class="group">
  <p class="text-gray-600 group-hover:text-black">Text changes on parent hover</p>
</div>
```

---

## Dark Mode

**System-controlled (default):**

```html
<div class="bg-white dark:bg-gray-900 text-black dark:text-white">
```

**Manual toggle (class-based):**

```js
// tailwind.config.js
module.exports = { darkMode: 'class', ... }
```

```html
<!-- Add/remove 'dark' class on root element via JS -->
<html id="root" class="dark">
  <div class="bg-white dark:bg-gray-900">…</div>
</html>
```

```js
// Toggle dark mode
document.getElementById('root').classList.toggle('dark');
```

---

## Style Reuse — @apply and @layer

When repeating the same set of utility classes across many elements, extract to a component class.

```css
/* input.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition;
  }
  .card {
    @apply bg-white rounded-xl shadow-md p-6;
  }
}

@layer base {
  h1 { @apply text-2xl font-bold; }
  h2 { @apply text-xl font-semibold; }
  a  { @apply text-blue-600 underline; }
}
```

```html
<button class="btn-primary">Save</button>
<div class="card">…</div>
```

**Rule:** Use `@apply` sparingly — prefer utility classes in JSX components.
Use it for global base styles (headings, links) and frequently repeated component patterns.

---

## tailwind.config.js — Customisation

### Custom Colors

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        'brand':  '#1DA1F2',
        'brand-dark': '#0c85d0',
        'silver': '#C0C0C0',
      },
    },
  },
};
```

Usage: `bg-brand`, `text-silver`

**Color with shades:**

```js
colors: {
  'primary': {
    50:  '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6',
    900: '#1e3a5f',
  },
}
```

Usage: `bg-primary-500`, `text-primary-900`

**Arbitrary color (no config needed):** `bg-[#1DA1F2]`

### Custom Screens (Breakpoints)

```js
theme: {
  screens: {
    'sm': '640px', 'md': '768px', 'lg': '1024px',
    'xl': '1280px', '2xl': '1536px',
    '3xl': '1800px',          // custom extra-large
    'mobile': '480px',        // custom named breakpoint
  },
},
```

### Custom Spacing

```js
theme: {
  extend: {
    spacing: {
      '18': '4.5rem',
      '72': '18rem',
      '84': '21rem',
    },
  },
},
```

### Disable Core Plugin

```js
module.exports = { corePlugins: { container: false, preflight: false } }
```

### Class Safelisting

Add classes that may not appear in scanned files (e.g., dynamically constructed):

```js
module.exports = { safelist: ['bg-red-500', 'text-3xl', 'lg:text-4xl'] }
```

### Plugins

```bash
npm install @tailwindcss/typography @tailwindcss/forms
```

```js
plugins: [
  require('@tailwindcss/typography'),   // .prose classes for rich text
  require('@tailwindcss/forms'),        // styled form controls
],
```

Usage: `<article class="prose lg:prose-xl">`, `<input class="form-input" />`

---

## Layout Quick Reference

```html
<!-- Container (centers content at breakpoint) -->
<div class="container mx-auto px-4">

<!-- Flexbox -->
<div class="flex items-center justify-between gap-4">
<div class="flex flex-col gap-2">
<div class="flex flex-wrap">

<!-- Grid -->
<div class="grid grid-cols-3 gap-6">
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
<div class="col-span-2">             <!-- span 2 columns -->

<!-- Position -->
<div class="relative">
  <div class="absolute top-0 right-0">badge</div>
</div>

<!-- Overflow -->
<div class="overflow-hidden">
<div class="overflow-x-auto">
```

---

## Typography Quick Reference

```html
<!-- Font size: text-xs text-sm text-base text-lg text-xl text-2xl … text-9xl -->
<h1 class="text-4xl font-bold tracking-tight">
<p class="text-base text-gray-600 leading-relaxed">

<!-- Font weight -->
<!-- font-thin font-light font-normal font-medium font-semibold font-bold font-extrabold -->

<!-- Text color: text-{color}-{shade} -->
<p class="text-gray-900 dark:text-gray-100">

<!-- Text align -->
<p class="text-center">  <p class="text-right">

<!-- Truncate long text -->
<p class="truncate">     <!-- single line -->
<p class="line-clamp-3"> <!-- 3 lines then … -->
```

---

## Spacing, Sizing, Effects

```html
<!-- Padding/Margin: p-{n} px-{n} py-{n} pt/pr/pb/pl-{n} -->
<!-- n = 0,1,2,3,4,5,6,8,10,12,16,20,24,32,40,48,64 (0.25rem each) -->
<div class="p-4 mx-auto mt-8">

<!-- Width/Height -->
<div class="w-full max-w-2xl h-screen min-h-0">
<img class="w-16 h-16 object-cover rounded-full">

<!-- Borders -->
<div class="border border-gray-200 rounded-lg">
<div class="border-2 border-blue-500 rounded-xl ring-2 ring-blue-300">

<!-- Shadow -->
<div class="shadow shadow-lg shadow-xl shadow-2xl">

<!-- Opacity -->
<div class="opacity-50 hover:opacity-100 transition">

<!-- Transitions -->
<button class="transition duration-200 ease-in-out hover:scale-105">
```

---

## Common Component Patterns

```html
<!-- Button variants -->
<button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
               active:bg-blue-800 transition disabled:opacity-50 disabled:cursor-not-allowed">
  Primary
</button>

<!-- Card -->
<div class="bg-white dark:bg-gray-800 rounded-2xl shadow-md p-6 hover:shadow-lg transition">

<!-- Badge -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs 
             font-medium bg-green-100 text-green-800">
  Active
</span>

<!-- Input -->
<input class="w-full px-3 py-2 border border-gray-300 rounded-lg 
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              dark:bg-gray-700 dark:border-gray-600 dark:text-white" />

<!-- Responsive nav (mobile stack → desktop row) -->
<nav class="flex flex-col md:flex-row gap-2 md:gap-6">
```

---

## Best Practices

| Rule | Reason |
|---|---|
| Never include CSS files in `content` config | Causes false class detection |
| Use complete class names (`bg-red-500` not `bg-${color}-500`) | Dynamic strings aren't scanned |
| Prefer `@layer components` over inline `@apply` in JSX | Keeps HTML clean for one-off reuse |
| Use `extend` not override in theme | Preserve default utilities |
| Use framework components (React, Vue) instead of HTML loops | Class strings in components = clean repetition |
| Check Tailwind v3 docs for new classes | Classes added/renamed across versions |

---

*Source: Bhat — Ultimate Tailwind CSS Handbook (BPB, 2023)*
