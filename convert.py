# encoding: utf8
import flatbuffers as Parser
import os
import string
import random
import shutil
import json
from shutil import copyfile

import sys


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


# override Table.String to avoid difference of 'bytes' between versions of Python
Table_String = Parser.Table.String
def Table_String_new(tab,off):
	return Table_String(tab,off).decode("utf-8")
Parser.Table.String = Table_String_new

str_types = (str,)
try:
	str_types += (bytes,)
except:
	pass
try:
	str_types += (unicode,)
except:
	pass

def normalizeResult(result):

	if isinstance(result,str_types):
		return result
	if isinstance(result,float):
		result = "%f"%result
		if "." in result:
			return result.rstrip("0").rstrip(".")
		return str(result)
	return str(result)

def writeFile(text):
	global csdPath
	with open(csdPath, "ab") as fileObj:
		fileObj.write(text.encode("utf-8"))
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

	writeFile(text)

def writeFooter():
	text = ''
	text = text + '    </Content>\n'
	text = text + '  </Content>\n'
	text = text + '</GameFile>\n'
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

	if path.startswith("Default/"):
		fileType = "Default"

	text = '  <%s Type="%s" Path="%s" Plist="%s" />\n' %(childKey, fileType, path, plistFile)
	return text

def getEasingText(easingData):
	if not easingData:
		return ""
	easingType = easingData.Type()
	if easingType == -1:
		return ""
	else:
		return '            <EasingData Type="%d" />\n' %(easingType)

def getFrameText(frameData, property):
	text = ""
	if property == "VisibleForFrame":
		realFrame = frameData.BoolFrame()
		text = text + '          <BoolFrame FrameIndex="%d" Tween="%s" Value="%s" />\n' %(realFrame.FrameIndex(), realFrame.Tween(), realFrame.Value())

	elif property == "Position":
		realFrame = frameData.PointFrame()
		text = text + '          <PointFrame FrameIndex="%d" X="%f" Y="%f">\n' %(realFrame.FrameIndex(), realFrame.Position().X(), realFrame.Position().Y())
		text = text + getEasingText(realFrame.EasingData())
		text = text + '          </PointFrame>\n'

	elif property == "Scale":
		realFrame = frameData.ScaleFrame()
		text = text + '          <ScaleFrame FrameIndex="%d" X="%f" Y="%f">\n' %(realFrame.FrameIndex(), realFrame.Scale().ScaleX(), realFrame.Scale().ScaleX())
		text = text + getEasingText(realFrame.EasingData())
		text = text + '          </ScaleFrame>\n'

	elif property == "RotationSkew":
		realFrame = frameData.ScaleFrame()
		text = text + '          <ScaleFrame FrameIndex="%d" X="%f" Y="%f">\n' %(realFrame.FrameIndex(), realFrame.Scale().ScaleX(), realFrame.Scale().ScaleX())
		text = text + getEasingText(realFrame.EasingData())
		text = text + '          </ScaleFrame>\n'

	elif property == "CColor":
		realFrame = frameData.ColorFrame()
		colorData = realFrame.Color()
		text = text + '          <ColorFrame FrameIndex="%d" Alpha="%d">\n' %(realFrame.FrameIndex(), colorData.A())
		text = text + '            <Color A="%d" R="%d" G="%d" B="%d" />' %(colorData.A(), colorData.R(), colorData.G(), colorData.B())
		text = text + '          </ColorFrame>\n'

	elif property == "FileData":
		realFrame = frameData.TextureFrame()
		text = text + '          <TextureFrame FrameIndex="%d" Tween="%s">\n' %(realFrame.FrameIndex(), realFrame.Tween())
		text = text + '          ' + getImageOption("TextureFile", realFrame.TextureFile())
		text = text + '          </TextureFrame>\n'

	elif property == "FrameEvent":
		realFrame = frameData.EventFrame()
		text = text + '          <EventFrame FrameIndex="%d" Value="%s">\n' %(realFrame.FrameIndex(), realFrame.Value())
		text = text + '          </EventFrame>\n'

	elif property == "Alpha":
		realFrame = frameData.IntFrame()
		text = text + '          <IntFrame FrameIndex="%d" Value="%d">\n' %(realFrame.FrameIndex(), realFrame.Value())
		text = text + getEasingText(realFrame.EasingData())
		text = text + '          </IntFrame>\n'

	elif property == "AnchorPoint":
		realFrame = frameData.ScaleFrame()
		text = text + '          <ScaleFrame FrameIndex="%d" X="%f" Y="%f">\n' %(realFrame.FrameIndex(), realFrame.Scale().ScaleX(), realFrame.Scale().ScaleX())
		text = text + getEasingText(realFrame.EasingData())
		text = text + '          </ScaleFrame>\n'

	elif property == "ZOrder":
		realFrame = frameData.IntFrame()
		text = text + '          <IntFrame FrameIndex="%d" Value="%d">\n' %(realFrame.FrameIndex(), realFrame.Value())
		text = text + '          </IntFrame>\n'

	elif property == "ActionValue":
		realFrame = frameData.InnerActionFrame()
		#todo
	elif property == "BlendFunc":
		realFrame = frameData.BlendFrame()
		text = text + '          <BlendFuncFrame FrameIndex="%d" Src="%d" Dst="%d">\n' %(realFrame.FrameIndex(), realFrame.BlendFunc().Src(), realFrame.BlendFunc().Dst())
		text = text + '          </BlendFuncFrame>\n'
	return text

