<div align="center">
  <img src="https://raw.githubusercontent.com/EZXLabs/ezcapsolver-py/main/assets/ez-captcha-logo.svg" alt="EZCaptchaSolver by EZXLabs" height="88">
  &nbsp;&nbsp;
  <img src="https://raw.githubusercontent.com/EZXLabs/ezcapsolver-py/main/assets/python.svg" alt="Python" height="88">
  <h1>EZCaptchaSolver Python SDK</h1>
  <p>
    <a href="https://github.com/EZXLabs/ezcapsolver-py/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/EZXLabs/ezcapsolver-py/actions/workflows/ci.yml/badge.svg"></a>
    <a href="https://pypi.org/project/ezcapsolver-py/"><img alt="PyPI" src="https://img.shields.io/pypi/v/ezcapsolver-py.svg"></a>
    <a href="https://github.com/EZXLabs/ezcapsolver-py/blob/main/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-blue.svg"></a>
    <a href="https://www.python.org"><img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-blue.svg?logo=python&logoColor=white"></a>
    <a href="https://ezxlabs.com"><img alt="EZXLabs website" src="https://img.shields.io/badge/website-ezxlabs.com-FFDB29?logoColor=black"></a>
  </p>
  <p>
    <a href="https://ezxlabs.com">🌐 Official website</a> &nbsp;·&nbsp;
    <a href="https://docs.ezxlabs.com/docs/captcha/api">📚 EZCaptchaSolver API reference</a> &nbsp;·&nbsp;
    <a href="https://github.com/EZXLabs/ezcapsolver-py/tree/main/examples">🧪 Examples</a> &nbsp;·&nbsp;
    <a href="#-supported-captcha-types">🧩 Captcha Types</a>
  </p>
  <p><b>English</b> &nbsp;·&nbsp; <a href="https://github.com/EZXLabs/ezcapsolver-py/blob/main/README.zh-CN.md">简体中文</a></p>
</div>

---

