"""CustomId 生成工具

生成用于可编辑消息的唯一标识符。
CustomId 是一个 6 位随机字符串，由字母和数字组成。
"""

from string import ascii_letters, digits
from random import choice

# 生成 6 位随机 customId（字母+数字）
# 用于标识可编辑消息，确保后续可以通过 customId 更新消息内容
generate_customid = lambda: "".join([choice(ascii_letters + digits) for _ in range(6)])
