# Analytics Page — Bento Redesign Spec
**Date:** 2026-04-08
**Phase:** 4 of the Container-Free + Bento UI overhaul
**Scope:** `frontend/src/pages/Analytics.tsx` (full rewrite)

---

## Overview

Replace the card-based Analytics page with a container-free, typography-first layout. Three zones stack vertically: a floating metric band, a period label separator, and a three-column bento grid (pie chart | bar chart | recommendations). No card wrappers — whitespace and typography do the organizational work.

---

## Approach

Single-file rewrite of `Analytics.tsx`. Existing `PieChart`, `BarChart`, and `CustomChartTooltip` are reused unchanged. Same two queries as current page. No new API endpoints.

---

## Page Structure

```
┌─────────────────────────────────────────────────┐
│  METRIC BAND (no container)                     │
│  94.2%  ·  42  ·  847  ·  7.2m                 │
│  ─────────────────────────────── border-b       │
│  LAST 30 DAYS                                   │
│  ─────────────────────────────── border-t       │
├──────────────┬──────────────┬────────────────────┤
│  PIE CHART   │  BAR CHART   │  RECOMMENDATIONS   │
│  (1fr)       │  (1fr)       │  (1.2fr)           │
└──────────────┴──────────────┴────────────────────┘
```

---

## Section 1 — Metric Band

**No container.** Numbers float directly on the page background.

**Layout:** `flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]`

**Four metrics:**

| Metric | Value source | Typography |
|---|---|---|
| Success rate | `analytics?.success_rate?.toFixed(1)` + `%` suffix | `text-5xl font-black tracking-tight` number + `text-2xl text-primary-500` suffix |
| Total incidents | `analytics?.total_incidents` | `text-5xl font-black tracking-tight` |
| Total executions | `analytics?.total_executions` | `text-5xl font-black tracking-tight` |
| Avg resolution | `analytics?.average_resolution_time_minutes?.toFixed(0)` + `m` suffix, or `—` if undefined | `text-5xl font-black tracking-tight` number + `text-2xl text-muted-foreground` suffix |

**Labels beneath each number:** `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground`

**Loading state:** `Skeleton className="h-12 w-20"` per number, `Skeleton className="h-3 w-16"` per label.

---

## Section 2 — Period Label

Between metric band and bento grid.

```tsx
<p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground py-4 border-t border-[hsl(var(--border)/0.4)]">
    Last 30 days
</p>
```

---

## Section 3 — Bento Grid

**Layout:** `grid grid-cols-[1fr_1fr_1.2fr] gap-6 items-start`

**No card wrappers** on any cell. Section labels use: `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mb-4`

### Left Cell — Incident Distribution (Pie Chart)

- Section label: `INCIDENT TYPES`
- Existing `PieChart` from current `Analytics.tsx` — reused with zero changes to chart config
- Container: `h-64 w-full`
- Same `COLORS` array: `['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']`
- Same `CustomChartTooltip` and `Legend`
- Chart renders directly on page background (no card)

### Middle Cell — Incident Volume (Bar Chart)

- Section label: `INCIDENT VOLUME`
- Existing `BarChart` from current `Analytics.tsx` — reused with zero changes to chart config
- Container: `h-64 w-full`
- Same gradient fill, `CartesianGrid`, `XAxis`, `YAxis`, `CustomChartTooltip`

### Right Cell — Recommendations

- Section label: `RECOMMENDATIONS`
- Container-free list, no card wrapper
- Each recommendation row:
  - Container: `py-3 pl-3 pr-2 border-l-[3px]`
  - Left border color by priority:
    - `high` → `border-l-red-500`
    - `medium` → `border-l-yellow-400`
    - `low` → `border-l-blue-400`
    - default → `border-l-gray-400`
  - Top line: `Badge` component (variant by priority: `high`→`danger`, `medium`→`warning`, `low`→`info`) + `text-xs text-muted-foreground` type label
  - Message: `text-sm text-foreground mt-1 leading-relaxed`
- Empty state: `<p className="text-sm text-muted-foreground py-2">No recommendations at this time</p>`
- Loading state: 3 rows of `Skeleton className="h-16 w-full border-l-[3px] border-l-muted pl-3"`

---

## Data Queries

| Query | Change |
|---|---|
| `analyticsApi.get({ days: 30 })` | Unchanged |
| `analyticsApi.recommendations()` | Unchanged |

---

## Files Changed

| File | Action |
|---|---|
| `frontend/src/pages/Analytics.tsx` | Full rewrite |

**Unchanged:**
- `frontend/src/components/CustomChartTooltip.tsx`
- `frontend/src/services/api.ts`
- All other files

---

## Out of Scope

- Day range selector (always 30 days this phase)
- Resolution time trend chart (no historical time-series data available from API)
- Mobile responsive stacking (Tailwind responsive prefixes handle it if needed, not required this phase)
