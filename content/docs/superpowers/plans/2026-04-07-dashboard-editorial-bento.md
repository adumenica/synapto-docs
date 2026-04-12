# Dashboard Editorial Bento Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the configurable react-grid-layout widget dashboard with a fixed editorial layout: typographic metric band → container-free incident list → two-column bottom row (Active Flows + charts).

**Architecture:** Single-file rewrite of `Dashboard.tsx`. Two obsolete files (`DashboardGrid.tsx`, `StatCards.tsx`) are deleted. `react-grid-layout` is removed from `package.json`. Existing `ActiveFlows` and `RecentActivity` components are untouched and reused. All layout done with Tailwind CSS Grid.

**Tech Stack:** React, TypeScript, Tailwind CSS, Recharts, `@tanstack/react-query`, Lucide React

---

## File Map

| File | Action |
|---|---|
| `frontend/src/pages/Dashboard.tsx` | Full rewrite |
| `frontend/src/components/dashboard/DashboardGrid.tsx` | Delete |
| `frontend/src/components/dashboard/widgets/StatCards.tsx` | Delete |
| `frontend/package.json` | Remove `react-grid-layout` |

**Unchanged (reused as-is):**
- `frontend/src/components/dashboard/ActiveFlows.tsx`
- `frontend/src/components/dashboard/widgets/RecentActivity.tsx`
- `frontend/src/components/CustomChartTooltip.tsx`

---

### Task 1: Remove react-grid-layout and delete obsolete components

**Files:**
- Modify: `frontend/package.json`
- Delete: `frontend/src/components/dashboard/DashboardGrid.tsx`
- Delete: `frontend/src/components/dashboard/widgets/StatCards.tsx`

- [ ] **Step 1: Remove react-grid-layout from package.json**

In `frontend/package.json`, find and remove this line from `"dependencies"`:
```json
"react-grid-layout": "^2.2.3",
```

- [ ] **Step 2: Delete DashboardGrid.tsx**

```bash
rm /Users/alind/Projects/Synapto/frontend/src/components/dashboard/DashboardGrid.tsx
```

- [ ] **Step 3: Delete StatCards.tsx**

```bash
rm /Users/alind/Projects/Synapto/frontend/src/components/dashboard/widgets/StatCards.tsx
```

- [ ] **Step 4: Run npm install to sync lock file**

```bash
cd /Users/alind/Projects/Synapto/frontend && npm install 2>&1 | tail -5 && echo "INSTALL_OK"
```

Expected: `INSTALL_OK` with no errors about missing packages.

- [ ] **Step 5: Verify TypeScript does not error on the deleted files being gone**

At this point `Dashboard.tsx` still imports `DashboardGrid` and `StatCards` — it will have TypeScript errors. That is expected. Check that TypeScript errors are *only* about those two imports:

```bash
cd /Users/alind/Projects/Synapto/frontend && ./node_modules/.bin/tsc --noEmit 2>&1 | grep "Dashboard.tsx" | head -10
```

Expected: errors about `DashboardGrid` and `StatCards` imports not found — nothing else.

- [ ] **Step 6: Commit**

```bash
cd /Users/alind/Projects/Synapto && git add frontend/package.json frontend/package-lock.json && git commit -m "chore(deps): remove react-grid-layout"
git rm frontend/src/components/dashboard/DashboardGrid.tsx frontend/src/components/dashboard/widgets/StatCards.tsx && git commit -m "refactor(dashboard): delete DashboardGrid and StatCards (replaced by editorial layout)"
```

---

### Task 2: Rewrite Dashboard.tsx with editorial layout

**Files:**
- Modify: `frontend/src/pages/Dashboard.tsx` — full replacement

- [ ] **Step 1: Replace the entire content of Dashboard.tsx**

Replace `frontend/src/pages/Dashboard.tsx` with:

