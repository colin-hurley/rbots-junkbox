import sys

### GENERIC JED PARSING LIBRARY ###

class JedFileCog:
	def parse(self, line):
		parts = line.strip().split(' ')
		self.name = parts[0]
		self.params = []
		self.param_types = dict()
		self.param_values = dict()
		for part in parts[1:]:
			nameparts = part.split(':')
			name = nameparts[0]
			valueparts = nameparts[1].split('=')
			type = valueparts[0]
			value = valueparts[1]
			self.params.append(name)
			self.param_types[name] = type
			self.param_values[name] = value
	def __str__(self):
		return self.name + ' {' + ','.join(self.params) + '}'

class JedFileCogsSection:
	def read(self, input):
		self.cogs = []
		for line in input:
			cog = JedFileCog()
			cog.parse(line)
			self.cogs.append(cog)
	def __str__(self):
		names = []
		for cog in self.cogs:
			names.append(cog.name)
		return ' '.join(names)

class JedFile:
	def read(self, path):
		self.path = path
		with open(path, 'r') as input:
			# TODO: expand this part as necessary for parsing other sections
			while True:
				line = input.readline()
				if line.strip() == 'SEC: COGS':
					break
			# Skip cog count line
			input.readline()
			# Read until 'END'
			lines = []
			while True:
				line = input.readline()
				if line.strip() == 'END':
					break
				lines.append(line)
			# Parse lines
			self.cogs_section = JedFileCogsSection()
			self.cogs_section.read(lines)
	def __str__(self):
		return 'JedFile[path=%s]' % self.path

### END ###

class Path:
	def __init__(self, cog):
		self.nodes = []
		nodenum = 0
		while True:
			name = 'node%d' % nodenum
			if name not in cog.params:
				break
			nodenum += 1
			value = cog.param_values[name]
			if value == '-1':
				continue
			self.nodes.append(int(cog.param_values[name]))

def report(jedfile):
	# first pass, bin nodes into paths and non-paths
	paths = []
	others = []
	for cog in jedfile.cogs_section.cogs:
		if cog.name.lower() == 'rbot-path.cog' or cog.name.lower() == 'rbot-pathctf.cog':
			paths.append(Path(cog))
		else:
			others.append(cog)

	# Get all the nodes
	nodes = [] # really want a set
	for path in paths:
		nodes.extend(path.nodes)

	# Find any matching thing refs in other cogs
	for cog in others:
		for param in cog.params:
			type = cog.param_types[param].lower()
			if type in ['thing', 'intx']:
				value = int(cog.param_values[param])
				if value in nodes:
					print 'Cog %s param %s (%s) value %d is also a node number' % (cog.name, param, type, value)

for path in sys.argv[1:]:
	jedfile = JedFile()
	jedfile.read(path)
	report(jedfile)
