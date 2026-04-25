# Fundamentals of HTML, SVG, CSS and JavaScript for Data Visualisation

**Source:** Peter Cook, *Fundamentals of HTML, SVG, CSS and JavaScript for Data Visualisation* (Leanpub, 2022).
**Scope of the book:** A primer for data people (Excel/R/Python users) who want to learn the four web languages well enough to read, modify, or build chart-oriented code. Cook explicitly defers chart construction, scales, axes, data joins, and D3 itself to his other book, *D3 Start to Finish*. This note captures Cook's content faithfully, then adds a "Beyond the book" reference for the intermediate viz patterns AI agents need.

---

## 1. The four web languages (Cook's framing)

A web data visualisation is built from four languages with very specific roles:

- **HTML** — describes the *content* (paragraphs, headings, images, the SVG container).
- **SVG** — describes *shapes* (lines, rectangles, circles, text, paths). This is what most interactive web charts are made of.
- **CSS** — describes *style and position* (colour, font, size, layout) of HTML and SVG elements.
- **JavaScript** — *manipulates* HTML/SVG, performs *computation*, and handles *interaction*.

---

## 2. HTML elements that matter for viz

Cook covers only the elements you actually need for charting. Tags come in pairs: opening `<p>`, closing `</p>`. Attributes go on the opening tag in `name="value"` form.

```html
<h1>Main heading</h1>      <!-- through <h6> -->
<ul>
  <li>List item one</li>
  <li>List item two</li>
</ul>

<img src="images/my-image.jpg" width="200px">   <!-- no closing tag -->

<div>
  <h1>Main title</h1>
  <h2>Secondary title</h2>
</div>

<svg width="800" height="600">
  <circle r="100"></circle>
</svg>
```

Cook's rule of thumb: for visualisation, headings + lists + images + `<div>` + `<svg>` is usually enough. `<div>` is the all-purpose grouping/layout block; the `<svg>` element is the canvas your chart shapes live inside, and you should always set its `width` and `height` because the default is small and shapes get clipped.

---

## 3. SVG (the heart of the book)

### 3.1 Coordinate system

