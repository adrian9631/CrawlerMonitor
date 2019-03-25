# XueqiuCrawler

## TODO-LIST
- [ ] Spider
  - [x] 解析 Regex 和 Xpath
  - [x] 存储 MongoDB
  - [x] 任务队列 RabbitMQ
  - [ ] 去重 Redis
  - [ ] 反爬
    - [x] 爬取频率控制
    - [x] ua 和 refered 字段变更
    - [x] Cookies 信息维护
    - [ ] IP 代理

- [ ] Celery
  - [x] 熟悉 Celery 基础配置
  - [x] 利用 exchange 和 queue 对 download 和 parse 进行解耦
  - [ ] 设置 schedule 定时任务进行 Cookie 或 IP 维护
  - [x] 对 task event 和 worker event 进行捕捉
  - [x] 对 worker 在分布式环境下进行时间同步
  - [x] 使用 flower 服务进行信息监控
  - [ ] 使用 supervisor 进行 Celery 程序控制

- [ ] Monitor
  - [x] 利用 statsd metrics (python) 构建监控指标 
  - [x] 利用 prometheus metrics (python) 构建监控指标
  - [x] 利用 prometheus rabbitmq exporter 进行指标信息采集
  - [x] 利用 pushgateway 对指标信息采集并进行缓存
  - [x] 熟悉 prometheus 基础配置
  - [x] 利用 prometheus 存储监控时序信息
  - [x] 利用 influxdb 存储监控时序信息
  - [x] 利用 grafana 对监控时序信息进行可视化 (Celery/RabbitMQ)
  - [x] 利用 grafana 制定 dashboard 模板并导出
  - [ ] 利用 prometheus 设置阈值规则报警（邮件/微信）
  - [ ] 利用 grafana 设置阈值规则邮件报警
  
 - [ ] Common
   - [ ] 单元测试 unittest
   - [ ] 配置集中化
   - [ ] 代码优化 
