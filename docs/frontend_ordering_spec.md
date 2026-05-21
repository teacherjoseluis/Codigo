# Frontend Ordering Application Specification

This document defines the first lightweight frontend for the restaurant system.
It is intended to support a waiter taking table orders, delivery/counter order
capture, kitchen preparation visibility, customer-ready notifications, and
customer payments while remaining flexible enough for related operational
workflows such as warehouse receiving.

The frontend should be mobile-first and usable as a responsive web application
or PWA. Native mobile shells can be added later if device integrations require
them, but the initial product contract should not depend on app-store delivery.

## Goals

- Let authenticated staff create, edit, submit, and close customer orders.
- Route submitted items to the correct preparation areas, such as kitchen or bar.
- Show preparation teams a focused queue of incoming work.
- Notify staff and optionally customers when items or orders are ready.
- Receive customer payments and keep payment state visible to operators.
- Support dine-in, takeaway, delivery, and future operational flows with the
  same workflow primitives.
- Provide a Material Design based UI with restaurant-configurable colors,
  logo, typography scale, and light/dark mode preferences.
- Surface offline, sync, validation, and conflict states explicitly.

## Non-goals for the first frontend phase

- Full restaurant administration, accounting, inventory management, or menu
  authoring.
- Direct PostgreSQL access from the client.
- A customer self-service marketplace with public account management.
- Final offline settlement of payments without server confirmation.
- Native-only hardware integrations. Printer, cash drawer, scanner, and payment
  terminal integrations should be abstracted behind optional adapters.

## User roles

The UI should derive visible navigation and actions from authenticated user
permissions and sucursal/ubicacion scope.

| Role | Primary jobs | Important permissions |
| --- | --- | --- |
| Server/waiter | Open tables, take orders, send items to preparation, deliver ready items, request payment | Create/update comandas for assigned sucursal/ubicaciones, view menu, mark delivered |
| Cashier | Review open checks, split/merge payment requests, record payments, close orders | View financial totals, receive payments, close comandas |
| Kitchen/bar operator | See preparation queue, start/hold/complete items | View routed preparation orders, mark items ready, manage temporary unavailable items if allowed |
| Manager | Monitor service, override conflicts, configure theme, inspect errors | Cross-area visibility, void/discount/override permissions, device management |
| Delivery/counter operator | Capture customer and fulfillment details, monitor ready state, hand off orders | Create delivery/takeaway orders, update fulfillment state |
| Customer recipient | Receive readiness/payment status notifications | Notification opt-in only; no staff access |

## Primary use cases

### Dine-in table service

1. Staff signs in and selects a sucursal and service area if more than one is
   available.
2. Staff opens an existing table or creates a new comanda for a table.
3. Staff adds menu items, modifiers, notes, and quantities.
4. Staff sends pending items to preparation.
5. Kitchen/bar sees routed items in a preparation queue.
6. Kitchen/bar marks items ready.
7. Staff receives an in-app and optional push notification, delivers items, and
   marks them delivered.
8. Cashier or staff closes the order and records payment.

### Takeaway and delivery order capture

1. Staff creates an order without an assigned table.
2. Staff enters customer name, phone, fulfillment mode, promised time, and
   delivery address if applicable.
3. Staff submits items to preparation.
4. Staff and optionally the customer receive readiness notifications.
5. Staff records pickup/delivery handoff and payment.

### Preparation team queue

1. Preparation operator signs in to a kitchen, bar, or other preparation area.
2. Operator sees incoming orders grouped by urgency and station.
3. Operator marks line items or whole preparation orders as ready.
4. Ready status propagates to the service/cashier views and notifications.

### Payment collection

1. Staff opens the payment screen from a comanda.
2. Staff reviews totals, discounts, taxes, service charge, paid amount, and
   remaining balance.
3. Staff selects one or more payment methods.
4. The client submits payment requests to the backend.
5. On success, the order transitions to paid/closed according to configured
   policy. On failure, payment state remains clearly unresolved.

