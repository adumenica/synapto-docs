# UI Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add CI/CD Risk Assessment page, Action Catalogue page, Service Health Dashboard widget, and real-time SSE incident updates to the Synapto frontend.

**Architecture:** One backend filter addition (knowledge-layer), one new backend SSE endpoint (api-gateway), five new frontend files (page + components + hook), and modifications to four existing frontend files. All frontend code follows the existing pattern: React Query, TanStack Table, Recharts, React Hook Form + Zod, `cn()` from `@/lib/utils`, `useToast` from `@/components/ui/Toast`.

**Tech Stack:** Python 3.11 / FastAPI (backend), React 18 / TypeScript / Vite (frontend), TanStack Query v5, React Hook Form v7, Zod v4, Recharts, Monaco Editor (`@monaco-editor/react`), Lucide React icons, Tailwind CSS

---

## Files Overview

### Backend
- Modify: `backend/knowledge-layer/main.py` — add `is_gold_standard` query filter to `GET /scripts`
- Modify: `backend/api-gateway/main.py` — add `GET /api/v1/incidents/stream` SSE endpoint

### Frontend
- Modify: `frontend/src/services/api.ts` — add `CICDDeployment`, `CICDRiskAssessment`, `CatalogueScript` types + `cicdApi`, `catalogueApi`
- Create: `frontend/src/components/cicd/RiskResultPanel.tsx` — result display component
- Create: `frontend/src/pages/CICDRisk.tsx` — CI/CD Risk Assessment page
- Create: `frontend/src/components/dashboard/ServiceHealthWidget.tsx` — service health sparkline widget
- Modify: `frontend/src/pages/Dashboard.tsx` — add `ServiceHealthWidget`
- Create: `frontend/src/hooks/useIncidentStream.ts` — SSE hook
- Modify: `frontend/src/pages/Incidents.tsx` — remove `refetchInterval`, add `useIncidentStream`
- Create: `frontend/src/components/catalogue/ScriptDrawer.tsx` — script detail side drawer
- Create: `frontend/src/pages/ActionCatalogue.tsx` — Action Catalogue page
- Modify: `frontend/src/components/incidents/IncidentDetailPanel.tsx` — add promotion banner
- Modify: `frontend/src/App.tsx` — add `/cicd` and `/catalogue` routes
- Modify: `frontend/src/components/Layout.tsx` — add two sidebar nav items

---

### Task 1: Add `is_gold_standard` filter to knowledge-layer

**Files:**
- Modify: `backend/knowledge-layer/main.py:652-687`

- [ ] **Step 1: Read the current `list_scripts` function**

Open `backend/knowledge-layer/main.py` around line 652. The function signature is:
```python
def list_scripts(
    category: Optional[str] = None,
    name: Optional[str] = None,
    tenant_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
```

- [ ] **Step 2: Add the `is_gold_standard` parameter and filter**

Replace the function signature and query block:

```python
@app.get("/scripts")
def list_scripts(
    category: Optional[str] = None,
    name: Optional[str] = None,
    tenant_id: Optional[str] = None,
    is_gold_standard: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List scripts in the library, optionally filtered by category, name, tenant, or gold standard status."""
    try:
        query = db.query(Script)
        if category:
            query = query.filter(Script.category == category)
        if name:
            query = query.filter(Script.name == name)
        if tenant_id:
            try:
                query = query.filter(Script.tenant_id == uuid.UUID(tenant_id))
            except (ValueError, AttributeError):
                pass
        if is_gold_standard is not None:
            query = query.filter(Script.is_gold_standard == is_gold_standard)

        scripts = query.order_by(Script.category, Script.name).all()
```

Also add `is_gold_standard` to the return dict for each script. Find the `return [` block and add the field:

```python
        return [
            {
                "id": str(s.id),
                "name": s.name,
                "description": s.description,
                "language": s.language.value,
                "content": s.content,
                "category": s.category,
                "meta_data": s.meta_data,
                "is_gold_standard": s.is_gold_standard,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in scripts
        ]
```

- [ ] **Step 3: Rebuild and verify**

```bash
cd /Users/alind/Projects/Synapto
docker compose build knowledge-layer 2>&1 | tail -3
docker compose up -d knowledge-layer
sleep 4
docker exec synapto-knowledge python3 -c "
import urllib.request
r = urllib.request.urlopen('http://localhost:8003/scripts?is_gold_standard=true')
print(r.read().decode())
"
```

Expected: JSON array (empty `[]` is fine — no gold scripts yet).

- [ ] **Step 4: Commit**

```bash
git add backend/knowledge-layer/main.py
git commit -m "feat(knowledge): add is_gold_standard filter to GET /scripts"
```

---

### Task 2: Add SSE incident stream endpoint to api-gateway

**Files:**
- Modify: `backend/api-gateway/main.py`

- [ ] **Step 1: Add imports at the top of api-gateway/main.py**

Find the existing imports block and add:

```python
import json
import asyncio
from fastapi.responses import StreamingResponse
```

(`json` and `asyncio` are stdlib — no install needed. `StreamingResponse` is from fastapi which is already installed.)

- [ ] **Step 2: Add the SSE endpoint**

Find `@app.get("/health")` and add this endpoint directly above it:

