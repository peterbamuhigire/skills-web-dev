# Compose Streaming Patterns

Companion to `SKILL.md` §6. Source: developer.android.com/develop/ui/compose/side-effects (fetched 2026-05-01).

## `LaunchedEffect` contract (verbatim)

> "Launches a coroutine when entering the Composition. Cancels the coroutine if LaunchedEffect leaves the Composition. If recomposed with different keys, cancels the existing coroutine and launches a new one."

Signature:

```kotlin
LaunchedEffect(vararg keys: Any?, block: suspend () -> Unit)
```

## Minimal streaming composable

```kotlin
@Composable
fun StreamedAnswer(prompt: String, tokens: (String) -> Flow<String>) {
    var text by remember { mutableStateOf("") }
    LaunchedEffect(prompt) {
        text = ""
        tokens(prompt).collect { chunk -> text += chunk }
    }
    Text(text, modifier = Modifier.animateContentSize())
}
```

Why this works: when the user changes the prompt, `LaunchedEffect` cancels the previous coroutine and launches a new one. When the user navigates away, the coroutine is cancelled automatically.

## Event-handler launches

```kotlin
@Composable
fun rememberCoroutineScope(factory: CoroutineContext = EmptyCoroutineContext): CoroutineScope
```

Use `rememberCoroutineScope` for click-handler initiation when you need a scope tied to the composition's lifetime but launched outside a `LaunchedEffect`.

## Long streams — virtualise

Appending to one growing `Text` recomposes and re-measures on every chunk. For chat-style streams, model each message as an item in `LazyColumn` and append chunks to the *current* message's state object:

```kotlin
data class Message(val id: Long, val text: MutableState<String>)

@Composable
fun ChatList(messages: List<Message>) {
  LazyColumn {
    items(messages, key = { it.id }) { msg ->
      Text(msg.text.value)
    }
  }
}
```

When accumulating into a list (e.g. chunked tokens), wrap reads in `derivedStateOf` to avoid recomposing on every list mutation.

## ViewModel side

```kotlin
fun ask(prompt: String) = viewModelScope.launch {
  client.messages.stream(prompt).collect { chunk -> _stream.emit(chunk.deltaText) }
}
```

Always use `viewModelScope` so streams cancel on `onCleared()`. Time out cloud streams at <= 15 s. Surface partial output on cancellation rather than discarding it.

## Backpressure

Cloud SDKs typically deliver tokens faster than Compose can re-render at 60 fps when the message is long. Either:

- Coalesce chunks with `Flow.sample(16)` so you re-render at most ~60 fps.
- Or keep raw chunks but render in a `LazyColumn` so layout work stays bounded.

## Pitfalls

- Launching from `GlobalScope` — leaks past navigation.
- Mutating `mutableStateListOf` without `derivedStateOf` — recomposes the world per token.
- Forgetting to reset `text` when the prompt changes — old tokens bleed into the new answer.