### Future adjacent flows

The same shell and notification framework should be extensible to warehouse
receiving, inventory movements, and dispatch workflows. Those flows should be
introduced as separate role-gated modules rather than mixed into the first
ordering navigation.

## Platform and architecture expectations

- Build as a responsive Material Design web client or PWA.
- Use the Django API as the only authoritative backend contract.
- Cache stable reads such as menu/catalog/theme data locally.
- Queue offline mutations only where the offline sync contract allows it.
- Use server-provided `X-Request-ID` values in error displays and support logs.
- Prefer optimistic UI only for reversible local states. Server-confirmed states
  are required for sending to preparation, payment acceptance, and order close.
- Keep client-side state normalized by comanda, item, preparation order, and
  payment identifiers.

## Navigation model

The application should expose modules based on role and device context:

```text
App shell
  Sign in / device setup
  Home dashboard
  Orders
    Table map
    Order list
    Order detail / item editor
  Preparation
    Queue
    Preparation order detail
  Payments
    Payment detail
    Payment result
  Notifications
  Settings
    Device/session
    Theme preview
    Diagnostics
```

On phones, use a bottom navigation bar for the most common modules available to
the current role. On tablets and desktops, use a navigation rail or drawer.

## Required screens

### 1. Sign in

Purpose: authenticate staff and establish a scoped session.

Content and actions:

- Username/password form.
- Optional remembered device name.
- Branch/location selector after successful login when the user has multiple
  authorized scopes.
- Offline indicator if the server cannot be reached.
- Link or flow for manager-assisted password reset if supported by backend.

States:

- Loading.
- Invalid credentials.
- Account disabled or not authorized for the selected location.
- Token expired with re-authentication prompt.
- Network unavailable.

Backend dependencies:

- `POST /api/v1/auth/login/`
- `GET /api/v1/auth/me/`
- `POST /api/v1/auth/logout/`

### 2. Device setup and session context

Purpose: bind the frontend instance to a restaurant, sucursal, ubicacion, and
role-specific working context.

Content and actions:

- Current user, sucursal, service area, and preparation area.
- Device label and push notification permission status.
- Button to switch authorized location.
- Last sync time and app version.

States:

- Device not registered for offline/push features.
- Push permission denied.
- User has no assigned sucursal or ubicacion.

### 3. Home dashboard

Purpose: give role-specific entry points and operational alerts.

Content and actions:

- Open orders count.
- Ready items awaiting delivery.
- Orders awaiting payment.
- Preparation queue counts by station.
- Offline/sync banner when applicable.
- Fast actions: new table order, new takeaway/delivery order, scan/search order.

States:

- Empty shift/no open work.
- Degraded backend health.
- Sync backlog requires attention.

### 4. Table map

Purpose: let dine-in staff open or create table orders quickly.

Content and actions:

- Floor/area filter.
- Table cards with status: available, seated, ordering, in preparation, ready,
  needs payment, paid, blocked.
- Occupancy, elapsed time, server, and outstanding alert badges.
- Action to open table/comanda.

States:

- No tables configured for selected area.
- Table locked by another active session.
- Stale table data warning.

Backend dependencies:

- `GET /api/v1/ubicaciones/`
- `GET /api/v1/comandas/abiertas/`
- `POST /api/v1/comandas/`

### 5. Order list

Purpose: support non-table and cross-table workflows.

Content and actions:

- Search by order number, table, customer, phone, or delivery reference.
- Filters: dine-in, takeaway, delivery, ready, needs payment, closed, cancelled.
- Sort: newest, oldest, promised time, readiness, table.
- Action to create a new order.

States:

- No matching orders.
- List partially stale while offline.
- Pagination/loading error with retry.

Backend dependencies:

- `GET /api/v1/comandas/abiertas/`
- Future: paged `GET /api/v1/comandas/`