```tsx
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { incidentsApi, analyticsApi } from '@/services/api'
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, LineChart, Line,
} from 'recharts'
import { ChevronRight } from 'lucide-react'
import ActiveFlows from '@/components/dashboard/ActiveFlows'
import CustomChartTooltip from '@/components/CustomChartTooltip'
import { Skeleton } from '@/components/ui/Skeleton'
import { Badge } from '@/components/ui/Badge'
import type { Incident } from '@/services/api'

// Fallback data used when API does not yet return historical resolution trend.
// TODO: replace with real per-day resolution data when API provides it.
const RESOLUTION_TREND_FALLBACK = [
    { day: 'Mon', time: 45 },
    { day: 'Tue', time: 38 },
    { day: 'Wed', time: 42 },
    { day: 'Thu', time: 35 },
    { day: 'Fri', time: 30 },
    { day: 'Sat', time: 28 },
    { day: 'Sun', time: 25 },
]

const SEVERITY_BORDER: Record<string, string> = {
    critical: 'border-l-red-500',
    high: 'border-l-orange-400',
    medium: 'border-l-yellow-400',
    low: 'border-l-blue-400',
    info: 'border-l-gray-400',
}

export default function Dashboard() {
    const navigate = useNavigate()

    const { data: incidents, isLoading: incidentsLoading } = useQuery({
        queryKey: ['incidents'],
        queryFn: () => incidentsApi.list({ limit: 50 }).then((res) => res.data),
    })

    const { data: analytics, isLoading: analyticsLoading } = useQuery({
        queryKey: ['analytics'],
        queryFn: () => analyticsApi.get({ days: 7 }).then((res) => res.data),
    })

    const incidentList: Incident[] = Array.isArray(incidents) ? incidents.slice(0, 8) : []
    const activeIncidentCount = Array.isArray(incidents)
        ? incidents.filter((i) => i.status !== 'resolved' && i.status !== 'closed').length
        : 0

    const successRate = analytics?.success_rate ?? 0
    const isAboveTarget = successRate > 90

    // If the API returns average_resolution_time_minutes, show it as a flat
    // reference line across all days. Otherwise fall back to sample data.
    const resolutionData = analytics?.average_resolution_time_minutes != null
        ? RESOLUTION_TREND_FALLBACK.map((d) => ({
              ...d,
              time: analytics.average_resolution_time_minutes as number,
          }))
        : RESOLUTION_TREND_FALLBACK

    return (
        <div className="space-y-8">

            {/* ── Metric Band ─────────────────────────────────────── */}
            <section aria-label="Key metrics">
                <div className="flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]">

                    {/* Resolution Rate */}
                    <div>
                        {analyticsLoading ? (
                            <div className="space-y-1">
                                <Skeleton className="h-14 w-24" />
                                <Skeleton className="h-3 w-16" />
                            </div>
                        ) : (
                            <>
                                <div className="flex items-baseline gap-0.5">
                                    <span className="text-5xl font-black tracking-tight text-gray-950 dark:text-white">
                                        {successRate.toFixed(1)}
                                    </span>
                                    <span className="text-2xl font-semibold text-primary-500">%</span>
                                </div>
                                <p className="mt-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                                    Resolved
                                </p>
                            </>
                        )}
                    </div>

                    {/* Active Incidents */}
                    <div>
                        {incidentsLoading ? (
                            <div className="space-y-1">
                                <Skeleton className="h-14 w-16" />
                                <Skeleton className="h-3 w-20" />
                            </div>
                        ) : (
                            <>
                                <span className="text-5xl font-black tracking-tight text-gray-950 dark:text-white">
                                    {Array.isArray(incidents) ? incidents.length : 0}
                                </span>
                                <p className="mt-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                                    Active Incidents
                                </p>
                            </>
                        )}
                    </div>

                    {/* Total Executions */}
                    <div>
                        {analyticsLoading ? (
                            <div className="space-y-1">
                                <Skeleton className="h-14 w-20" />
                                <Skeleton className="h-3 w-20" />
                            </div>
                        ) : (
                            <>
                                <span className="text-5xl font-black tracking-tight text-gray-950 dark:text-white">
                                    {analytics?.total_executions ?? 0}
                                </span>
                                <p className="mt-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                                    Executions
                                </p>
                            </>
                        )}
                    </div>

                    {/* Target Delta */}
                    <div className="ml-auto">
                        {analyticsLoading ? (
                            <div className="space-y-1">
                                <Skeleton className="h-8 w-32" />
                                <Skeleton className="h-3 w-20" />
                            </div>
                        ) : (
                            <>
                                <span className={`text-xl font-semibold ${isAboveTarget ? 'text-green-500' : 'text-red-500'}`}>
                                    {isAboveTarget ? '↑ above target' : '↓ below target'}
                                </span>
                                <p className="mt-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                                    vs 90% target
                                </p>
                            </>
                        )}
                    </div>
                </div>
            </section>

            {/* ── Incident List ───────────────────────────────────── */}
            <section aria-label="Active incidents">
                <div className="mb-3 flex items-center justify-between">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                        Active Incidents
                    </p>
                    <button
                        onClick={() => navigate('/incidents')}
                        className="text-xs text-primary-500 hover:underline"
                    >
                        View all →
                    </button>
                </div>
                <div className="mb-1 border-b border-[hsl(var(--border)/0.4)]" />

                {incidentsLoading ? (
                    <div>
                        {Array.from({ length: 5 }).map((_, i) => (
                            <div key={i} className="flex items-center justify-between py-3.5 pl-4">
                                <Skeleton className="h-4 w-2/3" />
                                <Skeleton className="h-4 w-1/4" />
                            </div>
                        ))}
                    </div>
                ) : incidentList.length === 0 ? (
                    <p className="py-6 text-sm text-gray-500 dark:text-gray-400">No active incidents</p>
                ) : (
                    <div>
                        {incidentList.map((incident) => (
                            <div
                                key={incident.id}
                                onClick={() => navigate('/incidents')}
                                className={[
                                    'group flex cursor-pointer items-center gap-3 border-l-[3px] py-3.5 pl-4 pr-2 transition-colors',
                                    'hover:bg-gray-50 dark:hover:bg-dark-800/60',
                                    SEVERITY_BORDER[incident.severity] ?? 'border-l-gray-400',
                                ].join(' ')}
                            >
                                <span className="flex-1 truncate text-sm font-semibold text-gray-950 dark:text-white">
                                    {incident.title}
                                </span>
                                <Badge
                                    variant={
                                        incident.status === 'resolved'
                                            ? 'success'
                                            : incident.status === 'investigating'
                                              ? 'warning'
                                              : 'danger'
                                    }
                                    className="shrink-0"
                                >
                                    {incident.status}
                                </Badge>
                                <span className="shrink-0 text-xs text-gray-500 dark:text-gray-400">
                                    {new Date(incident.created_at).toLocaleTimeString([], {
                                        hour: '2-digit',
                                        minute: '2-digit',
                                    })}
                                </span>
                                <ChevronRight
                                    className="h-4 w-4 shrink-0 text-gray-400 opacity-0 transition-opacity group-hover:opacity-100"
                                    aria-hidden="true"
                                />
                            </div>
                        ))}
                    </div>
                )}
            </section>

            {/* ── Bottom Row ──────────────────────────────────────── */}
            <section
                aria-label="Flows and analytics"
                className="grid grid-cols-1 gap-6 border-t border-[hsl(var(--border)/0.4)] pt-6 lg:grid-cols-[1fr_1.5fr]"
            >
                {/* Left — Active Flows */}
                <div>
                    <div className="mb-3 flex items-center gap-2">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                            Active Flows
                        </p>
                        <span
                            className={`h-2 w-2 rounded-full ${activeIncidentCount > 0 ? 'animate-pulse bg-green-500' : 'bg-gray-300 dark:bg-gray-600'}`}
                            aria-hidden="true"
                        />
                    </div>
                    <ActiveFlows />
                </div>

                {/* Right — Charts */}
                <div className="space-y-6">

                    {/* Incident Distribution */}
                    <div>
                        <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                            Incident Types
                        </p>
                        <div className="h-[200px] w-full">
                            {analyticsLoading ? (
                                <Skeleton variant="rect" className="h-full w-full rounded-2xl" />
                            ) : (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart
                                        data={
                                            Array.isArray(analytics?.top_incident_types)
                                                ? analytics.top_incident_types
                                                : []
                                        }
                                    >
                                        <CartesianGrid
                                            strokeDasharray="3 3"
                                            vertical={false}
                                            stroke="currentColor"
                                            strokeOpacity={0.15}
                                        />
                                        <XAxis
                                            dataKey="type"
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: 'currentColor', fontSize: 11 }}
                                            dy={10}
                                        />
                                        <YAxis
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: 'currentColor', fontSize: 11 }}
                                        />
                                        <Tooltip content={<CustomChartTooltip />} cursor={{ fill: 'transparent' }} />
                                        <Bar dataKey="count" fill="#2f6fed" radius={[8, 8, 0, 0]} barSize={34} />
                                    </BarChart>
                                </ResponsiveContainer>
                            )}
                        </div>
                    </div>

                    {/* Resolution Trend */}
                    <div>
                        <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                            Resolution Trend
                        </p>
                        <div className="h-[200px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={resolutionData}>
                                    <CartesianGrid
                                        strokeDasharray="3 3"
                                        vertical={false}
                                        stroke="currentColor"
                                        strokeOpacity={0.15}
                                    />
                                    <XAxis
                                        dataKey="day"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: 'currentColor', fontSize: 11 }}
                                        dy={10}
                                    />
                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: 'currentColor', fontSize: 11 }}
                                    />
                                    <Tooltip
                                        content={<CustomChartTooltip />}
                                        cursor={{ stroke: '#16a34a', strokeWidth: 2 }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="time"
                                        stroke="#16a34a"
                                        strokeWidth={3}
                                        dot={{ r: 4, fill: '#16a34a', strokeWidth: 2, stroke: 'hsl(var(--panel))' }}
                                        activeDot={{ r: 6, strokeWidth: 0 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}
```

