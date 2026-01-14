"""WhisperSent 模块 - 私聊发送确认包

包含 WhisperSentPackage 模型，表示私聊消息发送成功的确认。
"""

from pydantic import BaseModel
from typing import Literal

from pydantic.fields import Field


class WhisperSentPackage(BaseModel):
    """私聊发送确认包模型
    
    当你发送私聊消息后，服务器会返回此包作为确认。
    这是 info 命令的一个特殊子类型（type="whisper"）。
    
    属性:
        channel: 消息所在的频道
        cmd: 命令类型，始终为 "info"
        userid_from: 发送者的用户 ID（使用 alias="from"）
        text: 原始文本（包含 "You whispered to" 前缀）
        content: 实际私聊内容（从 text 中提取）
        time: 时间戳
        userid_to: 接收者的用户 ID（使用 alias="to"）
        type: 类型标识，始终为 "whisper"
        
    注意:
        此包用于确认私聊发送成功，不是接收私聊（接收用 WhisperPackage）。
    """
    channel: str
    cmd: Literal["info"]
    userid_from: int = Field(..., alias="from")  # from 是 Python 关键字
    text: str  # 原始文本
    content: str  # 实际内容，需要在程序中提取
    time: int
    userid_to: int = Field(..., alias="to")  # to 也使用 alias
    type: str = "whisper"