### 6. New order setup

Purpose: collect required context before item capture.

Content and actions:

- Order mode: dine-in, takeaway, delivery.
- Table or location assignment for dine-in.
- Customer name/phone for takeaway and delivery.
- Delivery address, delivery notes, and promised time for delivery.
- Optional party size and server assignment.

Validation:

- Dine-in orders require an available/authorized table.
- Delivery orders require customer contact and address fields configured by the
  restaurant as mandatory.
- Duplicate active order warning when a table already has an open comanda.

Backend dependencies:

- `POST /api/v1/comandas/`
- `GET /api/v1/ubicaciones/`

### 7. Menu browse and search

Purpose: add sellable items to an order.

Content and actions:

- Category tabs or chips.
- Search by name, code, barcode, or alias.
- Item cards with price, availability, preparation route, image, and warnings.
- Favorites/recent items for rapid entry.
- Quantity stepper and quick-add action.

States:

- Menu snapshot unavailable.
- Item temporarily unavailable.
- Price changed since local snapshot.
- Stock warning where inventory validation is configured.

Backend dependencies:

- `GET /api/v1/registros-maestro/`
- `GET /api/v1/registros-maestro/{id}/venta/`
- Future dedicated menu snapshot endpoint recommended.

### 8. Item customization

Purpose: capture modifiers, notes, and preparation instructions.

Content and actions:

- Quantity.
- Modifier groups with min/max selection rules.
- Extras, exclusions, temperature/cooking preference, and free-text kitchen note.
- Price impact preview.
- Allergy or compliance warning if configured.

Validation:

- Required modifier group missing.
- Too many selections in a modifier group.
- Unsupported note for a preparation route.
- Item cannot be prepared at selected location.

Backend dependencies:

- `POST /api/v1/comandas/{id}/items/`
- Future menu/modifier contract.

### 9. Order detail

Purpose: act as the central order workspace.

Content and actions:

- Header: order number, mode, table/customer, status, elapsed/promised time.
- Grouped item list by state: draft, sent, in preparation, ready, delivered,
  cancelled/voided.
- Item detail, duplicate, quantity adjustment, notes, void/remove where allowed.
- Totals summary.
- Actions: add items, send to preparation, mark delivered, request payment,
  close/cancel subject to permission.

States:

- Draft order with no items.
- Pending send.
- Partially ready order.
- Payment pending or partially paid.
- Conflict when another user changed the order.

Backend dependencies:

- `GET/PATCH /api/v1/comandas/{id}/`
- `GET/POST /api/v1/comandas/{id}/items/`
- `POST /api/v1/comandas/{id}/enviar-a-preparacion/`
- `POST /api/v1/comandas/{id}/items/{item_id}/entregar/`
- `POST /api/v1/comandas/{id}/cerrar/`

### 10. Send-to-preparation confirmation

Purpose: prevent accidental submission and expose blocking conditions.

Content and actions:

- Summary of draft items being sent.
- Route preview by preparation area.
- Warnings for unavailable stock, unavailable stations, or missing modifiers.
- Confirm and cancel actions.

States:

- All items route successfully.
- Some items blocked and cannot be sent.
- Some items require manager override.
- Server accepted command but preparation queue refresh is delayed.

### 11. Preparation queue

Purpose: give kitchen/bar operators a compact work queue.

Content and actions:

- Station selector if the user has multiple preparation areas.
- Queue cards grouped by status: new, in progress, delayed, ready.
- Order number, table/customer, item count, priority, elapsed/promised time.
- Quick action to mark item ready.
- Detail action for instructions and modifiers.

States:

- No active preparation orders.
- Delayed or overdue order indicator.
- Backend disconnected; queue is read-only and stale.

Backend dependencies:

- `GET /api/v1/preparacion/ordenes/`
- `POST /api/v1/preparacion/ordenes/{id}/items/{item_id}/lista/`

