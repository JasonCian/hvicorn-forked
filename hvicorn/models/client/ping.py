"""Ping 模块 - Ping 请求

包含 PingRequest 模型，用于表示发送 Ping 的请求。
"""

from typing import Literal
from pydantic import BaseModel


class PingRequest(BaseModel):
    """Ping 请求模型
    
    表示向服务器发送 Ping 请求以保持连接活跃。
    
    属性:
        cmd: 命令类型，始终为 "ping"
    """
    cmd: Literal["ping"] = "ping"
