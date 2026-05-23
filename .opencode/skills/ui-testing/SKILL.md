---
name: ui-testing
description: |
  Test the store's frontend UI via Chrome DevTools Protocol (CDP).
  Navigate pages, inspect rendered HTML, take screenshots, test cart/checkout,
  and verify templates render correctly.
license: MIT
compatibility: opencode
metadata:
  audience: developer
  workflow: testing
---

## Overview

Use this skill when you need to visually verify the store's frontend.
Since the sandbox may restrict network access (curl returning 000),
you must bind Django to the Tailscale IP and use Chrome via CDP.

## Prerequisites

- Django dev server running on the Tailscale IP
- Chromium installed (via Playwright: `~/.cache/ms-playwright/chromium-*/chrome-linux/chrome`)
- Python package `websocket-client` installed
- Tailscale IP added to `ALLOWED_HOSTS` in `config/settings/local.py`

## Workflow

### 1. Start services

```bash
# Kill old servers
kill $(ps aux | grep "manage.py" | grep -v grep | awk '{print $2}') 2>/dev/null

# Start Django on Tailscale IP
DATABASE_URL=sqlite:///db.sqlite3 uv run python manage.py runserver 100.88.73.119:8000 &

# Start Chrome headless with remote debugging
CHROME=~/.cache/ms-playwright/chromium-1223/chrome-linux/chrome
$CHROME \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --headless --no-sandbox \
  --disable-gpu --disable-software-rasterizer \
  --disable-dev-shm-usage --no-zygote \
  --use-gl=swiftshader \
  --user-data-dir=/tmp/chrome_dev &
```

### 2. Connect via CDP

Use the Chrome DevTools Protocol via WebSocket:

```python
import json, time, urllib.request
from websocket import create_connection

pages = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
ws_url = pages[0]['webSocketDebuggerUrl']

def send(cmd, **params):
    ws = create_connection(ws_url)
    msg = {'id': 1, 'method': cmd, 'params': params}
    ws.send(json.dumps(msg))
    time.sleep(1)
    resp = json.loads(ws.recv())
    ws.close()
    return resp.get('result', {})
```

### 3. Key CDP methods

| Method | Purpose |
|---|---|
| `Page.navigate` | Go to a URL |
| `Page.captureScreenshot` | Take PNG screenshot, returns base64 `data` |
| `Runtime.evaluate` | Run JS in the page, get results |
| `Runtime.evaluate` with `awaitPromise: true` | For async operations (fetch API calls) |

### 4. Testing patterns

**Check page title & content:**
```python
r = send('Runtime.evaluate', expression='document.title')
title = r.get('result', {}).get('value', '')
```

**Extract rendered data:**
```python
r = send('Runtime.evaluate', expression='JSON.stringify({
  title: document.title,
  cards: document.querySelectorAll(".card").length,
  body: document.body.innerText.substring(0,500)
})')
```

**Test form submission (add to cart, login):**
```python
script = '''
(async () => {
  const fd = new FormData();
  fd.append("product_id", "14");
  fd.append("variant_id", "16");
  fd.append("quantity", "1");
  const r = await fetch("/carrito/agregar/", {
    method: "POST",
    headers: {"X-CSRFToken": csrf},
    body: fd
  });
  return r.status + " " + (await r.text()).substring(0,200);
})()'''
ws = create_connection(ws_url)
msg = {'id': 2, 'method': 'Runtime.evaluate',
       'params': {'expression': script, 'awaitPromise': True}}
ws.send(json.dumps(msg))
# wait for response
resp = json.loads(ws.recv())
```

**Take screenshot:**
```python
r = send('Page.captureScreenshot', format='png')
if 'data' in r:
    import base64
    with open('/tmp/page.png', 'wb') as f:
        f.write(base64.b64decode(r['data']))
```

## Common checks

| Check | Selector / Expression |
|---|---|
| Page title | `document.title` |
| Navbar links | `document.querySelectorAll("nav a").map(a=>a.href)` |
| Cart badge | `document.querySelector("a[href*=carrito] .badge")?.innerText` |
| Product cards count | `document.querySelectorAll(".card").length` |
| Cart has items | `document.body.innerText.includes("Tu carrito está vacío")` |
| Login form | `document.querySelector("form input[type=password]") !== null` |
| Price display | `document.querySelector(".fs-3")?.innerText` |
| Discount badge | `document.querySelector(".mb-3 .badge")?.innerText` |
| Error status | `document.title.includes("DisallowedHost")` |

## Troubleshooting

- **Connection refused**: Make sure Chrome started with `--remote-debugging-port=9222`
- **DisallowedHost**: Add the Tailscale IP to `ALLOWED_HOSTS` in `local.py`
- **No screenshots**: Verify the `data` key exists in the `Page.captureScreenshot` result
- **Session not persisting**: Cart is session-based; use the same browser tab for add→verify flow