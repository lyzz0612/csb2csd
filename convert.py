import csbparsers as Parser
import flatbuffers
import os, sys, string, random, shutil

ENGINE_VERSION = "3.10.0.0"

script_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
targetOut = os.path.join(script_path, "csd")

if os.path.exists(targetOut):
	shutil.rmtree(targetOut)
os.mkdir(targetOut)

csdPath = ""

def writeFile(text):
	global csdPath
	with open(csdPath, "a") as fileObj:
		fileObj.write(text)
		fileObj.close()

def writeHeader(groupName):
	global ENGINE_VERSION
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
	if className == "Button":
		realOption = Parser.ButtonOptions()
	elif className == "CheckBox":
		realOption = Parser.CheckBoxOptions()
	elif className == "ImageView":
		realOption = Parser.ImageViewOptions()
	elif className == "ListView":
		realOption = Parser.ListViewOptions()
	elif className == "LoadingBar":
		realOption = Parser.LoadingBarOptions()
	elif className == "Node":
		realOption = Parser.WidgetOptions()
	elif className == "PageView":
		realOption = Parser.PageViewOptions()
	elif className == "Panel":
		realOption = Parser.PanelOptions()
	elif className == "Particle":
		realOption = Parser.ParticleSystemOptions()
	elif className == "ProjectNode":
		realOption = Parser.ProjectNodeOptions()
	elif className == "ScrollView":
		realOption = Parser.ScrollViewOptions()
	elif className == "Sprite":
		realOption = Parser.SpriteOptions()
	elif className == "Text":
		realOption = Parser.TextOptions()
	elif className == "TextAtlas":
		realOption = Parser.TextAtlasOptions()
	elif className == "TextBMFont":
		realOption = Parser.TextBMFontOptions()
	elif className == "TextField":
		realOption = Parser.TextFieldOptions()
	elif className == "SingleNode":
		realOption = Parser.SingleNodeOptions()
	
	if realOption:
		realOption._tab = optionData.Data()._tab
		return realOption
	else:
		return realOption

def getSingleProperty(optionData, optionType):
	funcList = dir(optionData)
	validFuncList = []
	for funcName in funcList:
		if funcName.startswith("_"):
			continue
		if funcName == "Init" or funcName.startswith("GetRoot"):
			continue
		validFuncList.append(funcName)
	text = '  <%s ' %(optionType)
	for funcName in validFuncList:
		func = getattr(optionData, funcName)
		result = func()
		text = text + '%s="%s" ' %(funcName, str(result))
	text = text + "/>\n"
	return text

def formatOption(optionData, funcKey, default="", optionKey=""):
	func = getattr(optionData, funcKey)
	result = str(func())
	if result == str(default):
		return ""
	if optionKey == "":
		optionKey = funcKey
	result = result.replace("\n", "&#xA;")
	text = '%s="%s" ' %(optionKey, result)
	return text

def getNormalOption(widgetOption, tab):
	sizeOption =  widgetOption.Size()
	anchorOption =  widgetOption.AnchorPoint()
	positionOption =  widgetOption.Position()
	colorOption =  widgetOption.Color()
	textList = [
		'%s  <Size X="%f" Y="%f" />' %(tab, sizeOption.Width(), sizeOption.Height()),
		'%s  <AnchorPoint ScaleX="%f" ScaleY="%f" />' %(tab, anchorOption.ScaleX(), anchorOption.ScaleY()),
		'%s  <Position X="%f" Y="%f" />' %(tab, positionOption.X(), positionOption.Y()),
		'%s  <CColor A="%d" R="%d" G="%d" B="%d" />\n' %(tab, colorOption.A(), colorOption.R(), colorOption.G(), colorOption.B()),
	]
	text = "\n".join(textList)
	return text

