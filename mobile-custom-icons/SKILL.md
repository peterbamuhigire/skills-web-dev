---
name: mobile-custom-icons
description: "Use custom PNG icons in mobile apps (Android and iOS) instead of library icons. Enforces placeholder usage, standard directories, and PROJECT_ICONS.md tracking. Applies to Jetpack Compose, XML layouts, and SwiftUI."
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, code generation, debugging, quality checks, and any task where it offers enhanced capabilities. If superpowers provides a better way to accomplish something, prefer it over the default approach.

# Mobile Custom PNG Icons

Use **custom PNG icons** in mobile apps instead of icon libraries. Whenever UI code includes an icon, the agent must use a PNG placeholder and update `PROJECT_ICONS.md` so the icon list is tracked for later upload.

## Scope

**Use for:** All mobile UI generation (Android Compose/XML and iOS SwiftUI).

**Do not use:** Material Icons, SF Symbols, Font Awesome, or any bundled icon libraries unless the user explicitly asks for them.

---

## Android

### Standard Icon Directory

- **Primary location:** `app/src/main/res/drawable/`
- **If you need 1:1 pixels (no scaling):** `app/src/main/res/drawable-nodpi/`

> If multiple densities are provided later, place them in `drawable-hdpi`, `drawable-xhdpi`, `drawable-xxhdpi`, `drawable-xxxhdpi` using the same file name.

### File Naming Rules (Android)

- Lowercase letters, numbers, underscores only
- No hyphens, no spaces, no uppercase
- File name becomes `R.drawable.<name>`

**Examples:**

- `cancel.png` -> `R.drawable.cancel`
- `chart.png` -> `R.drawable.chart`
- `filter.png` -> `R.drawable.filter`

### Compose Usage (Required)

```kotlin
Icon(
    painter = painterResource(R.drawable.cancel),
    contentDescription = "Cancel",
    modifier = Modifier.size(24.dp)
)
```

```kotlin
Image(
    painter = painterResource(R.drawable.chart),
    contentDescription = null,
    modifier = Modifier.size(48.dp)
)
```

### XML Usage (Required)

```xml
<ImageView
    android:layout_width="24dp"
    android:layout_height="24dp"
    android:src="@drawable/cancel"
    android:contentDescription="@string/cancel" />
```

---

## iOS

### iOS Asset Catalog

- **Primary location:** `Assets.xcassets/Icons/`
- Each icon gets its own `.imageset` folder inside `Icons/`
- Each `.imageset` folder contains the PNG files and a `Contents.json` manifest

**Directory structure example:**

```
Assets.xcassets/
  Icons/
    cancel.imageset/
      cancel@1x.png
      cancel@2x.png
      cancel@3x.png
      Contents.json
    chart.imageset/
      chart@1x.png
      chart@2x.png
      chart@3x.png
      Contents.json
```

**Contents.json template:**

```json
{
  "images": [
    { "filename": "cancel@1x.png", "idiom": "universal", "scale": "1x" },
    { "filename": "cancel@2x.png", "idiom": "universal", "scale": "2x" },
    { "filename": "cancel@3x.png", "idiom": "universal", "scale": "3x" }
  ],
  "info": { "version": 1, "author": "xcode" }
}
```

> During placeholder phase, provide at least the 2x variant. Xcode will scale for missing sizes.

### File Naming Rules (iOS)

- Lowercase letters, numbers, and hyphens allowed
- No spaces, no uppercase
- The `.imageset` folder name is the image identifier used in code

**Examples:**

- `cancel.imageset/` -> `Image("cancel")`
- `bar-chart.imageset/` -> `Image("bar-chart")`
- `filter.imageset/` -> `Image("filter")`

### SwiftUI Usage (Required)

```swift
Image("cancel")
    .resizable()
    .frame(width: 24, height: 24)

// Or with accessibility
Image("chart")
    .resizable()
    .aspectRatio(contentMode: .fit)
    .frame(width: 48, height: 48)
    .accessibilityLabel("Chart")
```

### UIKit Usage (Reference)

```swift
let icon = UIImage(named: "cancel")
imageView.image = icon
```

---

## PROJECT_ICONS.md (Required)

Maintain a `PROJECT_ICONS.md` file at the **project root**. Every time code introduces a new icon placeholder, **append a row**.

### Template

```markdown
# Project Icons

Android path: app/src/main/res/drawable/
iOS path: Assets.xcassets/Icons/

| Icon File  | Usage        | Screen/Component  | Status      | Platform      | Notes                    |
| ---------- | ------------ | ----------------- | ----------- | ------------- | ------------------------ |
| cancel.png | Close action | EditProfileTopBar | placeholder | Android + iOS | Provide 24dp/24pt PNG    |
```

### Update Rules

- Add a row **every time** a new icon placeholder is referenced in code.
- Use the exact file name used in code (e.g., `cancel.png`).
- Keep status as `placeholder` until the PNG is provided.
- Set **Platform** to `Android`, `iOS`, or `Android + iOS` depending on where the icon is used.

---

## Mandatory Checklist (Per UI Generation)

- [ ] Use PNG placeholders only (no icon libraries, no SF Symbols)
- [ ] **Android:** Use `painterResource(R.drawable.<name>)` or `@drawable/<name>`
- [ ] **iOS:** Use `Image("<name>")` referencing the asset catalog
- [ ] Placeholders use valid resource naming (underscores for Android, hyphens allowed for iOS)
- [ ] Add or update `PROJECT_ICONS.md` with the Platform column filled in
- [ ] For cross-platform projects, ensure the icon is listed once with `Android + iOS` platform
