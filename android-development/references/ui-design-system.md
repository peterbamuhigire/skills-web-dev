# UI Design System

Material 3 design tokens and reusable component standards.

## Design Tokens

```kotlin
object DesignSystem {

    object Colors {
        // Brand colors
        val Primary = Color(0xFF0F4680)
        val Secondary = Color(0xFF440479)
        val Tertiary = Color(0xFF006D40)

        // Semantic colors
        val Success = Color(0xFF2E7D32)
        val Error = Color(0xFFD32F2F)
        val Warning = Color(0xFFED6C02)
        val Info = Color(0xFF0288D1)

        // Surface colors
        val Surface = Color(0xFFFFFFFF)
        val Background = Color(0xFFF5F5F5)
        val OnSurface = Color(0xFF1C1B1F)
        val OnPrimary = Color(0xFFFFFFFF)
        val OnSecondary = Color(0xFFFFFFFF)

        // Dark theme variants
        val PrimaryDark = Color(0xFF90CAF9)
        val SurfaceDark = Color(0xFF1C1B1F)
        val BackgroundDark = Color(0xFF121212)
    }

    object Spacing {
        val xs = 4.dp
        val sm = 8.dp
        val md = 16.dp
        val lg = 24.dp
        val xl = 32.dp
        val xxl = 48.dp
    }

    object Shapes {
        val small = RoundedCornerShape(4.dp)
        val medium = RoundedCornerShape(8.dp)
        val large = RoundedCornerShape(16.dp)
        val extraLarge = RoundedCornerShape(28.dp)
        val pill = RoundedCornerShape(50)
    }

    object Elevation {
        val none = 0.dp
        val low = 1.dp
        val medium = 4.dp
        val high = 8.dp
        val highest = 16.dp
    }
}
```

## Theme Setup

```kotlin
@Composable
fun SaasAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) {
        darkColorScheme(
            primary = DesignSystem.Colors.PrimaryDark,
            surface = DesignSystem.Colors.SurfaceDark,
            background = DesignSystem.Colors.BackgroundDark
        )
    } else {
        lightColorScheme(
            primary = DesignSystem.Colors.Primary,
            secondary = DesignSystem.Colors.Secondary,
            surface = DesignSystem.Colors.Surface,
            background = DesignSystem.Colors.Background,
            error = DesignSystem.Colors.Error
        )
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        shapes = Shapes(
            small = DesignSystem.Shapes.small,
            medium = DesignSystem.Shapes.medium,
            large = DesignSystem.Shapes.large
        ),
        content = content
    )
}
```

## Standard Components

### Button

```kotlin
@Composable
fun StandardButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    variant: ButtonVariant = ButtonVariant.Primary,
    size: ButtonSize = ButtonSize.Medium,
    isLoading: Boolean = false,
    enabled: Boolean = true,
    leadingIcon: ImageVector? = null,
    trailingIcon: ImageVector? = null
) {
    val buttonColors = when (variant) {
        ButtonVariant.Primary -> ButtonDefaults.buttonColors(
            containerColor = DesignSystem.Colors.Primary,
            contentColor = DesignSystem.Colors.OnPrimary
        )
        ButtonVariant.Secondary -> ButtonDefaults.buttonColors(
            containerColor = DesignSystem.Colors.Secondary,
            contentColor = DesignSystem.Colors.OnSecondary
        )
        ButtonVariant.Outlined -> ButtonDefaults.outlinedButtonColors(
            contentColor = DesignSystem.Colors.Primary
        )
        ButtonVariant.Text -> ButtonDefaults.textButtonColors(
            contentColor = DesignSystem.Colors.Primary
        )
    }

    val height = when (size) {
        ButtonSize.Small -> 36.dp
        ButtonSize.Medium -> 48.dp
        ButtonSize.Large -> 56.dp
    }

    Button(
        onClick = onClick,
        modifier = modifier.height(height),
        colors = buttonColors,
        shape = DesignSystem.Shapes.medium,
        enabled = enabled && !isLoading
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(20.dp),
                strokeWidth = 2.dp,
                color = LocalContentColor.current
            )
        } else {
            leadingIcon?.let {
                Icon(it, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(DesignSystem.Spacing.xs))
            }
            Text(text)
            trailingIcon?.let {
                Spacer(Modifier.width(DesignSystem.Spacing.xs))
                Icon(it, contentDescription = null, modifier = Modifier.size(18.dp))
            }
        }
    }
}

enum class ButtonVariant { Primary, Secondary, Outlined, Text }
enum class ButtonSize { Small, Medium, Large }
```

### Standard Top Bar

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StandardTopBar(
    title: String,
    modifier: Modifier = Modifier,
    navigationIcon: ImageVector? = Icons.AutoMirrored.Filled.ArrowBack,
    onNavigationClick: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {}
) {
    TopAppBar(
        title = { Text(title) },
        modifier = modifier,
        navigationIcon = {
            if (navigationIcon != null && onNavigationClick != null) {
                IconButton(onClick = onNavigationClick) {
                    Icon(navigationIcon, contentDescription = "Navigate back")
                }
            }
        },
        actions = actions
    )
}
```

### Loading, Error, Empty States

```kotlin
@Composable
fun LoadingIndicator(modifier: Modifier = Modifier) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator()
    }
}

@Composable
fun ErrorMessage(
    message: String,
    modifier: Modifier = Modifier,
    onRetry: (() -> Unit)? = null
) {
    Column(
        modifier = modifier.fillMaxSize().padding(DesignSystem.Spacing.lg),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            Icons.Default.ErrorOutline,
            contentDescription = null,
            modifier = Modifier.size(48.dp),
            tint = DesignSystem.Colors.Error
        )
        Spacer(Modifier.height(DesignSystem.Spacing.md))
        Text(message, style = MaterialTheme.typography.bodyLarge, textAlign = TextAlign.Center)
        onRetry?.let {
            Spacer(Modifier.height(DesignSystem.Spacing.md))
            StandardButton(text = "Retry", onClick = it, variant = ButtonVariant.Outlined)
        }
    }
}

@Composable
fun EmptyState(
    title: String,
    message: String,
    modifier: Modifier = Modifier,
    actionText: String? = null,
    onAction: (() -> Unit)? = null
) {
    Column(
        modifier = modifier.fillMaxSize().padding(DesignSystem.Spacing.lg),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            Icons.Default.Inbox,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
        )
        Spacer(Modifier.height(DesignSystem.Spacing.md))
        Text(title, style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(DesignSystem.Spacing.sm))
        Text(message, style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
        if (actionText != null && onAction != null) {
            Spacer(Modifier.height(DesignSystem.Spacing.md))
            StandardButton(text = actionText, onClick = onAction)
        }
    }
}
```

## Component Rules

1. **Always accept `Modifier`** as a parameter
2. **Use Material 3** components as base
3. **Design tokens only** - no hardcoded colors/sizes
4. **Support dark theme** via `MaterialTheme.colorScheme`
5. **Accessibility** - always set `contentDescription` for icons
6. **Preview annotations** for all public components

```kotlin
@Preview(showBackground = true)
@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
private fun StandardButtonPreview() {
    SaasAppTheme {
        StandardButton(text = "Click Me", onClick = {})
    }
}
```