### 12. Preparation order detail

Purpose: support accurate preparation of a routed order.

Content and actions:

- Items with quantities, modifiers, notes, allergens, and routing metadata.
- Mark item ready.
- Optional hold/unhold or unavailable action if backend supports it.
- Print/reprint ticket action if a printer adapter exists.

States:

- Item already marked ready by another operator.
- Order cancelled after entering queue.
- Station no longer authorized.

### 13. Ready items and handoff

Purpose: help service staff deliver or hand off completed items.

Content and actions:

- Ready item list by table/order/customer.
- Push/in-app notification deep links to this screen.
- Mark delivered/handed off.
- For delivery/takeaway: customer notification and pickup confirmation.

States:

- Item ready but order was transferred/merged.
- Customer notification failed.
- Delivery handoff requires payment first.

Backend dependencies:

- `GET /api/v1/comandas/abiertas/`
- `POST /api/v1/comandas/{id}/items/{item_id}/entregar/`

### 14. Payment detail

Purpose: collect payment for an order.

Content and actions:

- Itemized total, taxes, discounts, service charge, tips, paid amount, remaining
  balance.
- Payment methods: cash, card, transfer, voucher, mixed payments.
- Cash received and change due.
- Reference/authorization fields for external methods.
- Optional split by amount, seat, or items in a later phase.
- Confirm payment action.

Validation:

- Payment amount must be positive and not exceed remaining balance unless
  overpayment/change is allowed.
- Payment method must be enabled for the selected sucursal/caja.
- Card/transfer references required when configured.
- Order cannot close while sent items are not delivered unless override exists.

Backend dependencies:

- `POST /api/v1/notas-venta/{id}/pagos/`
- `POST /api/v1/comandas/{id}/cerrar/`

### 15. Payment result and receipt

Purpose: make final state clear and support customer receipt flow.

Content and actions:

- Success/failure status.
- Order closed/remaining balance summary.
- Receipt number or nota de venta reference.
- Print, email, SMS/WhatsApp share, or download receipt actions when supported.
- Return to table map/order list.

States:

- Payment accepted but receipt generation delayed.
- Payment provider accepted but backend close failed.
- Duplicate payment detected.
- Payment rejected with retry/change-method options.

### 16. Notification center

Purpose: provide an auditable list of actionable alerts.

Content and actions:

- Ready items.
- Orders overdue for preparation.
- Payment failures.
- Sync conflicts.
- Manager override requests.
- Customer notification failures.
- Mark read, filter, and deep link to affected order.

States:

- Empty inbox.
- Notification stream disconnected.
- Permission denied for the linked resource.

### 17. Settings and diagnostics

Purpose: help staff and support understand device/session state.

Content and actions:

- Signed-in user and active role/scope.
- Theme preview and restaurant branding.
- Push notification permission and registered device token.
- Last successful API call and sync time.
- Queued offline commands.
- App version, API version, request ID from last error.
- Sign out.

States:

- Token expired.
- Device revoked.
- Local storage quota warning.

### 18. Manager theme configuration

Purpose: allow the restaurant's visual identity to be configured without code
changes.

Content and actions:

- Restaurant logo upload/reference.
- Primary, secondary, tertiary, error, surface, and background color values.
- Light/dark preview using Material Design tokens.
- Contrast validation.
- Reset to default palette.

Validation:

- Minimum WCAG contrast for text/action colors.
- Unsupported image format or size.
- Color value parsing errors.

Backend dependency:

- Future restaurant branding/settings endpoint.

## In-app notifications

The client should maintain an in-app notification store for current-session and
recent actionable events.

Required notification types:

- Item ready for delivery/handoff.
- Whole order ready.
- Preparation order overdue.
- Payment accepted.
- Payment failed or requires attention.
- Order changed by another user.
- Sync command applied.
- Sync command rejected or requires review.
- Push permission/device registration problem.
- Backend degraded or offline.

