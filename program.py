import os
from utilities import normalizePath

def findConfigFile(searchPath):
	while True:
		print("searching: "+searchPath)
		if os.path.isfile(searchPath+"/tsconfig.json"):
			print("config found")
			return searchPath+"/tsconfig.json"
		newPath = os.path.dirname(searchPath)
		if newPath == searchPath:
			return None
		searchPath = newPath

def resolveTripleslashReference(moduleName, containingFile):
	basepath = os.path.dirname(containingFile)
	return moduleName if moduleName[0] == "/" else basepath + "/" + moduleName

def computeCommonSourceDirectoryOfFilenames(fileNames, currentDirectory):
	commonPathComponents = list()
	for sourceFile in fileNames:
		sourcePath = currentDirectory+"/"+sourceFile if sourceFile[0] != "/" else sourceFile
		sourcePathComponents = normalizePath(sourcePath)
		
		if len(commonPathComponents) == 0:
			commonPathComponents = sourcePathComponents
			continue

		for i in range(0, min((len(commonPathComponents), len(sourcePathComponents)))):
			if commonPathComponents[i] != sourcePathComponents[i]:
				if i == 0:
					return ""

			commonPathComponents = commonPathComponents[:i]
			break

		if len(sourcePathComponents) < len(commonPathComponents):
			commonPathComponents = commonPathComponents[:i]

	if len(commonPathComponents) == 0:
		return currentDirectory

	return "/"+"/".join(commonPathComponents)

