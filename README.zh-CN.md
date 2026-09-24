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
    <a href="https://ezxlabs.com"><img alt="EZXLabs 官网" src="https://img.shields.io/badge/website-ezxlabs.com-FFDB29?logoColor=black"></a>
  </p>
  <p>
    <a href="https://ezxlabs.com">🌐 官网</a> &nbsp;·&nbsp;
    <a href="https://docs.ezxlabs.com/zh/docs/captcha/api">📚 EZCaptchaSolver API 文档</a> &nbsp;·&nbsp;
    <a href="https://github.com/EZXLabs/ezcapsolver-py/tree/main/examples">🧪 示例</a> &nbsp;·&nbsp;
    <a href="#-支持的验证码类型">🧩 验证码类型</a>
  </p>
  <p><a href="https://github.com/EZXLabs/ezcapsolver-py/blob/main/README.md">English</a> &nbsp;·&nbsp; <b>简体中文</b></p>
</div>

---

EZCaptchaSolver Python SDK 是 [EZXLabs](https://ezxlabs.com) 维护的开源 Python 客户端，用于接入其 CAPTCHA 识别任务 API。它为下列受支持的任务类型提供类型化请求、异步和阻塞客户端；该包还包含不用于解验证码的 TLS 转发任务。了解 SDK 产品系列请查看 [EZCaptchaSolver SDK 产品页](https://ezxlabs.com/zh/products/sdk)，查看 HTTP 请求与响应字段请访问 [EZCaptchaSolver API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api)，Python 调用代码请以[本仓库示例](https://github.com/EZXLabs/ezcapsolver-py/blob/main/examples/README.zh-CN.md)为准。

## 🧩 支持的验证码类型

验证码任务类型分为同步和异步两种：

- 同步：创建任务后阻塞请求，直到任务完成取得任务结果。
- 异步：创建任务成功后返回任务ID，后续可通过任务ID轮询尝试获取任务结果。适合验证码处理时长较久的任务类型。

同一种验证码任务类型能够同时支持同步和异步两种，几乎所有类型都会支持同步方式。然后有部分类型只会支持异步方式。

### reCAPTCHA v2

| 任务类型 | 支持方式 | 示例 | 描述 |
| :-: | :---: | :-: | --- |
| `ReCaptchaV2TaskProxyless` | all | [示例](#task-recaptchav2taskproxyless) | reCAPTCHA v2 解决方案 |
| `ReCaptchaV2TaskProxylessS9` | all | [示例](#task-recaptchav2taskproxylesss9) | reCAPTCHA v2，返回分值 ≥ 0.9 的 token |
| `ReCaptchaV2STaskProxyless` | all | [示例](#task-recaptchav2staskproxyless) | reCAPTCHA v2 携带挑战绑定的 `s` 参数 |
| `ReCaptchaV2EnterpriseTaskProxyless` | all | [示例](#task-recaptchav2enterprisetaskproxyless) | reCAPTCHA v2 企业版 |
| `ReCaptchaV2SEnterpriseTaskProxyless` | all | [示例](#task-recaptchav2senterprisetaskproxyless) | reCAPTCHA v2 企业版，并携带 `s` 参数 |
| `ReCaptchaV2Classification` | sync | [示例](#task-recaptchav2classification) | reCAPTCHA v2 图片识别 |

### reCAPTCHA v3

| 任务类型 | 支持方式 | 示例 | 描述 |
| :-: | :---: | :-: | --- |
| `ReCaptchaV3TaskProxyless` | all | [示例](#task-recaptchav3taskproxyless) | reCAPTCHA v3 解决方案 |
| `ReCaptchaV3TaskProxylessS9` | all | [示例](#task-recaptchav3taskproxylesss9) | reCAPTCHA v3，返回分值 ≥ 0.9 的 token |
| `ReCaptchaV3EnterpriseTaskProxyless` | all | [示例](#task-recaptchav3enterprisetaskproxyless) | reCAPTCHA v3 企业版 |
| `ReCaptchaV3EnterpriseTaskProxylessS9` | all | [示例](#task-recaptchav3enterprisetaskproxylesss9) | reCAPTCHA v3 企业版 返回分值 ≥ 0.9 的 token |

### FunCaptcha / Arkose Labs

| 任务类型 | 支持方式 | 示例 | 描述 |
| :-: | :---: | :-: | --- |
| `FuncaptchaTaskProxyless` | async | [示例](#task-funcaptchataskproxyless) | FunCaptcha / Arkose Labs 解决方案 |
| `FunCaptchaClassification` | sync | [示例](#task-funcaptchaclassification) | FunCaptcha 图片识别 |

### hCaptcha

| 任务类型 | 支持方式 | 示例 | 描述 |
| :-: | :---: | :-: | --- |
| `HCaptcha` | async | [示例](#task-hcaptcha) | hCaptcha 解决方案 |
| `HCaptchaClassification` | sync | [示例](#task-hcaptchaclassification) | hCaptcha 图片识别，支持单图与多图 |

### Cloudflare

| 任务类型 | 支持方式 | 示例 | 描述 |
| :-: | :---: | :-: | --- |
| `CloudFlare5STask` | async | [示例](#task-cloudflare5stask) | CF 5 秒盾，**必须**传 `proxy` |
| `CloudFlareTurnstileTask` | async | [示例](#task-cloudflareturnstiletask) | Turnstile，返回 token |

### Akamai

| 任务类型 | 支持方式 | 示例 | 描述 |
| :-: | :---: | :-: | --- |
| `AkamaiWEBTaskProxyless` | sync | [示例](#task-akamaiwebtaskproxyless) | Akamai Web 解决方案 |
| `AkamaiSBSDTaskProxyless` | sync | [示例](#task-akamaisbsdtaskproxyless) | Akamai SBSD 解决方案 |

> Akamai Web 是多轮流程：把本轮返回的 `encodedata` 作为下一轮的 `encode_data` 传入。这两个拼写在线格式上就是不同的，SDK 原样保留服务端的定义，不做「修正」。

### DataDome

| 任务类型 | 支持方式 | 示例 | 描述 |
| :-: | :---: | :-: | --- |
| `DataDomeTaskProxyless` | sync | [示例](#task-datadometaskproxyless) | 拦截后的挑战，分两步，靠 `step` 区分 |
| `DataDomeTagsTaskProxyless` | sync | [示例](#task-datadometagstaskproxyless) | 正常浏览路径上报指纹 |

### 其他

| 任务类型 | 支持方式 | 示例 | 描述 |
| :-: | :---: | :-: | --- |
| `PerimeterX` | async | [示例](#task-perimeterx) | PerimeterX 放行 cookie |
| `IncapsulaTaskProxyless` | sync | [示例](#task-incapsulataskproxyless) | Incapsula Reese84 载荷 |
| `TlsTask` | sync | [示例](#task-tlstask) | HTTP TLS 转发请求，返回上游响应 |

## 📦 安装

```bash
pip install ezcapsolver-py
```

需要 Python 3.12+。运行时依赖只有 [`httpx`](https://www.python-httpx.org/) 一个；两个客户端都建在它之上，因此行为不会漂移。

> 分发名是 `ezcapsolver-py`，导入名是 `ezcapsolver`。

## 🚀 快速开始

未显式传入密钥时，客户端会自动从环境变量 `EZCAPTCHA_API_KEY` 读取。

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

异步客户端的方法名完全一致，加 `await` 即可：

```python
from ezcapsolver import AsyncEzCapSolverClient

async with AsyncEzCapSolverClient() as client:
    solved = await client.solve_recaptcha_v2_task_proxyless(
        "https://example.com",
        "6Lc_your_site_key",
    )

    print("token =", solved.solution.token)
```

## 📖 使用说明

下面每种类型一段。片段都假设已经有一个 `client`，并省略了 `with` 块，以突出调用本身。

### 同步/异步

**每个任务类型都有两个方法**，参数与返回类型完全相同，区别只是走哪个端点：

```python
# 创建 + 轮询
solved = client.solve_recaptcha_v2_task_proxyless(url, site_key)
assert solved.task_id is not None

# 同步端点，一次请求拿结果
solved = client.sync_solve_recaptcha_v2_task_proxyless(url, site_key)
assert solved.task_id is None  # 同步端点不分配任务 ID
```

传任务对象的写法同理，`solve()` 恒轮询，`sync_solve()` 恒走同步端点：

```python
from ezcapsolver import ReCaptchaV2Task

task = ReCaptchaV2Task(website_url=url, website_key=site_key)

solved = client.solve(task)
solved = client.sync_solve(task)
```

每个任务类上的 `mode` 记录着服务端为该类型标注的执行方式，**仅供参考**——SDK 不读它来决定走哪条路。它的意义在于：走服务端不支持的那条路会被拒（同步侧返回 `ERROR_TASK_TYPE_NOT_ALLOWED`），而这种拒绝发生在**扣费之前**，代价只是一次往返，不是一次任务。

```python
from ezcapsolver import ReCaptchaV2ClassificationTask, TaskMode

ReCaptchaV2ClassificationTask.mode is TaskMode.SYNC  # True
```

### 代理格式

接受 `proxy` 的任务类型有两种格式，取决于任务类型：

| 格式 | 形态 | 适用 |
| --- | --- | --- |
| `NORMAL` | `protocol://username:password@host:port` | 除 FunCaptcha 外全部 |
| `FUN` | `protocol://host:port:username:password` | 仅 `FunCaptchaTask` |

`protocol` 取 `http`、`https` 或 `socks5`。**用户名和密码都必填**——无认证代理会被服务端判为非法
——且 host 不能是内网地址（`127.0.*`、`192.168.*`、`172.16.*`、`10.0.*`）。字段本身可选时留空没问题，
只有「非空但格式不对」才会被拒。

### reCAPTCHA v2

[reCAPTCHA v2 API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/recaptcha-v2)

前五个类型共用 `ReCaptchaV2Task` 与 `ReCaptchaSolution`，只有方法名不同。

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

参数与普通 v2 完全一致，走高分队列，返回分值 ≥ 0.9 的 token。

```python
solved = client.solve_recaptcha_v2_task_proxyless_s9(
    "https://example.com",
    "6Lc_your_site_key",
)

print("token =", solved.solution.token)
```

<a id="task-recaptchav2staskproxyless"></a>

#### ReCaptchaV2STaskProxyless

携带挑战绑定的 `s` 参数。该参数并非强制，不传时行为与普通 v2 一致。

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

企业版。若站点用了 `data-s` 之外的企业参数，作为关键字参数传入即可透传。

```python
solved = client.solve_recaptcha_v2_enterprise_task_proxyless(
    "https://example.com",
    "6Lc_your_site_key",
)

print("token =", solved.solution.token)
```

<a id="task-recaptchav2senterprisetaskproxyless"></a>

#### ReCaptchaV2SEnterpriseTaskProxyless

企业版，并携带 `s` 参数。

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

[reCAPTCHA v2 图片识别 API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/recaptcha-v2-classification)

直接识别图像宫格，返回格子下标而不是 token。

```python
solution = client.sync_solve_recaptcha_v2_classification(
    image_base64,
    "/m/0k4j",
    size=4,  # 1 = 1x1, 3 = 3x3, 4 = 4x4
).solution

if solution.is_multi:
    print("需要点选的格子", solution.objects)
elif solution.is_single:
    print("是否含目标物体:", solution.has_object)
else:
    print("结果类型:", solution.type, "透传字段:", solution.extra)
```

`ReClassificationSolution` 的 JSON 字段 `hasObject` 映射为 `has_object`。未知的 `type` 值原样保留，额外字段进入 `extra`。字段缺失时分别使用空类型、`False` 和空列表；`is_multi`、`is_single` 只判断 `type`。

### reCAPTCHA v3

[reCAPTCHA v3 API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/recaptcha-v3)

四个类型共用 `ReCaptchaV3Task` 与 `ReCaptchaSolution`。`page_action` 要与页面上 `grecaptcha.execute` 传的 `action` 一致，否则站点侧校验会失败。

> ⚠️ `is_invisible` 在 `ReCaptchaV2Task` 上默认 `False`，在 `ReCaptchaV3Task` 上默认 **`True`**，与服务端一致。两个模型的默认值并不相同。

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

[FunCaptcha API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/funcaptcha)

<a id="task-funcaptchataskproxyless"></a>

#### FuncaptchaTaskProxyless

```python
solved = client.solve_funcaptcha_task_proxyless(
    "https://example.com",
    "your-public-key",
)

print("token =", solved.solution.token)
```

> FunCaptcha 是唯一使用 `FUN` 代理格式的类型：`protocol://host:port:username:password`，账号密码在 host 之后而不是之前。

<a id="task-funcaptchaclassification"></a>

#### FunCaptchaClassification

```python
solution = client.sync_solve_funcaptcha_classification(
    image_base64,
    "Pick the animal facing left",
).solution

# 该类型的结果形态尚未确认，worker 返回的字段全部落在 extra 里。
print(solution.extra)
```

### hCaptcha

[hCaptcha API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/hcaptcha)

<a id="task-hcaptcha"></a>

#### HCaptcha

hCaptcha 的 token 字段是 `generated_pass_uuid`，不是 `token`——这是服务端的命名，SDK 原样保留。

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

单图用 `image`，多图用 `images`，全部字段都是可选的——不同的识别模块需要的输入组合不同。

```python
solution = client.sync_solve_hcaptcha_classification(
    images=images,
    question="Please click each image containing a bicycle",
).solution

# 形态同样未确认，全部字段在 extra 里。
print(solution.extra)
```

### Cloudflare

<a id="task-cloudflare5stask"></a>

#### CloudFlare5STask

[Cloudflare 5S API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/cloudflare-5s)

5 秒盾**必须**传 `proxy`，而且返回的不是单个 token，而是要回放到目标站点的 header 与放行 cookie：

```python
solution = client.solve_cloudflare_5s_task(
    "https://example.com",
    "http://user:pass@127.0.0.1:8080",
).solution

for name, value in solution.cookies.items():
    print(f"{name}={value}")
print("TLS 指纹 =", solution.tls_version)
```

把这些请求头和 cookie 重放到受保护站点才是真正通过挑战的动作——结果是一整套浏览器状态，不是一个 token。

<a id="task-cloudflareturnstiletask"></a>

#### CloudFlareTurnstileTask

[Cloudflare Turnstile API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/turnstile)

Turnstile 的 `proxy` 是可选的，返回单个 token。

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

[Akamai Web API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/akamai-web)

Akamai Web 是多轮流程：把本轮返回的 `encodedata` 作为下一轮的 `encode_data` 传回去。两个拼写在线格式上就是不同的，SDK 原样保留服务端的定义。

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

    print(f"第 {index} 轮 payload =", solution.payload)
    encode_data = solution.encodedata
```

<a id="task-akamaisbsdtaskproxyless"></a>

#### AkamaiSBSDTaskProxyless

[Akamai SBSD API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/akamai-sbsd)

单轮任务，六个字段全部必填。

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

DataDome 拦截后的挑战分两步，两步共用同一个方法，靠 `step` 区分；`DataDomeSolution` 里哪些字段有值取决于当前是哪一步：

```python
from ezcapsolver import DataDomeStep

# 第一步：从被拦截页面拿到挑战地址。
solution = client.sync_solve_data_dome_task_proxyless(
    html_b64,
    step=DataDomeStep.ONE,
).solution

print("挑战地址 =", solution.url)

# 第二步换成 DataDomeStep.TWO，结果里带回校验用的 body。
```

<a id="task-datadometagstaskproxyless"></a>

#### DataDomeTagsTaskProxyless

正常浏览路径上报指纹，字段名是 camelCase，与上面的 `DataDomeTask` 不同。

```python
solution = client.sync_solve_data_dome_tags_task_proxyless(
    "your-datadome-key",
    "https://example.com",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    bpc=1,
).solution

print(solution.extra)
```

### 其他

<a id="task-perimeterx"></a>

#### PerimeterX

[PerimeterX API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/perimeterx)

```python
solution = client.solve_perimeter_x("PX_your_app_id").solution

print("_px3   =", solution.px3)
print("_pxvid =", solution.pxvid)
```

<a id="task-incapsulataskproxyless"></a>

#### IncapsulaTaskProxyless

[Incapsula API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/incapsula)

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

[TLS 转发 API 文档](https://docs.ezxlabs.com/zh/docs/captcha/api/tls-forward)

这个类型不解验证码，而是借 worker 的 TLS 指纹发一次 HTTP 请求，把上游响应原样带回来：

```python
from ezcapsolver import TlsHttpMethod

solution = client.sync_solve_tls_task(
    "chrome",
    "http://user:pass@127.0.0.1:8080",
    "https://example.com/api",
    method=TlsHttpMethod.GET,
).solution

print(f"HTTP {solution.status}，响应体 {len(solution.body)} 字节")
```

### 任务对象

`solve_*` 快捷方法直接收字段，调用处只用到一种类型时不必再导入任务类。任务对象在别处构造、或者需要在函数之间传递时，用 `solve(task)`：

```python
from ezcapsolver import ReCaptchaV2Task

task = ReCaptchaV2Task(
    website_url="https://example.com",
    website_key="6Lc_your_site_key",
)
solved = client.solve(task)
```

两种写法的校验、错误与返回类型完全相同——快捷方法只是薄包装，方法名与其它语言 SDK 一致。同族变体（高分版、企业版）是只改 `task_type` 的子类，字段不重复声明。

### 结果模型

结果模型有具名字段，读结果不需要写 `solution["gRecaptchaResponse"]`。每个模型还带一个 `extra` 表，接住服务端后来新增的字段：

```python
solved.solution.token  # 已建模的字段
solved.solution.extra  # 本版本没建模的字段
solved.raw  # worker 返回的原始 JSON
```

worker 少给某个字段不会导致解码失败。在传输层，「响应里没有 `solution` 字段」与「`solution` 的值是 JSON `null`」也是分得开的：

```python
from ezcapsolver import MISSING

result = client.get_result(task_id)
if result.solution is MISSING:
    ...  # 任务还没完成
```

解码真的失败时，`SolutionDecodeError.raw` 会把原始值带出来——那正是排查所需要的东西。

### 额外参数

每个快捷方法末尾都有 `**extra`，未建模的关键字会被平铺进任务 JSON。服务端之后新增的参数不需要升级 SDK 就能用：

```python
solved = client.solve_cloudflare_turnstile_task(url, key, proxy=proxy, someNewField=1)
```

任务对象走 `extra` 表，效果相同。保留字段 `type` 以及模型已定义的字段始终由 SDK 掌控：

```python
from ezcapsolver import HCaptchaTask

task = HCaptchaTask(
    website_url="https://example.com",
    website_key="site-key",
    lang="en-US",
    invisible=False,
    # 本版本未建模的参数，或服务端之后才上线的参数。
    # 这里写已建模字段的名字会被丢弃
    extra={"futureFlag": True},
)
```

> ⚠️ `**extra` 意味着拼错的关键字会被原样发给 worker，而不是被拒绝。

每个任务结果也有一个 `extra` 表，会把模型里不存在、但服务端响应中存在的新字段传递回来：

```python
solution = client.solve_cloudflare_5s_task(url, proxy).solution

if "aFieldAddedLater" in solution.extra:
    print(solution.extra["aFieldAddedLater"])
```

### 定制化任务类型

任务类型是**开放集合**。直接把类型名当字符串传，参数用任意可序列化成 JSON 对象的映射，键名按线格式书写：

```python
solved = client.solve_raw(
    "BrandNewTaskType",
    {"websiteURL": "https://example.com", "anyFutureParam": 42},
)
print(solved.solution)  # 原始 JSON

# 同步端点的对应写法
solved = client.sync_solve_raw("BrandNewSyncType", {"input": "..."})
```

如果官方提供了新的验证码类型，但 SDK 还未同步更新时，可使用此方案临时代替。

### 低层工作流

`solve()` 是「创建 + 轮询」的一步到位写法。想自己掌控等待过程时可以拆开——比如需要把 task ID 持久化、跨进程重启后再取结果：

```python
task_id = client.create_task(ReCaptchaV2Task(website_url=url, website_key=key))
...
result = client.get_result(task_id)
if result.is_ready:
    print(result.solution)
```

## ⚙️ 配置

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

| 配置项 | 默认值 | 作用范围 |
| --- | :---: | --- |
| `timeout` | 30 秒 | 异步端点请求超时 |
| `sync_timeout` | 240 秒 | 同步端点请求超时，比服务端 180 秒的 Worker deadline 留了余量 |
| `polling` | 3 秒 × 50 次 | 结果查询，单任务上限 150 秒 |
| `proxy` | 无 | **SDK 自身出网**使用，与任务参数里的 `proxy` 无关 |
| `async_base_url` | `https://api.ez-captcha.com` | 异步任务与余额查询 |
| `sync_base_url` | `https://sync.ez-captcha.com` | 同步任务；服务端把两套部署拆开了 |

想把配置构造一次反复使用就传 `ClientConfig`；想复用自己已有的连接池就传 `http_client`。

> 传一个自带 `base_url` 的 `httpx` 客户端**不会**改变 SDK 的请求地址——SDK 构造的一律是绝对 URL，而 `httpx` 的 `base_url` 只对相对 URL 生效。要改地址请用 `async_base_url` / `sync_base_url`。

### 创建与等待分开

`solve()` 两件事一起做。想拿着 task_id 就把它们拆开——这正是 `PollingExhaustedError` 可恢复的前提，因为任务还在跑：

```python
task_id = client.create_task(task)
try:
    result = client.wait_for_result(task_id)
except PollingExhaustedError:
    # 已经扣过费了；服务端在创建后保留结果 5 分钟，再等一次比重复付费划算。
    result = client.wait_for_result(task_id, polling=PollingConfig(interval=5, max_attempts=20))
```

`solve()`、`solve_raw()`、`wait_for_result()` 都接受 `polling=`：任务类型之间耗时差别很大，一个客户端级预算套不住所有类型。`create_sync_task()` 是 `create_task()` 的同步端点对应物，返回未解码的 `TaskResult`。

## ⚠️ 错误处理

SDK 抛出的所有异常都继承自 `EzCaptchaError`，捕获这一个基类就能兜底。

| 异常 | 触发场景 |
| --- | --- |
| `ApiError` | EZCaptchaSolver 服务端错误, 包含错误详情内容 |
| `TransportError` | 网络连接失败或超时 |
| `PollingExhaustedError` | 轮询次数用尽，依然未完成 |
| `WaitInterruptedError` | 任务已创建并扣费，但等待中断；带 `task_id`，结果仍可取回 |
| `SolutionDecodeError` | 任务结果结构被调整，sdk未适配导致序列化失败. |
| `UnexpectedResponseError` | 响应违反 API 契约，包括 ready 却没有 solution |
| `EzCaptchaError` | 所有错误的基类；配置非法或缺少密钥时直接抛它 |

不论是哪种失败，判断「有没有一个**已扣费**的任务还能救回来」只需要问一句：

```python
from ezcapsolver import task_id_of

if task_id := task_id_of(exc):
    # 任务在服务端，结果自创建起保留五分钟。再等一次是免费的，
    # 重新创建任务要再扣一次费。
    solved = client.wait_for_result(task_id)
```

返回 `None` 表示没有扣过费，也就没有东西需要救。

```python
from ezcapsolver import ApiError, EzCaptchaError, PollingExhaustedError, SolutionDecodeError

try:
    solved = client.solve(task)
except ApiError as exc:
    # 错误码、描述与 HTTP 状态都在；字段校验失败还会在 exc.errors 里
    # 给出逐字段的原因。
    if exc.is_authentication_error():
        ...  # 停手：服务端按密钥计数，一分钟 30 次即封禁
    elif exc.is_terminal():
        ...  # 改请求；原样重发不会有任何变化
    elif exc.is_rate_limited():
        ...  # 被限流；这两个码都会自行解除，过一会儿再问
    print(exc.error_code, exc.error_description, exc.http_status)
except PollingExhaustedError as exc:
    # 轮询用尽。任务可能还在跑，而这次调用已经扣过费了——把 task_id 交给
    # wait_for_result() 再等，不要重复付费。服务端保留结果 5 分钟。
    print("未完成:", exc.task_id)
except SolutionDecodeError as exc:
    # worker 返回了本版本未建模的形态。
    print("非预期形态:", exc.raw)
except EzCaptchaError as exc:
    print(exc)
```

**`wait_for_result()` 唯一会重试的就是被限流的那次轮询。** `ERROR_REQUEST_LIMIT` 与 `ERROR_REQUEST_BANNED` 拒的是**这次查询**，不是任务：服务端在查任务之前就把请求挡回来了，任务仍在排队、也仍然扣着费。所以轮询循环消耗掉这一次机会后接着问，而不是把一个马上就要拿到的结果丢掉。其余任何 `ApiError` 都是这次轮询的答案，会直接结束等待。注意 `is_rate_limited()` 比 `not is_terminal()` 窄得多——后者对所有不认识的码也为真，其中就包括 worker 报告任务真的失败时用的那些码。

## 📝 日志

SDK 通过标准 `logging` 模块在 `ezcapsolver` logger 下输出，且只挂了 `NullHandler`，handler 与级别完全由宿主应用决定。

| 级别 | 事件 |
| :---: | --- |
| `INFO` | 任务创建、任务完成、余额查询 |
| `DEBUG` | 请求生命周期与每一次轮询 |
| `TRACE` | 每个请求、每个响应各一行，带截断后的报文 |

`TRACE`（`ezcapsolver.TRACE`，值为 5）比 `DEBUG` 低一级：DataDome 的 `html_b64` 与 Akamai 的 `script_base64` 动辄上兆，混进 `DEBUG` 会让这个级别没法用来看任务流程。

报文在渲染时会把**任意嵌套深度**下的 `clientKey` 与 `proxy` 全部替换成 `[REDACTED]`；未开启 `TRACE` 时报文根本不会被渲染，所以默认级别下没有开销。

把级别限定在这个 logger 上——全局 `DEBUG` 会让 SDK 的输出被 `httpx` 自己的日志淹没：

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("ezcapsolver").setLevel(logging.DEBUG)
```

## 🧵 并发

客户端构造后状态只读，底层 `httpx` 连接池本身可共享，因此**一个实例服务整个进程**即可。为每个任务新建客户端只会浪费连接。

```python
async with AsyncEzCapSolverClient() as client:
    results = await asyncio.gather(
        *(client.solve_recaptcha_v2_task_proxyless(u, k) for u, k in sites),
        return_exceptions=True,
    )
```

同步客户端同样可以安全地跨线程共享。

## 🧪 可运行示例

[`examples/`](https://github.com/EZXLabs/ezcapsolver-py/tree/main/examples) 里每种任务类型一个可运行文件，文件名取自线格式的任务类型名；另有五个讲 SDK 本身。完整清单见[示例索引](https://github.com/EZXLabs/ezcapsolver-py/blob/main/examples/README.zh-CN.md)。

```bash
export EZCAPTCHA_API_KEY=your-client-key

# 这两个用的是厂商自己的 demo 页面，可以直接跑通。
python examples/recaptcha_v2/recaptcha_v2_task_proxyless.py
python examples/hcaptcha/hcaptcha.py

# 其余的需要填入从目标站点抓到的 key 与页面数据，例如：
python examples/cloudflare/cloud_flare_turnstile_task.py
python examples/akamai/akamai_web_task_proxyless.py

# 讲 SDK 本身而非某个任务类型
python examples/async_client_task.py        # 客户端构造参数逐项说明
python examples/blocking_client_task.py     # 同上，同步版本
python examples/concurrency.py              # 一个客户端，多个协程
python examples/raw_usage.py                # 手动轮询、未知任务类型
python examples/logging_and_errors.py       # 各类错误与脱敏日志
```

需要代理的示例从 `EZCAPTCHA_PROXY` 读取；示例一律不硬编码凭据。

> 每次运行都会创建真实任务并**计费**，worker 失败也照扣。

## 🛠️ 开发

需要 Python 3.12+ 与 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync --all-groups

uv run ruff format --check . && uv run ruff check .
uv run mypy ezcapsolver examples
uv run pytest -q

uvx typos                              # 拼写检查
uv run --with pip-audit pip-audit      # 依赖安全审计
```

可选：装上 git hook，每次提交自动跑同一套检查。

```bash
uv tool install pre-commit && pre-commit install
```

约定与发布流程见 [CONTRIBUTING.md](https://github.com/EZXLabs/ezcapsolver-py/blob/main/CONTRIBUTING.md)。

## 📄 许可

基于 [Apache License 2.0](https://github.com/EZXLabs/ezcapsolver-py/blob/main/LICENSE) 授权。
