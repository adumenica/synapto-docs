# Sidebar Icon Rail Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 320px desktop sidebar with a 64px icon rail that reveals a floating label panel on hover, with a pin-to-open toggle persisted in localStorage.

**Architecture:** All changes are confined to `frontend/src/components/Layout.tsx`. The icon rail is a `w-16` flex-col aside; the label panel is an absolutely-positioned overlay child that fades in when `sidebarHovered || sidebarPinned`. Hover state is managed via `onMouseEnter`/`onMouseLeave` with a 200ms hide delay using `useRef`. The mobile drawer (`lg:hidden`) is untouched.

**Tech Stack:** React, TypeScript, Tailwind CSS, Lucide React, `@radix-ui/react-popover` (already installed)

---

## File Map

| File | Change |
|---|---|
| `frontend/src/components/Layout.tsx` | Replace desktop aside; add icon rail, label panel, avatar popover, hover/pin state |

No new files are created.

---

### Task 1: Add hover/pin state and new imports

**Files:**
- Modify: `frontend/src/components/Layout.tsx:1-32` (imports + state)

- [ ] **Step 1: Add new Lucide imports and Radix Popover import**

Replace the existing import block at the top of `Layout.tsx` with:

```tsx
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import {
    LayoutDashboard,
    Bell,
    AlertTriangle,
    Play,
    Code,
    BookOpen,
    Shield,
    BarChart3,
    Menu,
    X,
    LogOut,
    Settings,
    FileText,
    Sun,
    Moon,
    Search,
    Wifi,
    WifiOff,
    ChevronRight,
    Lock,
    LockOpen,
} from 'lucide-react'
import * as Popover from '@radix-ui/react-popover'
import { useState, useEffect, useRef, useMemo } from 'react'
import TenantSwitcher from '@/components/TenantSwitcher'
import { useTheme } from '@/hooks/useTheme'
import CommandPalette from '@/components/CommandPalette'
import NotificationPanel from '@/components/NotificationPanel'
import Breadcrumbs from '@/components/ui/Breadcrumbs'
import { useWebSocket } from '@/hooks/useWebSocket'
import { Tooltip, TooltipProvider } from '@/components/ui/Tooltip'
import { useOnboarding } from '@/hooks/useOnboarding'
import { useLicense } from '@/hooks/useLicense'
```

Note: `ChevronRight` stays until Task 3 removes it together with its usage in `NavLinks`. `User` is not needed.

- [ ] **Step 2: Add sidebarPinned and sidebarHovered state inside the Layout function**

Add these three lines directly after the existing `const [sidebarOpen, setSidebarOpen] = useState(false)` line (around line 49):

```tsx
const [sidebarPinned, setSidebarPinned] = useState<boolean>(() => localStorage.getItem('sidebar-pinned') === 'true')
const [sidebarHovered, setSidebarHovered] = useState(false)
const hideTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
```

- [ ] **Step 3: Add hover handlers and togglePin after the handleLogout function**

Add these after `handleLogout` (around line 88):

```tsx
const handleRailMouseEnter = () => {
    if (hideTimerRef.current) clearTimeout(hideTimerRef.current)
    setSidebarHovered(true)
}

const handleRailMouseLeave = () => {
    hideTimerRef.current = setTimeout(() => setSidebarHovered(false), 200)
}

const togglePin = () => {
    setSidebarPinned(prev => {
        const next = !prev
        localStorage.setItem('sidebar-pinned', String(next))
        return next
    })
}

const sidePanelVisible = sidebarPinned || sidebarHovered
```

- [ ] **Step 4: Verify TypeScript compiles with no errors**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors related to the new state/imports (there may be pre-existing errors — ignore those).

- [ ] **Step 5: Commit**

```bash
cd /Users/alind/Projects/Synapto/frontend && git add src/components/Layout.tsx && git commit -m "feat(layout): add hover/pin state and imports for icon rail"
```

---

### Task 2: Replace desktop aside with icon rail

**Files:**
- Modify: `frontend/src/components/Layout.tsx` — replace the `<aside className="hidden lg:flex lg:w-[320px]...">` block

- [ ] **Step 1: Replace the entire desktop aside block**

Locate and replace this block (lines ~274–349):

```tsx
<aside className="hidden lg:flex lg:w-[320px] lg:shrink-0">
    <div className="app-shell sticky top-3 flex h-[calc(100vh-1.5rem)] w-full flex-col rounded-[28px] p-5">
        ...all existing content...
    </div>
</aside>
```

Replace with:

