from telephone.model.cmd import TpCmd


async def hello(cmd: TpCmd):
	print("hello {author}".format(author=cmd.message.author.display_name))
