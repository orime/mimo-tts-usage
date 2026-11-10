# Xiaomi MiMo TTS 语音合成使用说明（本地缓存版）

> 本文件是官方文档的本地完整摘要，供 AI/开发者直接加载使用，无需每次重新抓网页。  
> 官方来源：
>
> - 使用指南：<https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5>
> - API 参考：<https://mimo.mi.com/docs/zh-CN/api/audio/tts>
> - 定价：<https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go>
> - 首次调用：<https://mimo.mi.com/docs/zh-CN/quick-start/summary/first-api-call>
>
> 本机实测：2026-11-01，使用按量付费 `sk-` Key + `api.xiaomimimo.com`，HTTP 200，成功生成合法 WAV。  
> 文档不存放明文 API Key；密钥统一从环境变量 `MIMO_API_KEY` 读取。

---

## 0. 给 AI 助手的 30 秒速查

1. **不是** OpenAI 的 `/v1/audio/speech`！走 **`POST /v1/chat/completions`**。
2. 要念的文字放在 `messages` 里 `role=assistant` 的 `content`；风格指令放在 `role=user`。
3. 音频参数放在顶层 `audio` 对象：`{"format":"wav","voice":"冰糖"}`。
4. 返回 JSON 中 `choices[0].message.audio.data` 是 **base64 音频**，解码后写文件即可。
5. 当前 **TTS 全系列限时免费**，不扣余额、不扣 Token Plan Credit。
6. API Key 从环境变量 `MIMO_API_KEY` 读取（本机约定放 `~/.env`，其他机器见 [§2.4](#24-新机器从零配置macos--windows-通用流程)），Base URL 用 `https://api.xiaomimimo.com/v1`。

```bash
# 最小可用 curl（需先 source ~/.env）
source ~/.env
curl -sS https://api.xiaomimimo.com/v1/chat/completions \
  -H "api-key: $MIMO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mimo-v2.5-tts",
    "messages": [
      {"role":"user","content":"用平静自然的语调"},
      {"role":"assistant","content":"你好，这是 MiMo 语音合成测试。"}
    ],
    "audio": {"format":"wav","voice":"冰糖"}
  }'
```

鉴权头两种写法等价：`api-key: $MIMO_API_KEY` 或 `Authorization: Bearer $MIMO_API_KEY`。

---

## 1. 模型列表（3 个）

| Model ID                    | 用途         | 音色来源                | 支持唱歌 | 备注                                |
| --------------------------- | ---------- | ------------------- | ---- | --------------------------------- |
| `mimo-v2.5-tts`             | 预置精品音色合成   | 预置音色 ID             | ✅    | 最常用；`voice` 可省略，默认 `mimo_default` |
| `mimo-v2.5-tts-voicedesign` | 用文字描述设计新音色 | `user` 消息即音色描述      | ❌    | 不支持 `voice` 字段；`user` 必填          |
| `mimo-v2.5-tts-voiceclone`  | 用音频样本克隆音色  | `voice` 传 base64 样本 | ❌    | 样本 ≤10MB，仅 mp3/wav                |

---

## 2. 端点、鉴权与 Key 管理

### 2.1 Base URL（按用途区分）

| 使用方式              | OpenAI 兼容 Base URL                        | Key 格式                   |
| ----------------- | ----------------------------------------- | ------------------------ |
| **按量付费（推荐给自建应用）** | `https://api.xiaomimimo.com/v1`           | `sk-xxxxx`               |
| Token Plan 订阅     | `https://token-plan-cn.xiaomimimo.com/v1` | `tp-xxxxx` / `ttp-xxxxx` |
| 批量推理              | `https://batch-api-cn.xiaomimimo.com/v1`  | `sk-xxxxx`               |

TTS 实际请求路径：

```
POST {BaseURL}/chat/completions
```

### 2.2 本机密钥存放（已配置）

全局环境文件：`~/.env`（权限 600）

```bash
# ~/.env 中的条目
export MIMO_API_KEY="sk-..."
```

加载方式：

```bash
source ~/.env
echo "${MIMO_API_KEY:0:8}..."   # 只看前缀，不要打印完整 key
```

约定：

- 代码/文档/脚本一律读 `os.environ["MIMO_API_KEY"]` 或 `$MIMO_API_KEY`，**不要把 key 写进源码或公开仓库**。
- 轮换 key 时只改 `~/.env`，不用改文档。

### 2.3 两种 Key 的差异与选择

|    | 按量付费 `sk-`                 | Token Plan `tp-`            |
| -- | -------------------------- | --------------------------- |
| 计费 | 按 token/时长扣余额；**TTS 限时免费** | 订阅 Credit；**TTS 不扣 Credit** |
| 合规 | 可用于任意应用                    | 官方限定编程工具场景，嵌 App 后端有封禁风险    |
| 适合 | 自建 TTS 服务、脚本、产品集成          | OpenCode/Claude Code 等编程场景  |

**自建项目请用按量付费 `sk-` Key。**

### 2.4 新机器从零配置（macOS / Windows 通用流程）

换电脑、换人使用时，按下面四步走。

**第 1 步：没有 Key？去官方申请一个（免费）**

1. 打开官方「首次调用」指南：<https://mimo.mi.com/docs/zh-CN/quick-start/summary/first-api-call>，按页面指引注册/登录小米开放平台。
2. 在控制台创建 API Key，选择**按量付费**类型，得到 `sk-xxxxx`。
3. TTS 目前限时免费，申请和调用都不需要先充值。
4. 复制 Key 后立刻保存到本地环境变量（下一步），**不要**贴进聊天记录、截图或任何会提交到仓库的文件。

**第 2 步：把 Key 写进环境变量**

macOS / Linux（写进 shell 配置文件，一次配置永久生效）：

```bash
# zsh（macOS 默认）用 ~/.zshrc；bash 用 ~/.bashrc
echo 'export MIMO_API_KEY="sk-你的key"' >> ~/.zshrc
chmod 600 ~/.zshrc        # 限制只有本人可读
source ~/.zshrc
```

Windows（PowerShell，写入用户级环境变量，对所有终端生效）：

```powershell
# 当前会话立即生效
$env:MIMO_API_KEY = "sk-你的key"
# 同时持久化到用户环境变量（新开的终端/程序才能读到）
[Environment]::SetEnvironmentVariable("MIMO_API_KEY", "sk-你的key", "User")
```

Windows 也可以走图形界面：`Win + R` → 输入 `sysdm.cpl` → 「高级」→「环境变量」→ 用户变量里新建 `MIMO_API_KEY`，值填 `sk-你的key`。

**第 3 步：检测是否配置成功**

```bash
# macOS / Linux
[ -n "$MIMO_API_KEY" ] && echo "env OK: ${MIMO_API_KEY:0:6}..." || echo "FAIL: MIMO_API_KEY 未设置"
```

```powershell
# Windows PowerShell
if ($env:MIMO_API_KEY) { "env OK: " + $env:MIMO_API_KEY.Substring(0,6) + "..." } else { "FAIL: MIMO_API_KEY 未设置" }
```

只打印前 6 位前缀即可，**不要**打印完整 Key。

**第 4 步：跑一次真实调用**

直接执行下方 [§10 本机连通性测试](#10-本机连通性测试记录) 的复现命令（把 `source ~/.env` 换成第 2 步的配置方式），看到 `OK 1xxxxx b'RIFF'` 即整条链路通了。

常见失败原因速查：

| 提示 | 原因 | 处理 |
| --- | --- | --- |
| `FAIL: MIMO_API_KEY 未设置` | 只写没 `source`，或 PowerShell 只设了 `$env:` 没做持久化，或新开窗口没重开 | 重新 `source ~/.zshrc`，或重开终端 |
| `401 Invalid API Key` | Key 复制不全 / 用错 Base URL | 核对前缀 `sk-` 配 `api.xiaomimimo.com` |
| 连接超时 | 网络不通或需代理 | 检查本机网络；企业网络需放行 `api.xiaomimimo.com` |

---

## 3. 请求体完整说明

### 3.1 字段

| 字段                            | 类型      | 必填  | 说明                                                     |
| ----------------------------- | ------- | --- | ------------------------------------------------------ |
| `model`                       | string  | 是   | `mimo-v2.5-tts` / `...-voicedesign` / `...-voiceclone` |
| `messages`                    | array   | 是   | 对话消息；见下方角色规则                                           |
| `audio`                       | object  | 建议  | 音频输出配置                                                 |
| `audio.format`                | string  | 否   | `wav`(默认) / `mp3` / `pcm` / `pcm16`；流式必须用 `pcm16`      |
| `audio.voice`                 | string  | 视模型 | 预置音色 ID，或 voiceclone 的样本 base64                        |
| `audio.optimize_text_preview` | boolean | 否   | 仅 voicedesign；true 时可省略 assistant 消息                   |
| `stream`                      | boolean | 否   | 默认 false；true 时 SSE 流式                                 |

### 3.2 messages 角色规则（关键！）

- **要朗读的正文** → 必须放在 `role: "assistant"` 的 `content`。  
  放到 `user` 里不会被念出来。
- **风格/语气/情绪指令** → 放在 `role: "user"` 的 `content`（自然语言控制）。  
  这段文字本身**不会**出现在合成语音里。
- `voicedesign`：`user` **必填**（内容就是音色设计描述）；若 `optimize_text_preview=true` 可省略 `assistant`。
- `voiceclone`：`user` 可为空字符串或风格指令；`voice` 必填为样本。

### 3.3 响应结构（非流式）

```json
{
  "id": "...",
  "object": "chat.completion",
  "model": "mimo-v2.5-tts",
  "choices": [{
    "index": 0,
    "finish_reason": "stop",
    "message": {
      "role": "assistant",
      "content": "",
      "audio": {
        "id": "...",
        "data": "<base64 音频>",
        "expires_at": null,
        "transcript": null
      }
    }
  }],
  "usage": {
    "prompt_tokens": 213,
    "completion_tokens": 97,
    "total_tokens": 310
  }
}
```

- `audio.data`：base64，按请求的 `audio.format` 解码即得 wav/mp3/pcm。
- `audio.transcript`：当前恒为 null（不返回识别文本）。
- `usage` 有 token 统计，但 TTS 限时免费，不产生费用。

### 3.4 流式响应

- `stream: true` + `audio.format: "pcm16"`（官方要求）。
- 每个 chunk：`choices[0].delta.audio.data` 为一段 base64 PCM16。
- PCM 参数：24kHz、16bit、单声道。
- 拼接所有 PCM → 写 WAV 头或直接交给 soundfile/ffmpeg。
- `mimo-v2.5-tts` 已支持低延迟实时流式；voicedesign/voiceclone 的流式目前是兼容模式（推理完成后一次性吐出）。

---

## 4. 预置音色（仅 `mimo-v2.5-tts`）

| 音色名     | Voice ID       | 语言              | 性别 |
| ------- | -------------- | --------------- | -- |
| MiMo-默认 | `mimo_default` | 因集群而异（中国集群默认冰糖） | -  |
| 冰糖      | `冰糖`           | 中文              | 女  |
| 茉莉      | `茉莉`           | 中文              | 女  |
| 苏打      | `苏打`           | 中文              | 男  |
| 白桦      | `白桦`           | 中文              | 男  |
| Mia     | `Mia`          | 英文              | 女  |
| Chloe   | `Chloe`        | 英文              | 女  |
| Milo    | `Milo`         | 英文              | 男  |
| Dean    | `Dean`         | 英文              | 男  |

用法：`"audio": {"voice": "冰糖"}`。

---

## 5. 风格控制（两种方式）

### 5.1 自然语言控制 → 放 `user` 消息

适合整段基调、导演式描述。

示例：

- 「用轻快上扬的语调向领导报喜，语速稍快，带着压抑不住的激动。」
- 「温柔治愈系女声，语速缓慢，适合睡前电台。」

导演模式三要素（可选进阶）：

- **角色**：身份、性格、气质、说话习惯
- **场景**：时间地点事件、对方反应、情绪位置
- **指导**：语速、气息、停顿、重音、共鸣、音色质感

### 5.2 音频标签控制 → 放 `assistant` 正文里

开头加整体风格标签，正文任意位置可插细粒度标签。

**风格标签格式**（半角/全角括号或方括号均可）：

```
(风格1 风格2)待合成内容
```

常用风格类型：

| 类型   | 示例                                           |
| ---- | -------------------------------------------- |
| 基础情绪 | 开心/悲伤/愤怒/恐惧/惊讶/兴奋/委屈/平静/冷漠                   |
| 复合情绪 | 怅然/欣慰/无奈/愧疚/释然/嫉妒/厌倦/忐忑/动情                   |
| 整体语调 | 温柔/高冷/活泼/严肃/慵懒/俏皮/深沉/干练/凌厉                   |
| 音色定位 | 磁性/醇厚/清亮/空灵/稚嫩/苍老/甜美/沙哑/醇雅                   |
| 人设腔调 | 夹子音/御姐音/正太音/大叔音/台湾腔                          |
| 方言   | 东北话/四川话/河南话/粤语                               |
| 角色扮演 | 孙悟空/林黛玉                                      |
| 唱歌   | 唱歌 / sing / singing（仅 `mimo-v2.5-tts`，必须放开头） |

细粒度 `[音频标签]` / 括号标签示例：

| 类型   | 示例                          |
| ---- | --------------------------- |
| 语速节奏 | 吸气/深呼吸/叹气/长叹一口气/喘息/屏息       |
| 情绪状态 | 紧张/害怕/激动/疲惫/委屈/撒娇/心虚/震惊/不耐烦 |
| 语音特征 | 颤抖/声音颤抖/变调/破音/鼻音/气声/沙哑      |
| 哭笑表达 | 笑/轻笑/大笑/冷笑/抽泣/呜咽/哽咽/嚎啕大哭    |

组合示例（正文内）：

```
（紧张，深呼吸）呼……冷静，冷静。不就是一个面试吗……（语速加快，碎碎念）自我介绍已经背了五十遍了，应该没问题的。
```

唱歌示例：

```
(唱歌)原谅我这一生不羁放纵爱自由，也会怕有一天会跌倒。
```

---

## 6. 三种使用模式完整示例

### 6.1 预置音色（`mimo-v2.5-tts`）

**Python（OpenAI SDK）**

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
with open("out.wav", "wb") as f:
    f.write(audio_bytes)
```

**curl**

```bash
source ~/.env
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

### 6.2 音色设计（`mimo-v2.5-tts-voicedesign`）

`user` 消息 = 音色描述；不支持 `voice` 字段。

```python
completion = client.chat.completions.create(
    model="mimo-v2.5-tts-voicedesign",
    messages=[
        {
            "role": "user",
            "content": (
                "一位年迈的老先生，说带北方口音的普通话，"
                "语速缓慢而沉稳，嗓音略带沙哑和沧桑感。"
            ),
        },
        {"role": "assistant", "content": "孩子，坐好，听爷爷给你讲一段往事。"},
    ],
    audio={"format": "wav", "optimize_text_preview": False},
)
```

写音色描述的要点：

- 1–4 句即可，覆盖性别年龄 + 音色质感 + 语气 + 语速。
- 避免矛盾特征（如「稚嫩童声 + CEO气场」）。
- 避免混响/EQ 等后期词；避免「普通的/正常的」等模糊词。
- 中英文均可。
- `optimize_text_preview=true` 时：可自动润色/生成播报文本，省略 assistant。

### 6.3 音色克隆（`mimo-v2.5-tts-voiceclone`）

样本要求：

- 格式：`mp3` 或 `wav`
- Base64 后 ≤ 10MB
- 必须带前缀：`data:audio/mpeg;base64,<b64>` 或 `data:audio/wav;base64,<b64>`

```python
import base64, os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MIMO_API_KEY"],
    base_url="https://api.xiaomimimo.com/v1",
)

with open("voice.mp3", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

completion = client.chat.completions.create(
    model="mimo-v2.5-tts-voiceclone",
    messages=[
        {"role": "user", "content": "用温柔的语气"},
        {"role": "assistant", "content": "这是我用你的音色说的第一句话。"},
    ],
    audio={
        "format": "wav",
        "voice": f"data:audio/mpeg;base64,{b64}",
    },
)
```

---

## 7. 流式调用示例（pcm16 → wav）

```python
import os, base64, numpy as np, soundfile as sf
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MIMO_API_KEY"],
    base_url="https://api.xiaomimimo.com/v1",
)

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
        pcm = base64.b64decode(audio["data"])
        chunks.append(np.frombuffer(pcm, dtype=np.int16))

if chunks:
    sf.write("stream.wav", np.concatenate(chunks), samplerate=24000)
```

---

## 8. 计费（截至 2026-11 核实）

| 项目                  | 状态                                        |
| ------------------- | ----------------------------------------- |
| TTS 三模型             | **限时免费**                                  |
| 按量付费账户              | 不扣余额                                      |
| Token Plan          | 不扣 Credit                                 |
| ASR `mimo-v2.5-asr` | **收费** ¥0.5/小时（Token Plan 30M Credits/小时） |
| 查用量                 | 控制台「账单明细/用量」                              |

注意：限时免费随时可能结束，上线产品前请再看一眼定价页。

---

## 9. 常见错误与排查

| 现象                           | 原因                         | 处理                                                                  |
| ---------------------------- | -------------------------- | ------------------------------------------------------------------- |
| 请求 `/v1/audio/speech` 返回 404 | 路径不存在（不是 OpenAI Audio API） | 改用 `/v1/chat/completions`                                           |
| 401 Invalid API Key          | Key 无效/过期/复制不全/用错 Base URL | 核对 `~/.env`；`sk-` 配 `api.xiaomimimo.com`，`tp-` 配 `token-plan-cn...` |
| 有 JSON 但 `audio` 为 null      | 未传 `audio` 对象，或正文放错角色      | 加 `audio`；正文放 assistant                                             |
| 没念出预期文字                      | 文字写在了 user 消息              | 正文移到 assistant                                                      |
| 流式拼不出完整音频                    | format 不是 pcm16            | `stream=true` 时强制 `pcm16`，24k 单声道拼接                                 |
| voiceclone 传样本失败             | 缺 data URI 前缀或超 10MB       | 加 `data:audio/mpeg;base64,`；压缩样本                                    |
| voicedesign 传了 voice         | 该模型不支持 voice               | 删掉 voice，把描述放 user                                                  |

---

## 10. 本机连通性测试记录

- 日期：2026-11-01
- Key 类型：按量付费 `sk-...`（存于 `~/.env` 的 `MIMO_API_KEY`）
- Endpoint：`POST https://api.xiaomimimo.com/v1/chat/completions`
- 模型：`mimo-v2.5-tts`，voice=`冰糖`，format=`wav`
- 结果：HTTP **200**，返回 base64，解码为合法 RIFF/WAVE，约 **122924 字节**
- 验证脚本逻辑：取 `choices[0].message.audio.data` → base64decode → 检查文件头 `RIFF....WAVE`

复现命令：

```bash
source ~/.env
python3 - <<'PY'
import os, json, base64, urllib.request
req = urllib.request.Request(
    "https://api.xiaomimimo.com/v1/chat/completions",
    data=json.dumps({
        "model": "mimo-v2.5-tts",
        "messages": [
            {"role": "user", "content": "用轻快活泼的语调"},
            {"role": "assistant", "content": "你好，这是小米语音合成测试。"},
        ],
        "audio": {"format": "wav", "voice": "冰糖"},
    }).encode(),
    headers={
        "api-key": os.environ["MIMO_API_KEY"],
        "Content-Type": "application/json",
    },
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    body = json.load(r)
wav = base64.b64decode(body["choices"][0]["message"]["audio"]["data"])
open("/tmp/mimo_tts_test.wav", "wb").write(wav)
print("OK", len(wav), wav[:4])
PY
```

---

## 11. 能力边界速记

**能做：**
- 中英预置音色、方言（东北/四川/河南/粤语）、角色扮演、唱歌（仅基础 TTS）
- 情绪/语速/停顿/气声等细粒度控制
- 文字设计音色、音频克隆音色
- 非流式 wav/mp3 与流式 pcm16

**不能/注意：**
- 不走 `/v1/audio/speech`
- voicedesign/voiceclone 不支持唱歌、不互相混用音色能力
- 克隆样本格式严格（mp3/wav + data URI + ≤10MB）
- 中文正文建议配合中文 voice（冰糖/茉莉/苏打/白桦）效果更稳

---

## 12. 维护说明

- 本文件在仓库中的位置：`docs/mimo-tts-usage.md`（仓库 `github.com/orime/mimo-tts-usage`）；Skill 本体见仓库根目录 `SKILL.md`
- 密钥：只存在各机器自己的环境变量 `MIMO_API_KEY`，任何情况下都不要提交进仓库
- 官方若改价/改接口，优先核对：定价页 + 本页 API 参考
- 相关姊妹能力：ASR 见官方 `/docs/zh-CN/quick-start/usage-guide/audio/Speech-Recognition`（收费，不在本文范围）
