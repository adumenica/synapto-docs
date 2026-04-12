# UI Features: CI/CD Risk, Action Catalogue, Service Health, Real-time Incidents

## Goal

Add four missing UI capabilities that close the gap between the AIOps backend (built in the previous session) and the frontend: a CI/CD risk assessment page, an Action Catalogue page, a live service health widget on the Dashboard, and real-time incident updates via SSE.

## Architecture

One backend addition (SSE endpoint) and five frontend additions. All frontend additions follow existing patterns: React Query for data, TanStack Table for tables, Recharts for charts, React Hook Form + Zod for forms, existing `components/ui/` primitives.

**Backend:**
- `GET /api/v1/incidents/stream` — SSE endpoint on api-gateway that reads from the Redis `events` stream and pushes new incident events as `text/event-stream`. Orchestration-layer already writes to Redis; no other backend changes needed.

**Frontend:**
- New page `/cicd` — CI/CD Risk Assessment
- New page `/catalogue` — Action Catalogue
- New Dashboard widget — `ServiceHealthWidget`
- New hook — `useIncidentStream` (SSE + React Query cache invalidation)
- Incident detail panel — promotion banner

---

## Feature 1: CI/CD Risk Assessment Page (`/cicd`)

**Route:** `/cicd`, top-level sidebar item (rocket icon, label "CI/CD Risk")

**Layout:** Two-column. Left column = form. Right column = live result panel. Result recalculates on every field change via debounced `POST /api/v1/cicd/risk-assessment`. No submit button.

**Form fields** (React Hook Form + Zod):
- `service_name` — text input
- `environment` — select: development / staging / production
- `changed_files` — number input (count, mapped to a generated array of that length for the API)
- `affected_services` — multi-value tag input (comma-separated, stored as array)
- `has_db_migration` — toggle switch
- `is_off_hours` — toggle switch
- `rollback_available` — toggle switch (default: true)
- `commit_message` — optional textarea

**Result panel** (right column):
- Risk score as large number (0.0–1.0)
- Risk level badge: low (green) / medium (amber) / high (orange) / critical (red)
- "Manual approval required" warning when `requires_manual_approval: true`
- Risk factors list (bulleted)
- Recommendation text block
- Empty state when no fields filled yet: "Fill in deployment details to see risk score"

**API:** `POST /api/v1/cicd/risk-assessment` — authenticated, body matches `CICDDeployment` schema.

**Files:**
- Create: `frontend/src/pages/CICDRisk.tsx`
- Create: `frontend/src/components/cicd/RiskResultPanel.tsx`
- Modify: `frontend/src/App.tsx` — add route
- Modify: `frontend/src/components/Layout.tsx` — add sidebar nav item

---

## Feature 2: Action Catalogue Page (`/catalogue`)

**Route:** `/catalogue`, top-level sidebar item (trophy icon, label "Action Catalogue")

**Layout:** Filterable table (TanStack Table) with an inline right-side drawer. Clicking a row opens the drawer; clicking again or pressing Escape closes it. The table does not shrink — the drawer overlays from the right edge.

**Table columns:** Name, Category, Language, Promoted (relative date), Actions (View button)

**Filters:** Search (name), Category dropdown, Language dropdown

**Drawer content:**
- Script name and metadata (category, language, promoted date)
- Monaco Editor in read-only mode showing script content
- "Source incident" link → opens incident detail panel
- "Remove from Catalogue" button (sets `is_gold_standard: false` via `PATCH /api/v1/knowledge/scripts/{id}`)

**Promotion banner on IncidentDetailPanel:**
- Rendered when `incident.meta_data.promotion_eligible === true`
- Amber/yellow callout banner at top of the panel
- Text: "This incident was resolved by AI. Promote the fix to the Action Catalogue?"
- Button: "Promote to Catalogue" → `POST /api/v1/incidents/{id}/promote`
- On success: banner disappears, toast "Promoted to Action Catalogue"
- On error: toast with error message

