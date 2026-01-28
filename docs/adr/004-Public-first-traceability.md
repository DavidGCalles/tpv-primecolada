# ADR 004: Privacy-First Public Traceability

* **Status:** Accepted
* **Date:** 2026-01-27
* **Deciders:** David G. Calles

## Context and Problem Statement

We have built a robust internal ledger (The Backend) and a secure access system for registered users (The Walled Garden). However, the physical reality of our business relies on a printed ticket with a QR code.

Currently, this QR code is a "Bridge to Nowhere."
1.  **The Void:** Scanning it leads to a 404 or the Login page. A walk-in customer holding a physical ticket should not be forced to sign up just to check if their clothes are dry.
2.  **The Privacy Risk:** If we simply opened the existing `/ventas/{id}` endpoint to the public, we would expose PII (Full Name, Phone Number) to anyone holding the ticket (or guessing the URL). This is a GDPR nightmare waiting to happen.

We need a way to expose **status** without exposing **identity**. We need a "Glass Wall": transparency for the laundry, opacity for the human.

## Decision Drivers

* **Zero Friction:** The "Guest" experience must be instantaneous. Scan QR -> See Status. No Login. No "Accept Cookies". No app download.
* **Privacy by Design:** It must be mathematically impossible for a guest user to retrieve PII (Phone/Name) from the public API.
* **Mobile-First:** The UI is consumed standing up, holding a bag of clothes. It must be a simple, giant "Traffic Light" interface.
* **Architectural Simplicity:** We want to avoid managing separate "Guest Tokens" or complex auth flows for ephemeral access.

## Considered Options

* **Option A: The Naive Open.** Open the existing `/ventas/{id}` endpoint to unauthenticated requests.
    * *Verdict:* **Rejected.** Immediate data leak. Unacceptable privacy risk.
* **Option B: The Tokenized QR.** Generate a short-lived JWT encoded in the QR code itself that grants read access.
    * *Verdict:* **Rejected.** Adds significant complexity to the QR generation and validation logic. Over-engineering for a laundry status check.
* **Option C: The Public Projection (Selected).** Create a dedicated "Public Facade" endpoint that returns a strictly sanitized subset of data (DTO).

## Decision Outcome

Chosen option: **Option C**.

We will implement a **Public Projection Pattern**. We are creating a dedicated, read-only "Guest Lane" in our architecture.

### 1. The Backend (The Mask)
We will implement a specific endpoint `GET /public/ventas/{id}`.
* **Auth:** `Public` (No Token required).
* **Logic:** Fetches the sale by ID.
* **The Projection (DTO):** It maps the internal data to a `PublicVentaSchema` that strictly allows **only**:
    * `id` (String)
    * `estado_actual` (Int/Enum)
    * `coste.total` (Float)
    * `updated_at` (Date)
    * `alias` (String - masked name, e.g., "David G.")
* **Security:** It explicitly strips `telefono`, full `nombre`, and `client_id` before the byte stream leaves the server.

### 2. The Frontend (The Traffic Light)
We will implement a new route `/track/{id}` in the SPA.
* **Guard:** None. Accessible to the world.
* **UX:** A "Hyper-Minimalist" interface.
    * **Visual:** Giant Status Indicator (Color coded: Blue/Red/Green).
    * **Content:** "Your laundry is [WASHING]".
    * **Action:** "Refresh" button.

### 3. Security Mechanism
We rely on **ID Entropy**.
* Firestore Document IDs are long, alphanumeric strings. The probability of an attacker "guessing" a valid ID by brute-force enumeration is negligible for the sensitivity level of the data (Laundry Status).
* Even if an ID is guessed, the attacker only learns that "Someone is drying clothes for 4€," which is non-identifiable information.

## Consequences

### Positive
* **GDPR Compliance:** PII is physically isolated from the public interface.
* **User Delight:** The "Scan & See" flow is frictionless, matching the speed of the physical world.
* **Separation of Concerns:** We decouple the "Admin/User" rich view from the "Guest" status view.

### Negative
* **Obscurity Limit:** While secure for privacy, this relies on the secrecy of the URL. Anyone with the link can see the status. This is a feature, not a bug, for this use case (sharing the link with a partner to pick up clothes).
* **New Attack Surface:** We open a public endpoint. We must ensure strict validation to prevent resource exhaustion (though Firestore handles scale well).