#!/usr/bin/env python3
"""HTTP checks against a restored MIRU API: /health/, admin login, GET /api/deposits/."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def _request(url: str, method: str = 'GET', body: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    data = None
    headers = {'Accept': 'application/json'}
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
            return resp.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode('utf-8', errors='replace')
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {'raw': raw}
        return exc.code, payload


def main() -> int:
    base = os.environ.get('RESTORE_BASE_URL', 'http://127.0.0.1:18000').rstrip('/')
    user = os.environ.get('RESTORE_ADMIN_USER', 'admin')
    password = os.environ.get('RESTORE_ADMIN_PASSWORD', 'admin123')
    expect_deposits = int(os.environ.get('EXPECT_DEPOSIT_COUNT', '0'))

    status, health = _request(f'{base}/health/')
    data = health.get('data') or {}
    if status != 200 or not health.get('success') or data.get('status') != 'ok':
        print(f'FAIL health: HTTP {status} envelope={health.get("success")} data.status={data.get("status")}')
        return 1
    if data.get('database') != 'connected':
        print(f'FAIL health: database={data.get("database")!r} (bukan connected)')
        return 1
    print('OK /health/ 200 database=connected')

    status, login = _request(
        f'{base}/api/auth/login/',
        method='POST',
        body={'username': user, 'password': password},
    )
    login_data = login.get('data') or {}
    token = login_data.get('access')
    if status != 200 or not login.get('success') or not token:
        print(f'FAIL login admin: HTTP {status} success={login.get("success")}')
        return 1
    role = (login_data.get('user') or {}).get('role')
    print(f'OK login {user} role={role}')

    status, deposits = _request(f'{base}/api/deposits/', token=token)
    if status != 200 or not deposits.get('success'):
        print(f'FAIL GET /api/deposits/: HTTP {status} success={deposits.get("success")}')
        return 1
    rows = deposits.get('data') or []
    pagination = (deposits.get('meta') or {}).get('pagination') or {}
    count = pagination.get('count', len(rows) if isinstance(rows, list) else 0)
    if expect_deposits > 0 and count < 1:
        print(f'FAIL baca setoran: pagination.count={count} (sumber punya {expect_deposits})')
        return 1
    first_id = rows[0].get('id') if isinstance(rows, list) and rows else None
    print(f'OK GET /api/deposits/ count={count} first_id={first_id}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
