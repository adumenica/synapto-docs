# Events + Executions Container-Free Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace card-based stat sections on Events and Executions pages with container-free metric bands matching the Analytics page pattern.

**Architecture:** Two independent single-file rewrites. Hero card removed from Events; stat cards removed from both pages; metric band added to both. All existing functionality (DataTable, EventModal, ExecutionDetail, filters, export, auto-refetch) is preserved unchanged.

**Tech Stack:** React, TypeScript, TanStack React Query, Tailwind CSS, existing `Badge`, `Skeleton`, `Select`, `Button`, `DataTable`, `DataTableToolbar` components.

---

## File Map

| File | Action |
|---|---|
| `frontend/src/pages/Events.tsx` | Full rewrite |
| `frontend/src/pages/Executions.tsx` | Full rewrite |

---

### Task 1: Rewrite `Events.tsx`

**Files:**
- Modify: `frontend/src/pages/Events.tsx` (full rewrite)

**Codebase context you need:**

- `Skeleton`: `import { Skeleton } from '@/components/ui/Skeleton'`
- `Select`: `import { Select } from '@/components/ui/Select'` — already used in this file
- `Button`: `import { Button } from '@/components/ui/Button'` — already used in this file
- `Badge`: `import { Badge } from '@/components/ui/Badge'` — already used in this file
- CSS variable: `--border` → use as `border-[hsl(var(--border)/0.4)]`
- Metric band layout: `flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]`
- Number typography: `text-5xl font-black tracking-tight`
- Label typography: `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1`
- Colors: Total = `text-foreground`, Critical = `text-red-400`, Sources = `text-blue-400`
- Computed metrics (client-side, from `eventsData`):
  - `totalEvents = eventsData?.length ?? 0`
  - `criticalCount = eventsData?.filter(e => e.severity === 'critical').length ?? 0`
  - `sourcesCount = new Set((eventsData ?? []).map(e => e.source)).size`
- `DataTableToolbar` already accepts children — `Button` goes as a child after the two `Select` filters
- The `Radar` icon is no longer needed (only used in the hero card being removed)
- `refetchInterval: 5000` stays on the query

- [ ] **Step 1: Replace the entire contents of `frontend/src/pages/Events.tsx`**

```tsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { eventsApi } from '@/services/api'
import { Bell, Activity, Server, Layout, Database } from 'lucide-react'
import type { ColumnDef } from '@tanstack/react-table'
import EventModal from '@/components/EventModal'
import DataTable from '@/components/ui/DataTable'
import DataTableToolbar from '@/components/ui/DataTableToolbar'
import { useToast } from '@/components/ui/Toast'
import { useDebounce } from '@/hooks/useDebounce'
import { exportToCSV } from '@/lib/export'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'

interface EventItem {
    id: string
    title: string
    description?: string
    source: string
    severity: string
    event_type: string
    received_at: string
}

const severityVariant = (severity: string) => {
    switch (severity) {
        case 'critical': return 'danger'
        case 'high': return 'orange'
        case 'medium': return 'warning'
        case 'low': return 'info'
        default: return 'neutral'
    }
}

const sourceIcon = (src: string) => {
    switch (src.toLowerCase()) {
        case 'prometheus': return <Activity className="h-4 w-4 text-orange-500" />
        case 'grafana': return <Layout className="h-4 w-4 text-orange-500" />
        case 'system': return <Server className="h-4 w-4 text-blue-500" />
        default: return <Database className="h-4 w-4 text-primary-500" />
    }
}

const columns: ColumnDef<EventItem, any>[] = [
    {
        id: 'severity',
        accessorKey: 'severity',
        header: 'Severity',
        size: 130,
        cell: ({ getValue }) => (
            <Badge variant={severityVariant(getValue()) as any} dot pulse={getValue() === 'critical'}>
                {getValue()}
            </Badge>
        ),
    },
    {
        id: 'title',
        accessorKey: 'title',
        header: 'Event',
        cell: ({ row }) => (
            <div>
                <div className="font-semibold text-gray-950 dark:text-white">{row.original.title}</div>
                {row.original.description && (
                    <div className="mt-1 max-w-md truncate text-xs text-gray-500 dark:text-gray-400">
                        {row.original.description}
                    </div>
                )}
            </div>
        ),
    },
    {
        id: 'source',
        accessorKey: 'source',
        header: 'Source',
        size: 160,
        cell: ({ getValue }) => (
            <div className="flex items-center gap-2">
                {sourceIcon(getValue())}
                <span className="font-medium capitalize text-gray-700 dark:text-gray-300">{getValue()}</span>
            </div>
        ),
    },
    {
        id: 'event_type',
        accessorKey: 'event_type',
        header: 'Type',
        size: 170,
        cell: ({ getValue }) => (
            <span className="rounded-xl border border-gray-200 bg-gray-50 px-2.5 py-1 text-xs font-medium text-gray-600 dark:border-dark-700 dark:bg-dark-800 dark:text-gray-400">
                {getValue()}
            </span>
        ),
    },
    {
        id: 'received_at',
        accessorKey: 'received_at',
        header: 'Received',
        size: 180,
        cell: ({ getValue }) => (
            <span className="text-xs tabular-nums text-gray-500 dark:text-gray-400">
                {new Date(getValue()).toLocaleString()}
            </span>
        ),
    },
]

export default function Events() {
    const [severity, setSeverity] = useState('')
    const [source, setSource] = useState('')
    const [globalFilter, setGlobalFilter] = useState('')
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [isCreating, setIsCreating] = useState(false)

    const debouncedFilter = useDebounce(globalFilter, 300)

    const { data: eventsData, isLoading, refetch } = useQuery({
        queryKey: ['events', severity, source],
        queryFn: () => eventsApi.list({
            limit: 100,
            severity: severity || undefined,
            source: source || undefined,
        }).then((res) => res.data),
        refetchInterval: 5000,
    })

    const toast = useToast()

    const handleCreateEvent = async (data: any) => {
        setIsCreating(true)
        try {
            await eventsApi.create(data)
            setIsModalOpen(false)
            toast.success('Event created successfully')
            refetch()
        } catch {
            toast.error('Failed to create event')
        } finally {
            setIsCreating(false)
        }
    }

    const handleExport = () => {
        const rows = eventsData || []
        exportToCSV(rows, [
            { header: 'Severity', accessorKey: 'severity' },
            { header: 'Title', accessorKey: 'title' },
            { header: 'Description', accessorKey: 'description' },
            { header: 'Source', accessorKey: 'source' },
            { header: 'Type', accessorKey: 'event_type' },
            { header: 'Received At', exportValue: (row) => new Date(row.received_at).toLocaleString() },
        ], 'events')
    }

    const filteredData = debouncedFilter
        ? (eventsData || []).filter((event) =>
            event.title.toLowerCase().includes(debouncedFilter.toLowerCase()) ||
            event.description?.toLowerCase().includes(debouncedFilter.toLowerCase()) ||
            event.event_type.toLowerCase().includes(debouncedFilter.toLowerCase()),
        )
        : (eventsData || [])

    const totalEvents = eventsData?.length ?? 0
    const criticalCount = eventsData?.filter((e) => e.severity === 'critical').length ?? 0
    const sourcesCount = new Set((eventsData ?? []).map((e) => e.source)).size

    const toolbar = (
        <DataTableToolbar
            table={null}
            globalFilter={globalFilter}
            onGlobalFilterChange={setGlobalFilter}
            onExport={handleExport}
            placeholder="Search signals, descriptions, or event types"
        >
            <div className="w-full sm:w-[190px]">
                <Select
                    options={[
                        { value: '', label: 'All severities' },
                        { value: 'critical', label: 'Critical' },
                        { value: 'high', label: 'High' },
                        { value: 'medium', label: 'Medium' },
                        { value: 'low', label: 'Low' },
                        { value: 'info', label: 'Info' },
                    ]}
                    value={severity}
                    onChange={(event) => setSeverity(event.target.value)}
                    className="py-2"
                    aria-label="Filter by severity"
                />
            </div>
            <div className="w-full sm:w-[180px]">
                <Select
                    options={[
                        { value: '', label: 'All sources' },
                        { value: 'prometheus', label: 'Prometheus' },
                        { value: 'grafana', label: 'Grafana' },
                        { value: 'custom', label: 'Custom' },
                    ]}
                    value={source}
                    onChange={(event) => setSource(event.target.value)}
                    className="py-2"
                    aria-label="Filter by source"
                />
            </div>
            <Button onClick={() => setIsModalOpen(true)}>
                <Bell className="h-4 w-4" />
                Create event
            </Button>
        </DataTableToolbar>
    )

    return (
        <div className="flex flex-col">
            {/* Metric band */}
            <div className="flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]">
                {isLoading ? (
                    <>
                        {Array.from({ length: 3 }).map((_, i) => (
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
                                {totalEvents}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Total Events
                            </p>
                        </div>
                        <div>
                            <p className="text-5xl font-black tracking-tight text-red-400">
                                {criticalCount}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Critical
                            </p>
                        </div>
                        <div>
                            <p className="text-5xl font-black tracking-tight text-blue-400">
                                {sourcesCount}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Sources
                            </p>
                        </div>
                    </>
                )}
            </div>

            {/* Table */}
            <div className="mt-6 min-h-0">
                <DataTable
                    columns={columns}
                    data={filteredData}
                    isLoading={isLoading}
                    emptyMessage="No events recorded in this timeframe"
                    storageKey="events"
                    defaultPageSize={25}
                    toolbar={toolbar}
                />
            </div>

            <EventModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleCreateEvent}
                isSaving={isCreating}
            />
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

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Events.tsx
git commit -m "feat(events): container-free metric band, remove hero card"
```