The EZCaptchaSolver Python SDK is an open-source Python client maintained by [EZXLabs](https://ezxlabs.com) for its CAPTCHA recognition task API. It provides typed requests and async and blocking clients for the supported task types below; the package also includes a TLS forwarding task that does not solve CAPTCHAs. For the wider SDK family, see the [EZCaptchaSolver SDK product page](https://ezxlabs.com/products/sdk); for HTTP request and response fields, see the [EZCaptchaSolver API reference](https://docs.ezxlabs.com/docs/captcha/api); for Python usage, see the [examples in this repository](https://github.com/EZXLabs/ezcapsolver-py/blob/main/examples/README.md).

## 🧩 Supported Captcha Types

Captcha task types come in a synchronous and an asynchronous form:

- Synchronous: the request blocks after the task is created and returns once the task is done.
- Asynchronous: creating the task returns a task ID, and the result is fetched later by polling that ID. This suits captcha types that take a while to solve.

A captcha type can support both forms at once, and almost every type supports the synchronous one. A few types are asynchronous only.

### reCAPTCHA v2

| Task type | Modes | Example | Description |
| :-: | :---: | :-: | --- |
| `ReCaptchaV2TaskProxyless` | all | [Example](#task-recaptchav2taskproxyless) | reCAPTCHA v2 |
| `ReCaptchaV2TaskProxylessS9` | all | [Example](#task-recaptchav2taskproxylesss9) | reCAPTCHA v2, returns a token scored ≥ 0.9 |
| `ReCaptchaV2STaskProxyless` | all | [Example](#task-recaptchav2staskproxyless) | reCAPTCHA v2 carrying the challenge-bound `s` parameter |
| `ReCaptchaV2EnterpriseTaskProxyless` | all | [Example](#task-recaptchav2enterprisetaskproxyless) | reCAPTCHA v2 Enterprise |
| `ReCaptchaV2SEnterpriseTaskProxyless` | all | [Example](#task-recaptchav2senterprisetaskproxyless) | reCAPTCHA v2 Enterprise, carrying the `s` parameter |
| `ReCaptchaV2Classification` | sync | [Example](#task-recaptchav2classification) | reCAPTCHA v2 image recognition |

### reCAPTCHA v3

| Task type | Modes | Example | Description |
| :-: | :---: | :-: | --- |
| `ReCaptchaV3TaskProxyless` | all | [Example](#task-recaptchav3taskproxyless) | reCAPTCHA v3 |
| `ReCaptchaV3TaskProxylessS9` | all | [Example](#task-recaptchav3taskproxylesss9) | reCAPTCHA v3, returns a token scored ≥ 0.9 |
| `ReCaptchaV3EnterpriseTaskProxyless` | all | [Example](#task-recaptchav3enterprisetaskproxyless) | reCAPTCHA v3 Enterprise |
| `ReCaptchaV3EnterpriseTaskProxylessS9` | all | [Example](#task-recaptchav3enterprisetaskproxylesss9) | reCAPTCHA v3 Enterprise, returns a token scored ≥ 0.9 |

### FunCaptcha / Arkose Labs

| Task type | Modes | Example | Description |
| :-: | :---: | :-: | --- |
| `FuncaptchaTaskProxyless` | async | [Example](#task-funcaptchataskproxyless) | FunCaptcha / Arkose Labs |
| `FunCaptchaClassification` | sync | [Example](#task-funcaptchaclassification) | FunCaptcha image recognition |

### hCaptcha

| Task type | Modes | Example | Description |
| :-: | :---: | :-: | --- |
| `HCaptcha` | async | [Example](#task-hcaptcha) | hCaptcha |
| `HCaptchaClassification` | sync | [Example](#task-hcaptchaclassification) | hCaptcha image recognition, single or multiple images |

### Cloudflare

| Task type | Modes | Example | Description |
| :-: | :---: | :-: | --- |
| `CloudFlare5STask` | async | [Example](#task-cloudflare5stask) | CF five-second interstitial, **requires** a `proxy` |
| `CloudFlareTurnstileTask` | async | [Example](#task-cloudflareturnstiletask) | Turnstile, returns a token |

### Akamai

| Task type | Modes | Example | Description |
| :-: | :---: | :-: | --- |
| `AkamaiWEBTaskProxyless` | sync | [Example](#task-akamaiwebtaskproxyless) | Akamai Web |
| `AkamaiSBSDTaskProxyless` | sync | [Example](#task-akamaisbsdtaskproxyless) | Akamai SBSD |

> Akamai Web is a multi-round flow: feed the `encodedata` of one round back as the `encode_data` of the next. The two spellings genuinely differ on the wire; the SDK keeps the service's definitions as they are rather than "fixing" them.

### DataDome

| Task type | Modes | Example | Description |
| :-: | :---: | :-: | --- |
| `DataDomeTaskProxyless` | sync | [Example](#task-datadometaskproxyless) | The challenge after an interception, in two steps selected by `step` |
| `DataDomeTagsTaskProxyless` | sync | [Example](#task-datadometagstaskproxyless) | Reports a fingerprint on the normal browsing path |

### Other

| Task type | Modes | Example | Description |
| :-: | :---: | :-: | --- |
| `PerimeterX` | async | [Example](#task-perimeterx) | PerimeterX clearance cookies |
| `IncapsulaTaskProxyless` | sync | [Example](#task-incapsulataskproxyless) | Incapsula Reese84 payload |
| `TlsTask` | sync | [Example](#task-tlstask) | HTTP request forwarded over TLS, returns the upstream response |

## 📦 Installation

```bash
pip install ezcapsolver-py
```

Requires Python 3.12+. The only runtime dependency is [`httpx`](https://www.python-httpx.org/); both clients are built on it, so their behaviour cannot drift apart.

> The distribution is named `ezcapsolver-py`, the import is `ezcapsolver`.

## 🚀 Quick Start

The client reads `EZCAPTCHA_API_KEY` from the environment when no key is passed explicitly.

```python
from ezcapsolver import EzCapSolverClient

with EzCapSolverClient() as client:
    solved = client.solve_recaptcha_v2_task_proxyless(
        "https://example.com",
        "6Lc_your_site_key",
    )

    print("task_id =", solved.task_id)
    print("token   =", solved.solution.token)
```

The async client has exactly the same method names; add `await`:

```python
from ezcapsolver import AsyncEzCapSolverClient

async with AsyncEzCapSolverClient() as client:
    solved = await client.solve_recaptcha_v2_task_proxyless(
        "https://example.com",
        "6Lc_your_site_key",
    )

    print("token =", solved.solution.token)
```

## 📖 Usage

One section per task type below. The snippets assume a `client` is already in scope, and leave out the `with` block to keep the call itself in focus.

### Sync / async

**Every task type has two methods**, taking the same arguments and returning the same type; only the endpoint differs:

```python
# Create, then poll
solved = client.solve_recaptcha_v2_task_proxyless(url, site_key)
assert solved.task_id is not None

# The synchronous endpoint, answering on the creating request
solved = client.sync_solve_recaptcha_v2_task_proxyless(url, site_key)
assert solved.task_id is None  # the synchronous endpoint assigns no task ID
```

The same holds for the task-object form: `solve()` always polls, `sync_solve()` always uses the synchronous endpoint.

```python
from ezcapsolver import ReCaptchaV2Task

task = ReCaptchaV2Task(website_url=url, website_key=site_key)

solved = client.solve(task)
solved = client.sync_solve(task)
```

Each task class carries a `mode` recording the execution mode the service documents for it. This is **informational** — nothing in the SDK reads it to pick a path. It matters because the service may reject a type on the endpoint it does not serve, with `ERROR_TASK_TYPE_NOT_ALLOWED` on the synchronous side. Such a rejection is refused **before** the task is billed, so it costs a round trip rather than a task.

```python
from ezcapsolver import ReCaptchaV2ClassificationTask, TaskMode

ReCaptchaV2ClassificationTask.mode is TaskMode.SYNC  # True
```

### Proxy format

Task types that accept a `proxy` take it in one of two shapes, decided by the task type:

| Format | Shape | Used by |
| --- | --- | --- |
| `NORMAL` | `protocol://username:password@host:port` | every type except FunCaptcha |
| `FUN` | `protocol://host:port:username:password` | `FunCaptchaTask` only |

`protocol` is one of `http`, `https` or `socks5`. **Both credentials are required** -- the service
rejects an unauthenticated proxy -- and the host may not be a private address (`127.0.*`,
`192.168.*`, `172.16.*`, `10.0.*`). Where the field is optional, leaving it empty is fine; it is
only a non-empty malformed value that is rejected.

### reCAPTCHA v2

[reCAPTCHA v2 API reference](https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v2)

The first five types share `ReCaptchaV2Task` and `ReCaptchaSolution`; only the method name differs.

<a id="task-recaptchav2taskproxyless"></a>

#### ReCaptchaV2TaskProxyless

```python
solved = client.solve_recaptcha_v2_task_proxyless(
    "https://example.com",
    "6Lc_your_site_key",
)

print("task_id =", solved.task_id)
print("token   =", solved.solution.token)
```

<a id="task-recaptchav2taskproxylesss9"></a>

#### ReCaptchaV2TaskProxylessS9

Identical parameters to plain v2; runs on the high-score queue and returns a token scored ≥ 0.9.

```python
solved = client.solve_recaptcha_v2_task_proxyless_s9(
    "https://example.com",
    "6Lc_your_site_key",
)

print("token =", solved.solution.token)
```

<a id="task-recaptchav2staskproxyless"></a>

#### ReCaptchaV2STaskProxyless

Carries the challenge-bound `s` parameter. It is not mandatory; without it the behaviour matches plain v2.

```python
solved = client.solve_recaptcha_v2_s_task_proxyless(
    "https://example.com",
    "6Lc_your_site_key",
    s="value-from-the-page",
)

print("token =", solved.solution.token)
```

<a id="task-recaptchav2enterprisetaskproxyless"></a>

#### ReCaptchaV2EnterpriseTaskProxyless

Enterprise. If the site uses enterprise parameters beyond `data-s`, pass them as keyword arguments and they are forwarded as-is.

```python
solved = client.solve_recaptcha_v2_enterprise_task_proxyless(
    "https://example.com",
    "6Lc_your_site_key",
)

print("token =", solved.solution.token)
```

<a id="task-recaptchav2senterprisetaskproxyless"></a>

#### ReCaptchaV2SEnterpriseTaskProxyless

Enterprise, carrying the `s` parameter.

```python
solved = client.solve_recaptcha_v2_s_enterprise_task_proxyless(
    "https://example.com",
    "6Lc_your_site_key",
    s="value-from-the-page",
)

print("token =", solved.solution.token)
```

<a id="task-recaptchav2classification"></a>

#### ReCaptchaV2Classification

[reCAPTCHA v2 classification API reference](https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v2-classification)

Recognises the image grid directly and returns tile indices rather than a token.

```python
solution = client.sync_solve_recaptcha_v2_classification(
    image_base64,
    "/m/0k4j",
    size=4,  # 1 = 1x1, 3 = 3x3, 4 = 4x4
).solution

if solution.is_multi:
    print("tiles to click", solution.objects)
elif solution.is_single:
    print("contains the object:", solution.has_object)
else:
    print("result type:", solution.type, "pass-through:", solution.extra)
```

On `ReClassificationSolution` the JSON field `hasObject` maps to `has_object`. An unknown `type` value is kept verbatim and extra fields land in `extra`. Missing fields fall back to an empty type, `False` and an empty list; `is_multi` and `is_single` only look at `type`.

### reCAPTCHA v3

[reCAPTCHA v3 API reference](https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v3)

The four types share `ReCaptchaV3Task` and `ReCaptchaSolution`. `page_action` has to match the `action` the page passes to `grecaptcha.execute`, otherwise the site-side check fails.

> ⚠️ `is_invisible` defaults to `False` on `ReCaptchaV2Task` and to **`True`** on `ReCaptchaV3Task`, matching the service. The two models do not share a default.

<a id="task-recaptchav3taskproxyless"></a>

#### ReCaptchaV3TaskProxyless

```python
solved = client.solve_recaptcha_v3_task_proxyless(
    "https://example.com",
    "6Lc_your_site_key",
    page_action="login",
)

print("task_id =", solved.task_id)
print("token   =", solved.solution.token)
```

<a id="task-recaptchav3taskproxylesss9"></a>

#### ReCaptchaV3TaskProxylessS9

```python
solved = client.solve_recaptcha_v3_task_proxyless_s9(
    "https://example.com",
    "6Lc_your_site_key",
    page_action="login",
)

print("token =", solved.solution.token)
```

<a id="task-recaptchav3enterprisetaskproxyless"></a>

#### ReCaptchaV3EnterpriseTaskProxyless

```python
solved = client.solve_recaptcha_v3_enterprise_task_proxyless(
    "https://example.com",
    "6Lc_your_site_key",
    page_action="login",
)

print("token =", solved.solution.token)
```

<a id="task-recaptchav3enterprisetaskproxylesss9"></a>

#### ReCaptchaV3EnterpriseTaskProxylessS9

```python
solved = client.solve_recaptcha_v3_enterprise_task_proxyless_s9(
    "https://example.com",
    "6Lc_your_site_key",
    page_action="login",
)

print("token =", solved.solution.token)
```

### FunCaptcha / Arkose Labs

[FunCaptcha API reference](https://docs.ezxlabs.com/docs/captcha/api/funcaptcha)

<a id="task-funcaptchataskproxyless"></a>

#### FuncaptchaTaskProxyless

```python
solved = client.solve_funcaptcha_task_proxyless(
    "https://example.com",
    "your-public-key",
)

print("token =", solved.solution.token)
```

> FunCaptcha is the one task type whose proxy uses the `FUN` format: `protocol://host:port:username:password`, with the credentials after the host rather than before it.

<a id="task-funcaptchaclassification"></a>

#### FunCaptchaClassification

```python
solution = client.sync_solve_funcaptcha_classification(
    image_base64,
    "Pick the animal facing left",
).solution

# The result shape of this type is unconfirmed; every field the worker returns lands in extra.
print(solution.extra)
```

### hCaptcha

[hCaptcha API reference](https://docs.ezxlabs.com/docs/captcha/api/hcaptcha)

<a id="task-hcaptcha"></a>

#### HCaptcha

The hCaptcha token field is `generated_pass_uuid`, not `token` — that is the service's naming, and the SDK keeps it.

```python
solved = client.solve_hcaptcha(
    "https://example.com",
    "your-site-key",
    "en-US",
    invisible=False,
)

print("token =", solved.solution.generated_pass_uuid)
```

<a id="task-hcaptchaclassification"></a>

#### HCaptchaClassification

Use `image` for one image and `images` for several; every field is optional, because different recognition modules need different combinations of input.

```python
solution = client.sync_solve_hcaptcha_classification(
    images=images,
    question="Please click each image containing a bicycle",
).solution

# The shape is unconfirmed here too; every field is in extra.
print(solution.extra)
```

### Cloudflare

<a id="task-cloudflare5stask"></a>

#### CloudFlare5STask

[Cloudflare 5S API reference](https://docs.ezxlabs.com/docs/captcha/api/cloudflare-5s)

The five-second interstitial **requires** a `proxy`, and returns not a single token but the headers and clearance cookies to replay against the target site:

```python
solution = client.solve_cloudflare_5s_task(
    "https://example.com",
    "http://user:pass@127.0.0.1:8080",
).solution

for name, value in solution.cookies.items():
    print(f"{name}={value}")
print("TLS fingerprint =", solution.tls_version)
```

Replaying those headers and cookies against the protected site is what actually clears the challenge — the result is a whole browser state, not a token.

<a id="task-cloudflareturnstiletask"></a>

#### CloudFlareTurnstileTask

[Cloudflare Turnstile API reference](https://docs.ezxlabs.com/docs/captcha/api/turnstile)

Turnstile's `proxy` is optional, and it returns a single token.

```python
solved = client.solve_cloudflare_turnstile_task(
    "https://example.com",
    "0x4AAA_your_site_key",
)

print("token =", solved.solution.token)
```

### Akamai

<a id="task-akamaiwebtaskproxyless"></a>

#### AkamaiWEBTaskProxyless

[Akamai Web API reference](https://docs.ezxlabs.com/docs/captcha/api/akamai-web)

Akamai Web is a multi-round flow: feed the `encodedata` of one round back as the `encode_data` of the next. The two spellings genuinely differ on the wire; the SDK keeps the service's definitions as they are.

```python
encode_data = ""

for index in range(1, 4):
    solution = client.sync_solve_akamai_web_task_proxyless(
        "https://example.com",
        "https://example.com/v3.js",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "zh-CN",
        index=index,
        abck=abck,
        bmsz=bmsz,
        script_base64=script_base64,
        encode_data=encode_data,
    ).solution

    print(f"round {index} payload =", solution.payload)
    encode_data = solution.encodedata
```

<a id="task-akamaisbsdtaskproxyless"></a>

#### AkamaiSBSDTaskProxyless

[Akamai SBSD API reference](https://docs.ezxlabs.com/docs/captcha/api/akamai-sbsd)

A single-round task; all six fields are required.

```python
solution = client.sync_solve_akamai_sbsd_task_proxyless(
    "https://example.com",
    "https://example.com/.well-known/sbsd",
    "value-from-the-page",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "zh-CN",
    script_base64,
).solution

print("payload =", solution.payload)
```

### DataDome

<a id="task-datadometaskproxyless"></a>

#### DataDomeTaskProxyless

The challenge after a DataDome interception runs in two steps that share one method and are selected by `step`; which fields of `DataDomeSolution` carry a value depends on the step:

```python
from ezcapsolver import DataDomeStep

# Step one: get the challenge address from the intercepted page.
solution = client.sync_solve_data_dome_task_proxyless(
    html_b64,
    step=DataDomeStep.ONE,
).solution

print("challenge address =", solution.url)

# Step two uses DataDomeStep.TWO, and the result carries the validation body.
```

<a id="task-datadometagstaskproxyless"></a>

#### DataDomeTagsTaskProxyless

Reports a fingerprint on the normal browsing path. Its field names are camelCase, unlike `DataDomeTask` above.

```python
solution = client.sync_solve_data_dome_tags_task_proxyless(
    "your-datadome-key",
    "https://example.com",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    bpc=1,
).solution

print(solution.extra)
```

### Other

<a id="task-perimeterx"></a>

#### PerimeterX

[PerimeterX API reference](https://docs.ezxlabs.com/docs/captcha/api/perimeterx)

```python
solution = client.solve_perimeter_x("PX_your_app_id").solution

print("_px3   =", solution.px3)
print("_pxvid =", solution.pxvid)
```

<a id="task-incapsulataskproxyless"></a>

#### IncapsulaTaskProxyless

[Incapsula API reference](https://docs.ezxlabs.com/docs/captcha/api/incapsula)

```python
solution = client.sync_solve_incapsula_task_proxyless(
    script,
    "https://example.com/sensor.js",
    "https://example.com",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    accept_language="zh-CN,zh;q=0.9",
).solution

print("reese84 =", solution.data)
```

<a id="task-tlstask"></a>

#### TlsTask

[TLS forwarding API reference](https://docs.ezxlabs.com/docs/captcha/api/tls-forward)

This type does not solve a captcha. It sends one HTTP request through the worker's TLS fingerprint and brings the upstream response back untouched:

```python
from ezcapsolver import TlsHttpMethod

solution = client.sync_solve_tls_task(
    "chrome",
    "http://user:pass@127.0.0.1:8080",
    "https://example.com/api",
    method=TlsHttpMethod.GET,
).solution

print(f"HTTP {solution.status}, {len(solution.body)} bytes of body")
```

### Task objects

The `solve_*` shortcuts take fields directly, so a call site that needs exactly one task type does not have to import its class. When the task object is built elsewhere, or has to be passed between functions, use `solve(task)`:

```python
from ezcapsolver import ReCaptchaV2Task

task = ReCaptchaV2Task(
    website_url="https://example.com",
    website_key="6Lc_your_site_key",
)
solved = client.solve(task)
```

Both forms share the same validation, errors and return types — the shortcuts are thin wrappers, and their names line up with the other language SDKs. Variants within a family (high-score, enterprise) are subclasses overriding only `task_type`, so field definitions are never repeated.

### Result models

Result models have named fields, so reading a result never means writing `solution["gRecaptchaResponse"]`. Each model also carries an `extra` map that catches fields the service adds later:

```python
solved.solution.token  # a modelled field
solved.solution.extra  # fields this release does not model
solved.raw  # the raw JSON the worker returned
```

A field the worker omits does not break decoding. At the transport level, "the response had no `solution` field" stays distinguishable from "`solution` was JSON `null`":

```python
from ezcapsolver import MISSING

result = client.get_result(task_id)
if result.solution is MISSING:
    ...  # the task has not finished
```

When decoding genuinely fails, `SolutionDecodeError.raw` carries the original value out — which is exactly what a diagnosis needs.

### Pass-through fields

Every shortcut ends in `**extra`, and unmodelled keywords are flattened into the task JSON. Parameters the service adds later work without an SDK upgrade:

```python
solved = client.solve_cloudflare_turnstile_task(url, key, proxy=proxy, someNewField=1)
```

Task objects use an `extra` map for the same effect. The reserved `type` field, and every field the model defines, always stay under the SDK's control:

```python
from ezcapsolver import HCaptchaTask

task = HCaptchaTask(
    website_url="https://example.com",
    website_key="site-key",
    lang="en-US",
    invisible=False,
    # A parameter this release does not model, or one the service ships later.
    # Naming a modelled field here instead would be dropped.
    extra={"futureFlag": True},
)
```

> ⚠️ `**extra` also means a misspelled keyword is forwarded to the worker rather than rejected.

Task results carry an `extra` map too, handing back fields present in the response but absent from the model:

```python
solution = client.solve_cloudflare_5s_task(url, proxy).solution

if "aFieldAddedLater" in solution.extra:
    print(solution.extra["aFieldAddedLater"])
```

### Custom task types

Task types are an **open set**. Pass the type name as a string and the parameters as any mapping that serialises to a JSON object, keyed by wire names:

```python
solved = client.solve_raw(
    "BrandNewTaskType",
    {"websiteURL": "https://example.com", "anyFutureParam": 42},
)
print(solved.solution)  # the raw JSON

# The synchronous-endpoint counterpart
solved = client.sync_solve_raw("BrandNewSyncType", {"input": "..."})
```

Use this when the service ships a new captcha type the SDK has not caught up with yet.

### Low-level workflow

`solve()` is the one-step form of "create, then poll". Take the wait apart when you need to own it — to persist the task ID and fetch the result after a process restart, for instance:

```python
task_id = client.create_task(ReCaptchaV2Task(website_url=url, website_key=key))
...
result = client.get_result(task_id)
if result.is_ready:
    print(result.solution)
```

## ⚙️ Configuration

```python
from ezcapsolver import EzCapSolverClient, PollingConfig

client = EzCapSolverClient(
    "your-client-key",
    timeout=30.0,
    sync_timeout=240.0,
    polling=PollingConfig(interval=3.0, max_attempts=50),
    app_id=42,
    proxy="http://127.0.0.1:8080",
    user_agent="my-app/1.0",
)
```

| Setting | Default | Scope |
| --- | :---: | --- |
| `timeout` | 30 s | Request timeout for the asynchronous endpoint |
| `sync_timeout` | 240 s | Request timeout for the synchronous endpoint, clearing the service's 180 s worker deadline |
| `polling` | 3 s × 50 | Result queries, capped at 150 s per task |
| `proxy` | none | **The SDK's own egress**, unrelated to the `proxy` inside task parameters |
| `async_base_url` | `https://api.ez-captcha.com` | Asynchronous tasks and balance queries |
| `sync_base_url` | `https://sync.ez-captcha.com` | Synchronous tasks; the service splits the two deployments |

Pass a `ClientConfig` to build the configuration once and reuse it; pass `http_client` to reuse a connection pool you already have.

> Passing an `httpx` client with its own `base_url` does **not** redirect the SDK — it always builds absolute URLs, and `httpx` applies `base_url` only to relative ones. Set `async_base_url` / `sync_base_url` instead.

### Creating and waiting separately

`solve()` does both. Split them when you want to hold on to the id — which is what makes a `PollingExhaustedError` recoverable, since the task keeps running:

```python
task_id = client.create_task(task)
try:
    result = client.wait_for_result(task_id)
except PollingExhaustedError:
    # Already billed; the service holds the result for five minutes after
    # creation, so wait for it again rather than paying twice.
    result = client.wait_for_result(task_id, polling=PollingConfig(interval=5, max_attempts=20))
```

`polling=` is accepted by `solve()`, `solve_raw()` and `wait_for_result()` alike: task types differ widely in how long they take, so one client-wide budget does not fit all of them. `create_sync_task()` is the synchronous counterpart of `create_task()`, returning the undecoded `TaskResult`.

## ⚠️ Errors

Every exception the SDK raises inherits from `EzCaptchaError`, so catching that one base class covers all of them.

| Exception | Raised when |
| --- | --- |
| `ApiError` | An EZCaptchaSolver service error, carrying the error details |
| `TransportError` | The network connection failed or timed out |
| `PollingExhaustedError` | The polling attempts ran out and the task is still unfinished |
| `WaitInterruptedError` | The task was created and billed, but the wait broke off; carries `task_id` so the result can still be fetched |
| `SolutionDecodeError` | The task result shape changed and the SDK has not caught up, so decoding failed. |
| `UnexpectedResponseError` | The response violates the API contract, including a ready result with no solution |
| `EzCaptchaError` | Base class, and raised directly when the configuration is invalid or the key is missing |

Whichever failure it is, one question answers whether a **billed** task is still recoverable:

```python
from ezcapsolver import task_id_of

if task_id := task_id_of(exc):
    # The task is on the service; its result is held for five minutes after
    # creation. Waiting again is free — creating a second task is billed again.
    solved = client.wait_for_result(task_id)
```

`None` means nothing was billed, so there is nothing to recover.

```python
from ezcapsolver import ApiError, EzCaptchaError, PollingExhaustedError, SolutionDecodeError

try:
    solved = client.solve(task)
except ApiError as exc:
    # The code, description and HTTP status are all there; a field validation
    # failure also lists the per-field reasons in exc.errors.
    if exc.is_authentication_error():
        ...  # stop: the service counts these per key and bans after thirty in a minute
    elif exc.is_terminal():
        ...  # fix the request; resending it changes nothing
    elif exc.is_rate_limited():
        ...  # throttled: both codes clear on their own, so ask again later
    print(exc.error_code, exc.error_description, exc.http_status)
except PollingExhaustedError as exc:
    # The polling budget ran out. The task may still be running, and this call
    # has already been billed — hand the id to wait_for_result() rather than
    # paying twice. The service holds the result for five minutes.
    print("unfinished:", exc.task_id)
except SolutionDecodeError as exc:
    # The worker returned a shape this release does not model.
    print("unexpected shape:", exc.raw)
except EzCaptchaError as exc:
    print(exc)
```

**A throttled poll is the one thing `wait_for_result()` retries.** `ERROR_REQUEST_LIMIT` and `ERROR_REQUEST_BANNED` refuse the *query*, not the task: the service turns the request away before it ever looks the task up, so the task is still queued and still billed. The loop spends the attempt and polls again rather than discarding a result that was about to arrive. Every other `ApiError` is the poll's answer and ends the wait. Note that `is_rate_limited()` is narrower than `not is_terminal()`, which is also true of every unrecognised code — including the worker codes that report a task that genuinely failed.

## 📝 Logging

The SDK logs through the standard `logging` module under the `ezcapsolver` logger, with only a `NullHandler` attached — handlers and levels are entirely the host application's decision.

| Level | Events |
| :---: | --- |
| `INFO` | Task created, task solved, balance queried |
| `DEBUG` | The request lifecycle and every polling attempt |
| `TRACE` | One line per request and per response, carrying the truncated body |

`TRACE` (`ezcapsolver.TRACE`, value 5) sits one step below `DEBUG`: a DataDome `html_b64` or an Akamai `script_base64` runs to megabytes, and mixing those into `DEBUG` would make the level unusable for watching the task lifecycle.

Bodies are rendered with `clientKey` and `proxy` replaced by `[REDACTED]` at **any nesting depth**; with `TRACE` off the body is never rendered at all, so the default level costs nothing.

Scope the level to this logger — a global `DEBUG` drowns the SDK's output in `httpx`'s own:

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("ezcapsolver").setLevel(logging.DEBUG)
```

## 🧵 Concurrency

A client's state is read-only after construction and the underlying `httpx` pool is shareable, so **one instance serves a whole process**. Creating a client per task only wastes connections.

```python
async with AsyncEzCapSolverClient() as client:
    results = await asyncio.gather(
        *(client.solve_recaptcha_v2_task_proxyless(u, k) for u, k in sites),
        return_exceptions=True,
    )
```

The blocking client is equally safe to share across threads.

## 🧪 Runnable Examples

[`examples/`](https://github.com/EZXLabs/ezcapsolver-py/tree/main/examples) holds one runnable file per task type, named after the wire task type, plus five about the SDK itself. The full list is in the [example index](https://github.com/EZXLabs/ezcapsolver-py/blob/main/examples/README.md).

```bash
export EZCAPTCHA_API_KEY=your-client-key

# These two use the vendors' own demo pages and run as they are.
python examples/recaptcha_v2/recaptcha_v2_task_proxyless.py
python examples/hcaptcha/hcaptcha.py

# The rest need a key and page data captured from the target site, for instance:
python examples/cloudflare/cloud_flare_turnstile_task.py
python examples/akamai/akamai_web_task_proxyless.py

# About the SDK itself rather than a task type
python examples/async_client_task.py        # every client setting, one by one
python examples/blocking_client_task.py     # the same, blocking
python examples/concurrency.py              # one client, many coroutines
python examples/raw_usage.py                # manual polling, unknown task types
python examples/logging_and_errors.py       # error paths and redacted logs
```

Examples that need a proxy read `EZCAPTCHA_PROXY`; none of them hard-code credentials.

> Every run creates a real task and is billed, whether or not the worker succeeds.

## 🛠️ Development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-groups

uv run ruff format --check . && uv run ruff check .
uv run mypy ezcapsolver examples
uv run pytest -q

uvx typos                              # spell check
uv run --with pip-audit pip-audit      # dependency audit
```

Optional: install the git hook so every commit runs the same checks.

```bash
uv tool install pre-commit && pre-commit install
```

Conventions and the release process are in [CONTRIBUTING.md](https://github.com/EZXLabs/ezcapsolver-py/blob/main/CONTRIBUTING.md).

## 📄 License

Licensed under the [Apache License 2.0](https://github.com/EZXLabs/ezcapsolver-py/blob/main/LICENSE).
