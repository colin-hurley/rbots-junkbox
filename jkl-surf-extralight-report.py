# Show surfaces with their extra light values
#
# This can be used to manually compare and correct extralight settings when
# importing new levels, since ZED apparently ignores this value.
#
# For example, the viewscreens on either side of the emperor's throne in
# mdm14_throne.jkl have their extralight reset to 0 upon opening in ZED.

import sys

class SurfaceParser:
	def __init__(self, count):
		self.values = []
		self.count = count
	def parse_line(self, line):
		line, ignore, ignore = line.partition('#')
		tokens = line.split()
		if len(tokens) > 10:
			num = int(tokens[0][:-1])
			extralight = float(tokens[8])
			self.values.append((num, extralight))
			self.count -= 1
	def is_done(self):
		return self.count == 0

class SectorParser:
	def __init__(self, count):
		self.sectornum = 0
		self.values = []
		self.count = count
	def parse_line(self, line):
		line, ignore, ignore = line.partition('#')
		if line.find('SECTOR ') == 0:
			self.sectornum = int(line.split()[1])
		elif line.find('SURFACES ') == 0:
			tokens = line.split()
			self.values.append((self.sectornum, int(tokens[1]), int(tokens[2])))
			self.count -= 1
	def is_done(self):
		return self.count == 0

def report(input):
	parser = None
	surfaces = None
	sectors = None
	for line in input:
		if parser is None:
			if line.find('World surfaces ') == 0:
				# Entering surfaces section
				tokens = line.split()
				count = int(tokens[2])
				surfaces = SurfaceParser(count)
				parser = surfaces
			elif line.find('World sectors ') == 0:
				# Entering sectors section
				tokens = line.split()
				count = int(tokens[2])
				sectors = SectorParser(count)
				parser = sectors
		if parser is not None:
			parser.parse_line(line)
			if parser.is_done():
				parser = None

	# Display report
	print 'SCNUM SFIDX SFNUM EXTRALIGHT'
	for sfnum, extralight in surfaces.values:
		if extralight > 0.0:
			secnum = -1
			secsfnum = -1
			for snum, sfnum0, sfcount in sectors.values:
				if sfnum0 <= sfnum and sfnum < (sfnum0 + sfcount):
					secnum = snum
					secsfnum = sfnum - sfnum0
			print '%d %d %d %f' % (secnum, secsfnum, sfnum, extralight)

for path in sys.argv[1:]:
	with open(path, 'r') as input:
		report(input)