# Design Document: Mobile-Friendly Documentation with Content Filtering

**Date:** 2026-04-13
**Status:** Approved

## Goal
The goal is to streamline the Synapto documentation repository by filtering out unwanted content categories and ensuring the remaining site is fully mobile-friendly via an intuitive hamburger menu navigation.

## Design Sections

### 1. Document Filtering
- **Elimination**: Remove the following directories from `content/docs/`:
    - `deployment/`
    - `manual/`
    - `reference/`
    - `superpowers/`
- **Landing Page Update**: Refactor `content/docs/index.md` to remove sections for API Reference and Configuration, focusing purely on "For Operators" and "For Developers".
- **Link Audit**: Scan remaining `.md` files in `for-developers/` and `for-operators/` to ensure no dead links point to the discarded content.

### 2. Mobile Navigation Header
- **Component: `components/MobileNav.tsx`**:
    - A client component that handles the open/close state of the mobile menu.
    - Features a sticky top bar with the Synapto branding and a "Menu" button.
- **Side Panel Integration**:
    - The existing `Sidebar` will be wrapped or modified to function as the slide-out drawer on mobile screens.
    - An overlay backdrop will be added to provide focus when the menu is active.
- **Responsiveness**:
    - Desktop: The sidebar remains fixed on the left (current behavior).
    - Mobile: The sidebar is hidden by default and toggled via the `MobileNav` header.

## Implementation Workflow
1. **Cleanup**: Perform file deletions and content updates.
2. **Refactor**: Implement `MobileNav` and update layout.
3. **Verification**: Confirm site builds and navigation works on all screen sizes.

---
*Self-Correction: Added Link Audit to ensure content integrity post-cleanup.*
