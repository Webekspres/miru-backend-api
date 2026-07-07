---
name: miru-feature-testing
description: >-
  Run and write Django tests for MIRU backend after creating or editing features.
  Validates JSON envelope responses, auth flows, and API contracts. Use when
  implementing or modifying backend features, before marking tasks complete,
  or when the user asks to test a feature.
---

# MIRU Backend Feature Testing

## When to Apply

Run this workflow **every time** you finish creating or editing a backend feature:

1. Write or update tests in `api/tests/`
2. Run the test suite
3. Fix failures before marking tasks done

## Quick Commands

```bash
# All tests (Docker)
docker compose exec web python manage.py test api.tests --verbosity=2

# Single module
docker compose exec web python manage.py test api.tests.test_auth --verbosity=2

# Local venv
python manage.py test api.tests --verbosity=2
```

## Test Standards

### 1. Extend `EnvelopeAPITestCase`

```python
from api.tests.base import EnvelopeAPITestCase

class MyFeatureTests(EnvelopeAPITestCase):
    def test_example(self):
        response = self.client.get('/api/waste-categories/')
        self.assert_envelope_success(response, 200)
```

### 2. Assert JSON Envelope (required)

Every API test must verify:

| Check | Success | Error |
|-------|---------|-------|
| `success` | `True` | `False` |
| `status_code` | matches HTTP | matches HTTP |
| `message` | present | present |
| `data` | payload | `null` |
| `meta.timestamp` | ISO 8601 WIT | present |
| `meta.request_id` | present | present |
| `code` | — | machine-readable |

Use helpers from `api/tests/base.py`:
- `assert_envelope_success(response, status_code)`
- `assert_envelope_error(response, status_code)`

### 3. File Organization

```
api/tests/
├── base.py           # EnvelopeAPITestCase + factories
├── test_auth.py      # Auth, registration, /api/auth/me/
├── test_deposits.py  # (per module)
└── test_*.py
```

Name files `test_<module>.py`. One test class per endpoint group.

### 4. What to Test per Feature

| Layer | Required tests |
|-------|----------------|
| Auth | login, refresh, 401, role in response |
| CRUD | create 201, list 200, retrieve 200, validation 400 |
| Permissions | 403 for wrong role, owner-only access |
| Business rules | 422 with domain `code` (when implemented) |

### 5. Use English Routes

Routes are English kebab-case. See `04-api-contracts-and-standards.md` §1.1:

- `/api/waste-categories/` not `/api/sampah/kategori/`
- `/api/deposits/` not `/api/transaksi/`
- `/api/auth/me/` for current user profile

### 6. Seed Data for Manual / Integration Tests

```bash
docker compose exec web python manage.py seed_data --flush
```

Creates 200+ records: categories, rewards, staff, 180 nasabah, deposits, pickups, etc.

Demo credentials: `admin/admin123`, `nasabah001/nasabah123`

## Workflow Checklist

```
- [ ] Feature implemented
- [ ] Tests added/updated in api/tests/test_<module>.py
- [ ] python manage.py test api.tests — ALL PASS
- [ ] Envelope format verified in tests
- [ ] Task list item marked done
- [ ] graphify update . (if code changed)
```

## Do Not

- Skip tests when marking task list items complete
- Assert raw DRF response without envelope fields
- Use Indonesian URL paths in new tests
- Commit failing tests

## Reference

- API contracts: `.ai-steering/04-api-contracts-and-standards.md`
- Task list: `.ai-steering/08-task-list.md`
- Route table: `README.md`