`(0,0)` is the **top-left** of the `<svg>`. **x increases to the right, y increases downward.** Every SVG element needs a closing tag (`<circle></circle>`, not `<circle/>` in Cook's examples). By default lines are drawn in white, so without CSS you won't see them.

### 3.2 The six elements Cook teaches

| Element | Attributes | Notes |
|---|---|---|
| `<line>` | `x1 y1 x2 y2` | Straight line from (x1,y1) to (x2,y2) |
| `<rect>` | `x y width height` | Top-left corner at (x,y) |
| `<circle>` | `cx cy r` | **Use `cx`/`cy`, not `x`/`y`** for the centre |
| `<text>` | `x y` | (x,y) is the *bottom-left* of the text. Content goes between tags. |
| `<g>` | (none required) | Group container. Like `<div>` but for SVG. |
| `<path>` | `d` | Free-form shape. `d` is a list of drawing commands. |

```html
<svg width="800" height="600">
  <line x1="20" y1="50" x2="220" y2="50"></line>
  <rect x="20" y="100" width="200" height="50"></rect>
  <circle cx="300" cy="50" r="50"></circle>
  <text x="300" y="150">SVG Text</text>
  <path d="M20,180 l200,0 l0,50 z"></path>
</svg>
```

### 3.3 Path commands

`d="M20,20 l200,0 l0,50 z"` reads:

- `M x,y` — **m**ove to absolute coordinate (uppercase = absolute).
- `l dx,dy` — **l**ine to relative offset (lowercase = relative).
- `L x,y` — **L**ine to absolute coordinate.
- `z` — close the shape back to the start.

Cook points readers to MDN's Paths tutorial for the rest.

### 3.4 SVG transforms

Apply via the `transform` attribute. Cook focuses on `translate` and `rotate` (he mentions but skips `scale`, `skewX`, `skewY`).

```html
<!-- translate: move by (dx, dy) -->
<circle r="50" transform="translate(200,75)"></circle>

<!-- rotate: degrees clockwise about origin (0,0) by default -->
<rect x="50" y="50" width="200" height="20" transform="rotate(20)"></rect>

<!-- rotate about a specified centre -->
<rect transform="rotate(20 150 60)"></rect>

<!-- combine: applied left-to-right as transformations of the coordinate system -->
<rect transform="rotate(45) translate(100,0)"></rect>
```

**Key Cook idiom:** put a circle at `(0,0)` with its label, wrap them in a `<g>`, and translate the group as a whole. Don't position individual elements:

```html
<g transform="translate(100,75)">
  <circle r="50"></circle>
  <text y="6">Label</text>     <!-- centred via CSS text-anchor: middle -->
</g>
```

Combining transforms transforms the **coordinate system**, in order. `rotate(45) translate(100,0)` first rotates the axes 45°, then moves 100 units along the *rotated* x-axis.

---

## 4. CSS

### 4.1 Structure

```css
selector {
  property: value;
  property: value;
}

h1 {
  color: green;
  font-size: 20px;
}
```

A stylesheet is a list of **rules**. Each rule has a **selector** and a list of **declarations** (`property: value;` pairs). When two rules conflict, the later one wins.

### 4.2 Units

| Unit | Meaning |
|---|---|
| `px` | Pixels |
| `rem` | Relative to the page's default font size (typically 16px → `1.5rem` = 24px) |
| `%` | Percentage of the parent element's value |
| `vw` / `vh` | Percentage of viewport width / height |

Colours: named (`red`, `steelblue`), `rgb(255, 100, 255)`, hex `#FF595E` or shortened `#FD3`.

### 4.3 Common HTML properties

`color`, `background-color`, `border` (e.g. `1px solid #aaa`, `1px dashed red`), `padding`, `margin`, `opacity` (0–1), `font-size`, `font-family` (`sans-serif`, `serif`, `Helvetica`), `font-weight` (`lighter` / `normal` / `bold`), `width`, `height`.

### 4.4 SVG-specific properties

These are CSS properties on SVG elements (Cook applies them via CSS rules, not attributes):

| Property | Meaning |
|---|---|
| `fill` | Interior colour of the shape (use `none` for no fill) |
| `stroke` | Outline colour |
| `stroke-width` | Outline width (e.g. `1px`) |
| `opacity` | 0–1 |
| `font-size`, `font-family`, `font-weight` | Text styling |
| `text-anchor` | Horizontal alignment of `<text>`: `start` / `middle` / `end` |

```css
circle { fill: #9E2A2B; }
text   { font-family: sans-serif; fill: white; text-anchor: middle; }
rect   { fill: none; stroke: #aaa; stroke-width: 1px; }
```

### 4.5 Selectors

```css
/* element type */
p { color: #333; }

/* id (unique element, prefix with #) */
#main-menu { margin: 1rem; }

/* class (multiple elements, prefix with .) */
div.item { border: 1px solid #aaa; padding: 1rem; }
.selected { background-color: #ccc; }   /* any element with class selected */

/* descendant: space-separated */
#main-menu div { padding: 1rem; }
.bar-chart .bar { fill: blue; }
.chart .legend .label { font-family: sans-serif; font-size: 0.75rem; }

/* pseudo-classes */
p:hover            { background-color: yellow; }
#main-menu div:first-child { font-weight: bold; }
#main-menu div:last-child  { /* ... */ }

/* grouped selectors */
h1, h2, h3, h4, h5, h6 { font-weight: lighter; }
```

`id` values must be unique. `class` values can repeat and an element can have multiple space-separated classes (e.g. `class="item selected"`).

### 4.6 Block vs inline; Flexbox

By default `<h1>`–`<h6>`, `<ul>`, `<div>` are **block** (stack vertically, take full parent width). `<img>` and `<svg>` are **inline** (sit side-by-side, sized by content). You can override with `display: block;`, `display: inline;`, or `display: inline-block;`.

Flexbox: set `display: flex` on the parent ("container") to lay out children ("items"):

```css
#container {
  display: flex;
  flex-direction: row;       /* or column */
  flex-wrap: nowrap;          /* or wrap */
  justify-content: space-between; /* flex-start | flex-end | center | space-around | space-between */
  align-items: center;        /* stretch | center | flex-start | flex-end */
}
```

Cook's go-to header pattern (nested flex containers):

```css
#header { height: 4rem; display: flex;
          justify-content: space-between; align-items: center; padding: 0 1rem; }
#menu   { display: flex; }
#menu div { padding-left: 1rem; }
```

Cook does not cover CSS Grid.

---

## 5. JavaScript fundamentals

Cook uses `let` (modern) over `var`. Statements end with `;` (optional but used throughout). He recommends [jsconsole.com](https://jsconsole.com) for experimentation.

### 5.1 Variables, types

```js
let myMessage = "Hello world!";
let a = 10;
let b = 20;
let c = a + b;   // 30
```

Five types covered: **strings**, **numbers**, **booleans**, **arrays**, **objects**.

### 5.2 Strings

```js
let s = "This is a string";
s.length;            // 16
s[0];                // "T"
s.split(' ');        // ["This", "is", "a", "string"]
s.toUpperCase();     // "THIS IS A STRING" (does not mutate s)
s.toLowerCase();

// String concatenation
let full = firstName + " " + lastName;

// String → number
parseFloat('123.456');  // 123.456
parseFloat('abc');      // NaN
parseFloat('1234abc');  // 1234
+'123';                 // 123 (but +'' is 0 — careful with missing data)
```

### 5.3 Numbers

```js
let n = 123.456;
Math.round(n);   // 123
Math.floor(n);   // 123
Math.ceil(n);    // 124
n.toString();    // "123.456"
Math.sqrt(100);  // 10
(10 + 20) * 2;   // 60
```

### 5.4 Booleans

`true`, `false`. Returned by `===`, `!==`, `>`, `<`, `>=`, `<=`.

### 5.5 Arrays

```js
let a = [10, 20, 30];
let nested = [[10, 20], [30, 40]];

a.length;             // 3
a[0];                 // 10
nested[0][1];         // 20

a.sort();             // mutates! and sorts as STRINGS — [11,10,9].sort() => [10,11,9]
a.reverse();          // mutates
a.push(70);           // mutates, adds to end
a.pop();              // mutates, removes & returns last
a.slice(1, 2);        // does not mutate; [start, end] inclusive in Cook's wording
a.concat(b);          // does not mutate
a.join(' and ');      // "10 and 20 and 30"
```

For numeric sort, pass a comparator: `a.sort((x, y) => x - y)`.

### 5.6 Objects

```js
let carrot = { foodGroup: "vegetable", color: "orange" };
carrot.foodGroup;       // "vegetable"
carrot["foodGroup"];    // same — square-bracket form lets you use a variable as the key

let day = "Tuesday";
let data = { Monday: 20, Tuesday: 30, Wednesday: 10 };
data[day];              // 30

// The canonical viz shape: array of objects
let countries = [
  { name: "Spain", capital: "Madrid",  population: 46.66 },
  { name: "China", capital: "Beijing", population: 1386 }
];
countries[0].name;      // "Spain"
```

### 5.7 Operators, conditionals (briefly)

Arithmetic `+ - * /`, comparison `===` (strict equality, preferred), `!==`, `<`, `>`, logical `&&`, `||`, `!`. `if / else if / else` works as expected.

### 5.8 Functions

```js
function double(x) {
  return x * 2;
}
double(5);              // 10

function joinNames(firstName, lastName) {
  return firstName + " " + lastName;
}
joinNames("Ana", "Matronic");

// Anonymous function (no name) — common as callback
data.forEach(function(d) { console.log(d); });
```

### 5.9 Iteration: forEach, map

```js
let data = [10, 50, 20, 80, 30];

// forEach: side-effect each element, returns nothing
data.forEach(function(d) { console.log(d); });

// map: returns a new array of the same length
let doubled = data.map(function(d) { return d * 2; });
// [20, 100, 40, 160, 60]
```

Cook recommends `forEach` over `for` loops for expressiveness. Other built-ins he doesn't cover (`filter`, `reduce`, `find`) are listed below.

### 5.10 Pure functions

Cook ends with the idea that functions returning a value without mutating outside state are "pure" and easier to reason about — a useful habit when wiring data through chart code.

---

# Beyond the book — intermediate viz patterns

Cook stops at JS fundamentals. This section adds the well-established patterns an AI coding agent needs to actually build a chart. All are stable, framework-agnostic conventions; D3 examples assume v7.

## A. Margin convention (Mike Bostock's pattern)

Every chart should use it. Define outer dimensions, subtract margins, draw inside a translated `<g>`.

```js
const margin = { top: 20, right: 20, bottom: 40, left: 50 };
const width  = 600 - margin.left - margin.right;
const height = 400 - margin.top  - margin.bottom;

const svg = d3.select("#chart")
  .append("svg")
    .attr("width",  width  + margin.left + margin.right)
    .attr("height", height + margin.top  + margin.bottom)
  .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);
```

## B. D3 selections and the data join

```js
// Selection
const bars = d3.select("#chart").selectAll("rect");

// Data join with enter / update / exit
const sel = svg.selectAll("rect.bar").data(values, d => d.id);

sel.exit().remove();                              // exit: data went away

const entered = sel.enter().append("rect")        // enter: new data
    .attr("class", "bar")
    .attr("y", height)                            // enter from baseline
    .attr("height", 0);

entered.merge(sel)                                // update + entered
    .attr("x", (d, i) => x(d.label))
    .attr("width", x.bandwidth())
    .attr("y", d => y(d.value))
    .attr("height", d => height - y(d.value));
```

Modern v7 alternative using `.join()`:

```js
svg.selectAll("rect.bar")
  .data(values, d => d.id)
  .join(
    enter => enter.append("rect").attr("class", "bar")
                  .attr("y", height).attr("height", 0),
    update => update,
    exit => exit.remove()
  )
  .attr("x", d => x(d.label))
  .attr("width", x.bandwidth())
  .attr("y", d => y(d.value))
  .attr("height", d => height - y(d.value));
```

## C. Scales

Scales map data values (input *domain*) to pixel values (output *range*).

```js
// Linear: continuous numeric → continuous numeric
const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value)]).nice()
    .range([height, 0]);    // inverted because y grows downward

// Log
const yLog = d3.scaleLog().domain([1, 1e6]).range([height, 0]);

// Time
const x = d3.scaleTime()
    .domain(d3.extent(data, d => d.date))
    .range([0, width]);

// Band: categorical → equally-spaced bands (bar charts)
const xBand = d3.scaleBand()
    .domain(data.map(d => d.label))
    .range([0, width])
    .padding(0.1);

// Ordinal: discrete domain → discrete range (categorical colour)
const colour = d3.scaleOrdinal()
    .domain(["A", "B", "C"])
    .range(d3.schemeTableau10);

// Sequential colour: continuous → interpolated colour
const heat = d3.scaleSequential(d3.interpolateBlues).domain([0, 100]);
```

## D. Axes

```js
const xAxis = d3.axisBottom(x).ticks(6).tickFormat(d3.format(",.0f"));
const yAxis = d3.axisLeft(y).ticks(5);

svg.append("g")
   .attr("class", "x-axis")
   .attr("transform", `translate(0,${height})`)
   .call(xAxis);

svg.append("g").attr("class", "y-axis").call(yAxis);
```

## E. Generators (line, area, arc, pie)

```js
// Line generator
const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.value))
    .curve(d3.curveMonotoneX);

svg.append("path")
   .datum(data)
   .attr("fill", "none")
   .attr("stroke", "steelblue")
   .attr("stroke-width", 1.5)
   .attr("d", line);

// Area generator
const area = d3.area()
    .x(d => x(d.date))
    .y0(height)
    .y1(d => y(d.value))
    .curve(d3.curveMonotoneX);

// Pie / arc (donut)
const pie = d3.pie().value(d => d.value).sort(null);
const arc = d3.arc().innerRadius(60).outerRadius(120);

svg.selectAll("path.slice")
   .data(pie(data)).join("path")
   .attr("class", "slice")
   .attr("d", arc)
   .attr("fill", d => colour(d.data.label));
```

## F. Responsive SVG with `viewBox` + ResizeObserver

Setting `width`/`height` attributes makes a fixed-size SVG. For responsive, use `viewBox` and let CSS size the element:

```html
<svg viewBox="0 0 600 400" preserveAspectRatio="xMidYMid meet"
     style="width:100%;height:auto;"></svg>
```

For chart code that needs to *re-render* on resize (e.g. recompute scales):

```js
const svgEl = document.querySelector("#chart svg");
const ro = new ResizeObserver(entries => {
  const { width, height } = entries[0].contentRect;
  redraw(width, height);
});
ro.observe(svgEl);
```

## G. Accessibility

SVG charts are inert by default. Minimum hardening:

```html
<svg role="img" aria-labelledby="chart-title chart-desc" viewBox="0 0 600 400">
  <title id="chart-title">Monthly revenue, 2024</title>
  <desc id="chart-desc">A line chart showing revenue rising from $1.2M in
  January to $3.4M in December, with a dip in August.</desc>
  <!-- shapes -->
</svg>
```

Per-mark labels: add `<title>` inside a shape for native tooltips, or use `aria-label`. For a fully a11y-friendly chart, also provide a data table fallback (`<table>` with the same data) and ensure focus states have visible outlines and sufficient colour contrast (≥3:1 for graphical objects).

## H. Animation and transitions

```js
svg.selectAll("rect.bar")
   .data(newData)
   .join("rect")
   .attr("class", "bar")
   .attr("x", d => x(d.label))
   .attr("width", x.bandwidth())
   .transition()
   .duration(750)
   .ease(d3.easeCubicOut)
   .attr("y", d => y(d.value))
   .attr("height", d => height - y(d.value));
```

CSS transitions also work for hover states:

```css
.bar { transition: fill 150ms ease-out; }
.bar:hover { fill: orange; }
```

Respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
```

## I. Common chart skeletons

### Bar chart

```js
const x = d3.scaleBand().domain(data.map(d => d.label))
            .range([0, width]).padding(0.1);
const y = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).nice()
            .range([height, 0]);

svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(x));
svg.append("g").call(d3.axisLeft(y));

