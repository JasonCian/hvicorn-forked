"""OnlineSet 模块 - 在线用户列表设置

包含 User 模型和 OnlineSetPackage，用于表示频道中的用户信息。
"""

from pydantic import BaseModel
from typing import Optional, Literal, List, Union


class User(BaseModel):
    """用户模型
    
    表示 hack.chat 频道中的一个用户。
    
    属性:
        channel: 用户所在的频道
        color: 用户昵称的颜色（字符串或 false）
        hash: 用户的唯一哈希值
        isBot: 是否为机器人
        isme: 是否是当前客户端自己
        level: 用户等级（权限等级）
        nick: 用户昵称
        trip: 识别码（tripcode，可选）
        uType: 用户类型（user/mod/admin）
        userid: 用户 ID
    """
    channel: Optional[str] = None
    color: Union[str, bool]  # 颜色可以是字符串或 false
    hash: str
    isBot: bool
    isme: bool
    level: int
    nick: str
    trip: Optional[str] = None  # 识别码，仅当用户使用了 tripcode 时存在
    uType: Literal["user", "mod", "admin"]
    userid: int


class OnlineSetPackage(BaseModel):
    """在线用户列表设置包
    
    当机器人首次加入频道或刷新时，服务器会发送此包，
    包含频道中所有在线用户的完整列表。
    
    属性:
        cmd: 命令类型，始终为 "onlineSet"
        channel: 频道名称
        nicks: 所有在线用户的昵称列表
        time: 时间戳
        users: 所有在线用户的详细信息列表
    """
    cmd: Literal["onlineSet"]
    channel: str
    nicks: List[str]  # 简单的昵称列表
    time: int
    users: List[User]  # 详细的用户信息列表