```tsx
<aside
    className="hidden lg:flex lg:w-16 lg:shrink-0"
    onMouseEnter={handleRailMouseEnter}
    onMouseLeave={handleRailMouseLeave}
>
    <div className="app-shell relative sticky top-3 flex h-[calc(100vh-1.5rem)] w-full flex-col items-center rounded-[28px] py-4">

        {/* Logo mark */}
        <Link
            to="/"
            className="mb-4 flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-slate-950 shadow-sm dark:bg-white"
            aria-label="Go to dashboard"
        >
            <img src="/logo.png" alt="Synapto" className="h-7 w-7 object-contain dark:invert" />
        </Link>

        {/* Nav icons */}
        <nav className="flex flex-1 flex-col items-center gap-1 overflow-y-auto py-2" aria-label="Main navigation">
            {navigation.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.href || (item.href !== '/' && location.pathname.startsWith(item.href))
                return (
                    <TooltipProvider key={item.name}>
                        <Tooltip content={item.name} side="right">
                            <Link
                                to={item.href}
                                aria-current={isActive ? 'page' : undefined}
                                data-tour={'tourId' in item ? (item as typeof item & { tourId?: string }).tourId : undefined}
                                className={[
                                    'relative flex h-10 w-10 items-center justify-center rounded-xl transition-colors',
                                    isActive
                                        ? 'bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-300'
                                        : 'text-gray-500 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-dark-800 dark:hover:text-white',
                                ].join(' ')}
                            >
                                {isActive && (
                                    <span
                                        className="absolute -left-[13px] h-6 w-[3px] rounded-r-full bg-primary-500"
                                        aria-hidden="true"
                                    />
                                )}
                                <Icon className="h-5 w-5" aria-hidden="true" />
                            </Link>
                        </Tooltip>
                    </TooltipProvider>
                )
            })}
        </nav>

        {/* Avatar — opens profile popover */}
        <Popover.Root>
            <Popover.Trigger asChild>
                <button
                    className="mt-auto flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary-600 text-sm font-semibold uppercase text-white shadow-sm transition-opacity hover:opacity-80"
                    aria-label="Open user profile"
                    data-tour="user-profile"
                >
                    {(user.username && user.username.charAt(0)) || 'U'}
                </button>
            </Popover.Trigger>
            <Popover.Portal>
                <Popover.Content
                    side="right"
                    sideOffset={12}
                    className="z-50 w-52 rounded-2xl border border-[hsl(var(--border)/0.6)] bg-[hsl(var(--panel)/0.95)] p-3 shadow-xl backdrop-blur-md"
                >
                    <div className="mb-3">
                        <p className="truncate text-sm font-semibold text-gray-900 dark:text-gray-100">
                            {user.fullName || user.username}
                        </p>
                        <p className="truncate text-xs text-gray-500 dark:text-gray-400">
                            {user.username}
                        </p>
                    </div>
                    <Link
                        to="/profile"
                        className="mb-1 flex w-full items-center gap-2 rounded-xl px-2 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-dark-800"
                    >
                        Profile settings
                    </Link>
                    <button
                        onClick={handleLogout}
                        className="flex w-full items-center gap-2 rounded-xl px-2 py-1.5 text-sm text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10"
                    >
                        <LogOut className="h-4 w-4" aria-hidden="true" />
                        Log out
                    </button>
                    <Popover.Arrow className="fill-[hsl(var(--panel)/0.95)]" />
                </Popover.Content>
            </Popover.Portal>
        </Popover.Root>

        {/* Label panel — hover/pin overlay */}
        <div
            className={[
                'absolute left-full top-0 z-40 h-full w-[220px] rounded-r-[28px] border-y border-r border-[hsl(var(--border)/0.5)] bg-[hsl(var(--panel)/0.88)] shadow-xl backdrop-blur-md transition-all',
                sidePanelVisible
                    ? 'pointer-events-auto translate-x-0 opacity-100 duration-150 ease-out'
                    : 'pointer-events-none -translate-x-2 opacity-0 duration-100 ease-in',
            ].join(' ')}
            aria-hidden={!sidePanelVisible}
        >
            {/* Pin button */}
            <button
                onClick={togglePin}
                className="absolute right-3 top-3 rounded-lg p-1.5 text-gray-400 transition-colors hover:text-gray-700 dark:hover:text-gray-200"
                aria-label={sidebarPinned ? 'Unpin sidebar' : 'Pin sidebar open'}
                tabIndex={sidePanelVisible ? 0 : -1}
            >
                {sidebarPinned
                    ? <Lock className="h-3.5 w-3.5" aria-hidden="true" />
                    : <LockOpen className="h-3.5 w-3.5" aria-hidden="true" />
                }
            </button>

            {/* Wordmark — same height as logo mark (h-11 + mb-4 = 60px) */}
            <div className="mb-4 flex h-11 items-center px-4 pt-4">
                <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-primary-600 dark:text-primary-300">
                        Synapto
                    </p>
                    <p className="text-sm font-semibold text-gray-950 dark:text-white">
                        Autonomous Core
                    </p>
                </div>
            </div>

            {/* Nav labels — gap-1 h-10 matches icon rail rows */}
            <nav className="flex flex-col gap-1 overflow-y-auto px-2 py-2" aria-hidden="true">
                {navigation.map((item) => {
                    const isActive = location.pathname === item.href || (item.href !== '/' && location.pathname.startsWith(item.href))
                    return (
                        <Link
                            key={item.name}
                            to={item.href}
                            tabIndex={sidePanelVisible ? 0 : -1}
                            className={[
                                'flex h-10 items-center rounded-xl px-3 text-sm transition-colors',
                                isActive
                                    ? 'font-semibold text-gray-950 dark:text-white'
                                    : 'font-medium text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white',
                            ].join(' ')}
                        >
                            {item.name}
                        </Link>
                    )
                })}
            </nav>
        </div>
    </div>
</aside>
```

