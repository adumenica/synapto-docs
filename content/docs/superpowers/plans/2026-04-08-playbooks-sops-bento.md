# Playbooks + SOPs Bento Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace card-based grids on Playbooks and SOPLibrary pages with container-free metric bands and left-border bento cells, matching the Phase 4–5 pattern.

**Architecture:** Two independent single-file rewrites. Each page gets a metric band (same `text-5xl font-black` pattern as Analytics/Events/Executions), an action row, and a 3-column bento grid with `border-l-[3px]` cells instead of card boxes. No new components, no new API endpoints. All modals preserved exactly.

**Tech Stack:** React 18, TypeScript (strict), TanStack React Query, Tailwind CSS, Lucide React, `@/components/ui/Skeleton`

---

### Task 1: Rewrite Playbooks.tsx

**Files:**
- Modify: `frontend/src/pages/Playbooks.tsx`

- [ ] **Step 1: Replace the entire file contents**

```tsx
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { playbooksApi, PlaybookCreate, Playbook } from '@/services/api'
import { Plus, X, Pencil, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { Skeleton } from '@/components/ui/Skeleton'

export default function Playbooks() {
    const [isCreating, setIsCreating] = useState(false)
    const [editingId, setEditingId] = useState<string | null>(null)
    const queryClient = useQueryClient()

    const { data: playbooks, isLoading } = useQuery({
        queryKey: ['playbooks'],
        queryFn: () => playbooksApi.list({}).then(res => res.data),
    })

    const activePlaybooks = playbooks?.filter(p => p.is_active)

    const [newPlaybook, setNewPlaybook] = useState<PlaybookCreate>({
        name: '',
        version: '1.0.0',
        description: '',
        steps: [
            {
                type: 'execute_script',
                name: 'Remediation Step',
                language: 'python',
                content: '# Your remediation code',
                timeout: 300
            }
        ]
    })

    const createMutation = useMutation({
        mutationFn: (data: PlaybookCreate) => playbooksApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['playbooks'] })
            resetForm()
        },
    })

    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<PlaybookCreate> }) =>
            playbooksApi.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['playbooks'] })
            resetForm()
        },
    })

    const deleteMutation = useMutation({
        mutationFn: (id: string) => playbooksApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['playbooks'] })
        },
    })

    const resetForm = () => {
        setIsCreating(false)
        setEditingId(null)
        setNewPlaybook({
            name: '',
            version: '1.0.0',
            description: '',
            steps: [{
                type: 'execute_script',
                name: 'Remediation Step',
                language: 'python',
                content: '# Your remediation code',
                timeout: 300
            }]
        })
    }

    const handleCreate = () => {
        if (newPlaybook.name) {
            if (editingId) {
                updateMutation.mutate({ id: editingId, data: newPlaybook })
            } else {
                createMutation.mutate(newPlaybook)
            }
        }
    }

    const handleEdit = (playbook: Playbook) => {
        setNewPlaybook({
            name: playbook.name,
            version: playbook.version,
            description: playbook.description,
            steps: playbook.steps,
            metadata: playbook.metadata
        } as PlaybookCreate)
        setEditingId(playbook.id)
        setIsCreating(true)
    }

    const handleDelete = (id: string) => {
        if (confirm('Are you sure you want to delete this playbook?')) {
            deleteMutation.mutate(id)
        }
    }

    return (
        <div className="space-y-6">
            {/* Metric Band */}
            <div className="flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]">
                {isLoading ? (
                    <>
                        {Array.from({ length: 2 }).map((_, i) => (
                            <div key={i} className="space-y-2">
                                <Skeleton className="h-12 w-20" />
                                <Skeleton className="h-3 w-16" />
                            </div>
                        ))}
                    </>
                ) : (
                    <>
                        <div>
                            <div className="text-5xl font-black tracking-tight text-foreground">
                                {playbooks?.length ?? 0}
                            </div>
                            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Total
                            </div>
                        </div>
                        <div>
                            <div className="text-5xl font-black tracking-tight text-green-400">
                                {activePlaybooks?.length ?? 0}
                            </div>
                            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Active
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Action Row */}
            <div className="flex items-center justify-end py-4">
                <button
                    onClick={() => setIsCreating(true)}
                    className="btn btn-primary flex items-center gap-2"
                >
                    <Plus className="w-4 h-4" />
                    Create Playbook
                </button>
            </div>

            {/* Create / Edit Modal */}
            {isCreating && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="card p-6 max-w-2xl w-full m-4 max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                                {editingId ? 'Edit Playbook' : 'Create Playbook'}
                            </h2>
                            <button onClick={resetForm} className="p-2 hover:bg-gray-100 dark:hover:bg-dark-800 rounded-lg">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Name
                                </label>
                                <input
                                    type="text"
                                    value={newPlaybook.name}
                                    onChange={(e) => setNewPlaybook({ ...newPlaybook, name: e.target.value })}
                                    className="input"
                                    placeholder="e.g., Critical Server Remediation"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Version
                                </label>
                                <input
                                    type="text"
                                    value={newPlaybook.version}
                                    onChange={(e) => setNewPlaybook({ ...newPlaybook, version: e.target.value })}
                                    className="input"
                                    placeholder="1.0.0"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Description
                                </label>
                                <textarea
                                    value={newPlaybook.description}
                                    onChange={(e) => setNewPlaybook({ ...newPlaybook, description: e.target.value })}
                                    className="input"
                                    rows={3}
                                    placeholder="Describe what this playbook does"
                                />
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => setIsCreating(false)}
                                    className="btn btn-secondary flex-1"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleCreate}
                                    disabled={!newPlaybook.name || createMutation.isPending || updateMutation.isPending}
                                    className="btn btn-primary flex-1"
                                >
                                    {createMutation.isPending || updateMutation.isPending ? 'Saving...' : (editingId ? 'Update Playbook' : 'Create Playbook')}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Bento Grid */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                {isLoading ? (
                    Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="border-l-[3px] border-l-muted pl-4 py-2 space-y-2">
                            <Skeleton className="h-4 w-3/4" />
                            <Skeleton className="h-3 w-full" />
                            <Skeleton className="h-3 w-full" />
                            <Skeleton className="h-3 w-1/2 mt-1" />
                        </div>
                    ))
                ) : activePlaybooks && activePlaybooks.length > 0 ? (
                    activePlaybooks.map((playbook) => (
                        <div
                            key={playbook.id}
                            className="group border-l-[3px] border-l-primary-500 pl-4 py-2 cursor-pointer hover:bg-[hsl(var(--panel)/0.4)] transition-colors rounded-r-sm"
                        >
                            <div className="flex items-start justify-between">
                                <h3 className="text-base font-semibold text-foreground line-clamp-2 flex-1">
                                    {playbook.name}
                                </h3>
                                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-2 shrink-0">
                                    <button
                                        onClick={() => handleEdit(playbook)}
                                        className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-[hsl(var(--panel)/0.6)] rounded transition-colors"
                                        title="Edit"
                                    >
                                        <Pencil className="w-3.5 h-3.5" />
                                    </button>
                                    <button
                                        onClick={() => handleDelete(playbook.id)}
                                        className="p-1.5 text-muted-foreground hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                                        title="Delete"
                                    >
                                        <Trash2 className="w-3.5 h-3.5" />
                                    </button>
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
                    ))
                ) : (
                    <div className="col-span-full py-16 text-center">
                        <p className="text-muted-foreground">No playbooks found. Create your first playbook to get started.</p>
                    </div>
                )}
            </div>
        </div>
    )
}
```

