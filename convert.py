import csbparsers as Parser
import flatbuffers
import os, string, random, shutil, json

import sys
reload(sys)
sys.setdefaultencoding('utf8')


ENGINE_VERSION = "3.10.0.0"

script_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
targetOut = os.path.join(script_path, "csd")

with open(os.path.join(script_path, "header_rule.json"), "r") as fileObj:
	HeaderRules = json.load(fileObj)
	fileObj.close()

with open(os.path.join(script_path, "child_rule.json"), "r") as fileObj:
	ChildRules = json.load(fileObj)
	fileObj.close()

if not os.path.exists(targetOut):
	os.mkdir(targetOut)

csdPath = ""

def writeFile(text):
	global csdPath
	with open(csdPath, "a") as fileObj:
		fileObj.write(text)
		fileObj.close()

def writeHeader(groupName):
	global ENGINE_VERSION, csdPath
	if os.path.exists(csdPath):
		os.remove(csdPath)
	randomId = random.sample(string.ascii_lowercase + "-" + string.digits, 36)
	randomId = "".join(randomId)
	text = ''
	text = text + '<GameFile>\n'
	text = text + '  <PropertyGroup Name="%s" Type="Layer" ID="%s" Version="%s" />\n' %(groupName, randomId, ENGINE_VERSION)
	text = text + '  <Content ctype="GameProjectContent">\n'
	text = text + '    <Content>\n'
	text = text + '      <Animation Duration="0" Speed="1.0000" />\n'

	writeFile(text)

def writeFooter():
	text = ''
	text = text + '    </Content>\n'
	text = text + '  </Content>\n'
	text = text + '</GameFile>\n'
	writeFile(text)

def writeRootNode(nodeTree):
	widgetOption = nodeTree.Options().Data()
	widgetSize = widgetOption.Size()
	widgetName = widgetOption.Name()
	text = ''
	text = text + '      <ObjectData Name="%s" ctype="Game%sObjectData">\n' %(widgetName, widgetName)
	text = text + '        <Size X="%f" Y="%f" />\n' %(widgetSize.Width(), widgetSize.Height())
	writeFile(text)

def getRealOption(className, optionData):
	realOption = None
	optionClassName = className + "Options"
	optionClass = getattr(Parser, optionClassName)
	if optionClass:
		realOption = optionClass()
	
	if realOption:
		realOption._tab = optionData.Data()._tab
		return realOption
	else:
		return optionData

def getHeaderOption(optionData, optionKey, valuePath, defaultValue="", replaceInfo=""):
	valueList = valuePath.split(".")
	parentValue = optionData
	for path in valueList:
		if not parentValue:
			return ""
		func = getattr(parentValue, path)
		if not func:
			return ""
		parentValue = func()
	result = str(parentValue)
	print optionKey, valuePath, result
	if result.upper() == str(defaultValue).upper():
		return ""
	result = result.replace("\n", "&#xA;")
	
	renameDict = {}
	if replaceInfo != "":
		renameList = replaceInfo.split(",")
		for renameText in renameList:
			kvList = renameText.split("=")
			renameDict[kvList[0]] = kvList[1]
	if renameDict.has_key(result):
		result = renameDict[result]
	text = '%s="%s" ' %(optionKey, result)
	#scale9sprite special
	if optionKey == "Scale9Enable" and result == "True":
		text = text + getHeaderOption(optionData, "Scale9OriginX", "CapInsets.X")
		text = text + getHeaderOption(optionData, "Scale9OriginY", "CapInsets.Y")
		text = text + getHeaderOption(optionData, "Scale9Width", "CapInsets.Width")
		text = text + getHeaderOption(optionData, "Scale9Height", "CapInsets.Width")
	return text

def getDefaultOptionHeader(widgetOption, tab):
	global HeaderRules
	text = tab + '<AbstractNodeData '
	DefaultRules = HeaderRules["Default"]
	for ruleOption in DefaultRules:
		text = text + getHeaderOption(widgetOption, ruleOption[0], ruleOption[1], ruleOption[2])
	return text

def writeOptionHeader(optionData, widgetOption, className, tab):
	global HeaderRules
	text = getDefaultOptionHeader(widgetOption, tab)
	if HeaderRules.has_key(className):
		ClassRules = HeaderRules[className]
		for ruleOption in ClassRules:
			text = text + getHeaderOption(optionData, ruleOption[0], ruleOption[1], ruleOption[2], ruleOption[3])
	
	text = text + 'ctype="%sObjectData">\n' %(className)
	writeFile(text)

