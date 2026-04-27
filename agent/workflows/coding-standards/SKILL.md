---
name: coding-standards
description: General coding standards and review guidance for TypeScript, JavaScript, React, and Node.js. Use when writing, refactoring, or reviewing code for naming, structure, readability, consistency, formatting, and project conventions.
---

# Coding Standards

## Overview

Use this skill when code needs to be easier to read, easier to change, and more consistent with the rest of the project. Apply the smallest standard that solves the problem, and follow the codebase's existing style when it is already clear.

## Core Principles

- Be consistent with the local codebase first.
- Prefer explicit, boring code over clever code.
- Keep functions small and focused.
- Name things by intent, not implementation details.
- Remove duplication when it hides the real rule or flow.

## TypeScript And JavaScript

- Type data at boundaries and public APIs.
- Avoid `any` unless there is no better option.
- Prefer narrow types, unions, and shared domain types.
- Keep parsing and validation close to input.
- Use early returns to reduce nesting.
- Prefer pure helpers for reusable logic.

## React

- Keep components focused on one responsibility.
- Derive state instead of duplicating it.
- Lift state only when multiple children truly need it.
- Prefer props and composition over deep coupling.
- Avoid unnecessary effects; use them for external synchronization.
- Split large components into smaller named pieces when the UI grows.

## Node And Backend Code

- Keep route handlers thin.
- Put business rules in services or domain functions.
- Put data access in repositories or query helpers.
- Validate input before side effects.
- Make errors actionable and stable.
- Prefer structured logging over ad hoc string logs.

## Formatting And Structure

- Match the repo formatter, lint rules, and file layout.
- Keep import groups tidy and ordered consistently.
- Group related code together and avoid mixed responsibilities.
- Prefer descriptive function names over inline anonymous logic when the block is non-trivial.
- Use comments only when the intent is not obvious from the code.

## Review Checklist

When reviewing or editing code, check:

- Is the intent obvious from names and structure?
- Is the change consistent with nearby code?
- Is there unnecessary nesting or duplication?
- Are types and validation strong enough at the boundaries?
- Would a future maintainer understand this without extra context?

## Good Defaults

- Prefer readability over brevity.
- Prefer deterministic behavior over implicit behavior.
- Prefer local conventions over generic personal style.
- Prefer one clear path through the code over many special cases.
