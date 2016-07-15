
# maybe call recorder ??

import time
import json

class Protocol:
	def __init__(self, name='',):
		self.name = name

	def write(**args):
		if not 'timestamp' in args:
			args['timestamp'] = time.time()
		with open(self.filename, 'a') as f:
			f.write(json.dumps(args))

	def load(self):
		with open(self.filename) as f:
			records = f.readlines()
		records = [json.loads(r) for r in records]
		return records