```python
@app.get("/api/v1/incidents/stream")
async def incident_stream(current_user: TokenPayload = Depends(get_current_user)):
    """
    SSE stream of incident events from Redis.
    Browsers connect with EventSource (cookies sent automatically).
    Pushes JSON: {"type": "incident.created"|"incident.updated", "incident_id": "..."}
    """
    async def event_generator():
        last_id = b"$"
        while True:
            try:
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None,
                    lambda: redis_client.xread({"events": last_id}, count=20, block=2000),
                )
                if results:
                    for _stream, messages in results:
                        for msg_id, fields in messages:
                            last_id = msg_id
                            raw_type = fields.get(b"type", b"").decode("utf-8", errors="ignore")
                            if raw_type.startswith("incident"):
                                incident_id = fields.get(b"incident_id", b"").decode("utf-8", errors="ignore")
                                payload = json.dumps({"type": raw_type, "incident_id": incident_id})
                                yield f"data: {payload}\n\n"
            except Exception as exc:
                logger.warning(f"SSE stream error: {exc}")
                await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
```

- [ ] **Step 3: Verify syntax**

```bash
python3 -c "import ast; ast.parse(open('backend/api-gateway/main.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Rebuild and verify**

```bash
docker compose build api-gateway 2>&1 | tail -3
docker compose up -d api-gateway
sleep 5
curl -s http://localhost:8000/health | python3 -m json.tool | grep status
```

Expected: `"status": "healthy"`

- [ ] **Step 5: Commit**

```bash
git add backend/api-gateway/main.py
git commit -m "feat(gateway): add SSE incident stream endpoint GET /api/v1/incidents/stream"
```

---

### Task 3: Add new types and API functions to api.ts

**Files:**
- Modify: `frontend/src/services/api.ts`

- [ ] **Step 1: Add CI/CD types after the `sopsApi` block**

Append to the end of `frontend/src/services/api.ts`:

```typescript
// ── CI/CD Risk Assessment ──────────────────────────────────────────────────

export interface CICDDeployment {
    service_name: string;
    changed_files: string[];       // array of filenames; UI sends ["file_1", ..., "file_N"]
    has_db_migration: boolean;
    is_off_hours: boolean;
    affected_services: string[];
    environment: 'development' | 'staging' | 'production';
    rollback_available: boolean;
    commit_message?: string;
}

export interface CICDRiskAssessment {
    risk_score: number;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    risk_factors: string[];
    requires_manual_approval: boolean;
    recommendation: string;
}

export const cicdApi = {
    assess: (data: CICDDeployment) =>
        api.post<CICDRiskAssessment>('/api/v1/cicd/risk-assessment', data),
};

// ── Action Catalogue ───────────────────────────────────────────────────────

export interface CatalogueScript {
    id: string;
    name: string;
    description?: string;
    language: ScriptLanguage;
    content: string;
    category: string;
    is_gold_standard: boolean;
    meta_data?: Record<string, any>;
    created_at: string;
    updated_at: string;
}

export const catalogueApi = {
    list: () =>
        api.get<CatalogueScript[]>('/api/v1/knowledge/scripts', {
            params: { is_gold_standard: true },
        }),

    remove: (id: string) =>
        api.patch<{ id: string; is_gold_standard: boolean }>(
            `/api/v1/knowledge/scripts/${id}`,
            { is_gold_standard: false },
        ),
};

export const promoteIncident = (id: string) =>
    api.post<{ success: boolean; message: string }>(`/api/v1/incidents/${id}/promote`);

// ── Service Health ─────────────────────────────────────────────────────────

export interface ServiceHealth {
    status: string;
    response_time_ms: number;
}

export interface HealthResponse {
    status: string;
    timestamp: string;
    services: Record<string, ServiceHealth>;
}

export const healthApi = {
    get: () => api.get<HealthResponse>('/health'),
};
```

- [ ] **Step 2: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend
npx tsc --noEmit 2>&1 | head -20
```

Expected: No errors (or only pre-existing errors unrelated to api.ts).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat(api): add CICDDeployment, CatalogueScript types and cicdApi, catalogueApi, healthApi"
```

---

### Task 4: Build RiskResultPanel component

**Files:**
- Create: `frontend/src/components/cicd/RiskResultPanel.tsx`

- [ ] **Step 1: Create the directory and component file**

```bash
mkdir -p frontend/src/components/cicd
```

Create `frontend/src/components/cicd/RiskResultPanel.tsx`:

```tsx
import { cn } from '@/lib/utils'
import type { CICDRiskAssessment } from '@/services/api'

interface Props {
    result: CICDRiskAssessment | null
    loading: boolean
}

const LEVEL_STYLES: Record<string, { bg: string; text: string; border: string; badge: string }> = {
    low:      { bg: 'bg-green-500/8',   text: 'text-green-400',  border: 'border-green-500/20',  badge: 'bg-green-500/15 text-green-300' },
    medium:   { bg: 'bg-yellow-500/8',  text: 'text-yellow-400', border: 'border-yellow-500/20', badge: 'bg-yellow-500/15 text-yellow-300' },
    high:     { bg: 'bg-orange-500/8',  text: 'text-orange-400', border: 'border-orange-500/20', badge: 'bg-orange-500/15 text-orange-300' },
    critical: { bg: 'bg-red-500/8',     text: 'text-red-400',    border: 'border-red-500/20',    badge: 'bg-red-500/15 text-red-300' },
}

