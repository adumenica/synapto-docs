# Events + Executions — Container-Free Redesign Spec
**Date:** 2026-04-08
**Phase:** 5 of the Container-Free + Bento UI overhaul
**Scope:** `frontend/src/pages/Events.tsx` and `frontend/src/pages/Executions.tsx` (full rewrites)

---

## Overview

Replace card-based stat sections on both Events and Executions pages with a container-free, typography-first metric band — the same pattern established in Analytics (Phase 4). No new components, no new API endpoints. Two independent single-file rewrites.

---

## Approach

- Full rewrite of `Events.tsx` and `Executions.tsx`
- `DataTable`, `EventModal`, `ExecutionDetail`, `DataTableToolbar` are reused unchanged
- Metric band: `text-5xl font-black` numbers, `text-[11px] uppercase tracking-[0.18em] text-muted-foreground` labels, `border-b border-[hsl(var(--border)/0.4)]` separator
- No period label on either page — data is live (auto-refetch), not time-windowed

---

## Page Structure (both pages)

```
┌─────────────────────────────────────────────────┐
│  METRIC BAND (no container)                     │
│  N  ·  N  ·  N  [· N]                          │
│  ─────────────────────────────── border-b       │
│  [toolbar: search + filters + optional button]  │
│  ┌─────────────────────────────────────────┐    │
│  │  DataTable                              │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

## Events.tsx

### Metric Band

**Layout:** `flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]`

| Metric | Value | Color |
|---|---|---|
| Total Events | `eventsData?.length ?? 0` | `text-foreground` |
| Critical | `eventsData?.filter(e => e.severity === 'critical').length ?? 0` | `text-red-400` |
| Sources | `new Set((eventsData ?? []).map(e => e.source)).size` | `text-blue-400` |

**Number typography:** `text-5xl font-black tracking-tight` (color per above)
**Label typography:** `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1`
**Loading:** 3 skeleton groups — `Skeleton className="h-12 w-20"` + `Skeleton className="h-3 w-16"` per metric

### Hero Card Removed

The "Signal operations" hero card (heading, prose description, `Radar` icon, badge) is removed entirely.

### Create Event Button

Moved from the hero card into `DataTableToolbar` as a child — rendered to the right of the filter selects, same as before functionally.

```tsx
<DataTableToolbar ...>
  {/* severity filter */}
  {/* source filter */}
  <Button onClick={() => setIsModalOpen(true)}>
      <Bell className="h-4 w-4" />
      Create event
  </Button>
</DataTableToolbar>
```

### DataTable + EventModal

Columns, `EventModal`, `handleCreateEvent`, `handleExport`, `refetchInterval: 5000`, `useDebounce` — all unchanged.

---

## Executions.tsx

### Metric Band

**Layout:** `flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]`

| Metric | Value | Color |
|---|---|---|
| Total | `executions?.length ?? 0` | `text-foreground` |
| Success | `executions?.filter(e => e.status === 'success').length ?? 0` | `text-green-400` |
| Failed | `executions?.filter(e => ['failed','timeout'].includes(e.status)).length ?? 0` | `text-red-400` |
| Running | `executions?.filter(e => e.status === 'running').length ?? 0` | `text-blue-400` |

**Number typography:** `text-5xl font-black tracking-tight` (color per above)
**Label typography:** `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1`
**Loading:** 4 skeleton groups — `Skeleton className="h-12 w-20"` + `Skeleton className="h-3 w-16"` per metric

### Stat Cards Removed

The 4 icon stat cards (`card p-4 flex items-center justify-between`) are removed entirely.

### Status Filter

The native `<select>` element is replaced with `<Select>` from `@/components/ui/Select` for consistency with Events.

```tsx
import { Select } from '@/components/ui/Select'

<Select
    options={[
        { value: '', label: 'All statuses' },
        { value: 'success', label: 'Success' },
        { value: 'failed', label: 'Failed' },
        { value: 'running', label: 'Running' },
        { value: 'timeout', label: 'Timeout' },
    ]}
    value={statusFilter}
    onChange={(e) => setStatusFilter(e.target.value)}
    aria-label="Filter by status"
/>
```

### DataTable + ExecutionDetail

Columns, `ExecutionDetail` sub-row, `handleExport`, `refetchInterval: 3000`, `useDebounce` — all unchanged.

### Page Header Removed

The `<h1>Executions</h1>` + subtitle paragraph are removed. The metric band is the page identity.

---

## Skeleton Loading

Both pages use `isLoading` from their primary query to gate the metric band:

```tsx
{isLoading ? (
    <>
        {Array.from({ length: N }).map((_, i) => (
            <div key={i} className="space-y-2">
                <Skeleton className="h-12 w-20" />
                <Skeleton className="h-3 w-16" />
            </div>
        ))}
    </>
) : (
    /* metric band numbers */
)}
```

---

## Files Changed

| File | Action |
|---|---|
| `frontend/src/pages/Events.tsx` | Full rewrite |
| `frontend/src/pages/Executions.tsx` | Full rewrite |

**Unchanged:**
- `frontend/src/components/ui/DataTable.tsx`
- `frontend/src/components/ui/DataTableToolbar.tsx`
- `frontend/src/components/EventModal.tsx`
- `frontend/src/services/api.ts`
- All other files

---

## Out of Scope

- Row click → detail panel for Events (not planned this phase)
- Time-range filter or pagination changes
- `ExecutionDetail` styling changes
- Mobile responsive breakpoints