**API:**
- `GET /api/v1/knowledge/scripts?is_gold_standard=true` — list catalogue scripts. **Note:** the `list_scripts` endpoint in knowledge-layer does not yet support this filter; the implementation plan must add `is_gold_standard: Optional[bool]` as a query param to `GET /scripts` in `backend/knowledge-layer/main.py` before the frontend can use it.
- `PATCH /api/v1/knowledge/scripts/{id}` — remove from catalogue (already implemented)
- `POST /api/v1/incidents/{id}/promote` — promote incident fix (already implemented)

**Files:**
- Create: `frontend/src/pages/ActionCatalogue.tsx`
- Create: `frontend/src/components/catalogue/ScriptDrawer.tsx`
- Modify: `frontend/src/components/incidents/IncidentDetailPanel.tsx` — add promotion banner
- Modify: `frontend/src/services/api.ts` — add catalogue and promote API calls
- Modify: `frontend/src/App.tsx` — add route
- Modify: `frontend/src/components/Layout.tsx` — add sidebar nav item

---

## Feature 3: Service Health Widget (Dashboard)

**Placement:** Full-width card added to `Dashboard.tsx`, positioned below the existing summary stats row and above the incident list.

**Data source:** `GET /health` on api-gateway — already returns `{ services: { [name]: { status, response_time_ms } } }`. Polled every 15s via React Query (`refetchInterval: 15000`).

**Widget layout:**
- Card header: "Service Health" + "N/13 healthy" summary badge + "updated Xs ago" timestamp
- Table rows: one per service. Columns: Service name, Status dot (green/red), Sparkline (last 10 response times using Recharts `LineChart` with `dot={false}`), Avg response time
- Sparkline data stored in a rolling 10-item array managed in component state; updated on each poll
- Down services highlighted with red row background
- No click interaction needed — read-only status view

**Files:**
- Create: `frontend/src/components/dashboard/ServiceHealthWidget.tsx`
- Modify: `frontend/src/pages/Dashboard.tsx` — add widget

---

## Feature 4: Real-time Incident Updates (SSE)

**Backend — SSE endpoint:**
- `GET /api/v1/incidents/stream` on api-gateway
- Reads from Redis `events` stream using `XREAD BLOCK 30000` (30s blocking read, then loop)
- Filters for `incident.*` event types
- Pushes `data: {type, incident_id, status}\n\n` as SSE
- Requires authentication: validates `Authorization: Bearer` header on connection
- Returns `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `X-Accel-Buffering: no`

**Frontend — `useIncidentStream` hook:**
- Creates an `EventSource` connection to `/api/v1/incidents/stream` with auth token in URL param (`?token=...`) since `EventSource` does not support custom headers
- On message: calls `queryClient.invalidateQueries(['incidents'])` to trigger a refetch
- On new incident event specifically: shows a toast "New incident detected"
- Auto-reconnects on error with 5s delay
- Closes connection on component unmount

**Incidents page changes:**
- Remove `refetchInterval: 5000` from the incidents React Query call
- Add `useIncidentStream()` call at the top of the component

**Files:**
- Modify: `backend/api-gateway/main.py` — add `GET /api/v1/incidents/stream` SSE endpoint
- Create: `frontend/src/hooks/useIncidentStream.ts`
- Modify: `frontend/src/pages/Incidents.tsx` — remove polling, add `useIncidentStream()`

---

## Component Patterns

All new components follow the existing codebase conventions:
- Tailwind CSS for styling, `cn()` from `clsx`/`tailwind-merge` for conditional classes
- Radix UI primitives from `components/ui/` for interactive elements
- React Query for all server state
- Loading states: `Skeleton` component from `components/ui/`
- Error states: inline error message with retry button
- Empty states: `EmptyState` component from `components/ui/`

---

## Navigation Changes

Two new entries added to the main sidebar nav in `Layout.tsx`, positioned between Incidents and SOP Library:

```
🚀  CI/CD Risk     → /cicd
🏆  Action Catalogue → /catalogue
```

Both are accessible to all authenticated users (no role restriction).

---

## Out of Scope

- Editing scripts from the Action Catalogue (read-only viewer)
- Historical CI/CD assessment history / audit log
- WebSocket-based real-time (SSE chosen for simplicity)
- Mobile-responsive layout (matches existing app behaviour)
