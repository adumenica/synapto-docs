# Incidents Page — Container-Free Redesign Spec
**Date:** 2026-04-07
**Phase:** 3 of the Container-Free + Bento UI overhaul
**Scope:** `frontend/src/pages/Incidents.tsx` (full rewrite), new `frontend/src/components/incidents/IncidentDetailPanel.tsx`, route update in `frontend/src/App.tsx`

---

## Overview

Replace the card-based expandable incident list with a container-free row list and a push-split detail panel. Clicking a row narrows the list to ~45% and slides in a scrollable detail panel on the right. The design follows the container-free direction established in Phases 1–2 — no card wrappers, whitespace and typography do the organizational work.

---

## Approach

Single-file rewrite of `Incidents.tsx` + a new `IncidentDetailPanel.tsx` component. The list and panel share the same route family: `/incidents` (list only) and `/incidents/:id` (list + panel). `Incidents.tsx` reads `useParams()` — if `:id` is present it renders the push-split layout. No new API endpoints.

---

## Page Structure

```
/incidents (no selection)
┌─────────────────────────────────────────┐
│  INCIDENTS header + count               │
│  ──────────────────────────────────     │ ← filter bar border-b
│  Search  │  Status ▾  │  Severity ▾    │
│  ──────────────────────────────────     │
│  ▌ High CPU — prod-db-01   CRITICAL 2m │
│  ▌ Memory leak — api-svc-3 HIGH     5m │
│  ▌ Disk space — storage-02 MEDIUM  12m │
└─────────────────────────────────────────┘

/incidents/:id (row selected)
┌───────────────────┬─────────────────────┐
│  LIST (45%)       │  DETAIL PANEL (55%) │
│  ▌ High CPU  ···  │  Memory leak        │
│  ▌ Memory ▶  ···  │  HIGH · OPEN · 5m   │ ← selected row highlighted
│  ▌ Disk      ···  │  ─────────────────  │
│                   │  DETAILS            │
│                   │  EXECUTIONS         │
│                   │  AI ANALYSIS        │
│                   │  TIMELINE           │
└───────────────────┴─────────────────────┘
```

---

## Section 1 — Page Header

**No card wrapper.** Header sits directly on page background.

- Title: `INCIDENTS` in `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground`
- Count: `incidents.length` in `text-5xl font-black tracking-tight` (total loaded, not filtered)
- No subtitle paragraph

---

## Section 2 — Filter Bar

**No card wrapper.** Inline `flex items-center gap-3` row sitting on the page background.

- `border-b border-[hsl(var(--border)/0.4)]` below the filter row separates it from the list
- Search input: borderless, `bg-transparent`, left-padded with `Search` icon
- Status select: borderless, `bg-transparent`
- Severity select: borderless, `bg-transparent`
- All three: `text-sm`, `focus:outline-none focus:ring-0`, placeholder color `text-muted-foreground`

---

## Section 3 — Incidents List

**No card wrappers.** Each row is a full-bleed horizontal strip.

**Layout when no row selected:** full width list.

**Layout when a row is selected:** `grid grid-cols-[45%_55%]` — list column + detail panel column. List column gets `border-r border-[hsl(var(--border)/0.4)]`.

**Row anatomy:**
- Container: `group flex items-center gap-4 py-3.5 pl-4 pr-3 cursor-pointer hover:bg-muted/30 transition-colors`
- Left border: `border-l-[3px] border-l-{color}` — severity mapping:
  - `critical` → `border-l-red-500`
  - `high` → `border-l-orange-400`
  - `medium` → `border-l-yellow-400`
  - `low` → `border-l-blue-400`
  - default → `border-l-gray-400`
- Title: `text-sm font-semibold text-foreground truncate`
- Sub-row: `text-xs text-muted-foreground` — monospace ID + separator + timestamp
- Right side: existing `Badge` component for status + `ChevronRight` icon (`h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100`)
- **Active row** (id matches URL param): `bg-[hsl(var(--panel)/0.6)]` background highlight, `border-l-primary-500` border override

**Click behavior:** `navigate('/incidents/' + incident.id)`

**Loading state:** 6 rows of skeleton — each `flex justify-between h-12 pl-4 border-l-[3px] border-l-muted`:
- `Skeleton className="h-4 w-2/3"`
- `Skeleton className="h-4 w-1/5"`

