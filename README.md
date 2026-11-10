# mimo-tts Skill

把小米 MiMo TTS 语音合成封装成一个 Agent Skill：AI 读了 `SKILL.md` 就会用 TTS（文字转语音 / 音色设计 / 音色克隆 / 唱歌），首次使用时会**主动引导用户配置 API Key**——用户可以直接把 Key 发在对话里让 AI 写入，也可以按 AI 给的命令自己配，或者按链接去申请一个。

- Skill 主体：[`SKILL.md`](./SKILL.md)
- 完整 API 参考文档：[`docs/mimo-tts-usage.md`](./docs/mimo-tts-usage.md)
- 配置检查 / 连通性测试脚本：[`scripts/check_mimo.py`](./scripts/check_mimo.py)

## 安装（给用户看，也给 AI 看）

如果你是用户，直接对你的 AI 助手说：

> 帮我安装这个 Skill：<https://github.com/orime/mimo-tts-usage>

AI 会克隆/下载本仓库，然后**问你要装到哪**。装到哪由你决定：

| 装在哪 | 路径 | 生效范围 |
| --- | --- | --- |
| 全局（所有项目可用，推荐） | `~/.agents/skills/mimo-tts/` | 你这台机器上的所有会话 |
| Claude Code 全局 | `~/.claude/skills/mimo-tts/` | Claude Code 所有项目 |
| 某个项目内（只这个项目用） | `<项目>/.claude/skills/mimo-tts/` 或 `<项目>/.agents/skills/mimo-tts/` | 仅该项目 |

AI 安装时应做的事：

1. 把本仓库内容（至少 `SKILL.md` + `scripts/` + `docs/`）复制到你指定的目录，目录名为 `mimo-tts`。
2. 安装完按 `SKILL.md` 第 0 步跑一次 `python3 scripts/check_mimo.py`，告诉你 Key 是否已配置。
3. 若未配置，按 `SKILL.md` 第 1 步引导你配置（三种方式任选）。

卸载 = 删除对应目录，无其他残留。

## 首次使用：API Key 怎么来

- **没有 Key**：去官方申请（免费）：<https://mimo.mi.com/docs/zh-CN/quick-start/summary/first-api-call>，选按量付费 `sk-` Key。
- **已有 Key**：装完 Skill 后 AI 会检测环境变量 `MIMO_API_KEY`；缺失时它会问你——把 Key 发给它，它写入本机；或它给你命令你自己配。
- **Key 放哪**：
  - macOS/Linux：`~/.env`（权限 600）里的 `export MIMO_API_KEY="sk-..."`
  - Windows：用户级环境变量 `MIMO_API_KEY`
- 当前 TTS 三模型**限时免费**，不扣费。

## 安全说明

- 本仓库不含任何 API Key，只教 AI 怎么安全地把 Key 存进你本机的环境变量。
- Key 不要写进代码、文档或提交到任何仓库。
- `check_mimo.py` 只打印 Key 前 6 位。

## 免责

MiMo TTS 为小米官方能力，接口与定价以其官方文档为准：
<https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5>
