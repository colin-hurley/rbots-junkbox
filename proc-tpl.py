import sys

### GENERIC JED PARSING LIBRARY ###

class TplFile:
	def read(self, path):
		self.path = path
		self.templates = dict()
		with open(path, 'r') as input:
			while True:
				line = input.readline()
				if line == '':
					break
				if line.startswith('#'):
					# Skip comments / metadata for now
					continue
				if len(line.strip()) == 0:
					# Skip blank lines
					continue
				try:
					template = Template()
					template.parse(line)
					self.templates[template.name] = template
				except Exception, e:
					print 'Warning: Ignoring malformed template line: ' + line.strip()

class Template:
	def parse(self, line):
		parts = line.strip().lower().split()
		self.name = parts[0]
		self.parent = parts[1]
		self.properties = dict()
		for property in parts[2:]:
			parts2 = property.split('=')
			pname = parts2[0]
			pvalue = parts2[1]
			self.properties[pname] = pvalue
	def __str__(self):
		return self.name

### END ###

def get_props_recursive(tplfile, curtpl, allprops, proporigins):
	pnames = []
	for pname in curtpl.properties:
		if pname in allprops:
			continue
		pnames.append(pname)
		allprops[pname] = curtpl.properties[pname]
		proporigins[pname] = curtpl.name
	if curtpl.parent != 'none' and curtpl.parent in tplfile.templates:
		pnames.extend(get_props_recursive(tplfile, tplfile.templates[curtpl.parent], allprops, proporigins))
	return pnames

def report(tplfile, tplnames):
	for tplname in tplnames:
		tpl = tplfile.templates[tplname]
		allprops = dict()
		proporigins = dict()
		print 'Template: %s (based on %s)' % (tpl.name, tpl.parent)
		print '----------------------------------------'
		allpropnames = get_props_recursive(tplfile, tpl, allprops, proporigins)
		allpropnames.sort()
		for pname in allpropnames:
			porigin = proporigins[pname]
			if porigin == tplname:
				porigin = ''
			print '  %-20s : %-30s : %s' % (pname, allprops[pname], porigin)

path = sys.argv[1]
tplfile = TplFile()
tplfile.read(path)
report(tplfile, sys.argv[2:])
