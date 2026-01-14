"""ChangeNick 模块 - 改名通知包

包含 ChangeNickPackage 模型，表示用户更改昵称的通知。
"""

from typing import Literal
from pydantic import BaseModel


class ChangeNickPackage(BaseModel):
    """改名通知包模型
    
    当用户更改昵称时，服务器会广播此包。
    这是 info 命令的一个特殊子类型，通过解析 "OldNick is now NewNick" 文本识别。
    
    属性:
        old_nick: 原昵称
        new_nick: 新昵称
        text: 原始文本（格式："OldNick is now NewNick"）
        cmd: 命令类型，始终为 "changenick"
        channel: 频道名称
        time: 时间戳
        
    注意:
        此模型是在 json_to_object 中通过解析 info 包的 text 字段生成的。
    """
    old_nick: str
    new_nick: str
    text: str
    cmd: Literal["changenick"]
    channel: str
    time: int
