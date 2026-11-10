#!/usr/bin/env python3
"""MiMo TTS 配置检查与连通性测试。

用法:
  python3 check_mimo.py          # 只检查 MIMO_API_KEY 是否配置（只显示前 6 位）
  python3 check_mimo.py --test   # 检查 + 发一次真实合成请求并校验 WAV

跨平台: macOS / Linux / Windows（仅用标准库）。
"""

import argparse
import base64
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ENV_NAME = "MIMO_API_KEY"
BASE_URL = "https://api.xiaomimimo.com/v1"


def find_key():
    """返回 (key, 来源描述)，找不到返回 (None, None)。"""
    key = os.environ.get(ENV_NAME)
    if key:
        return key, "环境变量"
    env_file = pathlib.Path.home() / ".env"
    if env_file.is_file():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("export "):
                    line = line[7:]
                if line.startswith(ENV_NAME + "="):
                    value = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if value:
                        shown = str(env_file).replace(str(pathlib.Path.home()), "~")
                        return value, shown
        except OSError as exc:
            print(f"WARN: 无法读取 {env_file}: {exc}", file=sys.stderr)
    return None, None


def live_test(key):
    payload = json.dumps({
        "model": "mimo-v2.5-tts",
        "messages": [
            {"role": "user", "content": "用平静自然的语调"},
            {"role": "assistant", "content": "你好，这是 MiMo 语音合成连通性测试。"},
        ],
        "audio": {"format": "wav", "voice": "冰糖"},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=payload,
        headers={
            "api-key": key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.load(resp)
    except urllib.error.HTTPError as exc:
        print(f"FAIL: HTTP {exc.code} {exc.reason}")
        if exc.code in (401, 403):
            print("  -> Key 无效或 Base URL 不匹配（sk- 应配 api.xiaomimimo.com）")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: 请求异常 {exc}")
        print("  -> 检查网络，或企业网络需放行 api.xiaomimimo.com")
        return False

    try:
        b64 = body["choices"][0]["message"]["audio"]["data"]
    except (KeyError, IndexError, TypeError):
        print(f"FAIL: 响应里没有 audio.data: {json.dumps(body)[:300]}")
        return False
    wav = base64.b64decode(b64)
    if wav[:4] != b"RIFF" or wav[8:12] != b"WAVE":
        print(f"FAIL: 返回内容不是合法 WAV（头部 {wav[:4]!r}）")
        return False
    out = pathlib.Path(os.environ.get("TMPDIR", "/tmp")) / "mimo_tts_check.wav"
    out.write_bytes(wav)
    print(f"OK: HTTP 200，合法 WAV，{len(wav)} 字节 -> {out}")
    return True


def main():
    parser = argparse.ArgumentParser(description="MiMo TTS 配置检查")
    parser.add_argument("--test", action="store_true", help="额外发一次真实合成请求")
    args = parser.parse_args()

    key, source = find_key()
    if not key:
        print("MISSING: 未找到 MIMO_API_KEY")
        print("  -> 请按 SKILL.md 第 1 步配置：")
        print("     - 直接把 Key 发给 AI 由其写入，或")
        print("     - macOS/Linux: echo 'export MIMO_API_KEY=\"sk-...\"' >> ~/.env && chmod 600 ~/.env")
        print("     - Windows: [Environment]::SetEnvironmentVariable(\"MIMO_API_KEY\",\"sk-...\",\"User\")")
        print("  -> 还没有 Key: https://mimo.mi.com/docs/zh-CN/quick-start/summary/first-api-call")
        return 1

    print(f"OK: 已配置 MIMO_API_KEY（来源: {source}，前缀 {key[:6]}...）")
    if not args.test:
        return 0
    print("TEST: 正在调用 mimo-v2.5-tts ...")
    return 0 if live_test(key) else 1


if __name__ == "__main__":
    sys.exit(main())
