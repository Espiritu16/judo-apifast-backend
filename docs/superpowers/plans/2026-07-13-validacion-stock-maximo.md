# Validacion Stock Maximo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent future replenishments and positive inventory adjustments from exceeding configured maximum stock, while keeping historical overstock records usable.

**Architecture:** Backend services validate projected stock before creating movements or receiving replenishments. Stock changes remain owned by database triggers through `movimiento_inventario` inserts, so service code does not update `parametro_inventario.stock_actual` directly.

**Tech Stack:** FastAPI, SQLAlchemy, MySQL triggers, pytest.

---

### Task 1: Reposicion Maximum Stock Validation

**Files:**
- Modify: `app/modules/reposiciones/repository.py`
- Modify: `app/modules/reposiciones/service.py`
- Test: `tests/services/test_reposiciones_service.py`

- [x] Add repository method to load inventory parameters for received detail product ids.
- [x] Add service validation that blocks receiving a detail when `stock_maximo > 0` and `stock_actual + cantidad_recibida > stock_maximo`.
- [x] Keep products already above max usable by blocking only positive increases.
- [x] Add tests for blocking over max and allowing max unset.

### Task 2: Movimiento Maximum Stock Validation And Single Stock Owner

**Files:**
- Modify: `app/modules/movimientos/service.py`
- Test: `tests/services/test_movimientos_service.py`

- [x] Add tests for positive adjustment over max and positive adjustment within max.
- [x] Remove direct stock/cost mutation from movement service because MySQL triggers apply stock and entry cost from inserted movements.
- [x] Validate `stock_maximo` before adding an entry or positive adjustment movement.
- [x] Keep salida/negative adjustment validations for stock availability and stock safety.

### Task 3: Validation

**Files:**
- No production file changes.

- [x] Run backend focused tests for reposiciones and movimientos.
- [x] Compile changed backend modules.
- [x] Restart backend after successful tests.