svg.selectAll("rect.bar").data(data).join("rect")
   .attr("class", "bar")
   .attr("x", d => x(d.label))
   .attr("y", d => y(d.value))
   .attr("width",  x.bandwidth())
   .attr("height", d => height - y(d.value))
   .attr("fill", "steelblue");
```

### Line chart

```js
const x = d3.scaleTime().domain(d3.extent(data, d => d.date)).range([0, width]);
const y = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).nice()
            .range([height, 0]);

const line = d3.line().x(d => x(d.date)).y(d => y(d.value));

svg.append("path").datum(data)
   .attr("fill", "none").attr("stroke", "steelblue").attr("stroke-width", 1.5)
   .attr("d", line);
```

### Scatter

```js
svg.selectAll("circle.point").data(data).join("circle")
   .attr("class", "point")
   .attr("cx", d => x(d.x))
   .attr("cy", d => y(d.y))
   .attr("r", 4)
   .attr("fill", d => colour(d.group))
   .attr("opacity", 0.7);
```

### Donut

```js
const radius = Math.min(width, height) / 2;
const g = svg.append("g").attr("transform", `translate(${width/2},${height/2})`);

const pie = d3.pie().value(d => d.value).sort(null);
const arc = d3.arc().innerRadius(radius * 0.6).outerRadius(radius);

