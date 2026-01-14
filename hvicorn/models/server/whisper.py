"""Whisper 模块 - 私聊消息包

包含 WhisperPackage 模型，表示从服务器接收到的私聊消息。
"""

from pydantic import BaseModel
from typing import Optional, Literal
from pydantic.fields import Field


class WhisperPackage(BaseModel):
    """私聊消息包模型
    
    表示接收到的私聊消息（别人发给你的）。
    注意：这是 info 命令的一个子类型（type="whisper"）。
    
    属性:
        channel: 消息所在的频道
        cmd: 命令类型，始终为 "info"
        nick: 发送者昵称（使用 alias="from" 因为 from 是 Python 关键字）
        text: 原始消息文本（包含格式化信息）
        content: 实际私聊内容（从 text 中提取）
        time: 时间戳
        userid_to: 接收者的用户 ID
        trip: 发送者的识别码（可选）
        type: 类型标识，始终为 "whisper"
    """
    channel: str
    cmd: Literal["info"]
    nick: str = Field(
        ..., alias="from"
    )  # 使用 from 字段，但映射到 nick （from 是保留关键字）
    text: str  # 原始文本
    content: str  # 实际内容，需要在程序中提取
    time: int
    userid_to: int
    trip: Optional[str] = None
    type: Literal["whisper"]
