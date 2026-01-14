"""Whisper 模块 - 私聊消息请求

包含 WhisperRequest 模型，用于表示发送私聊消息的请求。
"""

from pydantic import BaseModel
from typing import Literal


class WhisperRequest(BaseModel):
    """私聊消息请求模型
    
    表示向指定用户发送私聊消息的请求。
    私聊消息只有发送者和接收者可见。
    
    属性:
        cmd: 命令类型，始终为 "whisper"
        nick: 接收者的昵称
        text: 私聊内容
    """
    cmd: Literal["whisper"] = "whisper"
    nick: str
    text: str
