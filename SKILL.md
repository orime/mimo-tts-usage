---
name: mimo-tts
description: 小米 MiMo TTS 语音合成。当用户需要文字转语音、生成 wav/mp3、语音合成、克隆音色、设计音色、用 MiMo 唱歌/说话，或提到 MIMO_API_KEY、mimo-v2.5-tts、MiMo TTS 时使用。首次使用时先引导用户配置 API Key（用户可直接在对话里把 Key 发给 AI 写入环境变量，或按步骤自行配置）。
---

# MiMo TTS 语音合成

调用小米 MiMo TTS API 为用户生成语音。**不是** OpenAI 的 `/v1/audio/speech`，走 `POST /v1/chat/completions`。

## 第 0 步：每次使用前先检查配置

运行本技能目录下的检查脚本：

```bash
python3 scripts/check_mimo.py            # 只检查 Key 是否配置
python3 scripts/check_mimo.py --test     # 检查 + 发一次真实合成请求
```

（脚本路径相对本 SKILL.md 所在目录；若环境不便执行脚本，见下面的「手动检查」。）

手动检查：

```bash
# macOS / Linux
[ -n "$MIMO_API_KEY" ] && echo OK || echo MISSING
```

```powershell
# Windows PowerShell
if ($env:MIMO_API_KEY) { "OK" } else { "MISSING" }
```

- **OK** → 直接进入「API 速查」开始干活。
- **MISSING** → 走第 1 步引导，配置完成并测试通过后再干活。

## 第 1 步：首次使用 — 引导用户配置 API Key

检测到 Key 缺失时，**先向用户说明情况并给出三个选项**，不要擅自申请或编造 Key：

> 未检测到 API Key（环境变量 `MIMO_API_KEY`）。你可以：
> **A.** 直接把 Key 发在对话里，我来帮你写入本机配置；
> **B.** 我给你逐步命令，你自己在终端里配；
> **C.** 还没有 Key — 去官方文档申请（免费，TTS 目前限时免费）：
> <https://mimo.mi.com/docs/zh-CN/quick-start/summary/first-api-call>

### 选项 A：用户把 Key 发在对话里，由 AI 写入

1. 让用户发 Key（`sk-` 开头为按量付费 Key，推荐；`tp-`/`ttp-` 为 Token Plan 订阅 Key）。
2. 按用户操作系统写入：
   - **macOS / Linux**：追加到 `~/.env`，并确保权限 600：

     ```bash
     printf 'export MIMO_API_KEY="%s"\n' "$KEY" >> ~/.env
     chmod 600 ~/.env
     ```

     若用户的 shell 配置文件（`~/.zshrc` / `~/.bashrc`）里已有 `source ~/.env`，不用重复加；没有则加一行 `source ~/.env`，然后 `source ~/.zshrc`。
   - **Windows**：写入用户级环境变量（对所有新终端生效）：

     ```powershell
     [Environment]::SetEnvironmentVariable("MIMO_API_KEY", "sk-xxx", "User")
     $env:MIMO_API_KEY = "sk-xxx"   # 当前会话立即生效
     ```

3. 写入后运行 `python3 scripts/check_mimo.py --test` 验证，向用户报告结果。
4. **收到用户 Key 后，绝不在回复、日志、提交内容里回显完整 Key**，只显示前 6 位。

### 选项 B：用户自己配

把上面 macOS/Linux 或 Windows 对应命令原样给用户，让他自己粘贴执行，再让他回来跑 `check_mimo.py --test`。

### 选项 C：用户还没有 Key

引导去官方「首次调用」指南注册并创建按量付费 `sk-` Key，创建后回到选项 A/B。

### Key 与 Base URL 对应关系

| Key 类型 | Base URL |
| --- | --- |
| 按量付费 `sk-`（推荐自建应用） | `https://api.xiaomimimo.com/v1` |
| Token Plan `tp-`/`ttp-`（仅编程工具场景） | `https://token-plan-cn.xiaomimimo.com/v1` |

### 安全红线

- Key 只存环境变量 / `~/.env`，**永远不写进源码、文档、提交、聊天记录截图**。
- 展示 Key 只允许前 6 位前缀。
- 轮换 Key 只改 `~/.env` 或系统环境变量，不改技能文件。

