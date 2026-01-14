"""Emote 模块 - 动作消息包

包含 EmotePackage 模型，表示从服务器接收到的动作消息。
"""

from pydantic import BaseModel
from typing import Optional, Literal


class EmotePackage(BaseModel):
    """动作消息包模型
    
    表示从 hack.chat 服务器接收到的动作消息。
    动作消息在页面上以斜体显示。
    
    属性:
        channel: 消息所在的频道
        cmd: 命令类型，始终为 "emote"
        nick: 发送者的昵称
        text: 原始消息文本（包含昵称）
        content: 实际动作内容（从 text 中提取）
        time: 时间戳
        trip: 发送者的识别码（可选）
        userid: 用户 ID
    """
    channel: str
    cmd: Literal["emote"]
    nick: str
    text: str  # 原始文本
    content: str  # 实际内容，需要在程序中提取
    time: int
    trip: Optional[str] = None
    userid: int
