# Fix surface extralight values in a JED file to match a JKL
#
# This can be used to correct surface extralight settings when importing
# new levels, since ZED apparently ignores this value.
#
# For example, the viewscreens on either side of the emperor's throne in
# mdm14_throne.jkl have their extralight reset to 0 upon opening in ZED.

import os
import sys

class Surface:
	def __init__(self, tokens):
		self.num = int(tokens[0][:-1])
		self.extralight = float(tokens[8])

class SurfaceParser:
	def __init__(self, count):
		self.values = []
		self.count = count
	def parse_line(self, line):
		line, ignore, ignore = line.partition('#')
		tokens = line.split()
		if len(tokens) > 10:
			value = Surface(tokens)
			self.values.append(value)
			self.count -= 1
	def is_done(self):
		return self.count == 0

class Sector:
	def __init__(self, num, sf_tokens):
		self.num = num
		self.sfnum0 = int(sf_tokens[1])
		self.sfcount = int(sf_tokens[2])
	def contains_surface(self, surface):
		return self.sfnum0 <= surface.num and surface.num < (self.sfnum0 + self.sfcount)

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
			value = Sector(self.sectornum, tokens)
			self.values.append(value)
			self.count -= 1
	def is_done(self):
		return self.count == 0

class Jkl:
	def __init__(self, sectors, surfaces):
		self.sectors = sectors
		self.surfaces = surfaces
	def find_surface(self, scnum, scsfnum):
		for sector in self.sectors:
			if sector.num == scnum:
				sfnum = sector.sfnum0 + scsfnum
				for surface in self.surfaces:
					if surface.num == sfnum:
						return surface
		return None

def parse_jkl(input):
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

	return Jkl(sectors.values, surfaces.values)

def transform_jed(input, output, jkl):
	in_geo = False
	while True:
		line = input.readline()
		if line == '':
			break
		if line.find('SEC: GEO') == 0:
			output.write(line)
			line = input.readline() # 'SECS #'
			output.write(line)
			tokens = line.split()
			sector_count = int(tokens[1])
			sector_num = 0
			while sector_num < sector_count:
				output.write(input.readline()) # 'FILENAME.CMP ...'
				line = input.readline() # 'VXS #'
				output.write(line)
				tokens = line.split()
				vertex_count = int(tokens[1])
				vertex_num = 0
				while vertex_num < vertex_count:
					output.write(input.readline()) # 'X Y Z'
					vertex_num += 1
				line = input.readline() # 'SURFS #'
				output.write(line)
				tokens = line.split()
				scsf_count = int(tokens[1])
				scsf_num = 0
				while scsf_num < scsf_count:
					line = input.readline() # line 1: 'FILENAME.MAT ...'
					tokens = line.split()
					# Fix the extralight value on this line to match the JKL
					extralight = 0
					surface = jkl.find_surface(sector_num, scsf_num)
					if surface is not None:
						extralight = surface.extralight
					if extralight > 0:
						print 'DEBUG :: ScNum: %3d  ScSfIdx: %2d  SfNum: %4d  Extralight: %f' % (sector_num, scsf_num, surface.num, extralight)
					tokens[6] = str(extralight)
					output.write(' '.join(tokens) + '\n')
					line = input.readline() # line 2: xyz and rgb for surface vertices
					output.write(line)
					scsf_num += 1
				sector_num += 1
			continue
		output.write(line)

def fix_extralight(jkl_file_path, jed_file_path):
	with open(jkl_file_path, 'r') as input:
		jkl = parse_jkl(input)
	tmp_file_path = '%s.tmp' % jed_file_path
	with open(jed_file_path, 'r') as input:
		with open(tmp_file_path, 'w') as output:
			transform_jed(input, output, jkl)
	os.remove(jed_file_path)
	os.rename(tmp_file_path, jed_file_path)

fix_extralight(sys.argv[1], sys.argv[2])
