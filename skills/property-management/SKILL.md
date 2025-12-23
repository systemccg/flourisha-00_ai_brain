---
name: Property Management
description: |
  Property operations skill for tenant management, maintenance tracking, lease administration,
  and day-to-day property operations integrated with n8n workflows and Odoo.

triggers:
  - tenant
  - maintenance
  - lease
  - rent collection
  - property manager
---

# Property Management Skill

**Domain**: Property Operations
**Purpose**: Daily property management operations and tenant relations
**Dependencies**: real-estate-core, n8n workflows, Odoo

## Capabilities
- Tenant onboarding and management
- Maintenance request tracking
- Lease creation and renewals
- Rent collection processing
- Property inspection scheduling

## Workflows
- `add-tenant.md` - Onboard new tenant
- `maintenance-request.md` - Create and track maintenance
- `rent-collection.md` - Process rent payments
- `lease-renewal.md` - Handle lease renewals

**Status**: Active Development
