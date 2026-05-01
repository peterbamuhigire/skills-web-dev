# CLTD Logistics and Inventory Patterns

Use this reference for ERP, WMS, TMS, distribution, wholesale, import/export, fleet, and physical-goods systems. It translates CLTD network design, inventory management, and transportation concepts into implementable software requirements.

## Domain Model Additions

Core entities to consider beyond the base stock ledger:

- `network_nodes`: supplier, port, border, plant, warehouse, cross_dock, branch, customer_zone, disposal_site
- `trade_lanes`: origin node, destination node, mode, normal lead time, risk rating, cost basis
- `carriers`: carrier type, service levels, lanes served, rate card, claims process, tracking integration
- `fleet_assets`: vehicle, capacity, maintenance status, compliance documents, operating cost
- `shipments`: order linkage, carrier/fleet assignment, route, service level, Incoterms where relevant, lifecycle status
- `shipment_events`: booked, picked_up, in_transit, hub_scan, delayed, delivered, exception, returned
- `freight_documents`: BOL, waybill, freight bill, packing list, commercial invoice, customs declaration, certificate, proof of delivery
- `freight_claims`: damage, shortage, delay, lost shipment, claim value, evidence, recovery status
- `inventory_policies`: ABC class, review method, reorder point, safety stock, service level, MOQ, lot size, expiry/FEFO rule
- `in_transit_inventory`: stock committed to a shipment or transfer but not yet received at the destination
- `logistics_service_contracts`: 3PL/4PL/lead logistics provider scope, SLA, escalation path, data exchange method

## Network Design Requirements

- Represent the physical network explicitly: suppliers, warehouses, cross-docks, branches, trade corridors, customer zones, ports, and border points.
- Let planners compare service-level and total-cost tradeoffs: transport, warehouse handling, storage, safety stock, delivery frequency, customs clearance, and administration.
- Track current and target service levels by zone or customer class; do not hard-code one delivery promise for all customers.
- Support future network redesign triggers: new product lines, customer geography changes, supplier changes, freight-volume growth, trade-policy changes, or service-level changes.
- Include reverse logistics for returns, recalls, reusable packaging, repair, recycling, disposal, and supplier returns.

## Inventory Policy Requirements

- Separate cycle stock, safety stock, WIP, finished goods, packaging, spares, consigned stock, returns, quarantined stock, and in-transit stock where the business uses them.
- Support perpetual review for high-value or high-risk SKUs and periodic review for stable low-value SKUs where that is operationally acceptable.
- Use ABC classification to drive count frequency, approval thresholds, replenishment attention, and exception alerts.
- Calculate reorder points from demand, lead time, safety stock, MOQ, supplier reliability, route reliability, and current in-transit quantity.
- Treat backorders, stockouts, excess stock, slow stock, expiry, shrinkage, and negative availability as first-class exceptions.
- Keep inventory policy connected to finance: carrying cost, tied-up cash, duties, insurance, storage, handling, obsolescence, and write-off risk.

## Transportation Requirements

- Model private fleet, hired carrier, courier, freight forwarder, 3PL, 4PL, and lead-logistics-provider options without rewriting the order lifecycle.
- Support mode and carrier selection by cost, service level, lane, capacity, compliance, claims performance, tracking capability, and customer promise.
- Capture shipment lifecycle controls: booking, labels, pickup, dispatch, track-and-trace, expediting, consolidation, proof of delivery, returns, and claims.
- For owned fleets, include vehicle capacity, maintenance downtime, driver availability, route adherence, idle time, fuel, licensing, insurance, and compliance document expiry.
- For outsourced carriers, include SLA, rate card, lane coverage, cutoff times, pickup reliability, delivery reliability, fallback carrier, and escalation path.
- For import/export flows, include Incoterms, customs broker, commercial invoice, packing list, BOL/waybill, customs declarations, clearance status, duties, and risk-transfer point.

## Workflow Patterns

### Order to Delivery

1. Reserve stock by SKU, batch, and location.
2. Pick, pack, label, and stage the shipment.
3. Select carrier, route, service level, and dispatch window.
4. Generate shipment documents and customer notifications.
5. Track pickup, in-transit events, exceptions, proof of delivery, claims, and returns.
6. Release accounting and inventory postings from auditable source events.

### Replenish to Stock

1. Review demand, stock on hand, reserved stock, backorders, scheduled receipts, and in-transit inventory.
2. Apply item policy: ABC class, reorder point, safety stock, MOQ, lot size, expiry, and supplier lead time.
3. Create purchase, transfer, or production recommendations.
4. Route exceptions for shortages, expedite, defer, cancel, reschedule, or overload.
5. Receive against PO/transfer, quarantine where required, then put away and update available stock.

### Shipment Exception Handling

Use explicit workflows for delay, damage, shortage, wrong item, refused delivery, lost shipment, customs hold, route disruption, vehicle breakdown, and failed delivery. Each exception needs owner, SLA clock, customer communication, financial impact, and close code.

## Metrics and Dashboards

- Fill rate, stockout rate, backorder rate, and backorder age
- Inventory days, inventory turnover, carrying cost, slow-stock value, obsolete-stock value
- Safety-stock coverage for critical SKUs
- Dock-to-stock time, order fulfilment cycle time, pick accuracy, and inventory accuracy
- On-time pickup, on-time delivery, OTIF, route adherence, and exception closure time
- Transport cost per order, unit, km, tonne-km, or sales value
- Load utilisation, empty running, fleet utilisation, idle time, maintenance downtime, and backhaul contribution
- Freight claims, damage rate, loss rate, claim recovery value, and carrier scorecard
- Customs clearance lead time, documentation error rate, duty variance, and broker performance

## Acceptance Criteria for ERP Features

- Every physical movement has an auditable stock event and every shipment status has a timestamped event.
- Available stock excludes reserved, quarantined, damaged, expired, and in-transit quantities unless the business explicitly allows allocation from those pools.
- Backorders and stockouts are visible to sales, procurement, warehouse, and finance; they are not hidden in notes.
- Carrier/fleet selection is explainable from configured cost, service, lane, capacity, and compliance rules.
- Freight documents and proof of delivery are linked to the shipment and retained under the relevant retention policy.
- Claims and returns update inventory, customer service, finance, and carrier scorecards without manual reconciliation.
- Dashboards separate service metrics from cost metrics so management can see the time, cost, quality, and flexibility tradeoff.
