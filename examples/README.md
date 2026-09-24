# Examples

One file per task type, one directory per vendor. Filenames come from the wire
task type, so they line up with the
[Rust SDK](https://github.com/EZXLabs/ezcapsolver-rs/tree/main/examples)
file for file. The handful that are about the SDK itself rather than a task
type sit at the top level; `fixtures/` holds the sample images the
classification examples read.

English · [简体中文](README.zh-CN.md)

## Running them

```bash
export EZCAPTCHA_API_KEY=your-client-key
export EZCAPTCHA_PROXY=http://user:pass@host:port   # only where noted

python examples/recaptcha_v2/recaptcha_v2_task_proxyless.py
```

Every example builds its client with no key argument, so it is read from
`EZCAPTCHA_API_KEY`.

A few run exactly as written — `recaptcha_v2_task_proxyless.py`, `hcaptcha.py`
and both `*_client_task.py` files point at the vendors' own demo pages. The
rest carry placeholder site keys and page data that you replace with values
scraped from the site you are working against.

## reCAPTCHA v2

| Example | Task type | |
| --- | --- | --- |
| [`recaptcha_v2_task_proxyless.py`](recaptcha_v2/recaptcha_v2_task_proxyless.py) | `ReCaptchaV2TaskProxyless` | runs as written |
| [`recaptcha_v2_task_proxyless_s9.py`](recaptcha_v2/recaptcha_v2_task_proxyless_s9.py) | `ReCaptchaV2TaskProxylessS9` | score ≥ 0.9 |
| [`recaptcha_v2_s_task_proxyless.py`](recaptcha_v2/recaptcha_v2_s_task_proxyless.py) | `ReCaptchaV2STaskProxyless` | carries the `s` parameter |
| [`recaptcha_v2_enterprise_task_proxyless.py`](recaptcha_v2/recaptcha_v2_enterprise_task_proxyless.py) | `ReCaptchaV2EnterpriseTaskProxyless` | |
| [`recaptcha_v2_s_enterprise_task_proxyless.py`](recaptcha_v2/recaptcha_v2_s_enterprise_task_proxyless.py) | `ReCaptchaV2SEnterpriseTaskProxyless` | |
| [`recaptcha_v2_classification.py`](recaptcha_v2/recaptcha_v2_classification.py) | `ReCaptchaV2Classification` | image grid, `match` dispatch |

## reCAPTCHA v3

| Example | Task type | |
| --- | --- | --- |
| [`recaptcha_v3_task_proxyless.py`](recaptcha_v3/recaptcha_v3_task_proxyless.py) | `ReCaptchaV3TaskProxyless` | |
| [`recaptcha_v3_task_proxyless_s9.py`](recaptcha_v3/recaptcha_v3_task_proxyless_s9.py) | `ReCaptchaV3TaskProxylessS9` | score ≥ 0.9 |
| [`recaptcha_v3_enterprise_task_proxyless.py`](recaptcha_v3/recaptcha_v3_enterprise_task_proxyless.py) | `ReCaptchaV3EnterpriseTaskProxyless` | |
| [`recaptcha_v3_enterprise_task_proxyless_s9.py`](recaptcha_v3/recaptcha_v3_enterprise_task_proxyless_s9.py) | `ReCaptchaV3EnterpriseTaskProxylessS9` | |

## FunCaptcha / Arkose Labs

| Example | Task type | |
| --- | --- | --- |
| [`funcaptcha_task_proxyless.py`](funcaptcha/funcaptcha_task_proxyless.py) | `FuncaptchaTaskProxyless` | |
| [`funcaptcha_classification.py`](funcaptcha/funcaptcha_classification.py) | `FunCaptchaClassification` | raw solution |

## hCaptcha

| Example | Task type | |
| --- | --- | --- |
| [`hcaptcha.py`](hcaptcha/hcaptcha.py) | `HCaptcha` | runs as written |
| [`hcaptcha_classification.py`](hcaptcha/hcaptcha_classification.py) | `HCaptchaClassification` | raw solution |

## Cloudflare

| Example | Task type | |
| --- | --- | --- |
| [`cloud_flare_5s_task.py`](cloudflare/cloud_flare_5s_task.py) | `CloudFlare5STask` | needs a proxy; replays the state |
| [`cloud_flare_turnstile_task.py`](cloudflare/cloud_flare_turnstile_task.py) | `CloudFlareTurnstileTask` | |

## Akamai

| Example | Task type | |
| --- | --- | --- |
| [`akamai_web_task_proxyless.py`](akamai/akamai_web_task_proxyless.py) | `AkamaiWEBTaskProxyless` | multi-round handshake |
| [`akamai_sbsd_task_proxyless.py`](akamai/akamai_sbsd_task_proxyless.py) | `AkamaiSBSDTaskProxyless` | |

## DataDome

| Example | Task type | |
| --- | --- | --- |
| [`datadome_task_proxyless.py`](datadome/datadome_task_proxyless.py) | `DataDomeTaskProxyless` | two-step challenge |
| [`datadome_tags_task_proxyless.py`](datadome/datadome_tags_task_proxyless.py) | `DataDomeTagsTaskProxyless` | |

## Other protection systems

| Example | Task type | |
| --- | --- | --- |
| [`perimeter_x.py`](perimeterx/perimeter_x.py) | `PerimeterX` | Press & Hold |
| [`incapsula_task_proxyless.py`](incapsula/incapsula_task_proxyless.py) | `IncapsulaTaskProxyless` | Reese84 sensor |
| [`tls_task.py`](tls_forward/tls_task.py) | `TlsTask` | TLS-fingerprinted forwarding |

## Usage patterns

These are about the SDK rather than a task type.

| Example | What it shows |
| --- | --- |
| [`async_client_task.py`](async_client_task.py) | every client constructor setting, spelled out |
| [`blocking_client_task.py`](blocking_client_task.py) | the same, synchronously |
| [`concurrency.py`](concurrency.py) | one client serving many coroutines |
| [`raw_usage.py`](raw_usage.py) | manual `create_task` / `get_result` polling, and `solve_raw` for unknown task types |
| [`logging_and_errors.py`](logging_and_errors.py) | SDK logging, and every error type it raises |