**Empty state:** `<p className="py-8 text-sm text-muted-foreground">No incidents match your filters</p>` — no EmptyState component.

---

## Section 4 — Detail Panel

**Component:** `frontend/src/components/incidents/IncidentDetailPanel.tsx`

**Entry animation:** `animate-in slide-in-from-right-4 duration-200`

**Panel header:**
- Title: `text-lg font-bold text-foreground`
- Severity + status: inline `text-xs` labels, same color mapping as rows
- Close button: `X` (Lucide `X` icon), `h-4 w-4`, top-right, `onClick={() => navigate('/incidents')}`

**Scrolling:** `overflow-y-auto h-full` — panel scrolls independently from list.

**Section pattern:** Each section separated by `border-t border-[hsl(var(--border)/0.4)]`. Section label: `text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground pt-4 pb-2`.

### Sub-section: DETAILS
- Severity badge (existing `Badge`) + status badge side by side
- Created at: `text-xs text-muted-foreground`
- Incident ID: `font-mono text-xs text-muted-foreground`
- Description: `text-sm text-foreground leading-relaxed` (if present)

### Sub-section: AI ANALYSIS
Data source: `incident.meta_data?.ai_analysis`

- Root cause: `text-sm font-medium` in a `border-l-2 border-purple-500 pl-3` accent block
- Analysis summary: `text-sm text-muted-foreground`
- Remediation plan: numbered list, `text-sm`, each step prefixed with `text-xs font-mono bg-muted px-1.5 rounded`
- Confidence score: `text-sm font-bold text-green-600 dark:text-green-400`
- **Loading / no data state:** `<Loader className="h-4 w-4 animate-spin text-purple-400" />` + `"Analysis in progress..."`

### Sub-section: EXECUTIONS
`executionsApi.list()` does not currently support `incident_id` filtering. Render empty with a `{/* TODO: wire when executionsApi.list supports incident_id filter */}` comment.

Empty state: `<p className="text-sm text-muted-foreground py-2">No executions yet</p>`

Row shape (for when the API is wired): script name (`text-sm font-medium`) + status dot + timestamp (`text-xs text-muted-foreground`)

Status dot colors:
- `success` → `bg-green-500`
- `failed` → `bg-red-500`
- `running` → `bg-blue-500 animate-pulse`
- default → `bg-gray-400`

### Sub-section: TIMELINE
`eventsApi.list()` does not currently support `incident_id` filtering. Render empty with a `{/* TODO: wire when eventsApi.list supports incident_id filter */}` comment.

Empty state: `<p className="text-sm text-muted-foreground py-2">No events linked</p>`

Row shape (for when the API is wired): timestamp (`text-xs font-mono text-muted-foreground`) + source + alert name (`text-sm`).

---

## Routing

Add a nested route in `frontend/src/App.tsx`:

```tsx
<Route path="incidents" element={<Incidents />} />
<Route path="incidents/:id" element={<Incidents />} />
```

`Incidents.tsx` uses `const { id } = useParams()` to detect whether a detail panel should be shown.

---

## Data Queries

| Query | Change |
|---|---|
| `incidentsApi.list({ limit: 100, status })` | Unchanged — refetchInterval 5000ms kept |
| `incidentsApi.get(id)` | New — fetches full incident detail for the panel. `enabled: !!id` |
| `executionsApi.list({ limit: 20 })` | Not used yet — API doesn't support `incident_id` filter. Executions section renders empty with TODO comment |
| `eventsApi.list({ limit: 20 })` | Not used yet — API doesn't support `incident_id` filter. Timeline section renders empty with TODO comment |

---

## Files Changed

| File | Action |
|---|---|
| `frontend/src/pages/Incidents.tsx` | Full rewrite |
| `frontend/src/components/incidents/IncidentDetailPanel.tsx` | New component |
| `frontend/src/App.tsx` | Add `incidents/:id` route |

**Unchanged:**
- `frontend/src/services/api.ts` (all needed endpoints already exist)
- All other pages and components

---

## Out of Scope

- Script output display in the detail panel (future phase)
- Pass/fail result details per execution (future phase)
- Inline incident status editing from the panel
- Mobile responsive stacking (single column on small screens — handled by Tailwind responsive prefixes if needed but not required this phase)
