from dataclasses import dataclass, field
from ..backend.core import databaseclass


@databaseclass(table="players")
@dataclass
class TpPlayer:
	id_user: int
	wordle_points: int = field(init=False, default=0)
