"""Captcha 模块 - 验证码请求包

包含 CaptchaPackage 模型，表示服务器请求验证码。
"""

from typing import Literal
from pydantic import BaseModel


class CaptchaPackage(BaseModel):
    """验证码请求包模型
    
    当服务器要求进行验证码验证时，会发送此包。
    通常用于防止机器人滥用。
    
    属性:
        channel: 频道名称
        cmd: 命令类型，始终为 "captcha"
        text: 验证码相关信息
        time: 时间戳
        
    注意:
        大多数机器人无法自动处理验证码，可能需要人工干预。
    """
    channel: str
    cmd: Literal["captcha"]
    text: str
    time: int
