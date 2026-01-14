"""Chat 模块 - 聊天消息包

包含 ChatPackage 模型，表示从服务器接收到的聊天消息。
"""

from pydantic import BaseModel
from typing import Optional, Literal


class ChatPackage(BaseModel):
    """聊天消息包模型
    
    表示从 hack.chat 服务器接收到的公开聊天消息。
    
    属性:
        cmd: 命令类型，始终为 "chat"
        channel: 消息所在的频道
        color: 发送者昵称的颜色（可选）
        level: 发送者的等级
        nick: 发送者的昵称
        text: 消息文本内容
        time: 时间戳
        trip: 发送者的识别码（可选）
        uType: 用户类型（user/mod/admin）
        userid: 用户 ID
        customId: 自定义 ID（可编辑消息属性，可选）
    """
    cmd: Literal["chat"]
    channel: str
    color: Optional[str] = None
    level: int
    nick: str
    text: str
    time: int
    trip: Optional[str] = None
    uType: Literal["user", "mod", "admin"]
    userid: int
    customId: Optional[str] = None
