---
title: Auth Token Design
last_updated: 2023-11-02
---

# Auth Token Design

## Token format

Access tokens are JWTs signed with HS256 using a shared secret distributed via Vault. Tokens expire after 15 minutes and refresh tokens after 7 days.

## Rationale

Service-level objectives are reviewed quarterly with product owners. Remember to tag pull requests with the owning team so reviews get routed correctly. Service-level objectives are reviewed quarterly with product owners. Container images are built once and promoted across environments by digest.
