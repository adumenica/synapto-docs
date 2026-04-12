# Dashboard Editorial Bento — Design Spec
**Date:** 2026-04-07
**Phase:** 2 of the Container-Free + Bento UI overhaul
**Scope:** `frontend/src/pages/Dashboard.tsx` + deletion of `DashboardGrid.tsx`, `StatCards.tsx`

---

## Overview

Replace the configurable `react-grid-layout` widget grid with a fixed editorial layout. Three zones stack vertically: a typography-first metric band, a container-free incident list, and a two-column bottom row with Active Flows and charts. The design follows the "container-free" direction established in Phase 1 — no card wrappers around sections, whitespace and typography do the organizational work.

---

## Approach

Option A — Single-file rewrite of `Dashboard.tsx`. `DashboardGrid.tsx` and `StatCards.tsx` are deleted. `ActiveFlows.tsx` and `RecentActivity.tsx` are reused unchanged. `react-grid-layout` is removed from `package.json`.

---

## Page Structure

```
┌─────────────────────────────────────────┐
│  METRIC BAND (no container)             │
│  94.2%  ·  12  ·  847  ·  ↑ above      │
├─────────────────────────────────────────┤
│  INCIDENT LIST (no container)           │
│  ▌ High CPU — prod-db-01      2m ago    │
│  ▌ Memory leak — api-svc-3    5m ago    │
│  ▌ Disk space — storage-02   12m ago    │
├─────────────────────────────────────────┤ ← border-t separator
│  ACTIVE FLOWS   │  INCIDENT TYPES       │
│  (1fr)          │  (bar chart)  (1.5fr) │
│                 ├───────────────────────│
│                 │  RESOLUTION TREND     │
│                 │  (line chart)         │
└─────────────────────────────────────────┘
```

---

## Section 1 — Metric Band

**No container.** Numbers float directly on the page background.

**Layout:** `flex items-baseline gap-10 pb-8 border-b border-muted/40`

**Four metrics:**

| Metric | Value source | Typography |
|---|---|---|
| Resolution rate | `analytics?.success_rate` + `%` suffix | `text-5xl font-black tracking-tight` + `text-2xl text-primary-500` suffix |
| Active incidents | `incidents.length` (query limit 50) | `text-5xl font-black tracking-tight` |
| Total executions | `analytics?.total_executions` | `text-5xl font-black tracking-tight` |
| Delta indicator | `analytics?.success_rate > 90 ? '↑ above target' : '↓ below target'` | `text-xl font-semibold` — green if above, red if below |

**Labels beneath each number:** `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground`

**Loading state:** `Skeleton` at each number position — `h-12 w-20` per number, `h-4 w-16` per label.

---

## Section 2 — Incident List

**No card wrapper.** Rows render directly on page background.

**Section header:**
```
ACTIVE INCIDENTS                              View all →
```
- Label: `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground`
- "View all →" link: `text-xs text-primary-500 hover:underline`, navigates to `/incidents`
- `border-b border-muted/40` below header

**Row anatomy:**
- Left border: `3px solid` — color by severity: `critical` → `red-500`, `high` → `orange-400`, `medium` → `yellow-400`, `low` → `blue-400`, default → `gray-400`
- Title: `text-sm font-semibold text-foreground`
- Status: existing `Badge` component
- Timestamp: `text-xs text-muted-foreground`
- Chevron: `ChevronRight` from Lucide, `h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100`
- Row: `group flex items-center gap-3 py-3.5 pl-4 pr-2 cursor-pointer hover:bg-muted/40 transition-colors`
- Click: `navigate('/incidents')`

**Data:** `incidents` query with `limit: 10`. Display max 8 rows.

**Empty state:** `<p className="py-6 text-sm text-muted-foreground">No active incidents</p>` — no EmptyState component.

**Loading state:** 5 rows of `flex justify-between h-12` skeletons — `Skeleton className="h-4 w-2/3"` + `Skeleton className="h-4 w-1/4"`.

---

## Section 3 — Bottom Row

**Layout:** `grid grid-cols-[1fr_1.5fr] gap-6 items-start pt-6`

**Separator:** `border-t border-muted/50` between incident list and bottom row.

### Left — Active Flows

- `ActiveFlows` component rendered as-is (no visual changes)
- Section header above: `ACTIVE FLOWS` label + live pulsing dot
  - Dot: `h-2 w-2 rounded-full` — `bg-green-500 animate-pulse` when flows exist, `bg-muted` when empty
- No card wrapper

### Right — Two stacked charts

**Top: Incident Distribution**
- Existing `BarChart` (Recharts) from current Dashboard, data from `analytics?.top_incident_types`
- Section header: `INCIDENT TYPES` label
- No card wrapper — `ResponsiveContainer` fills width

**Bottom: Resolution Trend**
- Existing `LineChart` (Recharts) from current Dashboard
- Data: `analytics?.average_resolution_time_minutes` exists on API response — use as a single reference value with a label. If the field is `undefined`, fall back to hard-coded 7-day sample data with a `// TODO: wire to real data` comment. No new API endpoints in this phase.
- Section header: `RESOLUTION TREND` label

**Chart background:** matches page background (no card container), axes and grid lines use `stroke="currentColor" strokeOpacity={0.15}` for muted appearance.

---

## Data Queries

Same four queries as current Dashboard, with one change:

| Query | Change |
|---|---|
| `incidentsApi.list({ limit: 10 })` | Change limit to `50` (to show accurate count in metric band) |
| `eventsApi.list({ limit: 10 })` | Unchanged |
| `analyticsApi.get({ days: 7 })` | Unchanged |
| `executionsApi.list({ limit: 10 })` | Unchanged |

---

## Files Changed

| File | Action |
|---|---|
| `frontend/src/pages/Dashboard.tsx` | Full rewrite |
| `frontend/src/components/dashboard/DashboardGrid.tsx` | Delete |
| `frontend/src/components/dashboard/widgets/StatCards.tsx` | Delete |
| `frontend/package.json` | Remove `react-grid-layout` and `@types/react-grid-layout` |

**Unchanged:**
- `frontend/src/components/dashboard/ActiveFlows.tsx`
- `frontend/src/components/dashboard/widgets/RecentActivity.tsx`
- `frontend/src/components/CustomChartTooltip.tsx`
- All other dashboard components

---

## Out of Scope

- Popovers on incident rows (future phase — user confirmed navigate-only for now)
- New API endpoints for resolution trend historical data
- Dark mode changes (existing dark: classes continue to work)
- Mobile responsive adjustments (single column stacking handled by Tailwind responsive prefixes)
