"""Warn 模块 - 警告消息包

包含 WarnPackage 模型，表示从服务器接收到的警告消息。
"""

from pydantic import BaseModel
from typing import Literal


class WarnPackage(BaseModel):
    """警告消息包模型
    
    表示从 hack.chat 服务器接收到的警告消息。
    警告可能包括速率限制、违规提示等。
    
    属性:
        cmd: 命令类型，始终为 "warn"
        text: 警告文本内容
        
    注意:
        特定的警告文本（如速率限制）会在 json_to_object 中被识别
        并转换为 RateLimitedPackage。
    """
    cmd: Literal["warn"]
    text: str