export default function RiskResultPanel({ result, loading }: Props) {
    if (loading) {
        return (
            <div className="rounded-lg border border-[hsl(var(--border)/0.4)] p-6 flex items-center justify-center min-h-[280px]">
                <div className="flex flex-col items-center gap-3 text-muted-foreground">
                    <div className="h-8 w-8 rounded-full border-2 border-current border-t-transparent animate-spin" />
                    <span className="text-sm">Calculating risk...</span>
                </div>
            </div>
        )
    }

    if (!result) {
        return (
            <div className="rounded-lg border border-dashed border-[hsl(var(--border)/0.4)] p-6 flex items-center justify-center min-h-[280px]">
                <p className="text-sm text-muted-foreground text-center">
                    Fill in deployment details<br />to see the risk score
                </p>
            </div>
        )
    }

    const s = LEVEL_STYLES[result.risk_level] ?? LEVEL_STYLES.medium

    return (
        <div className={cn('rounded-lg border p-6 space-y-5', s.bg, s.border)}>
            {/* Score + level */}
            <div className="flex items-end gap-4">
                <span className={cn('text-6xl font-bold leading-none', s.text)}>
                    {result.risk_score.toFixed(2)}
                </span>
                <div className="mb-1 space-y-1">
                    <span className={cn('inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider', s.badge)}>
                        {result.risk_level}
                    </span>
                    {result.requires_manual_approval && (
                        <p className={cn('text-xs font-medium', s.text)}>
                            ⚠ Manual approval required
                        </p>
                    )}
                </div>
            </div>

            {/* Risk factors */}
            {result.risk_factors.length > 0 && (
                <div>
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                        Risk factors
                    </p>
                    <ul className="space-y-1">
                        {result.risk_factors.map((f) => (
                            <li key={f} className="text-sm flex items-start gap-2">
                                <span className={cn('mt-0.5 shrink-0', s.text)}>•</span>
                                <span>{f}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Recommendation */}
            <div className={cn('rounded-md p-3', s.bg)}>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                    Recommendation
                </p>
                <p className="text-sm">{result.recommendation}</p>
            </div>
        </div>
    )
}
```

- [ ] **Step 2: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | grep "cicd" | head -10
```

Expected: No errors mentioning cicd.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/cicd/
git commit -m "feat(cicd): add RiskResultPanel component"
```

---

### Task 5: Build CICDRisk page

**Files:**
- Create: `frontend/src/pages/CICDRisk.tsx`

- [ ] **Step 1: Create the page**

Create `frontend/src/pages/CICDRisk.tsx`:

```tsx
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState, useEffect } from 'react'
import { Rocket } from 'lucide-react'
import { cicdApi } from '@/services/api'
import type { CICDRiskAssessment } from '@/services/api'
import { useDebounce } from '@/hooks/useDebounce'
import RiskResultPanel from '@/components/cicd/RiskResultPanel'

const schema = z.object({
    service_name:      z.string().min(1, 'Required'),
    environment:       z.enum(['development', 'staging', 'production']),
    changed_files:     z.coerce.number().int().min(0).default(1),
    affected_services: z.string().default(''),
    has_db_migration:  z.boolean().default(false),
    is_off_hours:      z.boolean().default(false),
    rollback_available: z.boolean().default(true),
    commit_message:    z.string().optional(),
})

type FormValues = z.infer<typeof schema>

export default function CICDRisk() {
    const { register, control, watch, formState: { errors } } = useForm<FormValues>({
        resolver: zodResolver(schema),
        defaultValues: {
            environment: 'staging',
            changed_files: 1,
            has_db_migration: false,
            is_off_hours: false,
            rollback_available: true,
        },
    })

    const [result, setResult] = useState<CICDRiskAssessment | null>(null)
    const [loading, setLoading] = useState(false)

    const values = watch()
    const debouncedValues = useDebounce(values, 400)

    useEffect(() => {
        const { service_name, changed_files } = debouncedValues
        if (!service_name) { setResult(null); return }

        const payload = {
            service_name,
            environment: debouncedValues.environment,
            changed_files: Array.from({ length: Math.max(1, changed_files) }, (_, i) => `file_${i + 1}`),
            affected_services: debouncedValues.affected_services
                ? debouncedValues.affected_services.split(',').map(s => s.trim()).filter(Boolean)
                : [],
            has_db_migration: debouncedValues.has_db_migration,
            is_off_hours: debouncedValues.is_off_hours,
            rollback_available: debouncedValues.rollback_available,
            commit_message: debouncedValues.commit_message,
        }

        setLoading(true)
        cicdApi.assess(payload)
            .then(res => setResult(res.data))
            .catch(() => setResult(null))
            .finally(() => setLoading(false))
    }, [debouncedValues])

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3">
                <Rocket className="h-6 w-6 text-primary" />
                <div>
                    <h1 className="text-2xl font-bold">CI/CD Risk Assessment</h1>
                    <p className="text-sm text-muted-foreground">
                        Score a deployment for risk before going to production.
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* ── Left: Form ───────────────────────────────────── */}
                <div className="space-y-5">
                    <div>
                        <label className="block text-sm font-medium mb-1.5">Service name <span className="text-red-400">*</span></label>
                        <input
                            {...register('service_name')}
                            className="w-full rounded-md border border-[hsl(var(--border)/0.6)] bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                            placeholder="e.g. api-gateway"
                        />
                        {errors.service_name && <p className="text-xs text-red-400 mt-1">{errors.service_name.message}</p>}
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1.5">Environment</label>
                        <select
                            {...register('environment')}
                            className="w-full rounded-md border border-[hsl(var(--border)/0.6)] bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                        >
                            <option value="development">Development</option>
                            <option value="staging">Staging</option>
                            <option value="production">Production</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1.5">Changed files (count)</label>
                        <input
                            {...register('changed_files')}
                            type="number"
                            min={0}
                            className="w-full rounded-md border border-[hsl(var(--border)/0.6)] bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1.5">Affected services <span className="text-muted-foreground text-xs">(comma-separated)</span></label>
                        <input
                            {...register('affected_services')}
                            className="w-full rounded-md border border-[hsl(var(--border)/0.6)] bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                            placeholder="e.g. auth-service, api-gateway"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1.5">Commit message <span className="text-muted-foreground text-xs">(optional)</span></label>
                        <textarea
                            {...register('commit_message')}
                            rows={2}
                            className="w-full rounded-md border border-[hsl(var(--border)/0.6)] bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 resize-none"
                            placeholder="feat: add new endpoint"
                        />
                    </div>

                    {/* Toggles */}
                    <div className="space-y-3 pt-1">
                        {(
                            [
                                { name: 'has_db_migration',   label: 'Database migration included' },
                                { name: 'is_off_hours',        label: 'Off-hours deployment' },
                                { name: 'rollback_available',  label: 'Rollback available' },
                            ] as { name: keyof FormValues; label: string }[]
                        ).map(({ name, label }) => (
                            <Controller
                                key={name}
                                control={control}
                                name={name}
                                render={({ field }) => (
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm">{label}</span>
                                        <button
                                            type="button"
                                            role="switch"
                                            aria-checked={!!field.value}
                                            onClick={() => field.onChange(!field.value)}
                                            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${field.value ? 'bg-primary' : 'bg-muted'}`}
                                        >
                                            <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${field.value ? 'translate-x-4.5' : 'translate-x-0.5'}`} />
                                        </button>
                                    </div>
                                )}
                            />
                        ))}
                    </div>
                </div>

                {/* ── Right: Result ────────────────────────────────── */}
                <div>
                    <RiskResultPanel result={result} loading={loading} />
                </div>
            </div>
        </div>
    )
}
```

- [ ] **Step 2: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | grep "CICDRisk\|cicd" | head -10
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/CICDRisk.tsx
git commit -m "feat(cicd): add CICDRisk page with live two-column layout"
```

