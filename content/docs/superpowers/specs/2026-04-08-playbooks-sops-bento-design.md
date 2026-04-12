# Playbooks + SOPs — Bento Grid Redesign Spec
**Date:** 2026-04-08
**Phase:** 6 of the Container-Free + Bento UI overhaul
**Scope:** `frontend/src/pages/Playbooks.tsx` and `frontend/src/pages/SOPLibrary.tsx` (full rewrites)

---

## Overview

Add a container-free metric band to both Playbooks and SOPLibrary pages, and replace card-based grid cells with left-border bento cells. No new components, no new API endpoints. All modals (create/edit/view/delete) preserved unchanged.

---

## Approach

Two independent single-file rewrites. The pattern for each page:

```
Metric band (border-b separator)
↓
Toolbar / action row
↓
3-column bento grid (left-border cells, no card boxes)
```

Same `text-5xl font-black` metric band as Analytics, Events, and Executions.

---

## Page Structure (both pages)

```
┌─────────────────────────────────────────────────┐
│  METRIC BAND (no container)                     │
│  N  ·  N                                        │
│  ─────────────────────────────── border-b       │
│  action row (search / filters / create button)  │
│  ┌─────────────────────────────────────────┐    │
│  │  grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3   │
│  │  ▌ cell  ▌ cell  ▌ cell              │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

## Playbooks.tsx

### Metric Band

**Layout:** `flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]`

| Metric | Value | Color |
|---|---|---|
| Total | `playbooks?.length ?? 0` | `text-foreground` |
| Active | `activePlaybooks?.length ?? 0` | `text-green-400` |

**Number typography:** `text-5xl font-black tracking-tight`
**Label typography:** `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1`
**Loading:** 2 skeleton groups — `Skeleton className="h-12 w-20"` + `Skeleton className="h-3 w-16"`

### Action Row

Between the metric band and grid. Right-aligned "Create Playbook" button:

```tsx
<div className="flex items-center justify-end py-4">
    <button onClick={() => setIsCreating(true)} className="btn btn-primary flex items-center gap-2">
        <Plus className="w-4 h-4" />
        Create Playbook
    </button>
</div>
```

### Grid Cells

**Grid:** `grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3`

Each cell (`activePlaybooks.map`):

```tsx
<div
    key={playbook.id}
    className="group border-l-[3px] border-l-primary-500 pl-4 py-2 cursor-pointer hover:bg-[hsl(var(--panel)/0.4)] transition-colors rounded-r-sm"
>
    <div className="flex items-start justify-between">
        <h3 className="text-base font-semibold text-foreground line-clamp-2 flex-1">
            {playbook.name}
        </h3>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-2 shrink-0">
            <button onClick={() => handleEdit(playbook)} ...><Pencil className="w-3.5 h-3.5" /></button>
            <button onClick={() => handleDelete(playbook.id)} ...><Trash2 className="w-3.5 h-3.5" /></button>
        </div>
    </div>
    {playbook.description && (
        <p className="text-sm text-muted-foreground mt-1 line-clamp-2 leading-relaxed">
            {playbook.description}
        </p>
    )}
    <div className="flex items-center justify-between mt-3">
        <span className="text-[11px] text-muted-foreground">v{playbook.version}</span>
        <span className="text-[11px] text-muted-foreground">{playbook.steps.length} steps</span>
    </div>
</div>
```

All playbook cells use `border-l-primary-500` (single color — all displayed playbooks are active).

### Loading State

6 skeleton cells in the same grid:

```tsx
{Array.from({ length: 6 }).map((_, i) => (
    <div key={i} className="border-l-[3px] border-l-muted pl-4 py-2 space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-1/2 mt-1" />
    </div>
))}
```

### Empty State

No card wrapper:

```tsx
<div className="col-span-full py-16 text-center">
    <p className="text-muted-foreground">No playbooks found. Create your first playbook to get started.</p>
