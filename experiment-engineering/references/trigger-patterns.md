# Trigger Patterns

A trigger is the precise moment a user becomes eligible for the treatment. Three patterns cover nearly every real experiment. Choose one based on how the feature surfaces to the user.

## Exposure-Based Triggers

Fired when the feature is rendered on screen. Use when the feature is visible-by-default — banners, hero tiles, inline cards, modals that auto-open.

Generic logger signature:

```text
log_trigger(
  experiment_id: str,
  variant: str,
  user_id: str,
  session_id: str,
  trigger_type: "exposure",
  timestamp_ms: int,
  context: dict
)
```

Call site:

```text
# In the server-side render path, after variant assignment
variant = experiment_service.assign(user_id, "exp_hero_banner_v3")
hero = render_hero(variant)
log_trigger(
  experiment_id="exp_hero_banner_v3",
  variant=variant,
  user_id=user_id,
  session_id=session_id,
  trigger_type="exposure",
  timestamp_ms=now_ms(),
  context={"page": "home", "surface": "hero"}
)
return hero
```

Pitfall: if the hero is cached upstream of the trigger call, the trigger fires once but the user sees the variant many times. That is still correct — the trigger marks *eligibility*, not *impressions*.

## Action-Based Triggers

Fired when the user takes the specific action that reveals the feature. Use when the feature sits behind navigation — a tab click, a settings menu open, an overflow tap.

Call site:

```text
# On the "Settings" tab click handler, server-side
def on_settings_tab_opened(user_id, session_id):
  variant = experiment_service.assign(user_id, "exp_settings_layout_v2")
  log_trigger(
    experiment_id="exp_settings_layout_v2",
    variant=variant,
    user_id=user_id,
    session_id=session_id,
    trigger_type="action",
    timestamp_ms=now_ms(),
    context={"action": "settings_tab_opened"}
  )
  return render_settings(variant)
```

Pitfall: if the tab pre-fetches on hover, the trigger fires before the user committed. Fire on the navigation completion event, not the hover.

## Hybrid Triggers

Rendered-but-only-counts-if-visible. Use when visibility depends on scroll depth, viewport, or lazy-loading — below-the-fold modules, infinite-scroll cards.

Implementation: render the component, but fire the trigger only when the component enters the viewport (IntersectionObserver on web, view-holder bind on Android, didAppear on iOS), AND post the trigger server-side from the client event, AND de-duplicate server-side per user per experiment.

Call site (client fires, server persists):

```text
on_intersection_observed(component_id):
  if component_id == "upsell_card_below_fold":
    post_to_server({
      "experiment_id": "exp_upsell_card_v1",
      "variant": client_known_variant,
      "user_id": user_id,
      "session_id": session_id,
      "trigger_type": "hybrid",
      "timestamp_ms": now_ms(),
      "context": {"scroll_depth_pct": 72, "viewport_height_px": 896}
    })
```

Pitfall: client-only trigger firing is unsafe. Ad-blockers, broken JS, and bot traffic drop client events unequally across variants. Always post the client event to a server endpoint that persists the trigger; de-duplicate server-side on `(experiment_id, user_id)`.

## Rules Across All Three Patterns

- Log trigger events server-side. A client-only trigger is not trustworthy.
- Include `experiment_id`, `variant`, `user_id`, `session_id`, `timestamp`. Everything else is context.
- De-duplicate per `(experiment_id, user_id)` — one trigger per user per experiment is the right count for most analyses; impression counts belong in a separate event.
- The trigger event is not the success metric event. Do not conflate them.
- Fire the trigger as close to the divergence point as possible. A trigger that fires 3 clicks before the treatment actually appears is a dilution source.
