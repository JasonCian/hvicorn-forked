"""ChangeColor 模块 - 更改颜色请求

包含 ChangeColorRequest 模型，用于表示更改昵称颜色的请求。
"""

from typing import Literal
from pydantic import BaseModel


class ChangeColorRequest(BaseModel):
    """更改颜色请求模型
    
    表示更改机器人昵称显示颜色的请求。
    
    属性:
        cmd: 命令类型，始终为 "changecolor"
        color: 颜色值，可以是颜色名称（如 "red"、"blue"）或十六进制值（如 "#FF5733"）
               "reset" 表示重置为默认颜色
    """
    cmd: Literal["changecolor"] = "changecolor"
    color: str = "reset"  # 默认重置颜色