---

### Task 6: Build ServiceHealthWidget

**Files:**
- Create: `frontend/src/components/dashboard/ServiceHealthWidget.tsx`

- [ ] **Step 1: Create the component**

Create `frontend/src/components/dashboard/ServiceHealthWidget.tsx`:

```tsx
import { useQuery } from '@tanstack/react-query'
import { useRef } from 'react'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import { healthApi } from '@/services/api'
import { cn } from '@/lib/utils'

// Rolling history: service name → last 10 response_time_ms readings
const history: Record<string, number[]> = {}

function pushHistory(name: string, ms: number) {
    if (!history[name]) history[name] = []
    history[name] = [...history[name].slice(-9), ms]
    return history[name]
}

function avg(arr: number[]) {
    if (!arr.length) return 0
    return (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)
}

export default function ServiceHealthWidget() {
    const lastUpdated = useRef<Date | null>(null)

    const { data, isLoading } = useQuery({
        queryKey: ['health'],
        queryFn: () => healthApi.get().then(res => {
            lastUpdated.current = new Date()
            return res.data
        }),
        refetchInterval: 15_000,
    })

    const services = data?.services ? Object.entries(data.services) : []
    const healthyCount = services.filter(([, s]) => s.status === 'healthy').length
    const total = services.length

    if (isLoading) {
        return (
            <div className="rounded-lg border border-[hsl(var(--border)/0.4)] p-5">
                <div className="h-5 w-32 bg-muted/40 rounded animate-pulse mb-4" />
                {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="h-8 bg-muted/30 rounded mb-2 animate-pulse" />
                ))}
            </div>
        )
    }

    return (
        <div className="rounded-lg border border-[hsl(var(--border)/0.4)] overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-[hsl(var(--border)/0.4)]">
                <div className="flex items-center gap-3">
                    <h2 className="text-sm font-semibold">Service Health</h2>
                    <span className={cn(
                        'text-xs px-2 py-0.5 rounded-full font-medium',
                        healthyCount === total
                            ? 'bg-green-500/10 text-green-400'
                            : 'bg-red-500/10 text-red-400'
                    )}>
                        {healthyCount}/{total} healthy
                    </span>
                </div>
                {lastUpdated.current && (
                    <span className="text-xs text-muted-foreground">
                        polling every 15s
                    </span>
                )}
            </div>

            {/* Table */}
            <div className="divide-y divide-[hsl(var(--border)/0.3)]">
                {/* Column headers */}
                <div className="grid grid-cols-[160px_80px_1fr_70px] gap-4 px-5 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted/20">
                    <span>Service</span>
                    <span>Status</span>
                    <span>Response time</span>
                    <span className="text-right">Avg</span>
                </div>

                {services.map(([name, svc]) => {
                    const isDown = svc.status !== 'healthy'
                    const hist = pushHistory(name, svc.response_time_ms ?? 0)
                    const chartData = hist.map((v, i) => ({ i, v }))

                    return (
                        <div
                            key={name}
                            className={cn(
                                'grid grid-cols-[160px_80px_1fr_70px] gap-4 items-center px-5 py-2.5',
                                isDown && 'bg-red-500/5'
                            )}
                        >
                            <span className="text-sm font-mono truncate">{name}</span>

                            <div className="flex items-center gap-1.5">
                                <span className={cn(
                                    'h-2 w-2 rounded-full shrink-0',
                                    isDown ? 'bg-red-500 animate-pulse' : 'bg-green-500'
                                )} />
                                <span className={cn(
                                    'text-xs',
                                    isDown ? 'text-red-400' : 'text-green-400'
                                )}>
                                    {isDown ? 'down' : 'healthy'}
                                </span>
                            </div>

                            <div className="h-8">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData}>
                                        <Line
                                            type="monotone"
                                            dataKey="v"
                                            stroke={isDown ? '#ef4444' : '#6366f1'}
                                            strokeWidth={1.5}
                                            dot={false}
                                            isAnimationActive={false}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>

                            <span className={cn(
                                'text-xs text-right font-mono',
                                isDown ? 'text-red-400' : 'text-muted-foreground'
                            )}>
                                {isDown ? 'timeout' : `${avg(hist)}ms`}
                            </span>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
```

