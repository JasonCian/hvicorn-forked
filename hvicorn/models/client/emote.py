"""Emote 模块 - 动作消息请求

包含 EmoteRequest 模型，用于表示发送动作消息的请求。
"""

from typing import Literal
from pydantic import BaseModel


class EmoteRequest(BaseModel):
    """动作消息请求模型
    
    表示发送动作消息的请求（类似 IRC 的 /me 命令）。
    动作消息在页面上以斜体显示，格式如：*BotName does something*
    
    属性:
        cmd: 命令类型，始终为 "emote"
        text: 动作内容
        
    示例:
        EmoteRequest(text="挥手问好")
        # 显示为: *BotName 挥手问好*
    """
    cmd: Literal["emote"] = "emote"
    text: str
