import asyncio
import json
import socket
from pathlib import Path

import aiohttp
from ssl import create_default_context, CERT_NONE

# 读取 efuse.json
data = json.loads(Path("model-bin/raw/efuse.json").read_text())
mac = data["mac_address"]
hmac_key = data["hmac_key"]

# 探测本机 IP
def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

ip = get_local_ip()

# 构造请求数据
payload = {
    "application": {
        "version": "1.0.0",
        "elf_sha256": hmac_key,
    },
    "board": {
        "type": "demo-board",
        "name": "demo-app",
        "ip": ip,
        "mac": mac,
    }
}

headers = {
    "Device-Id": mac,
    "Content-Type": "application/json",
    "User-Agent": "demo-board/demo-app-1.0.0",
    "Accept-Language": "zh-CN"
}

# 关闭 SSL 校验（支持自签名）
ssl_ctx = create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = CERT_NONE

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(headers=headers, json=payload, ssl=ssl_ctx, url="https://api.tenclass.net/xiaozhi/ota/") as resp:
            print("HTTP 状态:", resp.status)
            try:
                print("响应 JSON:", await resp.json())
            except:
                print("响应文本:", await resp.text())

asyncio.run(main())
