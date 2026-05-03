# Amelie Suite — Architecture

## Overview

Amelie Suite is a technical publishing ecosystem designed to transform structured text into production-ready documents.

## Components

### Amelie MD
Publishing engine (Markdown → DOCX/PDF)

### Amelie Core
Shared processing layer (normalization, parsing, validation)

### Amelie Docs (planned)
Documentation system and live preview

### Amelie LaTeX (planned)
Advanced academic publishing backend

## Design Principles

- Separation of concerns
- Output-first design
- Deterministic processing
- Compatibility with external engines (e.g., Nancy)

## Relationship with Nancy

Nancy is not a dependency of Amelie Suite.

It is a complementary engine focused on:

- decision systems
- data intelligence
- machine learning