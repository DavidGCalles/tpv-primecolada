# ADR 001: Migration to Firebase Authentication and UID-based Identity

## Context and Problem Statement

The current authentication and user management system relies on phone numbers (`int`) as the primary key for the `clients` collection in Firestore. This approach presents several critical issues:
1.  **Security Risk:** Authentication is non-existent; possession of a phone number grants account access.
2.  **Identity Coupling:** User identity is tightly coupled to a changeable contact method (phone number).
3.  **Scalability limit:** Integrating third-party OAuth providers (Google, Apple) is difficult because they provide unique UIDs, not necessarily phone numbers.
4.  **Data Integrity:** Changing a user's phone number requires a cascade update across all relational collections (e.g., `ventas`).

We want to introduce a robust, standard authentication mechanism that supports Google Sign-In and Email/Password, separating the user's identity from their contact attributes.

## Decision Drivers

* Need for secure authentication (protecting Maria's business data).
* Requirement to support Google Sign-In for friction-less access.
* Need to decouple PII (Personally Identifiable Information) from database keys.
* Desire to use industry-standard practices (Firebase Auth) instead of ad-hoc solutions.

## Considered Options

* **Option A (Selected):** Full adoption of Firebase Auth UIDs as Firestore Document Keys. Refactor DB schema.
* **Option B:** Hybrid approach (Phone number as key, mapping table for UIDs).
* **Option C:** Keep current system (Phone number as key).

## Decision Outcome

Chosen option: **Option A**.

We will replace the current ad-hoc phone-based login with **Firebase Authentication**.
The Firestore schema will be refactored:
1.  **Clients Collection:** Document IDs will be the Firebase `UID` (string) instead of the phone number.
2.  **Ventas Collection:** The `client_id` field will store the `UID`.
3.  **Authentication Flow:** The Frontend will authenticate against Firebase, obtain a JWT, and send it to the Backend. The Backend will verify the token and extract the UID to authorize requests.

## Consequences

### Positive
* **Security:** High. Relies on Google's infrastructure.
* **Flexibility:** Users can change phone/email without losing history.
* **Standardization:** Codebase will follow standard Firebase patterns, easier for new devs to onboard.
* **Clean Data:** PII is stored as attributes, not keys.

### Negative
* **Breaking Changes:** The current frontend and backend logic regarding user lookup will break immediately.
* **Migration Effort:** Existing data in Firestore (keyed by phone) must be migrated to new documents keyed by UID (or placeholders until the user claims them).
* **Complexity:** Introduction of JWT verification middleware in the Python backend.