---

## API 速查

- **端点**：`POST {BaseURL}/chat/completions`
- **鉴权**：`api-key: $MIMO_API_KEY` 或 `Authorization: Bearer $MIMO_API_KEY`（等价）
- **正文放哪**：要朗读的文字放 `messages` 里 `role=assistant` 的 `content`；风格指令放 `role=user`（不会被念出来）。放错角色 = 念不出来。
- **音频参数**：顶层 `audio` 对象，`{"format":"wav","voice":"冰糖"}`
- **返回**：`choices[0].message.audio.data` 是 base64 音频，解码写文件即可
- **计费**：TTS 三模型目前**限时免费**（不扣余额/Credit），上线前请再核对定价页 <https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go>

### 三个模型

| Model ID | 用途 | voice 字段 | 唱歌 |
| --- | --- | --- | --- |
| `mimo-v2.5-tts` | 预置音色合成（最常用） | 可省略，默认 `mimo_default` | ✅ |
| `mimo-v2.5-tts-voicedesign` | 文字描述设计新音色 | ❌ 不支持，描述放 user | ❌ |
| `mimo-v2.5-tts-voiceclone` | 音频样本克隆 | ✅ base64 样本（data URI，≤10MB，mp3/wav） | ❌ |

### 请求字段

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `model` | 是 | 见上表 |
| `messages` | 是 | 角色规则见上 |
| `audio.format` | 否 | `wav`(默认) / `mp3` / `pcm` / `pcm16`；流式必须 `pcm16` |
| `audio.voice` | 视模型 | 预置音色 ID，或 voiceclone 样本 |
| `audio.optimize_text_preview` | 否 | 仅 voicedesign |
| `stream` | 否 | 默认 false；true 为 SSE 流式 |

### 预置音色（仅 `mimo-v2.5-tts`）

| 音色 | Voice ID | 语言 | 性别 |
| --- | --- | --- | --- |
| MiMo-默认 | `mimo_default` | 因集群而异（中国集群默认冰糖） | - |
| 冰糖 | `冰糖` | 中文 | 女 |
| 茉莉 | `茉莉` | 中文 | 女 |
| 苏打 | `苏打` | 中文 | 男 |
| 白桦 | `白桦` | 中文 | 男 |
| Mia | `Mia` | 英文 | 女 |
| Chloe | `Chloe` | 英文 | 女 |
| Milo | `Milo` | 英文 | 男 |
| Dean | `Dean` | 英文 | 男 |

中文正文建议配中文音色（冰糖/茉莉/苏打/白桦）。

### 响应结构（非流式）

```json
{"choices":[{"message":{"role":"assistant","content":"",
  "audio":{"data":"<base64>","transcript":null}}}],
 "usage":{"prompt_tokens":213,"completion_tokens":97,"total_tokens":310}}
```

---

## 代码示例

### 预置音色（Python，OpenAI SDK）

```python
import os, base64
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MIMO_API_KEY"],
    base_url="https://api.xiaomimimo.com/v1",
)

completion = client.chat.completions.create(
    model="mimo-v2.5-tts",
    messages=[
        {"role": "user", "content": "用轻快活泼的语调，语速稍快"},
        {"role": "assistant", "content": "你好！今天也要加油鸭！"},
    ],
    audio={"format": "wav", "voice": "冰糖"},
)

audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
open("out.wav", "wb").write(audio_bytes)
```

### curl（macOS/Linux；Windows 用等价 PowerShell Invoke-RestMethod）

```bash
curl -sS https://api.xiaomimimo.com/v1/chat/completions \
  -H "api-key: $MIMO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model":"mimo-v2.5-tts",
    "messages":[
      {"role":"user","content":"用平静自然的语调"},
      {"role":"assistant","content":"(磁性)夜已经深了，城市还在呼吸。"}
    ],
    "audio":{"format":"wav","voice":"Chloe"}
  }'
```

### 音色设计（voicedesign）

`user` 消息 = 音色描述（1–4 句，覆盖性别年龄+质感+语气+语速），不传 `voice`：