- [ ] **Step 2: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | grep "ServiceHealth" | head -5
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/dashboard/ServiceHealthWidget.tsx
git commit -m "feat(dashboard): add ServiceHealthWidget with sparkline response times"
```

---

### Task 7: Add ServiceHealthWidget to Dashboard

**Files:**
- Modify: `frontend/src/pages/Dashboard.tsx`

- [ ] **Step 1: Add the import**

In `frontend/src/pages/Dashboard.tsx`, add to the imports at the top:

```tsx
import ServiceHealthWidget from '@/components/dashboard/ServiceHealthWidget'
```

- [ ] **Step 2: Add the widget to the JSX**

Find the section comment `{/* ── Metric Band */}` in Dashboard.tsx. Add the widget between the metric band section and the chart/incident list section. Find the closing `</section>` of the metric band and add right after it:

```tsx
{/* ── Service Health ──────────────────────────────── */}
<ServiceHealthWidget />
```

- [ ] **Step 3: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | grep "Dashboard" | head -5
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Dashboard.tsx
git commit -m "feat(dashboard): add ServiceHealthWidget to Dashboard page"
```

---

### Task 8: Build useIncidentStream hook

**Files:**
- Create: `frontend/src/hooks/useIncidentStream.ts`

- [ ] **Step 1: Create the hook**

Create `frontend/src/hooks/useIncidentStream.ts`:

```typescript
import { useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/components/ui/Toast'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

/**
 * Connects to the SSE incident stream at GET /api/v1/incidents/stream.
 * On new incident events:  invalidates the 'incidents' React Query cache
 *                          and shows a toast notification.
 * Auto-reconnects on error with a 5s delay.
 * Cleans up on unmount.
 */
export function useIncidentStream() {
    const qc = useQueryClient()
    const { info } = useToast()
    const esRef = useRef<EventSource | null>(null)
    const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

    useEffect(() => {
        function connect() {
            const es = new EventSource(`${API_BASE_URL}/api/v1/incidents/stream`, {
                withCredentials: true,
            })
            esRef.current = es

            es.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    qc.invalidateQueries({ queryKey: ['incidents'] })
                    if (data.type === 'incident.created') {
                        info('New incident detected')
                    }
                } catch {
                    // ignore malformed messages
                }
            }

            es.onerror = () => {
                es.close()
                esRef.current = null
                retryTimer.current = setTimeout(connect, 5_000)
            }
        }

        connect()

        return () => {
            esRef.current?.close()
            esRef.current = null
            if (retryTimer.current) clearTimeout(retryTimer.current)
        }
    }, [qc, info])
}
```

- [ ] **Step 2: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | grep "useIncidentStream" | head -5
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/hooks/useIncidentStream.ts
git commit -m "feat(hooks): add useIncidentStream SSE hook"
```

---

### Task 9: Wire real-time updates to Incidents page

**Files:**
- Modify: `frontend/src/pages/Incidents.tsx`

- [ ] **Step 1: Add the import**

In `frontend/src/pages/Incidents.tsx`, add to existing imports:

```tsx
import { useIncidentStream } from '@/hooks/useIncidentStream'
```

- [ ] **Step 2: Add the hook call and remove polling**

Inside `export default function Incidents()`, immediately after the `useParams`/`useNavigate` lines, add:

```tsx
useIncidentStream()
```

Then find the `useQuery` call for incidents and remove `refetchInterval: 5000`:

```tsx
// Before:
const { data: incidentsData, isLoading } = useQuery({
    queryKey: ['incidents', status],
    queryFn: () =>
        incidentsApi.list({ limit: 100, status: status || undefined }).then(res => res.data),
    refetchInterval: 5000,   // ← remove this line
})

