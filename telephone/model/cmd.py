from dataclasses import dataclass
from dataclasses import field

import discord

@dataclass
class TpCmd:
	""" class to send general data about an interaction to a command """

	cmd: str = field(init=False, default="")
	tokens: list = field(default_factory=list)
	tokens_count: int = field(init=False, default=0)
	message: discord.Message = None
	client: discord.Client = None
	mentions: list = field(default_factory=list)
	mentions_count: int = field(init=False, default=0)
	guild: discord.Guild = None

	def __post_init__(self):
		if len(self.tokens) >= 1:
			self.tokens_count = len(self.tokens)
			self.cmd = self.tokens[0].lower()

		# remove mentions to us
		self.mentions = list(filter(lambda user : user.id != self.client.user.id, self.mentions))
		self.mentions_count = len(self.mentions)
