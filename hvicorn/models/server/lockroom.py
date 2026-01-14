"""Lockroom 模块 - 房间锁定通知包

包含 LockroomPackage 模型，表示被锁定频道拒绝的通知。
"""

from pydantic import BaseModel
from typing import Literal


class LockroomPackage(BaseModel):
    """房间锁定通知包模型
    
    当尝试加入被锁定的频道时，服务器会发送此包并将你移动到其他频道。
    这是 info 命令的一个特殊子类型，通过特定的警告文本识别。
    
    属性:
        cmd: 命令类型，始终为 "info"
        time: 时间戳
        
    注意:
        此模型是在 json_to_object 中通过匹配特定的警告文本生成的：
        "You have been denied access to that channel and have been moved somewhere else."
    """
    cmd: Literal["info"]
    time: int
