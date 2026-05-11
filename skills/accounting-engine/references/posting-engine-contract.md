# Posting Engine Contract

## Required Write Path

All ledger writes pass through `LedgerPostingService::post(JournalEntry $entry)`.

The method MUST:

- Start a database transaction.
- Lock or validate the accounting period.
- Validate all accounts belong to the same tenant and are active.
- Validate the source document exists and is postable.
- Validate `sum(debits) == sum(credits)` in the journal currency.
- Validate the idempotency key has not already posted a different payload.
- Insert a journal header and journal lines.
- Commit atomically.
- Emit a durable domain event for downstream caches and reports.

## Reversals

Reversal means a new journal with opposite debits/credits and `reverses_journal_id` pointing to the original. The original remains immutable.

Bad:

```php
$line->amount = 0;
$line->deleted_at = now();
$line->save();
```

Good:

```php
$poster->post($reversalFactory->reverse($originalJournal, $reason, $actorId));
```

## Mapping Resolver

Business code asks for accounts by business meaning, not code:

```php
$accounts = $resolver->forSale(
    tenantId: $tenantId,
    productCategoryId: $categoryId,
    paymentMethodId: $paymentMethodId,
    taxRateId: $taxRateId,
);
```

If a mapping is missing, return a structured error naming the missing mapping and stop posting.
