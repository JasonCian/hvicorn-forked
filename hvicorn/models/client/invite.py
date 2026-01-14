"""Invite 模块 - 邀请请求

包含 InviteRequest 模型，用于表示邀请用户到频道的请求。
"""

from typing import Literal
from pydantic import BaseModel
from typing import Optional


class InviteRequest(BaseModel):
    """邀请请求模型
    
    表示邀请指定用户加入某个频道的请求。
    
    属性:
        cmd: 命令类型，始终为 "invite"
        nick: 要邀请的用户昵称
        to: 目标频道名称（可选）
    """
    cmd: Literal["invite"] = "invite"
    nick: str
    to: Optional[str]
