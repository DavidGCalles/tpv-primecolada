# ADR 003: Decoupling Client Identity from Authentication (The Shadow User Protocol)

* **Status:** Accepted
* **Date:** 2026-01-25
* **Deciders:** David G. Calles
* **Predecessors:** [ADR-001](001-Firebase-authentication.md)

## Context and Problem Statement

**ADR-001** established Firebase Authentication as the standard for user management, deciding to use the Firebase `UID` as the document key in the Firestore `clients` collection.

While secure for app users, this creates a **critical operational blocker** in the physical store. When a walk-in customer arrives:
1.  They provide a phone number.
2.  They may NOT have the app installed or a registered account.
3.  The current `create_venta` endpoint requires a valid `client_id` (which implies a registered Firebase user).

We cannot force customers to download an app and register just to drop off clothes. We need a way to track sales and history via phone number immediately, while allowing the user to "claim" that history later if they decide to register digitally.

## Decision Drivers

* **Operational Velocity:** The Admin must be able to create a sale using *only* a phone number and name.
* **Data Continuity:** Sales created for an unregistered user must seamlessly merge into their profile if/when they register.
* **Single Source of Truth:** We must avoid splitting data between "verified" and "unverified" collections (e.g., `clients` vs `temp_clients`).

## Considered Options

* **Option A:** Create a separate `unverified_sales` collection. (Rejected: Fragmented data, complex analytics).
* **Option B:** Force Admin to register users on the spot. (Rejected: Too slow, privacy concerns).
* **Option C (Selected):** "Shadow User" Protocol. Decouple Firestore Document ID from Firebase UID.

## Decision Outcome

Chosen option: **Option C**.

We will decouple the database Identity from the Authentication Provider Identity.

1.  **Schema Change:** The `clients` collection document IDs will no longer be the Firebase `UID`. They will be auto-generated Firestore IDs (or UUIDs).
2.  **Shadow Profiles:**
    * A client document can exist *without* a `firebase_uid` (Shadow User), identified uniquely by `phone`.
    * A client document can have a `firebase_uid` (Registered User).
3.  **Sales Creation Flow:**
    * The API will accept `phone` instead of `client_id`.
    * Backend logic: `Search Client by Phone` -> `If Missing, Create Shadow Client` -> `Use Client Doc ID for Sale`.
4.  **Claiming Flow (The Merge):**
    * When a user logs in via Firebase for the first time, the system checks for an existing Shadow Client with their verified phone number.
    * If found, the system updates the Shadow Client with the `firebase_uid`. The user instantly inherits their physical purchase history.

## Consequences

### Positive
* **Zero Friction:** Walk-in customers are processed immediately.
* **Unified History:** No data migration needed when a physical customer becomes a digital user.
* **Simpler Queries:** All sales live in `ventas` and point to `clients`.

### Negative
* **Refactoring:** Requires modifying `clients.py` and `routes.py` to move away from `key=UID` logic implemented in ADR-001.
* **Security/Verification:** We must ensure the phone number verified by Firebase matches the "Shadow" phone number to prevent history theft.