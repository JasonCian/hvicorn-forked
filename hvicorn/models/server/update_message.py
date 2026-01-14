"""UpdateMessage 模块 - 消息更新包

包含 UpdateMessagePackage 模型，表示消息被编辑的通知。
"""

from pydantic import BaseModel
from typing import Literal


class UpdateMessagePackage(BaseModel):
    """消息更新包模型
    
    当有人编辑了之前发送的消息时，服务器会广播此包。
    所有在线用户（包括机器人）都会收到此通知。
    
    属性:
        channel: 频道名称
        cmd: 命令类型，始终为 "updateMessage"
        customId: 被编辑消息的唯一标识符
        level: 编辑者的等级
        mode: 编辑模式（overwrite/prepend/append/complete）
        text: 新的消息文本
        time: 时间戳
        userid: 编辑者的用户 ID
    """
    channel: str
    cmd: Literal["updateMessage"]
    customId: str
    level: int
    mode: Literal["overwrite", "prepend", "append", "complete"]
    text: str
    time: int
    userid: int
