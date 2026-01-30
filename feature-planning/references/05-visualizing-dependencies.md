## 📊 Visualizing Dependencies (DAG)

```
STEP 1: Analyze Market
  ↓ (output: market_analysis)
  ├─→ STEP 2: Identify Audience
  │   ↓ (output: audience_profile)
  │   └─→ STEP 4: Create Messaging
  │       ↓
  │       └─→ STEP 5: Validate
  │
  └─→ STEP 3a: Define Positioning  ← Can run PARALLEL with 3b
      ↓                              (both only need step 1)
      ├─→ STEP 4: Create Messaging

  └─→ STEP 3b: Analyze Competitors ← Can run PARALLEL with 3a
      ↓
      └─→ STEP 4: Create Messaging


Execution Order (respecting dependencies):
Time 0:   STEP 1 starts
Time 5:   STEP 1 done
Time 5:   STEP 2, 3a, 3b START TOGETHER (all depend on step 1)
Time 10:  STEP 2 done
Time 13:  STEP 3a done
Time 15:  STEP 3b done
Time 15:  STEP 4 starts (needs 3a, 3b, 2 all done)
Time 20:  STEP 4 done
Time 20:  STEP 5 starts
Time 25:  STEP 5 done
Time 25:  PLAN COMPLETE

Total time: 25 minutes (not 33, because we parallelized!)
```