Notification behavior:

- Display transient snackbars for low-risk confirmations.
- Display persistent banners for connectivity, sync backlog, payment ambiguity,
  and authorization problems.
- Badge navigation destinations with unresolved counts.
- Deep link each actionable notification to the exact order/item/payment.
- Deduplicate repeated events by event ID or resource/state tuple.
- Keep notifications readable after reconnect so staff can reconcile missed
  events.

## Push notifications

Push notifications are optional per device but recommended for mobile staff.

Required event categories:

- Ready item or order assigned to the user's scope.
- Overdue preparation or handoff alert.
- Customer pickup/delivery readiness confirmation failure.
- Manager override request.
- Device/session security event, such as forced sign-out.

Design requirements:

- Register device token after login and scope selection.
- Associate tokens with user, device ID, sucursal, ubicacion, and role.
- Respect browser/OS permission state and show clear recovery instructions.
- Include only minimal non-sensitive data in notification payloads.
- Use deep links that revalidate authorization after app open.
- Fall back to in-app polling or server-sent events when push is unavailable.
- Support quiet hours or per-role notification preferences in a later phase.

Backend capabilities needed:

- Device registration/revocation endpoint.
- Server event stream or polling endpoint for in-app notification sync.
- Push delivery provider integration.
- Notification audit table with delivery status and resource references.

## Customer notifications

Customer notifications should be opt-in and explicit. For the first phase,
customer-facing notification data can be captured by staff rather than exposed
through customer accounts.

Recommended channels:

- SMS.
- WhatsApp/message link where regionally appropriate.
- Email receipt.
- On-premise display or pager integration in a later phase.

Customer events:

- Order accepted.
- Order ready for pickup.
- Delivery dispatched.
- Payment receipt sent.

Error handling:

- Failed customer notifications should not block preparation state changes.
- The order should show a visible "customer notification failed" task.
- Staff should be able to retry or use an alternate contact method.

## Error and edge conditions

### Authentication and authorization

- Invalid credentials.
- Expired token.
- User disabled.
- User authenticated but not assigned to selected sucursal/ubicacion.
- User lacks permission for void, discount, close, payment, or manager override.
- Device revoked or session forced out.

UX requirements:

- Preserve unsent local draft data when re-authentication is required.
- Never show unauthorized resources after scope changes.
- Include support-friendly request IDs for server errors.

### Connectivity and offline

- Server unreachable on app launch.
- Network drops while editing an order.
- Network drops while sending to preparation.
- Network drops during payment submission.
- Local cache is stale.
- Offline command replay fails or conflicts.

UX requirements:

- Show a global online/offline banner.
- Label locally queued commands with pending status.
- Disable operations that cannot be safely queued, especially final payments and
  order close, unless the backend explicitly supports replay for that command.
- Provide retry and conflict-resolution paths.

### Order conflicts

- Two staff members edit the same order.
- Item price/menu availability changes after local selection.
- Table already has an active order.
- Item is cancelled after preparation starts.
- Preparation marks ready after order cancellation.
- Order close attempted with undelivered or unpaid items.

UX requirements:

- Refresh the affected order and show a concise conflict message.
- Preserve user-entered notes/quantities where safe.
- Require manager override for destructive state transitions.

### Payment failures

- Payment provider timeout.
- Duplicate submission/idempotency conflict.
- Declined card or invalid authorization.
- Cash drawer/printer integration failure after payment success.
- Payment accepted but receipt generation fails.
- Backend payment success but close-order command fails.

UX requirements:

- Treat unknown payment outcome as "needs review", not failed.
- Prevent blind repeated payment attempts when outcome is ambiguous.
- Show paid/remaining/unknown amounts separately.
- Provide a manager/audit path for reconciliation.

### Data and validation

- Missing required modifiers.
- Invalid delivery address/contact.
- Unsupported payment method for sucursal/caja.
- Unavailable menu item.
- Insufficient stock according to server validation.
- Server returns field-level validation errors.