- [ ] **Step 2: Verify TypeScript compiles with no errors**

```bash
cd /Users/alind/Projects/Synapto/frontend && ./node_modules/.bin/tsc --noEmit 2>&1 | head -20 && echo "TS_OK"
```

Expected: `TS_OK` with no errors.

- [ ] **Step 3: Commit**

```bash
cd /Users/alind/Projects/Synapto && git add frontend/src/pages/Dashboard.tsx && git commit -m "feat(dashboard): editorial bento layout — metric band, incident list, flows + charts"
```

---

### Task 3: Visual verification

- [ ] **Step 1: Start the frontend dev server**

```bash
cd /Users/alind/Projects/Synapto/frontend && npm run dev
```

Open `http://localhost:3000` in a browser and navigate to `/` (Dashboard).

- [ ] **Step 2: Verify metric band**

Check:
- [ ] Three large numbers visible: resolution rate (with % suffix), incidents count, executions count
- [ ] Delta indicator (↑ above target / ↓ below target) appears at right edge
- [ ] Numbers use `text-5xl font-black` — clearly the largest text on the page
- [ ] Small uppercase labels below each number
- [ ] `border-b` separator below the band
- [ ] Loading: skeleton placeholders appear before data loads

- [ ] **Step 3: Verify incident list**

