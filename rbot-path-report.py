import sys

def parse_cog_line(line):
	parts = line.split(' ')
	cog = parts[0]
	params = dict()
	for part in parts[1:]:
		nameparts = part.split(':')
		valueparts = nameparts[1].split('=')
		params[nameparts[0]] = valueparts[1]
	return cog, params

class Path:
	def __init__(self, line):
		self._cog, self._params = parse_cog_line(line)
		self.nodes = []
		nodenum = 0
		while True:
			paramname = 'node%d' % nodenum
			if paramname not in self._params or self._params[paramname] == '-1':
				break
			self.nodes.append(self._params[paramname])
			nodenum += 1

def report(input):
	incogs = False
	wrotecount = False
	skip = 0
	paths = []
	for line in input:
		if skip > 0:
			skip -= 1
			continue
		if not incogs:
			if line.strip() == 'SEC: COGS':
				# Entering cogs section
				skip = 1
				incogs = True
		elif line.strip() == 'END':
			# End of cog section
			incogs = False
		else:
			if line.startswith('rbot-path.cog') or line.startswith('rbot-pathctf.cog'):
				paths.append(Path(line))

	# Display report
	pathnum = 0
	for path in paths:
		intersections = []
		for node in path.nodes:
			if node in intersections:
				# Duplicate node in path -- already recorded as intersection
				continue
			for path2 in paths:
				if path2 == path:
					# Ignore self path
					continue
				if node in path2.nodes:
					intersections.append(node)
					break
		print 'Path %d' % pathnum
		print '\tNodes = ' + ' '.join(path.nodes)
		print '\tIntersections = ' + ' '.join(intersections)
		pathnum += 1

for path in sys.argv[1:]:
	with open(path, 'r') as input:
		report(input)