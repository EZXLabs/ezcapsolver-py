# 示例

一个文件对应一种任务类型，一个目录对应一个厂商。文件名取自线格式的任务类型名，与
[Rust SDK](https://github.com/EZXLabs/ezcapsolver-rs/tree/main/examples)
逐个对应。讲 SDK 本身而非任务类型的那几个放在顶层，`fixtures/` 是分类示例用到的
样例图片。

[English](README.md) · 简体中文

## 运行方式

```bash
export EZCAPTCHA_API_KEY=your-client-key
export EZCAPTCHA_PROXY=http://user:pass@host:port   # 仅标注需要的示例

python examples/recaptcha_v2/recaptcha_v2_task_proxyless.py
```

所有示例构造客户端时都不传 key，由它自己从 `EZCAPTCHA_API_KEY` 读取。

有几个可以直接跑通——`recaptcha_v2_task_proxyless.py`、`hcaptcha.py` 以及两个
`*_client_task.py` 用的是厂商自己的 demo 页面。其余的站点 key 和页面数据是占位值，
替换成你目标站点上抓到的实际值即可。

## reCAPTCHA v2

| 示例 | 任务类型 | |
| --- | --- | --- |
| [`recaptcha_v2_task_proxyless.py`](recaptcha_v2/recaptcha_v2_task_proxyless.py) | `ReCaptchaV2TaskProxyless` | 可直接运行 |
| [`recaptcha_v2_task_proxyless_s9.py`](recaptcha_v2/recaptcha_v2_task_proxyless_s9.py) | `ReCaptchaV2TaskProxylessS9` | 评分 ≥ 0.9 |
| [`recaptcha_v2_s_task_proxyless.py`](recaptcha_v2/recaptcha_v2_s_task_proxyless.py) | `ReCaptchaV2STaskProxyless` | 携带 `s` 参数 |
| [`recaptcha_v2_enterprise_task_proxyless.py`](recaptcha_v2/recaptcha_v2_enterprise_task_proxyless.py) | `ReCaptchaV2EnterpriseTaskProxyless` | |
| [`recaptcha_v2_s_enterprise_task_proxyless.py`](recaptcha_v2/recaptcha_v2_s_enterprise_task_proxyless.py) | `ReCaptchaV2SEnterpriseTaskProxyless` | |
| [`recaptcha_v2_classification.py`](recaptcha_v2/recaptcha_v2_classification.py) | `ReCaptchaV2Classification` | 图像宫格，`match` 分派 |

## reCAPTCHA v3

| 示例 | 任务类型 | |
| --- | --- | --- |
| [`recaptcha_v3_task_proxyless.py`](recaptcha_v3/recaptcha_v3_task_proxyless.py) | `ReCaptchaV3TaskProxyless` | |
| [`recaptcha_v3_task_proxyless_s9.py`](recaptcha_v3/recaptcha_v3_task_proxyless_s9.py) | `ReCaptchaV3TaskProxylessS9` | 评分 ≥ 0.9 |
| [`recaptcha_v3_enterprise_task_proxyless.py`](recaptcha_v3/recaptcha_v3_enterprise_task_proxyless.py) | `ReCaptchaV3EnterpriseTaskProxyless` | |
| [`recaptcha_v3_enterprise_task_proxyless_s9.py`](recaptcha_v3/recaptcha_v3_enterprise_task_proxyless_s9.py) | `ReCaptchaV3EnterpriseTaskProxylessS9` | |

## FunCaptcha / Arkose Labs

| 示例 | 任务类型 | |
| --- | --- | --- |
| [`funcaptcha_task_proxyless.py`](funcaptcha/funcaptcha_task_proxyless.py) | `FuncaptchaTaskProxyless` | |
| [`funcaptcha_classification.py`](funcaptcha/funcaptcha_classification.py) | `FunCaptchaClassification` | 返回原始结果 |

## hCaptcha

| 示例 | 任务类型 | |
| --- | --- | --- |
| [`hcaptcha.py`](hcaptcha/hcaptcha.py) | `HCaptcha` | 可直接运行 |
| [`hcaptcha_classification.py`](hcaptcha/hcaptcha_classification.py) | `HCaptchaClassification` | 返回原始结果 |

## Cloudflare

| 示例 | 任务类型 | |
| --- | --- | --- |
| [`cloud_flare_5s_task.py`](cloudflare/cloud_flare_5s_task.py) | `CloudFlare5STask` | 必须带代理；含状态重放 |
| [`cloud_flare_turnstile_task.py`](cloudflare/cloud_flare_turnstile_task.py) | `CloudFlareTurnstileTask` | |

## Akamai

| 示例 | 任务类型 | |
| --- | --- | --- |
| [`akamai_web_task_proxyless.py`](akamai/akamai_web_task_proxyless.py) | `AkamaiWEBTaskProxyless` | 多轮握手 |
| [`akamai_sbsd_task_proxyless.py`](akamai/akamai_sbsd_task_proxyless.py) | `AkamaiSBSDTaskProxyless` | |

## DataDome

| 示例 | 任务类型 | |
| --- | --- | --- |
| [`datadome_task_proxyless.py`](datadome/datadome_task_proxyless.py) | `DataDomeTaskProxyless` | 两步挑战 |
| [`datadome_tags_task_proxyless.py`](datadome/datadome_tags_task_proxyless.py) | `DataDomeTagsTaskProxyless` | |

## 其他防护系统

| 示例 | 任务类型 | |
| --- | --- | --- |
| [`perimeter_x.py`](perimeterx/perimeter_x.py) | `PerimeterX` | Press & Hold |
| [`incapsula_task_proxyless.py`](incapsula/incapsula_task_proxyless.py) | `IncapsulaTaskProxyless` | Reese84 传感器 |
| [`tls_task.py`](tls_forward/tls_task.py) | `TlsTask` | 指定 TLS 指纹转发请求 |

## 用法示例

这几个讲的是 SDK 本身，与具体任务类型无关。

| 示例 | 演示内容 |
| --- | --- |
| [`async_client_task.py`](async_client_task.py) | 客户端构造参数逐项说明 |
| [`blocking_client_task.py`](blocking_client_task.py) | 同上，同步版本 |
| [`concurrency.py`](concurrency.py) | 一个客户端服务多个协程 |
| [`raw_usage.py`](raw_usage.py) | 手动 `create_task` / `get_result` 轮询，以及用 `solve_raw` 调用未知任务类型 |
| [`logging_and_errors.py`](logging_and_errors.py) | SDK 日志，以及它会抛出的每种错误 |