g.selectAll("path").data(pie(data)).join("path")
   .attr("d", arc)
   .attr("fill", d => colour(d.data.label));
```

### Stacked area

```js
const stack = d3.stack().keys(["a", "b", "c"]);
const series = stack(data);

const area = d3.area()
    .x(d => x(d.data.date))
    .y0(d => y(d[0]))
    .y1(d => y(d[1]));

svg.selectAll("path.layer").data(series).join("path")
   .attr("class", "layer")
   .attr("d", area)
   .attr("fill", d => colour(d.key));
```

## J. Loading data

```js
// CSV with type coercion
const data = await d3.csv("data.csv", d => ({
  date: d3.timeParse("%Y-%m-%d")(d.date),
  value: +d.value
}));

// JSON
const json = await d3.json("data.json");

// Plain fetch
const res = await fetch("data.json");
const data2 = await res.json();
```

## K. Useful array methods Cook didn't cover

```js
arr.filter(d => d.value > 0);
arr.reduce((acc, d) => acc + d.value, 0);
arr.find(d => d.id === 42);
arr.some(d => d.value < 0);
arr.every(d => d.value >= 0);

// d3 helpers
d3.min(arr, d => d.value);
d3.max(arr, d => d.value);
d3.extent(arr, d => d.date);     // [min, max]
d3.sum(arr, d => d.value);
d3.mean(arr, d => d.value);
d3.median(arr, d => d.value);
d3.group(arr, d => d.category);  // Map of category -> entries
d3.rollup(arr, v => v.length, d => d.category); // group + reduce
```

## L. Selecting and manipulating with vanilla DOM (no D3)

For agents working without D3:

```js
const svgNS = "http://www.w3.org/2000/svg";
const svg = document.querySelector("svg");

