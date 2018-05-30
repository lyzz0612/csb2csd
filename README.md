# csb2csd
cocostudio csb反编成csd

## 原理说明
看官方的引擎解析，csb文件应该是一个flatbuffer转换后格式。同时在引擎中搜索找到了解析的原型（类似protobuf的proto文件）`cocos/editor-support/cocostudio/fbs-files/CSParseBinary.fbs`，于是用flatc工具生成了对应的python解析库`parse`，再根据解析出的数值内容按格式还原csd文件。
