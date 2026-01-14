"""Info 模块 - 信息消息包

包含 InfoPackage 模型，表示从服务器接收到的一般信息消息。
"""

from pydantic import BaseModel
from typing import Literal


class InfoPackage(BaseModel):
    """信息消息包模型
    
    表示从 hack.chat 服务器接收到的一般信息消息。
    这是 info 命令的基础类型，不带 type 字段或未识别的特殊类型。
    
    属性:
        cmd: 命令类型，始终为 "info"
        text: 信息文本内容
        
    注意:
        info 命令有多种子类型，如私聊、邀请、改名等，
        这些特殊类型会在 json_to_object 中被识别并转换为对应的模型。
    """
    cmd: Literal["info"]
    text: str
