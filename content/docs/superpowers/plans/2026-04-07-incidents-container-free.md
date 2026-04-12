# Incidents Container-Free Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the card-based expandable incident list with container-free rows and a push-split detail panel that slides in when a row is clicked.

**Architecture:** `Incidents.tsx` is a full rewrite — it reads `useParams()` to detect whether a detail panel should show. When `/incidents/:id` is matched, the layout switches to a two-column grid (45%/55%) with the list on the left and `IncidentDetailPanel` on the right. A new nested route `incidents/:id` is added to `App.tsx`. No new API endpoints.

**Tech Stack:** React, TypeScript, TanStack React Query, React Router v6 (`useParams`, `useNavigate`), Tailwind CSS, Lucide React icons, existing `Badge` + `Skeleton` components from `@/components/ui`.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `frontend/src/App.tsx` | Modify | Add `incidents/:id` nested route |
| `frontend/src/components/incidents/IncidentDetailPanel.tsx` | Create | Scrollable detail panel — header, DETAILS, AI ANALYSIS, EXECUTIONS stub, TIMELINE stub |
| `frontend/src/pages/Incidents.tsx` | Full rewrite | Container-free row list, filter bar, push-split layout |

---

### Task 1: Add `incidents/:id` route to App.tsx

**Files:**
- Modify: `frontend/src/App.tsx:33`

The file currently has:
```tsx
<Route path="incidents" element={<Incidents />} />
```

Add the `incidents/:id` route directly after it so React Router renders the same `Incidents` component with the `:id` param available via `useParams()`.

- [ ] **Step 1: Add the route**

In `frontend/src/App.tsx`, change line 33 from:
```tsx
                <Route path="incidents" element={<Incidents />} />
```
to:
```tsx
                <Route path="incidents" element={<Incidents />} />
                <Route path="incidents/:id" element={<Incidents />} />
```

- [ ] **Step 2: Verify TypeScript compiles**