def getTimeline(timeLineData):
	property = timeLineData.Property()
	text = '        <Timeline ActionTag="%d" Property="%s">\n' %(timeLineData.ActionTag(), timeLineData.Property())
	frameNum = timeLineData.FramesLength()
	for i in range(frameNum):
		frameData = timeLineData.Frames(i)
		text = text + getFrameText(frameData, property)
	text = text + '        </Timeline>\n'
	return text

def writeAction(actionData):
	duration = actionData.Duration()
	speed = actionData.Speed()
	timelineNum = actionData.TimeLinesLength()
	text = '      <Animation Duration="%d" Speed="%f">\n' %(duration, speed)
	for i in range(timelineNum):
		timeLineData = actionData.TimeLines(i)
		text = text + getTimeline(timeLineData)

	text = text + '      </Animation>\n'
	writeFile(text)

def writeAnimation(parseData):
	animationNum = parseData.AnimationListLength()
	if animationNum == 0:
		return
	text = '      <AnimationList>\n'
	for i in range(animationNum):
		animationData = parseData.AnimationList(i)
		text = text + '        <AnimationInfo Name="%s" StartIndex="%d" EndIndex="%d" />\n' %(animationData.Name(), animationData.StartIndex(), animationData.EndIndex())
	text += '      </AnimationList>\n'
	writeFile(text)

def writeRootNode(nodeTree):
	widgetOption = nodeTree.Options().Data()
	widgetSize = widgetOption.Size()
	if not widgetSize:
		boneOption = Parser.BoneNodeOptions()
		boneOption._tab = widgetOption._tab
		widgetOption = boneOption.NodeOptions()

	widgetSize = widgetOption.Size()
	widgetName = widgetOption.Name()
	text = ''
	nodeObject = {
		"Node": "GameNodeObjectData",
		"Scene": "GameNodeObjectData",
		"Layer": "GameLayerObjectData",
		"Skeleton": "SkeletonNodeObjectData",
	}
	if not nodeObject.get(widgetName):
		print("unknown widgetName:'%s', regarded as Node by default."%widgetName)
	text = text + '      <ObjectData Name="%s" ctype="%s">\n' %(widgetName, nodeObject.get(widgetName,"GameNodeObjectData"))
	text = text + '        <Size X="%f" Y="%f" />\n' %(widgetSize.Width(), widgetSize.Height())
	writeFile(text)

