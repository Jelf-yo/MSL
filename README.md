# MSL  *MakeSomeLogs(整点日志)*


本程序用于模拟生成各类日志。
		
	MSL/

	├── main.py                  # 主程序入口

	├── MSL/                     # 包含主要逻辑的模块

	│   ├── config.py            # 配置加载和管理

	│   ├── simulator.py          # 日志生成逻辑

	│   └── utils.py             # 工具函数（如文件读取等）

	├── samples/                 # 示例文件夹，包含样本和配置文件

	│   ├── testlog.sample       # 日志模板示例

	│   ├── testlog.conf         # 日志配置示例

	│   ├── srcaddr_list.list    # 源地址列表文件

	│   ├── rate_config.ini      # 频率配置文件

	│   ├── stress_rate.ini      # 压力测试频率配置文件

	│   └── trading_days.list    # 交易日列表

	└── output/                  # 输出文件夹，保存生成的日志

   	 	└── iis.sample           # 由程序自动创建的日志输出文件


# ***如何使用***

使用示例

***ps:使用前请chmod +x makeSomeLogs***
 
	./makeSomeLogs --template samples/testlog.sample --config samples/testlog.conf --output output/stress.log --rate_config samples/rate_config.ini &

 主程序为[makeSomeLogs],目前有下面几种参数(./makeSomeLogs -h可查看)。运行日志会生成落在logs/下

	--template	日志模板文件路径,必选
	
	--config	配置文件路径,必选
	
	--output	输出日志文件路径,必选
	
	--rate_config	频率控制配置文件路径,必选
	
	--trading_days	交易日列表文件路径，可选
	
	--stress_test	启用压力测试模式，尽可能快速地产生日志，可选
	
	--stress_rate	配合stress_test使用，压测速率


## **日志模板&日志配置文件**

一种日志模板搭配一个日志配置文件，其中的##token##为一个token，每一个token一一对应

**testlog.sample**

	<1>##timestamp## ##src_ip## ##src_port## This just for test.

 **testlog.conf**

	[default]
	token.1.token= ##timestamp##
	token.1.replacementType = timestamp
	token.1.replacement = %Y/%m/%d %H:%M:%S.%f
	
	token.2.token= ##src_ip##
	token.2.replacementType = file
	token.2.replacement = samples/srcaddr_list.list
	
	token.3.token= ##src_port##
	token.3.replacementType = random
	token.3.replacement = list["2231","2131","555","854"]

 ### 配置文件说明

 - *token: 对应sample样例中的位置*
 
 - *replacementType: 替换的类型，目前氛围几种类*
 	- *1.timestamp 时间戳类型；*
 
 	- *2.file，文件类型常用于指定IP池、用户名等；*
 
 	- *3.random，一个列表的随机字符串，多用于简单替换；*
 
 	- *4.static，静态值，一个固定值；*
 
	- *5.uuid，随机生成的md5类型的唯一ID；*
 
	- *6.number_range，随机数字范围，例如1000-9999。其他类型后续更新*
 
 - *replacement: 替换的内容。*
 	- *1.timestamp，为时间戳的格式类型,这里的%Y/%m等等均为Python的strftime 函数支持多种日期格式化指令，详情请自行搜索对应的指令，下面列出一些常用的；*
  
  	- *2.file,即为路径可以是相对路径也可以是绝对路径*
   
 	- *3.random，一个列表的随机字符串，list["abc","bcd"]；*
 
 	- *4.static，静态值，一个固定值；*
 
	- *5.uuid，随机生成的md5类型的唯一ID，uuid无需配置replacement，仅配置replacementType即可；*
 
	- *6.number_range，随机数字范围，例如1000-9999。其他类型后续更新*

		%Y：4 位数的年份，如 2024
	
		%y：2 位数的年份，如 24
	
		%m：月份（01-12），如 01 到 12
	
		%d：月份中的某一天（01-31），如 05
	
		%H：24 小时制的小时（00-23），如 14
	
		%M：分钟（00-59），如 30
	
		%S：秒（00-59），如 45
	
		%f：微秒（000000-999999），如 654321
	
		%z：UTC 偏移时间，如 +0100 或 -0500
	
		%Z：时区名称（如果可用），如 CST 或 UTC

 ### 关于频率控制说明 rate_config.ini

 **默认配置**
 ```ini
#交易日开市的频率
[trading_day_working]
start_time = 09:30
end_time = 15:00
rate = 1500

#交易日休市频率
[trading_day_non_working]
rate = 50

#工作日的工作时间频率
[weekday_working]
start_time = 09:00
end_time = 17:00
rate = 200

#工作日的非工作时间频率
[weekday_non_working]
rate = 50

#周末的忙时频率
[weekend_working]
start_time = 10:00
end_time = 16:00
rate = 70

#周末的闲时频率
[weekend_non_working]
rate = 30
```
1.为了更好的模拟正常的日志生成模块，分为了工作日工作时间/非工作时间、非工作日的忙时/闲时，同时还会有指定日志，如金融证券的交易日模式，仅需要提供交易日List即可，当交易日生效时,其他将不再生效，由于本程序仅用于模拟测试大致情况，当前版本未完美考虑开市休市时间，中午休市时间也算在开市时间内。

2.没有--trading_days参数默认为不使用交易日频率。

3.压测模式需要结合--stress_test和--stress_rate两个参数使用，使用--stress_test不需要配置值。

4.rate的单位是条/分钟,100则为每分钟100条，rate可以为范围，例如每分钟1000到5000条则为【1000-5000】连接符为【-】

### 压测模式

	./makeSomeLogs --template samples/testlog.sample --config samples/testlog.conf --output output/stress.log --rate_config samples/rate_config.ini --stress_test --stress_rate samples/stress_rate.ini &

压测建议可以直接用自带的示例日志，压测模式旨在根据当前配置性能尽可能快速地产生日志，所以不设有时间，压测模式需要结合--stress_test和--stress_rate两个参数使用，使用--stress_test不需要配置值。

*stress_rate.ini*

#压测频率,默认十万
[stress_test]
rate = 100000

