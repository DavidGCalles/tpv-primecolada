# PRODUCT REQUIREMENTS DOCUMENT (PRD)
**Product:** Primecolada Ecosystem

**Version:** 1.0

**Status:** In Development / Staging

**Date:** November 2025

## 1. Executive Summary
Primecolada v1.0 is the Minimum Viable Product designed to replace physical notebooks in laundromats with a **digital, cloud-based ledger**.
The goal of this release is to provide **Sales Management** for the operator and **Passive Traceability** for the customer. This release prioritizes software stability and UX over hardware integration.
* **Key Pivot:** We are removing the dedicated Websockets service to simplify the architecture, relying on standard HTTP/REST and Firestore for this version.

## 2. User Personas
1.  **The Operator (Admin):**
    * *Goal:* Process clothes fast. Needs to register drop-offs, update washing status, and close tickets via a tablet.
    * *Pain Point:* Answering "Is my laundry ready?" calls.
2.  **The Registered Customer:**
    * *Goal:* Track history of orders and see current status.
3.  **The Guest (Anonymous):**
    * *Goal:* Walk in, drop off clothes, receive a physical ticket with a QR, and scan it later to check status without downloading an app or creating an account.

## 3. Functional Requirements

### Epic 1: Authentication & Identity
**Status:** Mostly Implemented

| ID | Requirement | Status | Implementation Notes |
| :--- | :--- | :--- | :--- |
| **FR-1.1** | **Multi-Method Login:** Users must log in via Google or Email/Password. | ✅ Done | Implemented via Firebase Auth. |
| **FR-1.2** | **Role-Based Access:** System must distinguish between `Admin` (Operator) and `User` (Customer). | ✅ Done | Middleware checks `is_admin` flag in Firestore. |
| **FR-1.3** | **Guest Routing:** Anonymous/Guest users must be redirected to a useful landing page or public search, not a dead end. | ⚠️ **PENDING** | Currently redirects to an authenticated view (`UserView`) causing errors. Must be fixed to support Guest flow. |

### Epic 2: Core Sales Management (The Ledger)
**Status:** Implemented

| ID | Requirement | Status | Implementation Notes |
| :--- | :--- | :--- | :--- |
| **FR-2.1** | **Create Sale:** Admin can create a ticket with Customer Name, Phone, and Service Items (Washer/Dryer cost). | ✅ Done | `Ventas.vue` handles creation. API endpoint `POST /ventas` active. |
| **FR-2.2** | **State Machine:** Orders must flow through `EN_COLA` -> `LAVANDO` -> `PTE_RECOGIDA` -> `RECOGIDO`. | ✅ Done | Defined in `enums.py` and handled in `VentaCard.vue`. |
| **FR-2.3** | **Cost Calculation:** Auto-sum of Washer + Dryer services. | ✅ Done | Computed property in `VentaModal.vue`. |

### Epic 3: Traceability & Public Access (The "Gap")
**Status:** Partially Implemented / **CRITICAL FOR v1.0**

| ID | Requirement | Status | Implementation Notes |
| :--- | :--- | :--- | :--- |
| **FR-3.1** | **QR Generation:** System must generate a QR code for every sale pointing to a unique URL. | ✅ Done | `QrCodeModal.vue` generates QR pointing to `${origin}/venta/${id}`. |
| **FR-3.2** | **Public Order View:** A publicly accessible URL (`/venta/:id`) that displays the **Status** and **Total Cost** of a specific order. No login required. | 🔴 **MISSING** | **High Priority.** The route `/venta/:id` does not exist in the router. Current scans lead to 404/Home. |
| **FR-3.3** | **Privacy Masking:** The Public View must NOT show the customer's full phone number or sensitive data. Only First Name and Status. | 🔴 **MISSING** | Requires a new Backend Endpoint (or modification of `GET /ventas/:id`) to allow unauthenticated, limited read access. |

## 4. UI/UX Guidelines
* **Glassmorphism:** Continue using the existing glassmorphism aesthetic defined in the main CSS.
* **Public View:** Must be mobile-optimized. A simple "Traffic Light" interface for status:
    * 🔴 Queue / Error
    * 🟡 Washing / Drying
    * 🟢 Ready for Pickup

## 5. Out of Scope (v1.0)
* **Payments:** No Stripe/Redsys integration. Payments are marked manually by the Admin.
* **Hardware Integration:** No automatic printing or IoT connection to washers.
* **Push Notifications:** Users must scan the QR to check status; the system does not yet push alerts (WhatsApp/Email).