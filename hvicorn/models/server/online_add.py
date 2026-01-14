"""OnlineAdd 模块 - 用户加入包

包含 OnlineAddPackage 模型，表示有新用户加入频道。
"""

from pydantic import BaseModel
from typing import Union, Optional, Literal


class OnlineAddPackage(BaseModel):
    """用户加入包模型
    
    当有新用户加入频道时，服务器会发送此包。
    Bot 需要处理此包以更新本地的在线用户列表。
    
    属性:
        channel: 频道名称（可选）
        cmd: 命令类型，始终为 "onlineAdd"
        color: 用户昵称颜色（字符串或 false）
        hash: 用户哈希值
        isBot: 是否是机器人
        level: 用户等级
        nick: 用户昵称
        time: 时间戳
        trip: 用户识别码（可选）
        uType: 用户类型（user/mod/admin）
        userid: 用户 ID
    """
    channel: Optional[str] = None
    cmd: Literal["onlineAdd"]
    color: Union[bool, str]
    hash: str
    isBot: bool
    level: int
    nick: str
    time: int
    trip: Optional[str] = None
    uType: Literal["user", "mod", "admin"]
    userid: int
