"""UpdateUser 模块 - 用户信息更新包

包含 UpdateUserPackage 模型，表示用户信息发生变化。
"""

from pydantic import BaseModel
from typing import Union, Optional, Literal


class UpdateUserPackage(BaseModel):
    """用户信息更新包模型
    
    当用户的信息发生变化时（如改名、升级等），服务器会发送此包。
    Bot 需要处理此包以更新本地的用户信息。
    
    属性:
        channel: 频道名称（可选）
        cmd: 命令类型，始终为 "updateUser"
        color: 新的颜色（可选）
        hash: 新的哈希值（可选）
        isBot: 是否是机器人（可选）
        level: 新的等级（可选）
        nick: 新的昵称（可选）
        time: 时间戳（可选）
        trip: 新的识别码（可选）
        uType: 新的用户类型（可选）
        userid: 用户 ID（可选）
        
    注意:
        所有字段都是可选的，只有发生变化的字段会包含在包中。
        处理时需要检查字段是否为 None。
    """
    channel: Optional[str] = None
    cmd: Literal["updateUser"]
    color: Union[bool, str]
    hash: Optional[str] = None
    isBot: Optional[bool] = None
    level: Optional[int] = None
    nick: Optional[str] = None
    time: Optional[int] = None
    trip: Optional[str] = None
    uType: Optional[Literal["user", "mod", "admin"]] = None
    userid: Optional[int] = None