// After:
const { data: incidentsData, isLoading } = useQuery({
    queryKey: ['incidents', status],
    queryFn: () =>
        incidentsApi.list({ limit: 100, status: status || undefined }).then(res => res.data),
})
```

- [ ] **Step 3: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | grep "Incidents" | head -5
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Incidents.tsx
git commit -m "feat(incidents): replace 5s polling with SSE real-time updates"
```

---

### Task 10: Build ScriptDrawer component

**Files:**
- Create: `frontend/src/components/catalogue/ScriptDrawer.tsx`

- [ ] **Step 1: Create the directory and component**

```bash
mkdir -p frontend/src/components/catalogue
```

Create `frontend/src/components/catalogue/ScriptDrawer.tsx`:

```tsx
import { X, Trash2 } from 'lucide-react'
import Editor from '@monaco-editor/react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { catalogueApi } from '@/services/api'
import type { CatalogueScript } from '@/services/api'
import { useToast } from '@/components/ui/Toast'
import { useTheme } from '@/hooks/useTheme'
import { Badge } from '@/components/ui'

interface Props {
    script: CatalogueScript | null
    onClose: () => void
}

const LANG_MAP: Record<string, string> = {
    PYTHON: 'python',
    BASH: 'shell',
    SHELL: 'shell',
    POWERSHELL: 'powershell',
}

export default function ScriptDrawer({ script, onClose }: Props) {
    const qc = useQueryClient()
    const { success, error } = useToast()
    const { theme } = useTheme()

    const removeMutation = useMutation({
        mutationFn: () => catalogueApi.remove(script!.id),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ['catalogue'] })
            success('Removed from Action Catalogue')
            onClose()
        },
        onError: () => error('Failed to remove from catalogue'),
    })

    if (!script) return null

    return (
        <div className="fixed inset-y-0 right-0 z-50 w-[480px] bg-background border-l border-[hsl(var(--border)/0.4)] shadow-2xl flex flex-col animate-in slide-in-from-right-4 duration-200">
            {/* Header */}
            <div className="flex items-start justify-between p-5 border-b border-[hsl(var(--border)/0.4)]">
                <div className="flex-1 min-w-0 pr-4">
                    <div className="flex items-center gap-2 mb-1.5">
                        <span className="text-amber-400 text-lg">🏆</span>
                        <h2 className="text-base font-semibold truncate">{script.name}</h2>
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="neutral">{script.category}</Badge>
                        <Badge variant="neutral">{script.language}</Badge>
                    </div>
                </div>
                <button
                    onClick={onClose}
                    aria-label="Close drawer"
                    className="text-muted-foreground hover:text-foreground transition-colors shrink-0"
                >
                    <X className="h-4 w-4" />
                </button>
            </div>

            {/* Description */}
            {script.description && (
                <div className="px-5 py-3 border-b border-[hsl(var(--border)/0.4)]">
                    <p className="text-sm text-muted-foreground">{script.description}</p>
                </div>
            )}

            {/* Monaco editor */}
            <div className="flex-1 overflow-hidden">
                <Editor
                    height="100%"
                    language={LANG_MAP[script.language] ?? 'plaintext'}
                    value={script.content}
                    theme={theme === 'dark' ? 'vs-dark' : 'light'}
                    options={{
                        readOnly: true,
                        minimap: { enabled: false },
                        fontSize: 13,
                        lineNumbers: 'on',
                        scrollBeyondLastLine: false,
                        wordWrap: 'on',
                    }}
                />
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-[hsl(var(--border)/0.4)] flex items-center justify-between">
                <div className="text-xs text-muted-foreground">
                    Promoted {new Date(script.updated_at).toLocaleDateString()}
                </div>
                <button
                    onClick={() => removeMutation.mutate()}
                    disabled={removeMutation.isPending}
                    className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 transition-colors disabled:opacity-50"
                >
                    <Trash2 className="h-3.5 w-3.5" />
                    Remove from Catalogue
                </button>
            </div>
        </div>
    )
}
```

- [ ] **Step 2: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | grep "ScriptDrawer\|catalogue" | head -5
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/catalogue/
git commit -m "feat(catalogue): add ScriptDrawer component with Monaco viewer"
```

---

### Task 11: Build ActionCatalogue page

**Files:**
- Create: `frontend/src/pages/ActionCatalogue.tsx`

- [ ] **Step 1: Create the page**

Create `frontend/src/pages/ActionCatalogue.tsx`:

```tsx
import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Trophy, Search } from 'lucide-react'
import {
    useReactTable,
    getCoreRowModel,
    getFilteredRowModel,
    flexRender,
    createColumnHelper,
} from '@tanstack/react-table'
import { catalogueApi } from '@/services/api'
import type { CatalogueScript } from '@/services/api'
import { Badge } from '@/components/ui'
import { Skeleton } from '@/components/ui/Skeleton'
import { useDebounce } from '@/hooks/useDebounce'
import ScriptDrawer from '@/components/catalogue/ScriptDrawer'

const col = createColumnHelper<CatalogueScript>()

