# Seamless-Branching-SBD

## A tool for creating seamless branching Blu-rays!

## 命名标准
* Clip:
Clip#?, 00000_?, 00000, ...

* Video:
00000_0_01.avc, 00000_?.avc, ...

* Audio:
00000_0_01.ac3, ...

* PG:
00000_0_01.pes, 00000_0_01_?.pes, ?_slice?_clipXXXXX.pes, ...

## Properties:  
* 新增对SUHD的支持
* 新增对playitem自动排序
* 新增自定义界面尺寸
* 不会重复导入已存在的轨道  
* 自动寻找clip对应轨道  
* 对共享clip的playItem，其时间应是相同的
* (Required) 使用前必须完成对所有素材的构建
* (Required) 所有playitem都必须链接到clip上，所有clip都必须有video
* (X) 同一PlayList中重复clip的修改
* (X) Multiple angles
* (X) PIP
* (X) DV
* [TO DO] PlayMark