```python
completion = client.chat.completions.create(
    model="mimo-v2.5-tts-voicedesign",
    messages=[
        {"role": "user", "content": "一位年迈的老先生，带北方口音，语速缓慢沉稳，嗓音略带沙哑沧桑。"},
        {"role": "assistant", "content": "孩子，坐好，听爷爷给你讲一段往事。"},
    ],
    audio={"format": "wav", "optimize_text_preview": False},
)
```

### 音色克隆（voiceclone）

样本：mp3/wav，base64 后 ≤10MB，必须带 `data:audio/mpeg;base64,` 或 `data:audio/wav;base64,` 前缀：

```python
import base64
b64 = base64.b64encode(open("voice.mp3", "rb").read()).decode()
completion = client.chat.completions.create(
    model="mimo-v2.5-tts-voiceclone",
    messages=[
        {"role": "user", "content": "用温柔的语气"},
        {"role": "assistant", "content": "这是我用你的音色说的第一句话。"},
    ],
    audio={"format": "wav", "voice": f"data:audio/mpeg;base64,{b64}"},
)
```

### 流式（pcm16 → wav）

`stream=true` 必须配 `audio.format=pcm16`（24kHz、16bit、单声道），拼接 `choices[0].delta.audio.data` 各段：

```python
import base64, numpy as np, soundfile as sf
completion = client.chat.completions.create(
    model="mimo-v2.5-tts",
    messages=[
        {"role": "user", "content": "用播音腔，语速中等"},
        {"role": "assistant", "content": "欢迎收听今天的科技早报。"},
    ],
    audio={"format": "pcm16", "voice": "白桦"},
    stream=True,
)
chunks = []
for chunk in completion:
    if not chunk.choices:
        continue
    audio = getattr(chunk.choices[0].delta, "audio", None)
    if audio:
        chunks.append(np.frombuffer(base64.b64decode(audio["data"]), dtype=np.int16))
if chunks:
    sf.write("stream.wav", np.concatenate(chunks), samplerate=24000)
```

---

## 风格控制

**自然语言控制** → 放 `user` 消息（整段基调，不被念出），例如「温柔治愈系女声，语速缓慢，适合睡前电台。」

**音频标签** → 放 `assistant` 正文里，开头整体风格，正文可插细粒度标签：

```
(紧张，深呼吸）呼……冷静，冷静。不就是一个面试吗……（语速加快，碎碎念）自我介绍已经背了五十遍了。
```

- 风格类型：基础/复合情绪、语调（温柔/高冷/活泼…）、音色定位（磁性/清亮/沙哑…）、人设（夹子音/御姐音…）、方言（东北/四川/河南/粤语）、角色扮演（孙悟空/林黛玉）
- 细粒度标签：吸气/叹气/笑/抽泣/颤抖/破音/鼻音… 半角或全角括号均可
- **唱歌**：`(唱歌)` 开头，仅 `mimo-v2.5-tts`，例如 `(唱歌)原谅我这一生不羁放纵爱自由`

---

## 错误排查

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `/v1/audio/speech` 返回 404 | 不是 OpenAI Audio API | 改用 `/v1/chat/completions` |
| 401 Invalid API Key | Key 无效/复制不全/用错 Base URL | 核对环境变量；`sk-` 配 `api.xiaomimimo.com`，`tp-` 配 `token-plan-cn...` |
| `check_mimo.py` 报 MISSING | 只写没 source / PowerShell 未持久化 / 未开新终端 | 重 source 或重开终端，见第 1 步 |
| 有 JSON 但 `audio` 为 null | 没传 `audio` 对象 | 加 `audio` |
| 没念出预期文字 | 正文写在了 user 消息 | 正文移到 assistant |
| 流式拼不出完整音频 | format 不是 pcm16 | `stream=true` 强制 `pcm16` |
| voiceclone 失败 | 缺 data URI 前缀或超 10MB | 加前缀、压缩样本 |
| voicedesign 传了 voice | 不支持 voice | 删掉，描述放 user |

---

## 完整参考

更完整的字段说明、请求/响应原文、能力边界与维护说明见本仓库 `docs/mimo-tts-usage.md`。官方文档：

- 使用指南：<https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5>
- API 参考：<https://mimo.mi.com/docs/zh-CN/api/audio/tts>