const rect = document.createElementNS(svgNS, "rect");
rect.setAttribute("x", 10);
rect.setAttribute("y", 10);
rect.setAttribute("width", 100);
rect.setAttribute("height", 50);
rect.setAttribute("fill", "steelblue");
svg.appendChild(rect);
```

**Critical:** SVG elements MUST be created with `createElementNS` and the SVG namespace, not `createElement`. Otherwise they render as nothing.

## M. Event handling

```js
// D3
svg.selectAll("circle").on("mouseover", function(event, d) {
  d3.select(this).attr("fill", "orange");
  tooltip.style("opacity", 1).text(d.label)
         .style("left", `${event.pageX + 8}px`)
         .style("top",  `${event.pageY + 8}px`);
});

// Vanilla
rect.addEventListener("mouseover", e => { /* ... */ });
```

---

## Quick-reference cheat sheet

- **SVG y goes DOWN** from the top-left origin.
- Always set `width`/`height` on `<svg>`; or use `viewBox` + CSS for responsive.
- Use `<g transform="translate(...)">` to position chart areas; never hand-translate every child.
- Prefer **CSS** for static styling (`fill`, `stroke`), **attributes** for data-driven values (`cx`, `cy`, `r`, `d`).
- `circle` uses `cx`/`cy`/`r`. `<text>` `(x,y)` is the bottom-left baseline; centre with `text-anchor: middle`.
- `d3.scaleLinear().range([height, 0])` — flip the range for y so larger values render higher.
- The margin convention is non-negotiable for axes to have room.
- Use `.join()` (D3 v7+) over the older enter/update/exit pattern.
- Provide `<title>` and `<desc>` plus `role="img"` for accessibility.
- `prefers-reduced-motion` should disable transitions.