---

### Task 2: Rewrite `Executions.tsx`

**Files:**
- Modify: `frontend/src/pages/Executions.tsx` (full rewrite)

**Codebase context you need:**

- `Skeleton`: `import { Skeleton } from '@/components/ui/Skeleton'`
- `Select`: `import { Select } from '@/components/ui/Select'` — replaces the native `<select>` element
- CSS variable: `--border` → use as `border-[hsl(var(--border)/0.4)]`
- Metric band layout: `flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]`
- Number typography: `text-5xl font-black tracking-tight`
- Label typography: `text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1`
- Colors: Total = `text-foreground`, Success = `text-green-400`, Failed = `text-red-400`, Running = `text-blue-400`
- Computed metrics (client-side, from `executions`):
  - `totalCount = executions?.length ?? 0`
  - `successCount = executions?.filter(e => e.status === 'success').length ?? 0`
  - `failedCount = executions?.filter(e => ['failed','timeout'].includes(e.status)).length ?? 0`
  - `runningCount = executions?.filter(e => e.status === 'running').length ?? 0`
- The `Play` icon is no longer needed (only used in the stat cards being removed)
- `h-[calc(100vh-6rem)]` height constraint on outer div is removed — replaced with `flex flex-col`
- `refetchInterval: 3000` stays on the query
- `ExecutionDetail` function is kept exactly as-is (copy verbatim)

- [ ] **Step 1: Replace the entire contents of `frontend/src/pages/Executions.tsx`**

```tsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { executionsApi } from '@/services/api'
import type { ColumnDef, Row } from '@tanstack/react-table'
import { Clock, CheckCircle, XCircle, Loader, Terminal, AlertCircle } from 'lucide-react'
import DataTable from '@/components/ui/DataTable'
import DataTableToolbar from '@/components/ui/DataTableToolbar'
import { Select } from '@/components/ui/Select'
import { Skeleton } from '@/components/ui/Skeleton'
import { exportToCSV } from '@/lib/export'
import { useDebounce } from '@/hooks/useDebounce'

interface ExecutionItem {
    execution_id: string
    script_name: string
    script_language: string
    status: string
    execution_time_ms?: number
    exit_code?: number | null
    created_at: string
    stdout?: string
    stderr?: string
    error_message?: string
}

const statusBadge = (status: string) => {
    const base = 'flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider border shadow-sm'
    switch (status) {
        case 'success': return `${base} bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20`
        case 'failed':
        case 'timeout': return `${base} bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20`
        case 'running': return `${base} bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20`
        default: return `${base} bg-gray-500/10 text-gray-500 border-gray-500/20`
    }
}

const statusIcon = (status: string) => {
    switch (status) {
        case 'success': return <CheckCircle className="w-3.5 h-3.5" />
        case 'failed':
        case 'timeout': return <XCircle className="w-3.5 h-3.5" />
        case 'running': return <Loader className="w-3.5 h-3.5 animate-spin" />
        default: return <Clock className="w-3.5 h-3.5" />
    }
}

const columns: ColumnDef<ExecutionItem, any>[] = [
    {
        id: 'status',
        accessorKey: 'status',
        header: 'Status',
        size: 140,
        cell: ({ getValue }) => (
            <span className={statusBadge(getValue())}>
                {statusIcon(getValue())}
                {getValue()}
            </span>
        ),
    },
    {
        id: 'script_name',
        accessorKey: 'script_name',
        header: 'Script',
        cell: ({ getValue }) => (
            <div className="font-semibold text-gray-900 dark:text-gray-100">{getValue()}</div>
        ),
    },
    {
        id: 'script_language',
        accessorKey: 'script_language',
        header: 'Language',
        size: 110,
        cell: ({ getValue }) => (
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-gray-100 dark:bg-dark-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-dark-700">
                {getValue()}
            </span>
        ),
    },
    {
        id: 'execution_time_ms',
        accessorKey: 'execution_time_ms',
        header: 'Duration',
        size: 110,
        cell: ({ getValue }) => (
            <span className="font-mono text-xs text-gray-600 dark:text-gray-400">
                {getValue() ? `${getValue()}ms` : '—'}
            </span>
        ),
    },
    {
        id: 'created_at',
        accessorKey: 'created_at',
        header: 'Executed At',
        size: 160,
        cell: ({ getValue }) => (
            <span className="text-gray-500 dark:text-gray-400 text-xs tabular-nums">
                {new Date(getValue()).toLocaleString()}
            </span>
        ),
    },
]

function ExecutionDetail({ row }: { row: Row<ExecutionItem> }) {
    const exec = row.original
    const { data: details, isLoading } = useQuery({
        queryKey: ['execution', exec.execution_id],
        queryFn: () => executionsApi.getStatus(exec.execution_id).then(r => r.data),
    })
    const d = (details || exec) as any

    return (
        <div className="space-y-4">
            {isLoading ? (
                <div className="flex items-center gap-2 text-sm text-gray-500 py-4">
                    <Loader className="w-4 h-4 animate-spin text-primary-500" />
                    Fetching logs...
                </div>
            ) : (
                <>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {[
                            { label: 'Status', value: d.status, cls: d.status === 'success' ? 'text-green-500' : 'text-red-500' },
                            { label: 'Duration', value: d.execution_time_ms ? `${d.execution_time_ms}ms` : '—', cls: '' },
                            { label: 'Exit Code', value: String(d.exit_code ?? '—'), cls: 'font-mono' },
                            { label: 'Time', value: new Date(d.created_at).toLocaleTimeString(), cls: '' },
                        ].map(({ label, value, cls }) => (
                            <div key={label} className="p-3 bg-white dark:bg-dark-900 rounded-lg border border-gray-100 dark:border-dark-700">
                                <div className="text-xs text-gray-500 uppercase tracking-wider font-bold">{label}</div>
                                <div className={`text-sm font-bold mt-1 ${cls} text-gray-900 dark:text-gray-100`}>{value}</div>
                            </div>
                        ))}
                    </div>

                    {d.error_message && (
                        <div className="p-3 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-lg flex items-start gap-3">
                            <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                            <p className="text-sm text-red-600 dark:text-red-300 font-mono break-all">{d.error_message}</p>
                        </div>
                    )}

                    <div>
                        <div className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1.5 flex items-center gap-1.5">
                            <Terminal className="w-3.5 h-3.5" /> Standard Output
                        </div>
                        <div className="bg-gray-950 rounded-lg p-4 overflow-x-auto border border-gray-800 max-h-48">
                            <pre className="font-mono text-xs text-gray-300 whitespace-pre-wrap">
                                {d.stdout || <span className="text-gray-600 italic">No output</span>}
                            </pre>
                        </div>
                    </div>

                    {d.stderr && (
                        <div>
                            <div className="text-xs font-bold uppercase tracking-wider text-red-500 mb-1.5">Standard Error</div>
                            <div className="bg-gray-950 rounded-lg p-4 overflow-x-auto border border-red-900/50 max-h-48">
                                <pre className="font-mono text-xs text-red-400 whitespace-pre-wrap">{d.stderr}</pre>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

export default function Executions() {
    const [statusFilter, setStatusFilter] = useState('')
    const [globalFilter, setGlobalFilter] = useState('')
    const debouncedFilter = useDebounce(globalFilter, 300)

    const { data: executions, isLoading } = useQuery({
        queryKey: ['executions', statusFilter],
        queryFn: () => executionsApi.list({ limit: 100, status: statusFilter || undefined }).then(res => res.data),
        refetchInterval: 3000,
    })

    const totalCount = executions?.length ?? 0
    const successCount = executions?.filter((e: any) => e.status === 'success').length ?? 0
    const failedCount = executions?.filter((e: any) => ['failed', 'timeout'].includes(e.status)).length ?? 0
    const runningCount = executions?.filter((e: any) => e.status === 'running').length ?? 0

    const filteredData: ExecutionItem[] = debouncedFilter
        ? (executions || []).filter((e: any) =>
            e.script_name?.toLowerCase().includes(debouncedFilter.toLowerCase()) ||
            e.status?.toLowerCase().includes(debouncedFilter.toLowerCase())
          )
        : (executions || [])

    const handleExport = () => {
        exportToCSV(filteredData, [
            { header: 'Status', accessorKey: 'status' },
            { header: 'Script', accessorKey: 'script_name' },
            { header: 'Language', accessorKey: 'script_language' },
            { header: 'Duration (ms)', accessorKey: 'execution_time_ms' },
            { header: 'Exit Code', accessorKey: 'exit_code' },
            { header: 'Executed At', exportValue: (r) => new Date(r.created_at).toLocaleString() },
        ], 'executions')
    }

    const toolbar = (
        <DataTableToolbar
            table={null}
            globalFilter={globalFilter}
            onGlobalFilterChange={setGlobalFilter}
            onExport={handleExport}
            placeholder="Search scripts..."
        >
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
        </DataTableToolbar>
    )

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
                                {totalCount}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Total
                            </p>
                        </div>
                        <div>
                            <p className="text-5xl font-black tracking-tight text-green-400">
                                {successCount}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Success
                            </p>
                        </div>
                        <div>
                            <p className="text-5xl font-black tracking-tight text-red-400">
                                {failedCount}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Failed
                            </p>
                        </div>
                        <div>
                            <p className="text-5xl font-black tracking-tight text-blue-400">
                                {runningCount}
                            </p>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Running
                            </p>
                        </div>
                    </>
                )}
            </div>

            {/* Table */}
            <div className="mt-6 flex-1 min-h-0">
                <DataTable
                    columns={columns}
                    data={filteredData}
                    isLoading={isLoading}
                    emptyMessage="No executions found"
                    renderSubRow={(row) => <ExecutionDetail row={row} />}
                    storageKey="executions"
                    defaultPageSize={25}
                    toolbar={toolbar}
                />
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

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Executions.tsx
git commit -m "feat(executions): container-free metric band, remove stat cards"
```