def getNormalOptionHeader(widgetOption, tab):
	layoutComponent = widgetOption.LayoutComponent()
	skewOption = widgetOption.RotationSkew()
	layoutComponent = widgetOption.LayoutComponent()
	textList = [
		'%s<AbstractNodeData ' %(tab),
		formatOption(widgetOption, "Name"),
		formatOption(widgetOption, "Visible", True),
		formatOption(widgetOption, "ActionTag"),
		formatOption(widgetOption, "Tag"),
		formatOption(widgetOption, "FlipX", False),
		formatOption(widgetOption, "FlipY", False),
		formatOption(widgetOption, "IgnoreSize", False),
		formatOption(widgetOption, "TouchEnabled"),
		formatOption(widgetOption, "CallBackType", "None"),
		formatOption(widgetOption, "CallBackName", "None"),
		formatOption(widgetOption, "CustomProperty"),
		formatOption(widgetOption, "FrameEvent"),
		formatOption(skewOption, "RotationSkewX", 0.0),
		formatOption(skewOption, "RotationSkewY", 0.0),
		formatOption(layoutComponent, "LeftMargin", 0.0),
		formatOption(layoutComponent, "RightMargin", 0.0),
		formatOption(layoutComponent, "TopMargin", 0.0),
		formatOption(layoutComponent, "BottomMargin", 0.0),
		formatOption(layoutComponent, "HorizontalEdge"),
		formatOption(layoutComponent, "VerticalEdge"),
	]
	text = "".join(textList)
	return text

def getScale9HeaderOption(capinsertData, scale9Enable):
	if not scale9Enable:
		return " "
	text = 'Scale9Enable="%s" ' %(scale9Enable)
	text = text + 'LeftEage="%s" ' %(str(capinsertData.X()))
	text = text + 'RightEage="%s" ' %(str(capinsertData.X()+capinsertData.Width()))
	text = text + 'TopEage="%s" ' %(str(capinsertData.Y()+capinsertData.Height()))
	text = text + 'BottomEage="%s" ' %(str(capinsertData.Y()))
	return text

def getTextOutlineHeaderOption(optionData):
	text = ""
	text = text + formatOption(optionData, "OutlineEnabled")
	text = text + formatOption(optionData, "OutlineSize")
	return text

def getTextShadowHeaderOption(optionData):
	text = ""
	text = text + formatOption(optionData, "ShadowOffsetX")
	text = text + formatOption(optionData, "ShadowOffsetY")
	text = text + formatOption(optionData, "ShadowBlurRadius")
	text = text + formatOption(optionData, "ShadowEnabled")
	return text

