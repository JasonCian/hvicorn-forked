"""Uncatched 模块 - 未识别包

包含 UncatchedPackage 模型，表示未被框架识别的包。
"""

from pydantic import BaseModel


class UncatchedPackage(BaseModel):
    """未识别包模型
    
    当 json_to_object 无法识别某个包的类型时，
    会返回此模型，包含原始 JSON 数据。
    
    属性:
        rawjson: 原始 JSON 字典数据
        
    使用场景:
        - 服务器添加了新的命令类型，但框架还未支持
        - 特殊的服务器事件
        - 调试和日志记录
        
    注意:
        如果机器人经常收到 UncatchedPackage，可能需要更新 hvicorn 框架。
    """
    rawjson: dict
