# Analytics Bento Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the card-based Analytics page with a container-free, typography-first layout — metric band, period label, and a three-column bento grid (pie chart | bar chart | recommendations).

**Architecture:** Single-file rewrite of `Analytics.tsx`. Existing `PieChart`, `BarChart`, and `CustomChartTooltip` are reused unchanged from the current file. Same two queries. No new files, no new API endpoints.

**Tech Stack:** React, TypeScript, TanStack React Query, Recharts, Tailwind CSS, existing `Badge` + `Skeleton` UI components.

---

## File Map

| File | Action |
|---|---|
| `frontend/src/pages/Analytics.tsx` | Full rewrite |

---

### Task 1: Rewrite `Analytics.tsx`

**Files:**
- Modify: `frontend/src/pages/Analytics.tsx` (full rewrite)

**Codebase context you need:**

- `Badge` component: `import { Badge } from '@/components/ui'` — variants include `danger`, `warning`, `info`, `neutral`. Also export `BadgeProps` from the same path.
- `Skeleton` component: `import { Skeleton } from '@/components/ui/Skeleton'`
- `CustomChartTooltip`: `import CustomChartTooltip from '@/components/CustomChartTooltip'`
- CSS variables: `--border` and `--panel` are defined in `index.css`. Use as `hsl(var(--border)/0.4)`.
- `analytics.top_incident_types` is `Array<{ type: string; count: number }>`.
- `recommendations` is `any[]` where each item has `priority: string`, `type: string`, `message: string`.
- Priority → border color (full class strings — no dynamic concatenation, Tailwind needs to see them):
  - `'high'` → `'border-l-red-500'`
  - `'medium'` → `'border-l-yellow-400'`
  - `'low'` → `'border-l-blue-400'`
- Priority → Badge variant: `'high'` → `'danger'`, `'medium'` → `'warning'`, `'low'` → `'info'`

- [ ] **Step 1: Replace the entire contents of `frontend/src/pages/Analytics.tsx`**