const columns = [
    col.accessor('name', {
        header: 'Name',
        cell: info => (
            <div className="flex items-center gap-2">
                <span className="text-amber-400 text-sm">🏆</span>
                <span className="font-medium text-sm">{info.getValue()}</span>
            </div>
        ),
    }),
    col.accessor('category', {
        header: 'Category',
        cell: info => <Badge variant="neutral" className="text-xs">{info.getValue()}</Badge>,
    }),
    col.accessor('language', {
        header: 'Language',
        cell: info => <span className="text-sm text-muted-foreground">{info.getValue()}</span>,
    }),
    col.accessor('updated_at', {
        header: 'Promoted',
        cell: info => (
            <span className="text-xs text-muted-foreground">
                {new Date(info.getValue()).toLocaleDateString()}
            </span>
        ),
    }),
]

export default function ActionCatalogue() {
    const [search, setSearch] = useState('')
    const [categoryFilter, setCategoryFilter] = useState('')
    const [langFilter, setLangFilter] = useState('')
    const [selected, setSelected] = useState<CatalogueScript | null>(null)

    const debouncedSearch = useDebounce(search, 300)

    const { data: scripts = [], isLoading } = useQuery({
        queryKey: ['catalogue'],
        queryFn: () => catalogueApi.list().then(res => res.data),
    })

    const filtered = useMemo(() => {
        return scripts.filter(s => {
            const matchSearch = !debouncedSearch || s.name.toLowerCase().includes(debouncedSearch.toLowerCase())
            const matchCat = !categoryFilter || s.category === categoryFilter
            const matchLang = !langFilter || s.language === langFilter
            return matchSearch && matchCat && matchLang
        })
    }, [scripts, debouncedSearch, categoryFilter, langFilter])

    const categories = useMemo(() => [...new Set(scripts.map(s => s.category))].sort(), [scripts])
    const languages = useMemo(() => [...new Set(scripts.map(s => s.language))].sort(), [scripts])

    const table = useReactTable({
        data: filtered,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
    })

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3">
                <Trophy className="h-6 w-6 text-amber-400" />
                <div>
                    <h1 className="text-2xl font-bold">Action Catalogue</h1>
                    <p className="text-sm text-muted-foreground">
                        Gold-standard scripts promoted from resolved incidents.
                    </p>
                </div>
                <span className="ml-auto text-sm text-muted-foreground">
                    {scripts.length} script{scripts.length !== 1 ? 's' : ''}
                </span>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-3 flex-wrap">
                <div className="relative flex-1 min-w-[200px] max-w-sm">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                    <input
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Search scripts..."
                        className="w-full rounded-md border border-[hsl(var(--border)/0.6)] bg-background pl-9 pr-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                    />
                </div>
                <select
                    value={categoryFilter}
                    onChange={e => setCategoryFilter(e.target.value)}
                    className="rounded-md border border-[hsl(var(--border)/0.6)] bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                >
                    <option value="">All categories</option>
                    {categories.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <select
                    value={langFilter}
                    onChange={e => setLangFilter(e.target.value)}
                    className="rounded-md border border-[hsl(var(--border)/0.6)] bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                >
                    <option value="">All languages</option>
                    {languages.map(l => <option key={l} value={l}>{l}</option>)}
                </select>
            </div>

            {/* Table */}
            {isLoading ? (
                <div className="space-y-2">
                    {Array.from({ length: 5 }).map((_, i) => (
                        <Skeleton key={i} className="h-12 w-full" />
                    ))}
                </div>
            ) : filtered.length === 0 ? (
                <div className="rounded-lg border border-dashed border-[hsl(var(--border)/0.4)] py-16 text-center">
                    <Trophy className="h-8 w-8 text-muted-foreground/40 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground">No gold-standard scripts yet.</p>
                    <p className="text-xs text-muted-foreground mt-1">
                        Promote an AI-resolved incident to add the first entry.
                    </p>
                </div>
            ) : (
                <div className="rounded-lg border border-[hsl(var(--border)/0.4)] overflow-hidden">
                    <table className="w-full text-sm">
                        <thead>
                            {table.getHeaderGroups().map(hg => (
                                <tr key={hg.id} className="bg-muted/20 border-b border-[hsl(var(--border)/0.4)]">
                                    {hg.headers.map(h => (
                                        <th key={h.id} className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                            {flexRender(h.column.columnDef.header, h.getContext())}
                                        </th>
                                    ))}
                                    <th className="px-4 py-3" />
                                </tr>
                            ))}
                        </thead>
                        <tbody className="divide-y divide-[hsl(var(--border)/0.3)]">
                            {table.getRowModel().rows.map(row => (
                                <tr
                                    key={row.id}
                                    onClick={() => setSelected(row.original)}
                                    className="hover:bg-muted/20 cursor-pointer transition-colors"
                                >
                                    {row.getVisibleCells().map(cell => (
                                        <td key={cell.id} className="px-4 py-3">
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </td>
                                    ))}
                                    <td className="px-4 py-3 text-right">
                                        <span className="text-xs text-muted-foreground hover:text-foreground">View →</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Drawer */}
            {selected && (
                <>
                    <div
                        className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm"
                        onClick={() => setSelected(null)}
                    />
                    <ScriptDrawer script={selected} onClose={() => setSelected(null)} />
                </>
            )}
        </div>
    )
}
```

- [ ] **Step 2: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | grep "ActionCatalogue" | head -5
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/ActionCatalogue.tsx
git commit -m "feat(catalogue): add ActionCatalogue page with filterable table and drawer"
```

---

### Task 12: Add promotion banner to IncidentDetailPanel

**Files:**
- Modify: `frontend/src/components/incidents/IncidentDetailPanel.tsx`

- [ ] **Step 1: Add imports**

In `frontend/src/components/incidents/IncidentDetailPanel.tsx`, add to existing imports:

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { promoteIncident } from '@/services/api'
import { useToast } from '@/components/ui/Toast'
```

- [ ] **Step 2: Add mutation + banner inside the component**

Inside `export default function IncidentDetailPanel`, after the `handleReject` function and before the loading state check, add:

```tsx
const qc = useQueryClient()
const { success: toastSuccess, error: toastError } = useToast()

const promoteMutation = useMutation({
    mutationFn: () => promoteIncident(id),
    onSuccess: (res) => {
        toastSuccess(res.data.message)
        refetch()
        qc.invalidateQueries({ queryKey: ['catalogue'] })
    },
    onError: () => toastError('Promotion failed'),
})
```

- [ ] **Step 3: Render the banner**

Inside the `return (...)` block, find the comment `{/* Header */}` and add the promotion banner directly above it:

```tsx
{/* [ENTERPRISE] AI Promotion Banner */}
{incident.meta_data?.promotion_eligible && (
    <div className="bg-amber-500/10 border border-amber-500/25 rounded-lg p-4 mb-5">
        <p className="text-sm font-semibold text-amber-400 mb-1">
            🏆 This incident was resolved by AI
        </p>
        <p className="text-xs text-amber-200/70 mb-3">
            Promote the fix to the Action Catalogue to reuse it for future incidents.
        </p>
        <button
            onClick={() => promoteMutation.mutate()}
            disabled={promoteMutation.isPending}
            className="px-4 py-2 bg-amber-500 text-white text-xs font-bold rounded-md hover:bg-amber-600 transition-colors disabled:opacity-50"
        >
            {promoteMutation.isPending ? 'Promoting…' : 'Promote to Catalogue'}
        </button>
    </div>
)}
```

- [ ] **Step 4: TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | grep "IncidentDetailPanel" | head -5
```

Expected: No errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/incidents/IncidentDetailPanel.tsx
git commit -m "feat(incidents): add promotion banner to IncidentDetailPanel"
```

---

### Task 13: Add routes and navigation

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/Layout.tsx`

- [ ] **Step 1: Add routes to App.tsx**

In `frontend/src/App.tsx`, add two imports after the existing page imports:

```tsx
import CICDRisk from '@/pages/CICDRisk'
import ActionCatalogue from '@/pages/ActionCatalogue'
```

Then inside the `<Route path="/" ...>` block, add after `<Route path="sops" ...>`:

```tsx
<Route path="cicd" element={<CICDRisk />} />
<Route path="catalogue" element={<ActionCatalogue />} />
```

- [ ] **Step 2: Add nav items to Layout.tsx**

In `frontend/src/components/Layout.tsx`, add two icon imports to the lucide-react import block:

```tsx
Rocket,
Trophy,
```

Then in the `baseNavigation` array, add after the Incidents entry (after line 50):

```tsx
{ name: 'CI/CD Risk', href: '/cicd', icon: Rocket, subtitle: 'Score deployments for risk before production' },
{ name: 'Action Catalogue', href: '/catalogue', icon: Trophy, subtitle: 'Gold-standard scripts from resolved incidents' },
```

- [ ] **Step 3: Full TypeScript check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | head -20
```

Expected: No errors (or only pre-existing ones).

- [ ] **Step 4: Build check**

```bash
cd /Users/alind/Projects/Synapto/frontend && npm run build 2>&1 | tail -10
```

Expected: Build succeeds.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.tsx frontend/src/components/Layout.tsx
git commit -m "feat(nav): add CI/CD Risk and Action Catalogue routes and sidebar items"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Feature 1 CI/CD Risk page — Tasks 3, 4, 5, 13
- ✅ Feature 2 Action Catalogue page — Tasks 1, 3, 10, 11, 13
- ✅ Feature 2 Promotion banner — Task 12
- ✅ Feature 3 Service Health widget — Tasks 6, 7
- ✅ Feature 4 SSE endpoint — Task 2
- ✅ Feature 4 useIncidentStream hook — Task 8
- ✅ Feature 4 Incidents polling removed — Task 9
- ✅ `is_gold_standard` backend filter (spec note) — Task 1

**Placeholder scan:** No TBDs or incomplete steps. All code blocks are complete.

**Type consistency:**
- `CICDDeployment` / `CICDRiskAssessment` defined in Task 3, used in Tasks 4, 5 ✅
- `CatalogueScript` defined in Task 3, used in Tasks 10, 11, 12 ✅
- `healthApi.get()` returns `HealthResponse` defined in Task 3, used in Task 6 ✅
- `useIncidentStream` created in Task 8, imported in Task 9 ✅
- `ScriptDrawer` created in Task 10, imported in Task 11 ✅
- `promoteIncident` added to api.ts in Task 3, used in Task 12 ✅
