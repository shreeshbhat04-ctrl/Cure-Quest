# Ingredients Marketplace: Implementation Guide

The Marketplace (Rx Pantry) is a feature designed to help users shop for doctor-approved ingredients that align with their specific dietary protocols (e.g., Anti-Inflammatory).

## Core Components to Extract

1.  **Safety Status Logic**: The marketplace uses three states for ingredients:
    *   **Safe**: Recommended based on the current health protocol.
    *   **Watch**: Monitor intake; potentially problematic in large quantities.
    *   **Avoid**: Non-compliant with the current prescription/protocol.

2.  **Bento Layout**:
    *   **Header**: Search and restriction badges.
    *   **Stats Grid**: Summary of daily targets (calories, protein).
    *   **Categorized Sidebar**: Quick filtering by ingredient types.
    *   **Compliance Insight**: AI-generated suggestions based on shopping patterns.

## Implementation Steps

### 1. Data Structure
Create a library file `src/lib/ingredients.ts` to manage the ingredient database. Each item should include:
- `id`: Unique identifier.
- `name`: Ingredient name.
- `status`: 'Safe' | 'Watch' | 'Avoid'.
- `category`: 'Fresh' | 'Protein' | 'Pantry' | 'Dairy'.
- `reason`: Clinical justification for the status.
- `price`: Current market price.

### 2. UI Theme Integration
**CRITICAL**: The UI must use the existing **Cure-Quest Nurture theme**:
- Use `glass-panel` for cards instead of solid backgrounds.
- Use `--color-primary` (Sage) and `--color-secondary` (Sand/Terracotta) for accents.
- Maintain the global background image with the dynamic overlay.

### 3. Screen Development
Create `src/screens/MarketplaceScreen.tsx`:
- Use `AnimatePresence` for smooth filtering transitions.
- Implement the search and category filters.
- Use `lucide-react` icons (ShieldCheck, ShieldAlert, etc.) for status indicators.

### 4. Navigation Integration
Update `src/components/Layout.tsx` to include the "Marketplace" tab and add a shopping cart icon to the header for tracking selected items.

---
*Note: This document has been updated with implementation instructions. Original code references are preserved in the development branch.*