</div>
```

### Modals Unchanged

`isCreating` modal (create/edit) preserved exactly as-is.

---

## SOPLibrary.tsx

### Metric Band

**Layout:** `flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]`

| Metric | Value | Color |
|---|---|---|
| Total SOPs | `sops?.length ?? 0` | `text-foreground` |
| Categories | `new Set((sops ?? []).map(s => s.category \|\| 'Uncategorized')).size` | `text-blue-400` |

When `selectedCategory !== 'all'`, the query returns filtered data — "Total SOPs" shows the count for the selected category, which is correct contextual behavior.

**Number typography:** `text-5xl font-black tracking-tight`
**Label typography:** `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1`
**Loading:** 2 skeleton groups — `Skeleton className="h-12 w-20"` + `Skeleton className="h-3 w-16"`

### Search + Category Row

The existing search input, category pills, and "Create SOP" button are consolidated into one row:

```tsx
<div className="flex flex-col sm:flex-row gap-3 py-4">
    {/* search input — unchanged */}
    {/* category pills — unchanged */}
    {/* Create SOP button — moved here from standalone header */}
</div>
```

The standalone `flex justify-between` header (h1 + Create SOP button) is removed. The metric band replaces the h1.

### Category Border Color

Deterministic color derived from the category string — stable across renders and filter states regardless of what other categories are present:

```tsx
const CATEGORY_COLORS = [
    'border-l-blue-400',
    'border-l-green-400',
    'border-l-amber-400',
    'border-l-purple-400',
    'border-l-pink-400',
    'border-l-cyan-400',
]

function categoryBorderColor(cat: string): string {
    let h = 0
    for (let i = 0; i < cat.length; i++) h = (h * 31 + cat.charCodeAt(i)) & 0xffff
    return CATEGORY_COLORS[h % CATEGORY_COLORS.length]
}
```

All 6 full class strings appear in the `CATEGORY_COLORS` array — Tailwind will include them in the build.

### Grid Cells

**Grid:** `grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3`

Each cell (`filteredSOPs.map`):

```tsx
<div
    key={sop.id}
    onClick={() => handleViewSOP(sop)}
    className={`group border-l-[3px] ${categoryBorderColor(sop.category || 'Uncategorized')} pl-4 py-2 cursor-pointer hover:bg-[hsl(var(--panel)/0.4)] transition-colors rounded-r-sm`}
>
    <div className="flex items-start justify-between">
        <h3 className="text-base font-semibold text-foreground line-clamp-2 flex-1">
            {sop.title}
        </h3>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-2 shrink-0">
            <button onClick={(e) => handleEditClick(sop, e)} ...><Edit2 className="w-3.5 h-3.5" /></button>
            <button onClick={(e) => { e.stopPropagation(); setSopToDelete(sop) }} ...><Trash2 className="w-3.5 h-3.5" /></button>
        </div>
    </div>
    <p className="text-sm text-muted-foreground mt-1 line-clamp-3 leading-relaxed">
        {sop.description || sop.content.substring(0, 120) + '…'}
    </p>
    <div className="flex items-center justify-between mt-3">
        <span className="text-[11px] text-muted-foreground">{sop.category || 'Uncategorized'}</span>
        <span className="text-[11px] text-muted-foreground">{formatDate(sop.updated_at || sop.created_at)}</span>
    </div>
</div>
```

### Loading State

6 skeleton cells in the same grid:

```tsx
{Array.from({ length: 6 }).map((_, i) => (
    <div key={i} className="border-l-[3px] border-l-muted pl-4 py-2 space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-2/3" />
        <Skeleton className="h-3 w-1/2 mt-1" />
    </div>
))}
```

### Empty State

Container-free — no `card` wrapper:

```tsx
<div className="col-span-full py-16 text-center">
    <p className="text-muted-foreground mb-4">
        {searchQuery ? 'No SOPs match your search' : 'No SOPs yet'}
    </p>
    {!searchQuery && (
        <button onClick={() => setIsCreateModalOpen(true)} className="btn btn-primary flex items-center gap-2 text-sm mx-auto">
            <Plus className="w-4 h-4" />
            Create SOP
        </button>
    )}
</div>
```

### Modals Unchanged

View modal, Edit modal, Create modal, `ConfirmModal` (delete) — all preserved exactly as-is.

---

## Skeleton Import

Both files require:
```tsx
import { Skeleton } from '@/components/ui/Skeleton'
```

---

## Files Changed

| File | Action |
|---|---|
| `frontend/src/pages/Playbooks.tsx` | Full rewrite |
| `frontend/src/pages/SOPLibrary.tsx` | Full rewrite |

**Unchanged:**
- All modal components
- `frontend/src/components/admin/ConfirmModal.tsx`
- `frontend/src/services/api.ts`
- All other files

---

## Out of Scope

- Playbook detail/expand view
- SOP inline preview (still uses view modal)
- Mobile responsive stacking beyond existing breakpoints
- Search on Playbooks (not currently present, not added)
