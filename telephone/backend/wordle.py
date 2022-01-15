import random
from dataclasses import dataclass
from dataclasses import field

import telephone.backend.core as becore
import telephone.utils.core as tputils

@becore.databaseclass(table="wordles")
@dataclass
class TpWordle:
	id_wordle: int
	word: str = field(init=False)
	solved: int = field(init=False)


def init_valid_wordles():
	init_word_list("wordlist.txt", "wordle_candidates")


def init_valid_guesses():
	init_word_list("guesslist.txt", "wordle_valid_guesses")


def init_word_list(f_name, table):

	tputils.logMsg("loading word list")

	words = tuple()
	file = None
	try:
		file = open(f_name, "r")
		f_lines = file.readlines()

		f_lines = map(lambda l: l.rstrip(), f_lines)
		words = tuple(filter(lambda l: len(l) == 5 and l.find("'") == -1, f_lines))

	except IOError:
		print("Could not read {} file.".format(f_name))
	finally:
		if file is not None:
			file.close()

	if len(words) > 0:
		becore.execute_sql_query("REPLACE INTO {table} VALUES {values}".format(
			table=table,
			values=",".join(map(lambda x: "(%s)", words))
		), words)

	tputils.logMsg("done loading word list")


def get_wordle_for_user(id_user: int):
	data = becore.execute_sql_query(
		"SELECT id_wordle FROM wordles WHERE id_wordle NOT IN (SELECT id_wordle FROM wordle_guesses WHERE id_guess = %S) LIMIT 1",
		id_user
	)
	if len(data) > 0:
		return data[0][0]
	return None


def generate_new_wordle():
	words = becore.execute_sql_query("SELECT word FROM wordle_candidates")
	chosen = random.choice(words)[0]

	wordle_id = becore.execute_sql_query("INSERT INTO wordles (word) VALUES (%s)", chosen)

	return wordle_id
