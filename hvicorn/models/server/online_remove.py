"""OnlineRemove 模块 - 用户离开包

包含 OnlineRemovePackage 模型，表示有用户离开频道。
"""

from pydantic import BaseModel
from typing import Literal


class OnlineRemovePackage(BaseModel):
    """用户离开包模型
    
    当有用户离开频道时，服务器会发送此包。
    Bot 需要处理此包以从本地的在线用户列表中移除该用户。
    
    属性:
        nick: 离开的用户昵称
        cmd: 命令类型，始终为 "onlineRemove"
        time: 时间戳
        userid: 用户 ID
    """
    nick: str
    cmd: Literal["onlineRemove"]
    time: int
    userid: int
