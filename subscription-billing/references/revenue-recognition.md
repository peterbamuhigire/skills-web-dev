# Revenue Recognition

Use this reference when billing design or reporting needs to distinguish cash collection from recognized SaaS revenue.

## Core Concept

Cash collected in advance for a subscription is not all earned immediately. It is usually recognized ratably over the service period unless a different accounting treatment is justified.

## Deferred Revenue

When an annual subscription is paid upfront:

- cash increases immediately
- a deferred or unearned revenue liability is recorded
- revenue is recognized month by month as service is delivered

## Simple Example

For a 12-month prepaid subscription of 1,200 USD:

- at payment: debit cash 1,200, credit deferred revenue 1,200
- each month: debit deferred revenue 100, credit subscription revenue 100

## Standards Context

- ASC 606 is the common US framework
- IFRS 15 is the parallel international framework
- for most SaaS subscriptions, revenue recognition is ratable over the subscription period

## Why Product Teams Should Care

- prepaid cash flow can hide poor revenue quality if reporting is sloppy
- refunds, pauses, credits, and downgrades affect both billing and recognition logic
- finance, product, and engineering need the same contract dates and entitlement dates to reconcile correctly