- [ ] **Step 2: Verify the build passes**

Run from `frontend/`:
```bash
npm run build 2>&1 | tail -20
```
Expected: no TypeScript errors, build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Playbooks.tsx
git commit -m "feat(ui): rewrite Playbooks with metric band and bento grid (Phase 6)"
```

---

### Task 2: Rewrite SOPLibrary.tsx

**Files:**
- Modify: `frontend/src/pages/SOPLibrary.tsx`

- [ ] **Step 1: Replace the entire file contents**

```tsx
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sopsApi, SOP, SOPCreate } from '@/services/api'
import {
    Search,
    Plus,
    Calendar,
    Tag,
    Trash2,
    Edit2,
    X,
    Save
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
// @ts-expect-error no type declarations available
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
// @ts-expect-error no type declarations available
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import ConfirmModal from '../components/admin/ConfirmModal'
import { Skeleton } from '@/components/ui/Skeleton'

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

export default function SOPLibrary() {
    const queryClient = useQueryClient()
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedCategory, setSelectedCategory] = useState<string>('all')
    const [selectedSOP, setSelectedSOP] = useState<SOP | null>(null)
    const [isViewModalOpen, setIsViewModalOpen] = useState(false)
    const [sopToDelete, setSopToDelete] = useState<SOP | null>(null)

    const [isEditModalOpen, setIsEditModalOpen] = useState(false)
    const [editingSOP, setEditingSOP] = useState<SOP | null>(null)
    const [editForm, setEditForm] = useState({ title: '', category: '', content: '' })

    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
    const [createForm, setCreateForm] = useState({ title: '', category: '', content: '' })

    const { data: sops, isLoading } = useQuery({
        queryKey: ['sops', selectedCategory],
        queryFn: () => sopsApi.list(selectedCategory === 'all' ? undefined : selectedCategory).then(res => res.data)
    })

    const createMutation = useMutation({
        mutationFn: (data: SOPCreate) => sopsApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['sops'] })
            setIsCreateModalOpen(false)
            setCreateForm({ title: '', category: '', content: '' })
        }
    })

    const deleteMutation = useMutation({
        mutationFn: (id: string) => sopsApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['sops'] })
            setSopToDelete(null)
        }
    })

    const updateMutation = useMutation({
        mutationFn: (data: { id: string; sop: Partial<SOPCreate> }) => sopsApi.update(data.id, data.sop),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['sops'] })
            setIsEditModalOpen(false)
            setEditingSOP(null)
            if (selectedSOP && editingSOP?.id === selectedSOP.id) {
                setIsViewModalOpen(false)
            }
        }
    })

    const filteredSOPs = sops?.filter(sop =>
        sop.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        sop.description?.toLowerCase().includes(searchQuery.toLowerCase())
    )

    const categories = Array.from(new Set(sops?.map(s => s.category) || []))

    const handleViewSOP = (sop: SOP) => {
        setSelectedSOP(sop)
        setIsViewModalOpen(true)
    }

    const handleEditClick = (sop: SOP, e?: React.MouseEvent) => {
        if (e) e.stopPropagation()
        setEditingSOP(sop)
        setEditForm({ title: sop.title, category: sop.category || '', content: sop.content })
        setIsEditModalOpen(true)
    }

    const handleSaveEdit = () => {
        if (!editingSOP) return
        updateMutation.mutate({ id: editingSOP.id, sop: editForm })
    }

    const handleSaveCreate = () => {
        createMutation.mutate(createForm)
    }

    const formatDate = (dateString: string) =>
        new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })

    // Shared form field styles
    const fieldClass = "w-full px-3 py-2 bg-white dark:bg-dark-900 border border-gray-200 dark:border-dark-700 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none text-sm text-gray-900 dark:text-gray-100 transition-all"
    const labelClass = "block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5"

    return (
        <div className="space-y-6">
            {/* Metric Band */}
            <div className="flex flex-wrap items-baseline gap-10 pb-8 border-b border-[hsl(var(--border)/0.4)]">
                {isLoading ? (
                    <>
                        {Array.from({ length: 2 }).map((_, i) => (
                            <div key={i} className="space-y-2">
                                <Skeleton className="h-12 w-20" />
                                <Skeleton className="h-3 w-16" />
                            </div>
                        ))}
                    </>
                ) : (
                    <>
                        <div>
                            <div className="text-5xl font-black tracking-tight text-foreground">
                                {sops?.length ?? 0}
                            </div>
                            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Total SOPs
                            </div>
                        </div>
                        <div>
                            <div className="text-5xl font-black tracking-tight text-blue-400">
                                {new Set((sops ?? []).map(s => s.category || 'Uncategorized')).size}
                            </div>
                            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground mt-1">
                                Categories
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Search + Category + Create Row */}
            <div className="flex flex-col sm:flex-row gap-3 py-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search SOPs..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-9 pr-4 py-2 text-sm bg-white dark:bg-dark-800 border border-gray-200/70 dark:border-dark-700/70 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
                    />
                </div>
                <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 flex-wrap">
                    <button
                        onClick={() => setSelectedCategory('all')}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all border ${selectedCategory === 'all'
                            ? 'nav-item-active'
                            : 'nav-item-inactive'
                            }`}
                    >
                        All
                    </button>
                    {categories.map(category => (
                        <button
                            key={category}
                            onClick={() => setSelectedCategory(category)}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all border ${selectedCategory === category
                                ? 'nav-item-active'
                                : 'nav-item-inactive'
                                }`}
                        >
                            {category}
                        </button>
                    ))}
                </div>
                <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="btn btn-primary flex items-center gap-2 self-start sm:self-auto"
                >
                    <Plus className="w-4 h-4" />
                    Create SOP
                </button>
            </div>

            {/* Bento Grid */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                {isLoading ? (
                    Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="border-l-[3px] border-l-muted pl-4 py-2 space-y-2">
                            <Skeleton className="h-4 w-3/4" />
                            <Skeleton className="h-3 w-full" />
                            <Skeleton className="h-3 w-full" />
                            <Skeleton className="h-3 w-2/3" />
                            <Skeleton className="h-3 w-1/2 mt-1" />
                        </div>
                    ))
                ) : filteredSOPs && filteredSOPs.length > 0 ? (
                    filteredSOPs.map((sop) => (
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
                                    <button
                                        onClick={(e) => handleEditClick(sop, e)}
                                        className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-[hsl(var(--panel)/0.6)] rounded transition-colors"
                                        title="Edit SOP"
                                    >
                                        <Edit2 className="w-3.5 h-3.5" />
                                    </button>
                                    <button
                                        onClick={(e) => { e.stopPropagation(); setSopToDelete(sop) }}
                                        className="p-1.5 text-muted-foreground hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                                        title="Delete SOP"
                                    >
                                        <Trash2 className="w-3.5 h-3.5" />
                                    </button>
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
                    ))
                ) : (
                    <div className="col-span-full py-16 text-center">
                        <p className="text-muted-foreground mb-4">
                            {searchQuery ? 'No SOPs match your search' : 'No SOPs yet'}
                        </p>
                        {!searchQuery && (
                            <button
                                onClick={() => setIsCreateModalOpen(true)}
                                className="btn btn-primary flex items-center gap-2 text-sm mx-auto"
                            >
                                <Plus className="w-4 h-4" />
                                Create SOP
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* Delete Confirmation */}
            {sopToDelete && (
                <ConfirmModal
                    title="Delete SOP"
                    message={
                        <span>
                            Are you sure you want to delete <strong className="text-white">{sopToDelete.title}</strong>?
                            This cannot be undone.
                        </span>
                    }
                    confirmLabel="Delete"
                    danger
                    onConfirm={() => deleteMutation.mutate(sopToDelete.id)}
                    onCancel={() => setSopToDelete(null)}
                />
            )}

            {/* View Modal */}
            {isViewModalOpen && selectedSOP && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <div className="bg-white dark:bg-dark-900 border border-gray-200 dark:border-dark-700 rounded-[14px] shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
                        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200/70 dark:border-dark-700/70">
                            <div>
                                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                                    {selectedSOP.title}
                                </h2>
                                <div className="flex items-center gap-4 mt-1 text-xs text-gray-400">
                                    <span className="flex items-center gap-1">
                                        <Tag className="w-3 h-3" /> {selectedSOP.category || 'Uncategorized'}
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <Calendar className="w-3 h-3" /> Updated {formatDate(selectedSOP.updated_at)}
                                    </span>
                                </div>
                            </div>
                            <button
                                onClick={() => setIsViewModalOpen(false)}
                                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-dark-800 rounded-lg transition-colors"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto px-6 py-5 scrollbar-thin">
                            <article className="prose dark:prose-invert max-w-none prose-sm">
                                <ReactMarkdown
                                    components={{
                                            code({ inline, className, children, ...props }: any) {
                                            const match = /language-(\w+)/.exec(className || '')
                                            return !inline && match ? (
                                                <SyntaxHighlighter
                                                    style={vscDarkPlus}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    {...props}
                                                >
                                                    {String(children).replace(/\n$/, '')}
                                                </SyntaxHighlighter>
                                            ) : (
                                                <code className={className} {...props}>
                                                    {children}
                                                </code>
                                            )
                                        }
                                    }}
                                >
                                    {selectedSOP.content}
                                </ReactMarkdown>
                            </article>
                        </div>

                        <div className="px-6 py-4 border-t border-gray-200/70 dark:border-dark-700/70 flex justify-end gap-3">
                            <button
                                onClick={() => {
                                    handleEditClick(selectedSOP)
                                    setIsViewModalOpen(false)
                                }}
                                className="btn btn-primary flex items-center gap-2 text-sm"
                            >
                                <Edit2 className="w-3.5 h-3.5" />
                                Edit SOP
                            </button>
                            <button
                                onClick={() => setIsViewModalOpen(false)}
                                className="btn btn-secondary text-sm"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Create Modal */}
            {isCreateModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <div className="bg-white dark:bg-dark-900 border border-gray-200 dark:border-dark-700 rounded-[14px] shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
                        <div className="px-6 py-4 border-b border-gray-200/70 dark:border-dark-700/70 flex items-center justify-between">
                            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Create SOP</h2>
                            <button
                                onClick={() => setIsCreateModalOpen(false)}
                                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-dark-800 rounded-lg transition-colors"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4 scrollbar-thin">
                            <div>
                                <label className={labelClass}>Title</label>
                                <input
                                    type="text"
                                    value={createForm.title}
                                    onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                                    className={fieldClass}
                                    placeholder="e.g., Database Recovery Procedure"
                                    autoFocus
                                />
                            </div>

                            <div>
                                <label className={labelClass}>Category</label>
                                <input
                                    type="text"
                                    value={createForm.category}
                                    onChange={(e) => setCreateForm({ ...createForm, category: e.target.value })}
                                    className={fieldClass}
                                    placeholder="e.g., Database, Network, Security"
                                />
                            </div>

                            <div>
                                <label className={labelClass}>Content (Markdown)</label>
                                <textarea
                                    value={createForm.content}
                                    onChange={(e) => setCreateForm({ ...createForm, content: e.target.value })}
                                    className={`${fieldClass} resize-none font-mono`}
                                    rows={10}
                                    placeholder={"# Procedure Title\n\n## Overview\n\n1. Step one...\n2. Step two..."}
                                />
                                <p className="text-[11px] text-gray-400 mt-1">{createForm.content.length} characters</p>
                            </div>
                        </div>

                        <div className="px-6 py-4 border-t border-gray-200/70 dark:border-dark-700/70 flex justify-end gap-3">
                            <button
                                onClick={() => setIsCreateModalOpen(false)}
                                className="btn btn-secondary text-sm"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSaveCreate}
                                disabled={!createForm.title || createMutation.isPending}
                                className="btn btn-primary flex items-center gap-2 text-sm disabled:opacity-50"
                            >
                                <Save className="w-3.5 h-3.5" />
                                {createMutation.isPending ? 'Creating…' : 'Create SOP'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Edit Modal */}
            {isEditModalOpen && editingSOP && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <div className="bg-white dark:bg-dark-900 border border-gray-200 dark:border-dark-700 rounded-[14px] shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
                        <div className="px-6 py-4 border-b border-gray-200/70 dark:border-dark-700/70 flex items-center justify-between">
                            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Edit SOP</h2>
                            <button
                                onClick={() => setIsEditModalOpen(false)}
                                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-dark-800 rounded-lg transition-colors"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4 scrollbar-thin">
                            <div>
                                <label className={labelClass}>Title</label>
                                <input
                                    type="text"
                                    value={editForm.title}
                                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                                    className={fieldClass}
                                />
                            </div>

                            <div>
                                <label className={labelClass}>Category</label>
                                <input
                                    type="text"
                                    value={editForm.category}
                                    onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                                    className={fieldClass}
                                />
                            </div>

                            <div>
                                <label className={labelClass}>Content (Markdown)</label>
                                <textarea
                                    value={editForm.content}
                                    onChange={(e) => setEditForm({ ...editForm, content: e.target.value })}
                                    className={`${fieldClass} resize-none font-mono`}
                                    rows={12}
                                />
                                <p className="text-[11px] text-gray-400 mt-1">{editForm.content.length} characters</p>
                            </div>
                        </div>

                        <div className="px-6 py-4 border-t border-gray-200/70 dark:border-dark-700/70 flex justify-end gap-3">
                            <button
                                onClick={() => setIsEditModalOpen(false)}
                                className="btn btn-secondary text-sm"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSaveEdit}
                                disabled={!editForm.title || updateMutation.isPending}
                                className="btn btn-primary flex items-center gap-2 text-sm disabled:opacity-50"
                            >
                                <Save className="w-3.5 h-3.5" />
                                {updateMutation.isPending ? 'Saving…' : 'Save Changes'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
```

- [ ] **Step 2: Verify the build passes**

Run from `frontend/`:
```bash
npm run build 2>&1 | tail -20
```
Expected: no TypeScript errors, build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/SOPLibrary.tsx
git commit -m "feat(ui): rewrite SOPLibrary with metric band and bento grid (Phase 6)"
```