UX requirements:

- Show field-level messages near the failing input.
- Keep a summary error at the top of long forms.
- Map backend `code` values to localized, actionable text.

## Authentication and security requirements

- Use Django `contrib.auth` token authentication for the first phase, consistent
  with the existing API roadmap.
- Store tokens in secure browser storage appropriate to the selected frontend
  architecture. If implemented as a browser app, prefer HTTP-only secure cookies
  when the backend supports them; otherwise use short-lived tokens and strict
  XSS controls.
- Require re-authentication for sensitive actions where configured, such as
  manager overrides, large discounts, or cash drawer close.
- Scope all loaded data by authenticated sucursal/ubicacion mappings.
- Do not trust client-calculated totals for final payment.
- Redact sensitive customer/payment information from logs and push payloads.
- Include audit metadata for user, device, request ID, and source screen on
  write operations where the backend accepts it.

## Material Design and theming

Use Material Design 3 as the design foundation.

Design token categories:

- Color: primary, on-primary, secondary, tertiary, surface, background, error,
  warning, success, outline, disabled.
- Typography: display, headline, title, body, label.
- Shape: small, medium, large corner radius tokens.
- Elevation: app bar, cards, dialogs, bottom sheets.
- Spacing: 4 px base grid with density adjustments for kitchen/tablet views.
- Motion: simple transitions for navigation, snackbars, dialogs, and status
  changes.

Restaurant-configurable theme:

- Primary brand color.
- Secondary/accent color.
- Logo.
- Light/dark default.
- Optional high-contrast mode.
- Status color overrides only if contrast remains valid.

Default status color semantics:

- Available/open: neutral/surface.
- In progress/preparing: primary.
- Ready: success.
- Attention/overdue: warning.
- Error/blocked: error.
- Paid/closed: secondary or neutral success variant.

Critical design rules:

- Color must never be the only status indicator; include labels/icons.
- Kitchen queue typography should prioritize distance readability.
- Touch targets should be at least 48 x 48 dp.
- Dialogs for destructive actions must state the consequence and affected order.
- Payment screens should be calm and explicit; avoid auto-dismissing ambiguous
  payment results.

## Accessibility and localization

- Meet WCAG 2.1 AA contrast for configured themes.
- Support keyboard navigation for desktop/tablet stations.
- Provide semantic labels for screen readers.
- Do not rely only on sound or color for notifications.
- Support Spanish-first text with an English translation path.
- Format currency, dates, and phone/address fields by restaurant locale.
- Keep iconography paired with text for critical actions.

## Data model concepts needed by the frontend

The frontend should receive stable DTOs even if backend persistence spans legacy
tables and high-level support tables.

Recommended client-facing resources:

- `UserSession`
- `DeviceRegistration`
- `RestaurantTheme`
- `MenuSnapshot`
- `MenuCategory`
- `MenuItem`
- `ModifierGroup`
- `ModifierOption`
- `Comanda`
- `ComandaItem`
- `PreparationOrder`
- `PreparationOrderItem`
- `Payment`
- `NotificationEvent`

Recommended common fields:

- `id`
- `display_id`
- `status`
- `created_at`
- `updated_at`
- `version` or `etag`
- `sucursal_id`
- `ubicacion_id`
- `request_id` on mutation results

## API gaps and recommendations

The existing API roadmap already identifies the core comanda endpoints. The
frontend will also benefit from these additional contracts:

```text
GET  /api/v1/menu/snapshot/
GET  /api/v1/theme/
GET  /api/v1/notifications/
POST /api/v1/notifications/{id}/read/
POST /api/v1/devices/register/
POST /api/v1/devices/revoke/
GET  /api/v1/realtime/events/        # SSE, websocket, or long-poll contract
GET  /api/v1/payments/methods/
GET  /api/v1/comandas/{id}/totals/
POST /api/v1/comandas/{id}/void/
POST /api/v1/comandas/{id}/discounts/
```

