"""Invite 模块 - 邀请通知包

包含 InvitePackage 模型，表示收到的频道邀请。
"""

from pydantic import BaseModel, Field
from typing import Literal


class InvitePackage(BaseModel):
    """邀请通知包模型
    
    当有人邀请你加入另一个频道时，会收到此包。
    这是 info 命令的一个特殊子类型（type="invite"）。
    
    属性:
        channel: 当前所在的频道
        cmd: 命令类型，始终为 "invite"
        from_nick: 邀请者的昵称（使用 alias="from"）
        invite_channel: 被邀请加入的频道名称（使用 alias="inviteChannel"）
        text: 原始文本
        time: 时间戳
        to_userid: 被邀请者的用户 ID
        type: 类型标识，始终为 "invite"
    """
    channel: str
    cmd: Literal["invite"]
    from_nick: str = Field(..., alias="from")  # from 是 Python 关键字
    invite_channel: str = Field(..., alias="inviteChannel")
    text: str
    time: int
    to_userid: int
    type: Literal["invite"]
