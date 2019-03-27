# CrawlerMonitor

## Introduction
&emsp;&emsp;本项目在celery分布式基础上构建监控方案demo，在编写Statsd+InfluxDB方案代码进行调研过程中，转向Prometheus的怀抱 ，使用Grafana对监控序列进行可视化，爬虫部分目前只完成对下载和解析进行简单解耦，反爬部分和代码结构优化等后续会陆续进行完善。

## QuickStart
&emsp;&emsp;本项目环境为 Ubuntu 16.04 LTS 以及使用 Python 3.6.5 (Anaconda), 安装执行流程默认适配上述环境，具体各部分安装配置请移步 [快速安装](https://github.com/adrianyoung/CrawlerMonitor/wiki/%E5%BF%AB%E9%80%9F%E5%AE%89%E8%A3%85)，其中包括 RabbitMQ、MongoDB、Python 相关库、 Celery (推荐使用 4.1.1 版本)、Prometheus、Grafana 等安装配置，操作启动控制请参考 [快速启动](https://github.com/adrianyoung/CrawlerMonitor/wiki/%E5%BF%AB%E9%80%9F%E5%90%AF%E5%8A%A8)，可分为手动启动和后台运行。后续会考虑 docker 容器化。启动三个实例 worker 跑了几分钟，从 MongoDB 导出的几千条 Json 数据 [此处](https://drive.google.com/file/d/1Vy71M9Jy7Mj4rFRCoj-PRvztsJbZOIJ8/view?usp=sharing) 。

## FlowChart  
&emsp;&emsp;简单画个流程图：  

<img src="https://drive.google.com/uc?export=view&id=1GO8Pdn77eM73cuiODSVpwIZ5T0gC0wFr" width = "650" height = "400" alt="sentence_model" align=center /> 

## Metrics
&emsp;&emsp;通过调研发现，在statsd 和 prometheus 的客户端均有对 metrics 的实现，后者在类型上支持较为丰富一点，这里使用 prometheus metrics 设计监控指标 metrics，其设计如下表，并采用 worker，task，results 三个主要标签维度进行合理划分，各个类型 metric 的定义和使用，详细可见 [Prometheus官网](https://prometheus.io/docs/concepts/metric_types/) 以及对应的 [Python 客户端](https://github.com/prometheus/client_python)。  


|Type|Name|Worker|Task|Results|
|:--:|:---|:----:|:--:|:-----:|
|Gauge|workers_state|√|||
|Counter|workers_processed|√|||
|Gauge|workers_active|√|||
|Counter|tasks_counter|√|√|√|
|Summary|tasks_runtime|√|√||
|Info|tasks_info|√|√|√|  
  
&emsp;&emsp;这里只涉及任务和工作单元层面，爬虫异常层面仍需进一步设计指标

## ScreenShot
&emsp;&emsp;Grafana 监控界面 Dashboard 模板  

<img src="https://drive.google.com/uc?export=view&id=18DeLCoc08Gws6hPjOfpCTTALIiS6QC2B" width = "500" height = "300" alt="sentence_model" align=center />  

&emsp;&emsp;获取 Dashboard 模板: 直接在 Grafana 里 import 粘贴 https://grafana.com/dashboards/9970/ 即可。


## TODO-LIST
- [ ] Spider
  - [x] 解析 Regex 和 Xpath
  - [x] 存储 MongoDB
  - [x] 任务队列 RabbitMQ
  - [ ] 去重 Redis
  - [ ] 异常处理
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
  - [x] 使用 supervisor 进行 Celery 程序控制

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
  - [x] 利用 grafana 设置阈值规则报警(邮件)  
  - [ ] 利用 prometheus 设置阈值规则报警（邮件/微信）

  
 - [ ] Common
   - [x] 配置集中
   - [ ] 高可用方案
   - [ ] 容器化
   - [ ] 单元测试
   - [ ] 代码优化 
   
