"""Join 模块 - 加入频道请求

包含 JoinRequest 模型，用于表示加入 hack.chat 频道的请求。
"""

from typing import Literal, Optional
from pydantic import BaseModel


class JoinRequest(BaseModel):
    """加入频道请求模型
    
    表示机器人请求加入一个 hack.chat 频道。
    这是机器人连接后发送的第一个命令。
    
    属性:
        cmd: 命令类型，始终为 "join"
        nick: 要使用的昵称
        channel: 要加入的频道名称
        password: 频道密码（如果需要）
        
    示例:
        JoinRequest(nick="MyBot", channel="programming", password="secret123")
    """
    cmd: Literal["join"] = "join"
    nick: str
    channel: str
    password: Optional[str] = None
