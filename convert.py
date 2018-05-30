import csbparsers as Parser
import flatbuffers
import os, sys, string, random

ENGINE_VERSION = "3.10.0.0"

script_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
targetOut = os.path.join(script_path, "csd")

csdPath = ""

def writeFile(text):
	global csdPath
	print text
	# with open(csdPath, "a") as fileObj:
	# 	fileObj.write(text)
	# 	fileObj.close()

def writeHeader(groupName):
	global ENGINE_VERSION, SCENE_SIZE
	randomId = random.sample(string.ascii_lowercase + "-" + string.digits, 36)
	text = ''
	text = text + '<GameFile>\n'
	text = text + '  <PropertyGroup Name="%s" Type="Scene" ID="%s" Version="%s" />\n' %(groupName, randomId, ENGINE_VERSION)
	text = text + '  <Content ctype="GameProjectContent">\n'
	text = text + '    <Content>\n'
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
	text = ''
	text = text + '      <ObjectData Name="%s" ctype="GameNodeObjectData">\n' %(widgetOption.Name())
	text = text + '        <Size X="%f" Y="%f" />\n' %(widgetSize.Width(), widgetSize.Height())
	writeFile(text)

def writeOption(nodeTree, tab):
	widgetOption = nodeTree.Options().Data()
	layoutComponent = widgetOption.LayoutComponent()
	className = nodeTree.Classname()
	textList = [
		'<AbstractNodeData Name="%s" ' %(widgetOption.Name()),
		'Visible="%s" ' %(widgetOption.Visible()),
		'ActionTag="%d" ' %(widgetOption.ActionTag()),
		'Tag="%s" ' %(widgetOption.Tag()),
		'LeftMargin="%f" ' %(layoutComponent.LeftMargin()),
		'ctype="%sObjectData">' %(className),
	]
	text = "".join(textList)
	writeFile(text)

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