def getImageOption(childKey, resourceData):
	fileType = "Default"
	if resourceData.ResourceType() == 0:
		fileType = "Normal"
	elif resourceData.ResourceType() == 1:
		fileType = "PlistSubImage"
	path = resourceData.Path()
	plistFile = resourceData.PlistFile()
	if path == "" and plistFile == "":
		return '  <%s />\n' %(childKey)
	text = '  <%s Type="%s" Path="%s" Plist="%s" />\n' %(childKey, fileType, path, plistFile)
	return text


def getChildProperty(optionData, optionKey, valuePath, renameProperty="", specialType=""):
	valueList = valuePath.split(".")
	parentValue = optionData
	for path in valueList:
		func = getattr(parentValue, path)
		if not func:
			return ""
		parentValue = func()

	if specialType == "ImageData":
		return getImageOption(optionKey, parentValue)

	funcList = dir(parentValue)
	validFuncList = []
	for funcName in funcList:
		if funcName.startswith("_"):
			continue
		if funcName == "Init" or funcName.startswith("GetRoot"):
			continue
		validFuncList.append(funcName)
	renameDict = {}
	if renameProperty != "":
		renameList = renameProperty.split(",")
		for renameText in renameList:
			kvList = renameText.split("=")
			renameDict[kvList[1]] = kvList[0]
	text = '  <%s ' %(optionKey)
	for funcName in validFuncList:
		func = getattr(parentValue, funcName)
		result = func()
		keyValue = funcName
		if renameDict.has_key(funcName):
			keyValue = renameDict[funcName]
		text = text + '%s="%s" ' %(keyValue, str(result))
	text = text + "/>\n"
	return text


def getDefaultOptionChild(widgetOption, tab):
	global ChildRules
	DefaultRules = ChildRules["Default"]
	text = ""
	for childRule in DefaultRules:
		text = text + tab + getChildProperty(widgetOption, childRule[0], childRule[1], childRule[2], childRule[3])
	return text


def writeChildOption(realOption, widgetOption, className, tab):
	global ChildRules
	text = getDefaultOptionChild(widgetOption, tab)

	if ChildRules.has_key(className):
		ClassRules = ChildRules[className]
		for childRule in ClassRules:
			text = text + tab + getChildProperty(realOption, childRule[0], childRule[1], childRule[2], childRule[3])
	writeFile(text)

def writeOption(nodeTree, tab):
	optionData = nodeTree.Options()
	className = nodeTree.Classname()
	realOption = getRealOption(className, optionData)
	try:
		widgetOption = realOption.WidgetOptions()
	except:
		widgetOption = realOption.NodeOptions()
	else:
		pass
	
	writeOptionHeader(realOption, widgetOption, className, tab)
	writeChildOption(realOption, widgetOption, className, tab)

def recursionConvertTree(nodeTree, level = 0):
	baseTab = '      ' + "    "*level
	if level > 0:
		writeOption(nodeTree, baseTab)

	childNum = nodeTree.ChildrenLength()
	if childNum > 0:
		writeFile(baseTab + '  <Children>\n')
		for i in range(childNum):
			child = nodeTree.Children(i)
			recursionConvertTree(child, level + 1)
		writeFile(baseTab + '  </Children>\n')
	if level > 0:
		writeFile(baseTab + '</AbstractNodeData>\n')
	else:
		writeFile(baseTab + '</ObjectData>\n')

def startConvert(csbPath, csparsebinary):
	global csdPath, targetOut
	_, fileName = os.path.split(csbPath)
	groupName,_ = os.path.splitext(fileName)
	csdPath = os.path.join(targetOut, groupName + ".csd")

	nodeTree = csparsebinary.NodeTree()

	writeHeader(groupName)
	writeRootNode(nodeTree)
	recursionConvertTree(nodeTree)
	writeFooter()

def dealWithCsbFile(csbPath):
	with open(csbPath, "rb") as fileObj:
		buf = fileObj.read()
		fileObj.close()

		buf = bytearray(buf)
		csparsebinary = Parser.CSParseBinary.GetRootAsCSParseBinary(buf, 0)
		startConvert(csbPath, csparsebinary)

def main():
	if len(sys.argv) < 2:
		print "csb path needed."
		exit(0)
	dealWithCsbFile(sys.argv[1])

if __name__ == '__main__':
    main()