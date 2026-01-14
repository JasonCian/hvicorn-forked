"""ChangeNick 模块 - 更改昵称请求

包含 ChangeNickRequest 模型，用于表示更改昵称的请求。
"""

from typing import Literal
from pydantic import BaseModel


class ChangeNickRequest(BaseModel):
    """更改昵称请求模型
    
    表示更改机器人昵称的请求。
    昵称必须符合规则：1-24 字符，仅包含字母、数字和下划线。
    
    属性:
        cmd: 命令类型，始终为 "changenick"
        nick: 新的昵称
        
    注意:
        更改昵称前应该使用 verifyNick() 函数验证昵称的合法性。
    """
    cmd: Literal["changenick"] = "changenick"
    nick: str