- [ ] **Step 2: Verify the app renders without errors**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: no new TypeScript errors.

- [ ] **Step 3: Commit**

```bash
cd /Users/alind/Projects/Synapto/frontend && git add src/components/Layout.tsx && git commit -m "feat(layout): replace desktop sidebar with 64px icon rail + label panel"
```

---

### Task 3: Remove ChevronRight from NavLinks and imports (mobile cleanup)

The `NavLinks` component used in the mobile drawer still renders a `ChevronRight` icon for active items. Remove both the usage and the import together.

**Files:**
- Modify: `frontend/src/components/Layout.tsx` — `NavLinks` component

- [ ] **Step 1: Remove ChevronRight usage from NavLinks and its import**

In `NavLinks`, locate:

```tsx
<div className="flex items-center gap-2">
    <span className="text-sm font-semibold">{item.name}</span>
    {isActive && <ChevronRight className="h-3.5 w-3.5 opacity-60" aria-hidden="true" />}
</div>
```

Replace with:

```tsx
<span className="text-sm font-semibold">{item.name}</span>
```

Then in the import block, remove `ChevronRight,` from the lucide-react import list.

- [ ] **Step 2: Verify TypeScript compiles clean**

```bash
cd /Users/alind/Projects/Synapto/frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
cd /Users/alind/Projects/Synapto/frontend && git add src/components/Layout.tsx && git commit -m "fix(layout): remove ChevronRight from mobile NavLinks after import removal"
```

---

### Task 4: Final visual verification

- [ ] **Step 1: Start the frontend dev server**

```bash
cd /Users/alind/Projects/Synapto/frontend && npm run dev
```

Open `http://localhost:3000` in a browser.

- [ ] **Step 2: Verify desktop layout**

Check:
- [ ] Sidebar is 64px wide, showing only icons
- [ ] Active page has a left accent bar on its icon
- [ ] Hovering the rail reveals the label panel with a smooth fade+slide animation
- [ ] Moving mouse from rail to label panel keeps panel visible (no flicker)
- [ ] Moving mouse away from label panel hides it after ~200ms
- [ ] Pin button (LockOpen icon) appears in top-right of label panel
- [ ] Clicking pin locks panel open; icon changes to Lock
- [ ] Refreshing the page with pin on keeps panel open (localStorage persisted)
- [ ] Clicking pin again unpins; panel hides on mouse-out
- [ ] Logo mark links to `/`
- [ ] Clicking avatar opens popover with name, username, "Profile settings" link, "Log out" button
- [ ] "Log out" logs the user out correctly
- [ ] "Profile settings" navigates to `/profile`
- [ ] All 9 nav icons (+ admin if applicable) are present and functional

- [ ] **Step 3: Verify mobile layout**

Resize browser to below `lg` breakpoint (< 1024px):
- [ ] Mobile hamburger menu button appears in header
- [ ] Tapping it opens the existing mobile drawer (unchanged)
- [ ] Mobile drawer shows full nav labels + subtitles (NavLinks unchanged)
- [ ] Closing the drawer works

- [ ] **Step 4: Verify dark mode**

Toggle dark mode:
- [ ] Icon rail renders correctly in dark mode
- [ ] Label panel renders correctly in dark mode
- [ ] Avatar popover renders correctly in dark mode

- [ ] **Step 5: Commit any fixes found during visual review, then final commit**

```bash
cd /Users/alind/Projects/Synapto/frontend && git add src/components/Layout.tsx && git commit -m "chore(layout): visual fixes from icon rail review"
```

(Skip this commit if no fixes were needed.)