def getRealOption(className, optionData):
	realOption = None
	nameMap = {
		"Particle":"ParticleSystem"
	}
	optionClassName = nameMap.get(className,className) + "Options"

	try:
		optionClass = getattr(Parser, optionClassName)
	except Exception as e:
		print("error no match className: " + optionClassName)
		return 

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

	result = normalizeResult(parentValue)

	# ignoring field 'LabelText' will lead to a csd file parsing error
	if not optionKey in ["LabelText","ButtonText","PlaceHolderText"]:
		# ignore if equals default value
		if result.upper() == str(defaultValue).upper():
			return ""
		result = result.replace("\n", "&#xA;")
	
	renameDict = {}
	if replaceInfo != "":
		renameList = replaceInfo.split(",")
		for renameText in renameList:
			kvList = renameText.split("=")
			renameDict[kvList[0]] = kvList[1]
	if result in renameDict:
		result = renameDict[result]
	text = '%s="%s" ' %(optionKey, result)

	#scale9sprite special
	# if optionKey == "Scale9Enabled":
	# # if optionKey == "Scale9Enable" and result == "True":
	# 	text = text + getHeaderOption(optionData, "Scale9OriginX", "CapInsets.X")
	# 	text = text + getHeaderOption(optionData, "Scale9OriginY", "CapInsets.Y")
	# 	text = text + getHeaderOption(optionData, "Scale9Width", "CapInsets.Width")
	# 	text = text + getHeaderOption(optionData, "Scale9Height", "CapInsets.Height")
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
	if className in HeaderRules:
		ClassRules = HeaderRules[className]
		for ruleOption in ClassRules:
			text = text + getHeaderOption(optionData, ruleOption[0], ruleOption[1], ruleOption[2], ruleOption[3])
	text = text + 'ctype="%sObjectData">\n' %(className)
	writeFile(text)


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
		result = normalizeResult(func())
		keyValue = funcName
		if funcName in renameDict:
			keyValue = renameDict[funcName]
		# if isinstance(result, float) and result > 1.1:
		# 	result = int(result)
		text = text + '%s="%s" ' %(keyValue, result)
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

	if className in ChildRules:
		ClassRules = ChildRules[className]
		for childRule in ClassRules:
			text = text + tab + getChildProperty(realOption, childRule[0], childRule[1], childRule[2], childRule[3])
	writeFile(text)

def writeOption(nodeTree, tab):
	optionData = nodeTree.Options()
	className = nodeTree.Classname()
	realOption = getRealOption(className, optionData)
	if not realOption:
		defaultText = tab + '<AbstractNodeData ctype="%seObjectData">\n' %(className)
		writeFile(defaultText)
		return
	try:
		widgetOption = realOption.WidgetOptions()
	except:
		widgetOption = realOption.NodeOptions()
	
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

def startConvert(csbPath, csparsebinary, targetPath):
	global csdPath, targetOut
	_, fileName = os.path.split(csbPath)
	groupName,_ = os.path.splitext(fileName)
	# csdPath = os.path.join(targetOut, groupName + ".csd")
	# csdPath = os.path.join(os.path.splitext(csbPath)[0] + ".csd")
	fileDir,_ = os.path.split(targetPath)
	if not os.path.exists(fileDir):
		os.makedirs(fileDir)
	csdPath = targetPath

	nodeTree = csparsebinary.NodeTree()

	writeHeader(groupName)
	writeAction(csparsebinary.Action())
	# writeAnimation(csparsebinary)
	writeRootNode(nodeTree)
	recursionConvertTree(nodeTree)
	writeFooter()

def dealWithCsbFile(csbPath,targetPath):
	with open(csbPath, "rb") as fileObj:
		buf = fileObj.read()
		fileObj.close()

		buf = bytearray(buf)
		csparsebinary = Parser.CSParseBinary.GetRootAsCSParseBinary(buf, 0)
		startConvert(csbPath, csparsebinary, targetPath)
	print("csd generated: %s"%targetPath)

def main():
	if len(sys.argv) != 3:
		print("反编译csb文件")
		print("usage:\tpython convert.py <infile> <outfile>")
		print("\tpython convert.py <infolder> <outfolder>")
		exit(0)
	inpath = sys.argv[1]
	outpath = sys.argv[2]
	if(os.path.isdir(inpath)):
		# treat input as a folder
		for root,dirs,files in os.walk(inpath):

			for p in [os.path.join(root,f) for f in files]:
				outfile = os.path.join(outpath,os.path.relpath(p,inpath))
				outdir  = os.path.dirname(outfile)
				if not os.path.exists(outdir):
					os.makedirs(outdir)
				if os.path.splitext(p)[1] in [".csb"]:
					outfile = os.path.splitext(outfile)[0]+".csd"
					dealWithCsbFile(p,outfile)
				else:
					copyfile(p,outfile)
		print("translation completed! check your artifacts under %s"%os.path.realpath(outpath))
	else:
		# treat input as a single file
		dealWithCsbFile(inpath,outpath)

if __name__ == '__main__':
    main()