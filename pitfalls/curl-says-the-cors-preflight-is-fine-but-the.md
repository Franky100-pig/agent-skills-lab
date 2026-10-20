# curl says the CORS preflight is fine but the browser still fails with Failed to fetch

Date: 2026-10-20 · Tags: `cors` `preflight` `browser-only` `verification`

## Symptom

An AI-help static page calls an LLM API directly from the browser with
`Authorization: Bearer <key>`. Server-side checks all look green, but every
real browser dies with `TypeError: Failed to fetch`:

```text
网络错误：Failed to fetch（需能访问 api.siliconflow.cn 或 open.bigmodel.cn）
```

The confusing part: curl-ing the preflight by hand **shows CORS headers** —

```text
HTTP/2 204
access-control-allow-credentials: true
access-control-allow-methods: GET,POST,DELETE,PUT,PATCH
access-control-allow-headers: *
access-control-allow-origin: *
```

— and the plain POST with the same key works from the terminal (HTTP 200). So
"the API and CORS are fine" seems like a safe conclusion. It isn't.

## The wrong assumption

"Preflight passes as long as the response **has** `Access-Control-Allow-*`
headers." Wrong on two counts:

1. `Access-Control-Allow-Headers: *` is a wildcard that **never covers
   `Authorization`**. MDN, verbatim: *"The Authorization header doesn't accept
   wildcard and always needs to be listed explicitly."* The browser evaluates
   the preflight strictly: requested header `authorization` is not matched by
   `*` → preflight fails → `fetch` rejects with `Failed to fetch`. curl never
   runs a CORS check, so curl cannot see this class of failure at all.
2. Presence ≠ validity. A provider can return `allow-origin` but still fail
   the check (missing `allow-headers`, wildcard + credentials mode, etc.).
   You have to compare the returned headers against **exactly what the browser
   requests** (`Access-Control-Request-Headers: authorization,content-type`),
   not just confirm some CORS headers exist.

## Spot it in 5 seconds

Ask: **did the preflight response list `authorization` explicitly in
`Access-Control-Allow-Headers`?** One command:

```bash
curl -sD - -o /dev/null -X OPTIONS "https://api.example.com/v1/chat/completions" \
  -H "Origin: https://your.site" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  | grep -i access-control-allow-headers
# `*`                          -> browser will still fail for Authorization
# `authorization,content-type` -> actually OK
```

Definitive ground truth is the browser console (F12 → Network → the OPTIONS
row): Chrome prints the exact failing rule, e.g. *"Response to preflight
request doesn't pass access control check: ... Authorization"*.

## Fix

You cannot fix the provider from the client; `Authorization` is mandatory for
keyed APIs, so the preflight cannot be avoided either. Real options:

- Pick a provider whose preflight lists `authorization` explicitly. Verified
  on 2026-10-20: DeepSeek, Moonshot, Aliyun Dashscope all return
  `access-control-allow-headers: authorization,content-type`; SiliconFlow
  returns `*` (broken for browsers); open.bigmodel.cn returned no CORS headers
  on OPTIONS at all that day.
- Or route through a same-origin/proxy backend that adds the header
  server-side.

For the record: there is no client-side workaround — `no-cors` gives opaque
responses, and moving the key out of `Authorization` (query/body) is both
unsupported and worse for leakage.

## Globalise it

- Any browser-direct call to an OpenAI-compatible API (chat UIs, playgrounds,
  static-site AI widgets) hits this; providers differ wildly in CORS hygiene
  and change it without notice.
- Same shape of bug as "the smoke test passes but only tests half the
  contract": curl validates the server, never the browser's stricter reading.
- Also bites people testing with HTTPie/Postman — none of them execute the
  CORS check; only a real browser does.

## Evidence

Real transcript from 2026-10-20 (LA Helper ai-help):

```text
=== SiliconFlow preflight (via curl) ===
HTTP/2 204
access-control-allow-credentials: true
access-control-allow-methods: GET,POST,DELETE,PUT,PATCH
access-control-allow-headers: *
access-control-allow-origin: *

=== same key, plain POST via curl ===
HTTP 200
{"choices":[{"message":{"content":"ok",...}}]}

=== browser ===
TypeError: Failed to fetch   (preflight rejected: Authorization not covered by *)
```

Contrast, same day:

```text
=== DeepSeek preflight ===
access-control-allow-headers: authorization,content-type   <- explicit, browser-OK
access-control-allow-origin: https://your.site

=== Aliyun Dashscope preflight ===
access-control-allow-headers: authorization, content-type  <- explicit, browser-OK
access-control-allow-origin: *
```

## Takeaway

`Access-Control-Allow-Headers: *` does not cover `Authorization` — a curl
preflight "pass" only proves headers exist, never that the browser's CORS
check succeeds.