```tsx
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/services/api'
import CustomChartTooltip from '@/components/CustomChartTooltip'
import {
    BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Legend,
} from 'recharts'
import { Badge } from '@/components/ui'
import { Skeleton } from '@/components/ui/Skeleton'
import type { BadgeProps } from '@/components/ui'

type BadgeVariant = NonNullable<BadgeProps['variant']>

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

const PRIORITY_BORDER: Record<string, string> = {
    high: 'border-l-red-500',
    medium: 'border-l-yellow-400',
    low: 'border-l-blue-400',
}

const PRIORITY_BADGE: Record<string, BadgeVariant> = {
    high: 'danger',
    medium: 'warning',
    low: 'info',
}

export default function Analytics() {
    const { data: analytics, isLoading } = useQuery({
        queryKey: ['analytics'],
        queryFn: () => analyticsApi.get({ days: 30 }).then(res => res.data),
    })

    const { data: recommendations, isLoading: recsLoading } = useQuery({
        queryKey: ['recommendations'],
        queryFn: () => analyticsApi.recommendations().then(res => res.data),
    })

    return (
        <div className="flex flex-col">
            {/* Metric band */}
            <div className="flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]">
                {isLoading ? (
                    <>
                        {Array.from({ length: 4 }).map((_, i) => (
                            <div key={i} className="space-y-2">
                                <Skeleton className="h-12 w-20" />
                                <Skeleton className="h-3 w-16" />
                            </div>
                        ))}
                    </>
                ) : (
                    <>
                        <div>
                            <p className="text-5xl font-black tracking-tight text-foreground">
                                {analytics?.success_rate?.toFixed(1) ?? '—'}
                                <span className="text-2xl text-primary-500">%</span>
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Success Rate
                            </p>
                        </div>
                        <div>
                            <p className="text-5xl font-black tracking-tight text-foreground">
                                {analytics?.total_incidents ?? '—'}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Total Incidents
                            </p>
                        </div>
                        <div>
                            <p className="text-5xl font-black tracking-tight text-foreground">
                                {analytics?.total_executions ?? '—'}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Total Executions
                            </p>
                        </div>
                        <div>
                            <p className="text-5xl font-black tracking-tight text-foreground">
                                {analytics?.average_resolution_time_minutes != null
                                    ? analytics.average_resolution_time_minutes.toFixed(0)
                                    : '—'}
                                {analytics?.average_resolution_time_minutes != null && (
                                    <span className="text-2xl text-muted-foreground">m</span>
                                )}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Avg Resolution
                            </p>
                        </div>
                    </>
                )}
            </div>

            {/* Period label */}
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground py-4">
                Last 30 days
            </p>

            {/* Bento grid */}
            <div className="grid grid-cols-[1fr_1fr_1.2fr] gap-6 items-start">
                {/* Pie chart */}
                <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mb-4">
                        Incident Types
                    </p>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <defs>
                                    {(analytics?.top_incident_types || []).map((_, index) => (
                                        <radialGradient key={index} id={`pieGrad${index}`} cx="50%" cy="50%" r="50%">
                                            <stop offset="0%" stopColor={COLORS[index % COLORS.length]} stopOpacity={1} />
                                            <stop offset="100%" stopColor={COLORS[index % COLORS.length]} stopOpacity={0.7} />
                                        </radialGradient>
                                    ))}
                                </defs>
                                <Pie
                                    data={analytics?.top_incident_types || []}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ type, percent }: { type: string; percent: number }) =>
                                        `${type}: ${(percent * 100).toFixed(0)}%`
                                    }
                                    outerRadius={90}
                                    innerRadius={40}
                                    fill="#8884d8"
                                    dataKey="count"
                                    paddingAngle={3}
                                >
                                    {(analytics?.top_incident_types || []).map((_, index) => (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={`url(#pieGrad${index})`}
                                            stroke="rgba(255,255,255,0.08)"
                                            strokeWidth={1}
                                        />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomChartTooltip />} />
                                <Legend
                                    wrapperStyle={{ fontSize: '11px', color: '#9ca3af', paddingTop: '8px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Bar chart */}
                <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mb-4">
                        Incident Volume
                    </p>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={analytics?.top_incident_types || []} barSize={28}>
                                <defs>
                                    <linearGradient id="colorTrends" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.9} />
                                        <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.2} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    vertical={false}
                                    stroke="rgba(107,114,128,0.15)"
                                />
                                <XAxis
                                    dataKey="type"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#9ca3af', fontSize: 11 }}
                                    dy={8}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#9ca3af', fontSize: 11 }}
                                />
                                <Tooltip
                                    content={<CustomChartTooltip />}
                                    cursor={{ fill: 'rgba(107,114,128,0.06)' }}
                                />
                                <Bar dataKey="count" fill="url(#colorTrends)" radius={[6, 6, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Recommendations */}
                <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mb-4">
                        Recommendations
                    </p>
                    {recsLoading ? (
                        <div className="space-y-3">
                            {Array.from({ length: 3 }).map((_, i) => (
                                <div key={i} className="h-16 border-l-[3px] border-l-muted pl-3 flex flex-col justify-center gap-1.5">
                                    <Skeleton className="h-4 w-16" />
                                    <Skeleton className="h-4 w-full" />
                                </div>
                            ))}
                        </div>
                    ) : recommendations && recommendations.length > 0 ? (
                        <div className="space-y-1">
                            {recommendations.map((rec, index) => (
                                <div
                                    key={index}
                                    className={`py-3 pl-3 pr-2 border-l-[3px] ${PRIORITY_BORDER[rec.priority] ?? 'border-l-gray-400'}`}
                                >
                                    <div className="flex items-center gap-2 mb-1">
                                        <Badge variant={PRIORITY_BADGE[rec.priority] ?? 'neutral'}>
                                            {rec.priority}
                                        </Badge>
                                        <span className="text-xs text-muted-foreground">{rec.type}</span>
                                    </div>
                                    <p className="text-sm text-foreground leading-relaxed">{rec.message}</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm text-muted-foreground py-2">No recommendations at this time</p>
                    )}
                </div>
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
Expected: build succeeds with no TypeScript errors.

- [ ] **Step 3: Verify ESLint passes**

```bash
npm run lint
```
Expected: 0 warnings, 0 errors.

- [ ] **Step 4: Visual verification checklist**

Start the dev server (`npm run dev`) and open http://localhost:3000/analytics. Verify:

- [ ] Page has no card wrappers anywhere — numbers and charts float directly on page background
- [ ] Metric band: four large numbers (success rate, incidents, executions, avg resolution) with small uppercase labels below each
- [ ] `%` suffix on success rate is `text-primary-500` (blue), `m` suffix on avg resolution is `text-muted-foreground`
- [ ] Loading state: skeleton blocks at each metric position
- [ ] "Last 30 days" period label appears between the metric band and the charts
- [ ] Three-column grid: pie chart left, bar chart middle, recommendations right
- [ ] Recommendations have colored left borders (red=high, yellow=medium, blue=low)
- [ ] Recommendations show `Badge` + type label on first line, message text below
- [ ] Empty state "No recommendations at this time" renders when list is empty

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/Analytics.tsx
git commit -m "feat(analytics): container-free bento layout with metric band"
```