Recommended backend behaviors:

- Idempotency keys for order item creation, send-to-preparation, payment, and
  close operations.
- Version/ETag checks on mutable resources.
- Explicit state machines for comanda, item, preparation order, and payment.
- Dedicated read model for active order dashboards.
- Notification event table with resource links and read state.
- Theme endpoint scoped by restaurant/sucursal.

## State machines

### Comanda

```text
draft -> open -> sent_to_preparation -> partially_ready -> ready
      -> partially_delivered -> delivered -> payment_pending
      -> partially_paid -> paid -> closed

Any non-closed state may move to cancelled/voided with permission and audit.
```

### Comanda item

```text
draft -> sent -> in_preparation -> ready -> delivered
draft/sent -> cancelled
ready/delivered -> void_requested -> voided (manager/audit path)
```

### Preparation item

```text
queued -> in_progress -> ready
queued/in_progress -> held
queued/in_progress -> cancelled
```

### Payment

```text
draft -> submitted -> accepted -> posted
submitted -> declined
submitted -> unknown_outcome -> needs_review
accepted/posted -> refunded_or_reversed (future)
```

## Offline behavior

Align with `docs/offline_sync_spec.md`.

Cacheable:

- Authenticated user profile after login.
- Restaurant theme.
- Menu snapshot.
- Table/location list.
- Last known open orders for display with stale labels.

Queueable only with idempotency and backend replay support:

- Create order.
- Add draft items.
- Update draft notes/modifiers.

Require online confirmation:

- Send to preparation.
- Mark ready/delivered if the backend cannot safely replay it.
- Payment submission.
- Close order.
- Manager override.

UX requirements:

- Every offline-created order/item gets a temporary local ID until mapped to a
  server ID.
- Show pending sync counts in app shell.
- Keep failed replay commands visible until resolved.
- Prevent the user from mistaking local drafts for kitchen-accepted orders.

## Observability and support

- Capture frontend error logs with user, device, route, order ID, and request ID.
- Track key workflow timings: order opened, sent to prep, item ready, delivered,
  payment submitted, payment confirmed.
- Track notification delivery/open events.
- Track offline duration and command replay outcomes.
- Provide a diagnostics export for support without exposing secrets or full
  payment data.

## Initial milestone recommendation

### Milestone 1: staff order-taking MVP

- Sign in and scoped session.
- Theme loading with Material default fallback.
- Table map/order list.
- New order setup.
- Menu browse/search.
- Item customization.
- Order detail.
- Send to preparation.
- In-app ready notifications via polling.
- Ready item handoff.

### Milestone 2: preparation and payments

- Preparation queue/detail screens.
- Payment detail/result screens.
- Receipt action placeholders.
- Stronger order/payment error states.
- Notification center.

### Milestone 3: PWA operations

- Push notification device registration.
- Offline cache for menu/theme/table data.
- Safe queued draft mutations.
- Diagnostics screen.
- Customer SMS/WhatsApp/email notification integration.

### Milestone 4: manager configuration

- Theme configuration UI.
- Role notification preferences.
- Override flows.
- Expanded analytics and service dashboard.

## Acceptance criteria for the first frontend release

- A waiter can sign in, select scope, create a dine-in order, add items, send
  them to preparation, receive a ready notification, mark items delivered, and
  reach a payment-ready state.
- A kitchen/bar user can see routed items and mark them ready.
- A cashier can record at least one supported payment method and see a clear
  success/failure/unknown result.
- The app clearly distinguishes draft, sent, ready, delivered, paid, offline,
  pending sync, and error states.
- Theme colors can be loaded from configuration or fall back to a valid Material
  palette.
- All mutation failures show actionable messages and request IDs when available.
- Push notification absence does not block the workflow; in-app notifications
  remain available.