def writeOptionHeader(optionData, widgetOption, className, tab):
	text = getNormalOptionHeader(widgetOption, tab)
	if className == "Button":
		# text = text + formatOption(optionData, "Text")
		# text = text + formatOption(optionData, "IsLocalized")
		# text = text + formatOption(optionData, "FontSize")
		# text = text + formatOption(optionData, "FontName")
  		text = text + getScale9HeaderOption(optionData.CapInsets(), optionData.Scale9Enabled())
  		text = text + getTextShadowHeaderOption(optionData)
	elif className == "CheckBox":
		text = text + formatOption(optionData, "DisplayState")
		text = text + formatOption(optionData, "SelectedState")
	elif className == "ImageView":
  		text = text + getScale9HeaderOption(optionData.CapInsets(), optionData.Scale9Enabled())
	elif className == "ListView":
		text = text + formatOption(optionData, "ClipEnabled")
		text = text + formatOption(optionData, "BounceEnabled")
		text = text + formatOption(optionData, "ItemMargin")
		text = text + formatOption(optionData, "ColorType")
		text = text + formatOption(optionData, "BgColorOpacity")
		text = text + formatOption(optionData, "DirectionType")
		text = text + formatOption(optionData, "HorizontalType")
		text = text + formatOption(optionData, "VerticalType")
	elif className == "LoadingBar":
		text = text + formatOption(optionData, "Percent")
		text = text + formatOption(optionData, "Direction")
	elif className == "Node":
		pass
	elif className == "PageView":
		text = text + formatOption(optionData, "ClipEnabled")
		text = text + formatOption(optionData, "ColorType")
		text = text + formatOption(optionData, "BgColorOpacity")
	elif className == "Panel":
		text = text + formatOption(optionData, "ClipEnabled")
		text = text + formatOption(optionData, "ColorType")
		text = text + formatOption(optionData, "BgColorOpacity")
	elif className == "Particle":
		pass
	elif className == "ProjectNode":
		text = text + formatOption(optionData, "FileName")
		text = text + formatOption(optionData, "InnerActionSpeed")
	elif className == "ScrollView":
		text = text + formatOption(optionData, "ClipEnabled")
		text = text + formatOption(optionData, "ColorType")
		text = text + formatOption(optionData, "BgColorOpacity")
		text = text + formatOption(optionData, "Direction")
		text = text + formatOption(optionData, "BounceEnabled")
		text = text + formatOption(optionData, "ScrollbarEnabeld")
		text = text + formatOption(optionData, "ScrollbarAutoHide")
		text = text + formatOption(optionData, "ScrollbarAutoHideTime")
	elif className == "Sprite":
		pass
	elif className == "Text":
		text = text + formatOption(optionData, "FontSize")
		# text = text + formatOption(optionData, "FontName")
		text = text + formatOption(optionData, "Text", "", "LabelText")
		# text = text + formatOption(optionData, "IsLocalized")
		# text = text + formatOption(optionData, "AreaWidth")
		# text = text + formatOption(optionData, "AreaHeight")
		# text = text + formatOption(optionData, "HAlignment")
		# text = text + formatOption(optionData, "VAlignment")
  		text = text + getTextOutlineHeaderOption(optionData)
  		text = text + getTextShadowHeaderOption(optionData)
	elif className == "TextAtlas":
		text = text + formatOption(optionData, "StringValue")
		text = text + formatOption(optionData, "StartCharMap")
		text = text + formatOption(optionData, "ItemWidth")
		text = text + formatOption(optionData, "ItemHeight")
	elif className == "TextBMFont":
		text = text + formatOption(optionData, "Text")
		text = text + formatOption(optionData, "IsLocalized")
	elif className == "TextField":
		text = text + formatOption(optionData, "FontName")
		text = text + formatOption(optionData, "FontSize")
		text = text + formatOption(optionData, "Text")
		text = text + formatOption(optionData, "IsLocalized")
		text = text + formatOption(optionData, "PlaceHolder")
		text = text + formatOption(optionData, "PasswordEnabled")
		text = text + formatOption(optionData, "PasswordStyleText")
		text = text + formatOption(optionData, "MaxLengthEnabled")
		text = text + formatOption(optionData, "MaxLength")
		text = text + formatOption(optionData, "AreaWidth")
		text = text + formatOption(optionData, "AreaHeight")
		text = text + formatOption(optionData, "IsCustomSize")
	elif className == "SingleNode":
		pass
	text = text + 'ctype="%sObjectData">\n' %(className)
	writeFile(text)

def getImageResource(resourceData, childKey):
	fileType = "Normal"
	if resourceData.ResourceType() == 1:
		fileType = "PlistSubImage"
	text = '  <%s Type="%s" Path="%s" Plist="%s" />\n' %(childKey, fileType, resourceData.Path(), resourceData.PlistFile())
	return text

def writeChildOption(realOption, widgetOption, className, tab):
	text = getNormalOption(widgetOption, tab)

	if className == "Button":
		text = text + tab + getSingleProperty(realOption.TextColor(), "TextColor")
		text = text + tab + getSingleProperty(realOption.OutlineColor(), "OutlineColor")
		text = text + tab + getImageResource(realOption.NormalData(), "NormalFileData")
		text = text + tab + getImageResource(realOption.PressedData(), "PressedFileData")
		text = text + tab + getImageResource(realOption.DisabledData(), "DisabledFileData")
	elif className == "CheckBox":
		pass
	elif className == "ImageView":
		text = text + tab + getImageResource(realOption.FileNameData(), "FileData")
	elif className == "ListView":
		pass
	elif className == "LoadingBar":
		pass
	elif className == "Node":
		pass
	elif className == "PageView":
		pass
	elif className == "Panel":
		pass
	elif className == "Particle":
		pass
	elif className == "ProjectNode":
		pass
	elif className == "ScrollView":
		pass
	elif className == "Sprite":
		text = text + tab + getImageResource(realOption.FileNameData(), "FileData")
		text = text + tab + getSingleProperty(realOption.BlendFunc(), "BlendFunc")
	elif className == "Text":
		text = text + tab + getImageResource(realOption.FontResource(), "FontResource")
	elif className == "TextAtlas":
		pass
	elif className == "TextBMFont":
		pass
	elif className == "TextField":
		pass
	elif className == "SingleNode":
		pass
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
	writeFile(tab + '</AbstractNodeData>\n')

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