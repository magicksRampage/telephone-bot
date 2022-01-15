import discord


async def respond(msg: str, author: discord.User):
	await author.send(msg)
