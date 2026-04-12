# Sidebar Icon Rail — Design Spec
**Date:** 2026-04-07  
**Phase:** 1 of the Container-Free + Bento UI overhaul  
**Scope:** `frontend/src/components/Layout.tsx` only

---

## Overview

Replace the current 320px desktop sidebar (icon + title + subtitle per nav item) with a minimal icon rail that expands via hover to reveal labels. State (pinned open vs collapsed) is persisted in localStorage.

---

## Structure

### Layer 1 — Icon Rail (always visible)

- **Width:** `64px`, fixed, full viewport height
- **Contents (top to bottom):**
  - Logo mark (icon only, no wordmark)
  - Nav icons — `40px` touch target each, vertically stacked
  - Avatar icon at bottom — clicking opens a profile popover
- **Active item:** filled icon + `3px` left accent bar (`var(--primary-500)`, `border-radius: 0 2px 2px 0`)
- **Inactive item:** `text-muted-foreground`, brightens to `text-foreground` on hover
- **No text anywhere in this layer**

### Layer 2 — Label Panel (overlay, hover-triggered)

- **Width:** `220px`
- **Position:** absolute, `left: 64px`, full height, overlays main content
- **Trigger:** `group-hover` on the rail wrapper — CSS only
- **Reveal animation:** `opacity-0 translate-x-[-8px]` → `opacity-100 translate-x-0`, `transition-all duration-150 ease-out`
- **Hide animation:** `transition-all duration-100 ease-in`, `delay-200` (prevents flicker)
- **Contents:** nav item labels only, vertically aligned with their corresponding icon rows
- **Active label:** `font-weight: 600`, `text-foreground`
- **Inactive label:** `text-muted-foreground`
- **Background:** frosted glass — `backdrop-blur-md` + subtle right-side shadow
- **Pin control:** `LockOpen` / `Lock` Lucide icon at top-right corner of panel; clicking toggles pin state

---

## Pin State

Stored in localStorage under key `sidebar-pinned` (`"true"` / `"false"`).

| State | Behavior |
|---|---|
| `pinned: false` (default) | Hover shows panel; mouse-out hides it (with 200ms delay) |
| `pinned: true` | Panel stays open regardless of hover; click pin icon to unpin |

Read on mount via `useState` initializer — no flash of wrong state.

---

## Interaction Details

| Interaction | Behavior |
|---|---|
| Hover rail (unpinned) | Panel reveals after 0ms, hides after 200ms delay on mouse-out |
| Click nav item (unpinned) | Navigate + panel closes immediately (no delay) |
| Click nav item (pinned) | Navigate; panel stays open |
| Click pin icon | Toggle pin state, persist to localStorage |
| Click avatar (bottom of rail) | Open Radix Popover with name, email, logout button |

---

## Layout Changes

The desktop layout is a flex row with `gap-6`. The aside is `shrink-0` with explicit width; main content fills the remainder automatically.

| Element | Before | After |
|---|---|---|
| Desktop sidebar (`<aside>`) | `lg:w-[320px] shrink-0` | `lg:w-16 shrink-0` (64px) |
| Label panel | n/a | `absolute left-16` overlay, does not affect flex layout |
| Main content | flex-1, fills remaining width | flex-1, fills remaining width (unchanged) |
| Mobile sidebar | Overlay drawer (unchanged) | Unchanged |

---

## Displaced Elements & New Homes

| Element | Old Location | New Location |
|---|---|---|
| Live sync indicator (WebSocket) | Bottom of sidebar | Header — small colored dot + "Live"/"Offline" label beside existing icons |
| Workspace indicator (page title + role badge) | Top of sidebar | Removed — already present in header breadcrumb |
| User profile card (name, email, logout) | Bottom of sidebar | Radix Popover on avatar click (bottom of icon rail) |

---

## Files Changed

- `frontend/src/components/Layout.tsx` — only file modified
  - Remove existing `lg:` desktop sidebar block
  - Add icon rail + label panel inline (not extracted to separate components — used once)
  - Adjust content wrapper margin
  - Move sync indicator to header section
  - Add avatar popover

---

## Out of Scope

- Mobile navigation (unchanged)
- Header redesign beyond sync indicator placement
- Any page-level layout changes
- Admin sidebar or nested navigation
