optionDeclarations = {
	"charset": {"type": "string"},
	"declaration": {"shortName": "d", "type": "boolean"}}

def getOptionNameMap():
	if optionNameMapCache:
		pass

def parseCommandLine(commandLine, readFile=None):
	options = None
	fileNames = list()
	errors = list()
	optionNameMap, shortOptionNames = getOptionNameMap()