"""测试插件示例

最简单的 hvicorn 插件示例，演示插件的基本结构。
这个插件注册一个自定义命令，响应简单的问候消息。

使用方法:
    await bot.load_plugin("testplugin", command_name="/hello")
"""

import hvicorn


async def plugin_init(bot: hvicorn.Bot, command_name: str):
    """插件初始化函数
    
    所有 hvicorn 插件必须定义 plugin_init 函数。
    
    Args:
        bot: hvicorn Bot 实例
        command_name: 要注册的命令名称（由加载插件时传入）
    """
    async def hello(ctx: hvicorn.CommandContext):
        """Hello 命令处理器"""
        await ctx.respond("Hello from a hvicorn plugin")

    # 注册命令到 bot
    bot.register_command(command_name, hello)
