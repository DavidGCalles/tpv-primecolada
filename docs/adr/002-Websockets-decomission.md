# ADR 002: Decommission Websockets and Remove Printing State

* **Status:** Accepted
* **Date:** 2026-01-25
* **Deciders:** David G. Calles
* **Consulted:** Sparring Partner (AI)

## Context and Problem Statement

The current architecture includes a `primecolada-websockets` service and a specific `IMPRIMIENDO` (Printing) state for sales. This design anticipated a physical setup with thermal printers receiving real-time push notifications.

However, the physical infrastructure (hardware, network topology) does not exist. Currently, creating a sale sends it to an "Imprimiendo" limbo where it stays until manually moved to "En Cola" (In Queue). This creates:

1.  **Fake Complexity:** We are maintaining code (Websockets, simulated states) for hardware that isn't there.
2.  **Operational Friction:** The user must manually click to confirm a "print" action that never physically happened.
3.  **Zombie Views:** The "Printing" widget in the frontend serves no functional purpose.

We need to align the software with the current physical reality of the business.

## Decision Drivers

* **YAGNI (You Aren't Gonna Need It):** We are building states for a future that is not yet defined.
* **Operational Efficiency:** Reducing unnecessary clicks for the operator.
* **Infrastructure Simplification:** Reducing the number of containers and maintenance surface.
* **Eliminate "Magical Thinking":** If there is no printer, there is no "Printing" state.

## Considered Options

* **Option A (Selected):** Full Decommission. Remove Websockets service **AND** the `IMPRIMIENDO` state/view.
* **Option B:** Tech Swap. Remove Websockets but keep `IMPRIMIENDO` state using HTTP Polling.
* **Option C:** Status Quo. Keep Websockets and `IMPRIMIENDO` state.

## Decision Outcome

Chosen option: **Option A**.

We will completely excise the "Printing" concept from the v1 scope.

1.  **Architecture:** The `primecolada-websockets` service will be deleted from the repository and `docker-compose`.
2.  **Backend Logic:**
    * The `IMPRIMIENDO` state is deprecated for new sales.
    * New sales will be created directly in `EN_COLA` (State 2).
    * Endpoints related to "imprimiendo" (`/ventas/imprimiendo`) will be removed.
3.  **Frontend UX:**
    * The "Printing" widget/view is removed.
    * User feedback upon sale creation will be a simple notification (Toast): "Order created and queued".
    * Any physical identification (if needed) will rely on browser-native printing (`window.print()`) or handwritten tags, without blocking the digital workflow.

## Consequences

### Positive

* **Zero Infrastructure Cost:** One less container to build, deploy, and monitor.
* **Codebase Reduction:** Significant deletion of frontend/backend boilerplate code.
* **Faster UX:** Operators skip a redundant validation step.
* **Truthful Modeling:** The software reflects the actual process (Order -> Queue), not a hypothetical one.

### Negative

* **Loss of Simulation:** We lose the visual cue that "something is being processed" before the queue, although this was fake processing.
* **Future Rework:** If we introduce physical networked printers later, we will have to re-implement a printing subsystem (likely different from the current naive websocket implementation).