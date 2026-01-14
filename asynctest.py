"""hvicorn 异步运行示例

最简单的 hvicorn 机器人示例，演示基本的异步使用方式。
包含启动函数和简单的 Ping-Pong 命令。
"""

from hvicorn import Bot, CommandContext
from asyncio import run

# 创建 Bot 实例
bot = Bot(nick="HvicornTest", channel="lounge")


@bot.startup
async def startup():
    """启动函数 - 机器人启动后自动执行"""
    await bot.send_message("Hi this is a hvicorn demo, but in async")


@bot.command("Ping")
async def pong(ctx: CommandContext):
    """Ping 命令处理器 - 响应 Pong"""
    await ctx.respond("Pong (in async)!")


# 使用 asyncio.run() 运行异步 bot
run(bot.run())
