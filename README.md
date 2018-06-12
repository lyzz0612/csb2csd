# csb2csd
cocostudio csb反编成csd

建完工程搜了遍才发现已经有大佬实现了[csb2csd](https://github.com/DavidFeng/csb2csd)。可惜在windows系统折腾了几遍竟然没法编译成功(linux上一遍过了)。还是决定自己手撸一个好了。

## 原理说明
看官方的引擎解析，csb文件应该是一个flatbuffer转换后格式。同时在引擎中搜索找到了解析的原型（类似protobuf的proto文件）`cocos/editor-support/cocostudio/fbs-files/CSParseBinary.fbs`，于是用flatc工具生成了对应的python解析库`parse`，再根据解析出的数值内容按格式还原csd文件。

## 待完成
1. 支持粒子特效、骨骼动画
2. 支持动画曲线的points
3. ……

## 踩过的坑
1. 对比引擎用的CSParseBinary_generated.h和给出的CSParseBinary.fbs，发现fbs中的isLocalized位置有问题需要手动移至最后
2. 九宫格数据Scale9OriginX，Scale9OriginY，Scale9Width，Scale9Height必须是整数否则会解析错误，取出的浮点数要去除小数点和0
3. 编辑器里显示的九宫格用的是LeftEage、RightEage、TopEage、BottomEage，而不是2中的几个字段
4. 字段名不一致容易写错的：

   | fbs字段名   | 编辑器字段  |
   |------------|------------|
   | ClipEnabled | ClipAble  |
   | Scale9Enabled | Scale9Enable  |
   | TouchScaleEnable | TouchScaleChangeAble  |
   
5. flatc导出python时bool类型的默认值未生效，默认值全部都是false，一些默认值为true的会有问题，已手动修改
6. 骨骼动画、粒子特效的结构描述竟然不在CSParseBinary.fbs里面，暂只整合进了SketonNode

