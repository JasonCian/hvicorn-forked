"""Custom 模块 - 自定义请求

包含 CustomRequest 模型，用于发送原始 JSON 数据。
"""

from pydantic import BaseModel


class CustomRequest(BaseModel):
    """自定义请求模型
    
    用于发送原始 JSON 数据，绕过 Pydantic 验证。
    这是一个特殊模型，允许发送任意 JSON 结构到服务器。
    
    属性:
        rawjson: 原始 JSON 字典
        
    警告:
        使用此模型会绕过类型检查和验证，使用时需谨慎。
        只在需要发送框架不支持的特殊请求时使用。
    """
    rawjson: dict