Check:
- [ ] Section header "ACTIVE INCIDENTS" with "View all →" link at right
- [ ] Each row has a colored left border matching severity (red=critical, orange=high, yellow=medium, blue=low)
- [ ] Each row shows: title, status badge, timestamp, chevron on hover
- [ ] Clicking any row navigates to `/incidents`
- [ ] Empty state shows "No active incidents" if list is empty
- [ ] Loading: 5 skeleton rows appear before data loads

- [ ] **Step 4: Verify bottom row**

Check:
- [ ] Two-column layout on `lg:` screens (≥1024px), single column on mobile
- [ ] Left: "ACTIVE FLOWS" label + pulsing green dot (or gray if no active incidents) + ActiveFlows component beneath
- [ ] Right: two charts stacked — "INCIDENT TYPES" bar chart + "RESOLUTION TREND" line chart
- [ ] Charts render on page background (no card wrapper around them)
- [ ] `border-t` separator above the bottom row

- [ ] **Step 5: Verify dark mode**

Toggle dark mode — all sections should render correctly.

- [ ] **Step 6: Commit any visual fixes found, or skip if none needed**

```bash
cd /Users/alind/Projects/Synapto && git add frontend/src/pages/Dashboard.tsx && git commit -m "fix(dashboard): visual fixes from review"
```
