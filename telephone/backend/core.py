import time
from dataclasses import Field
from dataclasses import asdict
from dataclasses import fields

import MySQLdb

from ..config import core as tpcfg

db_pool = {}
db_pool_id = 0

""" connect to the database """
def databaseConnect():
	conn_info = None

	conn_id_todelete = []

	global db_pool
	global db_pool_id

	# Iterate through open connections and find the currently active one.
	for pool_id in db_pool:
		conn_info_iter = db_pool.get(pool_id)

		if conn_info_iter['closed'] == True:
			if conn_info_iter['count'] <= 0:
				conn_id_todelete.append(pool_id)
		else:
			conn_info = conn_info_iter

	# Close and remove dead connections.
	if len(conn_id_todelete) > 0:
		for pool_id in conn_id_todelete:
			conn_info_iter = db_pool[pool_id]
			conn_info_iter['conn'].close()

			del db_pool[pool_id]

	# Create a new connection.
	if conn_info == None:
		db_pool_id += 1
		conn_info = {
		'conn': MySQLdb.connect(host = "localhost", user = "telephone-bot", passwd = "telephone" , db = tpcfg.database, charset = "utf8mb4"),
			'created': int(time.time()),
			'count': 1,
			'closed': False
		}
		db_pool[db_pool_id] = conn_info
	else:
		conn_info['count'] += 1

	return conn_info

""" close (maybe) the active database connection """
def databaseClose(conn_info):
	conn_info['count'] -= 1

	# Expire old database connections.
	if (conn_info['created'] + 60) < int(time.time()):
		conn_info['closed'] = True

"""
	Execute a given sql_query. (the purpose of this function is to minimize repeated code and keep functions readable)
"""
def execute_sql_query(sql_query: str = None, sql_replacements: tuple = None):
	data = None

	cursor = None
	conn_info = None
	try:
		conn_info = databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()
		cursor.execute(sql_query, sql_replacements)
		if sql_query.lower().startswith("select"):
			data = cursor.fetchall()
		elif sql_query.lower().startswith("replace") or sql_query.lower().startswith("insert"):
			data = cursor.lastrowid
		conn.commit()
	finally:
		if cursor is not None:
			# Clean up the database handles.
			cursor.close()
		if conn_info is not None:
			databaseClose(conn_info)

	return data



def databaseclass(table: str):
	def databaseclass_inner(cls):
		old_init = cls.__init__
		class_fields: tuple[Field, ...] = fields(cls)
		init_fields = []
		db_fields = []
		for f in class_fields:
			if f.init:
				init_fields.append(f.name)
			else:
				db_fields.append(f.name)

		def new_init(*args, **kwargs):
			old_init(*args, **kwargs)

			self = args[0]
			init_values = list(args[1:])
			for i in range(len(init_fields)):
				if len(init_values) == i:
					init_values.append(None)
				if init_values[i] is None:
					init_values[i] = kwargs.get(init_fields[i])

			db_values = execute_sql_query("SELECT {to_select} FROM {table} WHERE {cond}".format(
				to_select=", ".join(db_fields),
				table=table,
				cond=" AND ".join(map(
						lambda name: "{name} = %s".format(name=name),
						init_fields
					))
			), init_values)

			if len(db_values) > 0:
				for i in range(len(db_values[0])):
					name = db_fields[i]
					value = db_values[0][i]
					setattr(self, name, value)
			else:
				self.persist()

		cls.__init__ = new_init

		def persist(self):

			self_as_dict = asdict(self)
			execute_sql_query("REPLACE INTO {table} ({fields}) VALUES ({values})".format(
				table=table,
				fields=", ".join(map(lambda cf: cf.name, class_fields)),
				values=", ".join(map(lambda cf: "%s", class_fields))
			), map(lambda cf: self_as_dict.get(cf.name), class_fields))

		cls.persist = persist

		return cls

	return databaseclass_inner

