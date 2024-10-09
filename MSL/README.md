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