Run from `frontend/`:
```bash
npm run build
```
Expected: build succeeds with no TypeScript errors. (The `Incidents` component doesn't use `useParams` yet, so no errors expected at this stage.)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat(incidents): add incidents/:id route for detail panel"
```

---

### Task 2: Create `IncidentDetailPanel` component

**Files:**
- Create: `frontend/src/components/incidents/IncidentDetailPanel.tsx`

This component receives `id: string` and `onClose: () => void` as props. It fetches the full incident via `incidentsApi.get(id)` and renders a scrollable panel with four sections: DETAILS, AI ANALYSIS, EXECUTIONS (stub), TIMELINE (stub).

**Badge variant reference** (from `frontend/src/components/ui/Badge.tsx`):
- severity `critical` → `'danger'`, `high` → `'orange'`, `medium` → `'warning'`, `low` → `'info'`, `info` → `'neutral'`
- status `resolved` → `'success'`, `failed` → `'danger'`, `open` → `'info'`, `investigating` → `'warning'`, `remediating` → `'primary'`, `closed` → `'neutral'`

- [ ] **Step 1: Create the directory and file**

Create `frontend/src/components/incidents/IncidentDetailPanel.tsx` with this complete implementation:

```tsx
import { useQuery } from '@tanstack/react-query'
import { X, Loader } from 'lucide-react'
import { Badge } from '@/components/ui'
import { Skeleton } from '@/components/ui/Skeleton'
import { incidentsApi } from '@/services/api'
import type { BadgeProps } from '@/components/ui'

type BadgeVariant = NonNullable<BadgeProps['variant']>

const SEVERITY_BADGE: Record<string, BadgeVariant> = {
    critical: 'danger',
    high: 'orange',
    medium: 'warning',
    low: 'info',
    info: 'neutral',
}

const STATUS_BADGE: Record<string, BadgeVariant> = {
    resolved: 'success',
    failed: 'danger',
    open: 'info',
    investigating: 'warning',
    remediating: 'primary',
    closed: 'neutral',
}

interface IncidentDetailPanelProps {
    id: string
    onClose: () => void
}

export default function IncidentDetailPanel({ id, onClose }: IncidentDetailPanelProps) {
    const { data: incident, isLoading } = useQuery({
        queryKey: ['incident', id],
        queryFn: () => incidentsApi.get(id).then(res => res.data),
        enabled: !!id,
    })

    if (isLoading) {
        return (
            <div className="h-full overflow-y-auto p-5 space-y-4 animate-in slide-in-from-right-4 duration-200">
                <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                        <Skeleton className="h-5 w-48" />
                        <Skeleton className="h-4 w-24" />
                    </div>
                    <button
                        onClick={onClose}
                        aria-label="Close panel"
                        className="text-muted-foreground hover:text-foreground transition-colors shrink-0 mt-1 ml-4"
                    >
                        <X className="h-4 w-4" />
                    </button>
                </div>
                <div className="border-t border-[hsl(var(--border)/0.4)] pt-4 space-y-3">
                    <Skeleton className="h-3 w-20" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                </div>
            </div>
        )
    }

    if (!incident) return null

    const aiAnalysis = incident.meta_data?.ai_analysis

    return (
        <div className="h-full overflow-y-auto p-5 animate-in slide-in-from-right-4 duration-200">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1 min-w-0 pr-4">
                    <h2 className="text-lg font-bold text-foreground leading-tight">{incident.title}</h2>
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                        <Badge variant={SEVERITY_BADGE[incident.severity] ?? 'neutral'} dot>
                            {incident.severity}
                        </Badge>
                        <Badge
                            variant={STATUS_BADGE[incident.status] ?? 'neutral'}
                            dot
                            pulse={incident.status === 'investigating' || incident.status === 'remediating'}
                        >
                            {incident.status}
                        </Badge>
                    </div>
                </div>
                <button
                    onClick={onClose}
                    aria-label="Close panel"
                    className="text-muted-foreground hover:text-foreground transition-colors shrink-0 mt-1"
                >
                    <X className="h-4 w-4" />
                </button>
            </div>

            {/* DETAILS */}
            <section className="border-t border-[hsl(var(--border)/0.4)]">
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground pt-4 pb-2">
                    Details
                </p>
                <dl className="space-y-1.5 text-sm">
                    <div className="flex gap-2">
                        <dt className="text-muted-foreground w-20 shrink-0">ID</dt>
                        <dd className="font-mono text-xs text-foreground break-all">{incident.id}</dd>
                    </div>
                    <div className="flex gap-2">
                        <dt className="text-muted-foreground w-20 shrink-0">Created</dt>
                        <dd className="text-foreground">{new Date(incident.created_at).toLocaleString()}</dd>
                    </div>
                    {incident.resolved_at && (
                        <div className="flex gap-2">
                            <dt className="text-muted-foreground w-20 shrink-0">Resolved</dt>
                            <dd className="text-foreground">{new Date(incident.resolved_at).toLocaleString()}</dd>
                        </div>
                    )}
                </dl>
                {incident.description && (
                    <p className="mt-3 text-sm text-foreground leading-relaxed">{incident.description}</p>
                )}
            </section>

            {/* AI ANALYSIS */}
            <section className="border-t border-[hsl(var(--border)/0.4)] mt-4">
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground pt-4 pb-2">
                    AI Analysis
                </p>
                {aiAnalysis ? (
                    <div className="space-y-4">
                        {aiAnalysis.root_cause_prediction && (
                            <div>
                                <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground mb-1.5">
                                    Root Cause
                                </p>
                                <div className="border-l-2 border-purple-500 pl-3 text-sm font-medium text-foreground">
                                    {aiAnalysis.root_cause_prediction}
                                </div>
                            </div>
                        )}
                        {aiAnalysis.analysis && (
                            <div>
                                <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground mb-1.5">
                                    Summary
                                </p>
                                <p className="text-sm text-muted-foreground leading-relaxed">{aiAnalysis.analysis}</p>
                            </div>
                        )}
                        {Array.isArray(aiAnalysis.remediation_plan) && aiAnalysis.remediation_plan.length > 0 && (
                            <div>
                                <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground mb-1.5">
                                    Remediation Plan
                                </p>
                                <ol className="space-y-1.5">
                                    {aiAnalysis.remediation_plan.map((step: string, idx: number) => (
                                        <li key={idx} className="flex items-start gap-2 text-sm text-foreground">
                                            <span className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded text-muted-foreground shrink-0 mt-0.5">
                                                {idx + 1}
                                            </span>
                                            {step}
                                        </li>
                                    ))}
                                </ol>
                            </div>
                        )}
                        {aiAnalysis.confidence_score !== undefined && (
                            <p className="text-sm">
                                <span className="text-muted-foreground">Confidence: </span>
                                <span className="font-bold text-green-600 dark:text-green-400">
                                    {Math.round(aiAnalysis.confidence_score * 100)}%
                                </span>
                            </p>
                        )}
                        {incident.meta_data?.ai_analyzed_at && (
                            <p className="text-xs text-muted-foreground">
                                Processed {new Date(incident.meta_data.ai_analyzed_at).toLocaleTimeString()}
                            </p>
                        )}
                    </div>
                ) : (
                    <div className="flex items-center gap-2 py-2 text-sm text-muted-foreground">
                        <Loader className="h-4 w-4 animate-spin text-purple-400 shrink-0" />
                        Analysis in progress...
                    </div>
                )}
            </section>

            {/* EXECUTIONS */}
            <section className="border-t border-[hsl(var(--border)/0.4)] mt-4">
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground pt-4 pb-2">
                    Executions
                </p>
                {/* TODO: wire when executionsApi.list supports incident_id filter */}
                <p className="text-sm text-muted-foreground py-2">No executions yet</p>
            </section>

            {/* TIMELINE */}
            <section className="border-t border-[hsl(var(--border)/0.4)] mt-4 pb-6">
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground pt-4 pb-2">
                    Timeline
                </p>
                {/* TODO: wire when eventsApi.list supports incident_id filter */}
                <p className="text-sm text-muted-foreground py-2">No events linked</p>
            </section>
        </div>
    )
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run from `frontend/`:
```bash
npm run build
```
Expected: build succeeds. Fix any type errors before continuing.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/incidents/IncidentDetailPanel.tsx
git commit -m "feat(incidents): add IncidentDetailPanel component"
```

---

### Task 3: Rewrite `Incidents.tsx`

**Files:**
- Modify: `frontend/src/pages/Incidents.tsx` (full rewrite)

This is the list page. It reads `useParams()` for the selected incident `id`. When `id` is present the layout becomes a two-column grid: list (45%) + detail panel (55%). Rows are full-bleed strips with a left severity border. The filter bar has no card wrapper.

**Important class names** — use full strings (not dynamic concatenation) so Tailwind doesn't purge them:

```ts
const SEVERITY_BORDER: Record<string, string> = {
    critical: 'border-l-red-500',
    high: 'border-l-orange-400',
    medium: 'border-l-yellow-400',
    low: 'border-l-blue-400',
}
```

**Badge variants** — same as Task 2:
```ts
const STATUS_BADGE: Record<string, BadgeVariant> = {
    resolved: 'success',
    failed: 'danger',
    open: 'info',
    investigating: 'warning',
    remediating: 'primary',
    closed: 'neutral',
}
```

- [ ] **Step 1: Replace the entire contents of `frontend/src/pages/Incidents.tsx`**

```tsx
import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { Search, ChevronRight } from 'lucide-react'
import { incidentsApi } from '@/services/api'
import { Badge } from '@/components/ui'
import { Skeleton } from '@/components/ui/Skeleton'
import { useDebounce } from '@/hooks/useDebounce'
import IncidentDetailPanel from '@/components/incidents/IncidentDetailPanel'
import type { BadgeProps } from '@/components/ui'

type BadgeVariant = NonNullable<BadgeProps['variant']>

const SEVERITY_BORDER: Record<string, string> = {
    critical: 'border-l-red-500',
    high: 'border-l-orange-400',
    medium: 'border-l-yellow-400',
    low: 'border-l-blue-400',
}

const STATUS_BADGE: Record<string, BadgeVariant> = {
    resolved: 'success',
    failed: 'danger',
    open: 'info',
    investigating: 'warning',
    remediating: 'primary',
    closed: 'neutral',
}

export default function Incidents() {
    const { id } = useParams<{ id?: string }>()
    const navigate = useNavigate()

    const [status, setStatus] = useState<string>('')
    const [severity, setSeverity] = useState<string>('')
    const [search, setSearch] = useState<string>('')

    const debouncedSearch = useDebounce(search, 300)

    const { data: incidentsData, isLoading } = useQuery({
        queryKey: ['incidents', status],
        queryFn: () =>
            incidentsApi.list({ limit: 100, status: status || undefined }).then(res => res.data),
        refetchInterval: 5000,
    })

    const incidents = useMemo(() => {
        let filtered = incidentsData || []
        if (severity) filtered = filtered.filter(i => i.severity === severity)
        if (debouncedSearch) {
            const q = debouncedSearch.toLowerCase()
            filtered = filtered.filter(
                i =>
                    i.title.toLowerCase().includes(q) ||
                    i.description?.toLowerCase().includes(q)
            )
        }
        return filtered
    }, [incidentsData, severity, debouncedSearch])

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)]">
            {/* Page header — show total loaded count, not filtered count */}
            <div className="pb-4">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mb-1">
                    Incidents
                </p>
                <p className="text-5xl font-black tracking-tight text-foreground">
                    {isLoading ? '—' : (incidentsData?.length ?? 0)}
                </p>
            </div>

            {/* Filter bar */}
            <div className="flex flex-wrap items-center gap-3 pb-3 border-b border-[hsl(var(--border)/0.4)]">
                <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
                    <input
                        type="text"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Search incidents..."
                        className="w-full pl-6 pr-2 py-1.5 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
                    />
                </div>
                <select
                    value={status}
                    onChange={e => setStatus(e.target.value)}
                    className="bg-transparent text-sm text-foreground focus:outline-none cursor-pointer"
                >
                    <option value="">All Statuses</option>
                    <option value="open">Open</option>
                    <option value="investigating">Investigating</option>
                    <option value="remediating">Remediating</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                    <option value="failed">Failed</option>
                </select>
                <select
                    value={severity}
                    onChange={e => setSeverity(e.target.value)}
                    className="bg-transparent text-sm text-foreground focus:outline-none cursor-pointer"
                >
                    <option value="">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="info">Info</option>
                </select>
            </div>

            {/* Content area — list only, or push-split when panel is open */}
            <div className={`flex-1 overflow-hidden mt-3 ${id ? 'grid grid-cols-[45%_55%]' : 'flex flex-col'}`}>
                {/* Incident list */}
                <div
                    className={`overflow-y-auto h-full ${id ? 'border-r border-[hsl(var(--border)/0.4)]' : ''}`}
                >
                    {isLoading ? (
                        <div className="space-y-2">
                            {Array.from({ length: 6 }).map((_, i) => (
                                <div
                                    key={i}
                                    className="flex justify-between items-center h-12 pl-4 border-l-[3px] border-l-muted"
                                >
                                    <Skeleton className="h-4 w-2/3" />
                                    <Skeleton className="h-4 w-1/5" />
                                </div>
                            ))}
                        </div>
                    ) : incidents.length > 0 ? (
                        incidents.map(incident => (
                            <div
                                key={incident.id}
                                onClick={() => navigate(`/incidents/${incident.id}`)}
                                className={[
                                    'group flex items-center gap-4 py-3.5 pl-4 pr-3 cursor-pointer',
                                    'hover:bg-muted/30 transition-colors',
                                    'border-l-[3px]',
                                    id === incident.id
                                        ? 'border-l-primary-500 bg-muted/50'
                                        : (SEVERITY_BORDER[incident.severity] ?? 'border-l-gray-400'),
                                ].join(' ')}
                            >
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-semibold text-foreground truncate">
                                        {incident.title}
                                    </p>
                                    <div className="flex items-center gap-1.5 mt-0.5">
                                        <span className="text-xs font-mono text-muted-foreground">
                                            #{incident.id.substring(0, 8)}
                                        </span>
                                        <span className="text-xs text-muted-foreground">·</span>
                                        <span className="text-xs text-muted-foreground">
                                            {new Date(incident.created_at).toLocaleString()}
                                        </span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 shrink-0">
                                    <Badge variant={STATUS_BADGE[incident.status] ?? 'neutral'}>
                                        {incident.status}
                                    </Badge>
                                    <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="py-8 text-sm text-muted-foreground">
                            {debouncedSearch || status || severity
                                ? 'No incidents match your filters'
                                : 'No incidents found'}
                        </p>
                    )}
                </div>

                {/* Detail panel — only rendered when an incident is selected */}
                {id && (
                    <IncidentDetailPanel id={id} onClose={() => navigate('/incidents')} />
                )}
            </div>
        </div>
    )
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run from `frontend/`:
```bash
npm run build
```
Expected: build succeeds with no TypeScript errors. Common pitfalls:
- `useParams<{ id?: string }>()` — the generic ensures `id` can be `string | undefined`
- `BadgeVariant` type must match the imported `BadgeProps['variant']`

- [ ] **Step 3: Verify with ESLint**

```bash
npm run lint
```
Expected: 0 warnings, 0 errors.

- [ ] **Step 4: Visual verification checklist**

Start the dev server (`npm run dev`) and verify in the browser at http://localhost:3000:

**List view (`/incidents`):**
- [ ] Page header: small `INCIDENTS` label + large count number, no card wrapper
- [ ] Filter bar: no card wrapper — search, status, severity sitting inline on page background
- [ ] Each row has a left border colored by severity (red=critical, orange=high, yellow=medium, blue=low)
- [ ] Row hover shows light `bg-muted/30` highlight and `ChevronRight` icon appears
- [ ] No rounded cards anywhere in the list

**Push-split view (`/incidents/:id` — click any row):**
- [ ] List narrows to ~45% width
- [ ] Detail panel slides in from the right with animation
- [ ] Selected row highlighted with blue left border + `bg-muted/50`
- [ ] Detail panel shows: title, severity badge, status badge, DETAILS section, AI ANALYSIS section
- [ ] If incident has `meta_data.ai_analysis`: root cause, summary, remediation plan, confidence score are visible
- [ ] If incident has no AI analysis: spinner + "Analysis in progress..." is shown
- [ ] EXECUTIONS section shows "No executions yet"
- [ ] TIMELINE section shows "No events linked"
- [ ] Panel scrolls independently from the list
- [ ] X button navigates back to `/incidents` and collapses the panel

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/Incidents.tsx
git commit -m "feat(incidents): container-free row list with push-split detail panel"
```
