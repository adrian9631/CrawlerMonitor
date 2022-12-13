# CrawlerMonitor

## Introduction
&emsp;&emsp;本项目在 Celery 分布式爬虫的基础上构建监控方案 Demo，在编写 Statsd + InfluxDB 方案代码进行调研过程中，转向了 Prometheus 的怀抱 ，使用 Grafana 对监控序列进行可视化，爬虫部分目前只完成对下载和解析进行简单解耦，反爬部分和代码结构优化等后续会陆续进行完善。

## QuickStart
&emsp;&emsp;本项目环境为 Ubuntu 16.04 LTS 以及使用 Python 3.6.5 (Anaconda), 安装执行流程默认适配上述环境，具体各部分安装配置请移步 [快速安装](https://github.com/adrianyoung/CrawlerMonitor/wiki/%E5%BF%AB%E9%80%9F%E5%AE%89%E8%A3%85)，其中包括 RabbitMQ、MongoDB、Python 相关库、 Celery (推荐使用 4.1.1 版本)、Prometheus、Grafana 等安装配置，操作启动控制请参考 [快速启动](https://github.com/adrianyoung/CrawlerMonitor/wiki/%E5%BF%AB%E9%80%9F%E5%90%AF%E5%8A%A8)，可分为手动启动和后台运行。后续会考虑 docker 容器化。启动三个实例 worker 跑了几分钟，从 MongoDB 导出的几千条 Json 数据 [此处](https://drive.google.com/file/d/1Vy71M9Jy7Mj4rFRCoj-PRvztsJbZOIJ8/view?usp=sharing) 。

## FlowChart  
&emsp;&emsp;简单画个流程图：  

<img src="https://drive.google.com/uc?export=view&id=1GO8Pdn77eM73cuiODSVpwIZ5T0gC0wFr" width = "650" height = "400" alt="sentence_model" align=center /> 

## Metrics
&emsp;&emsp;通过调研发现，在statsd 和 prometheus 的客户端均有对 metrics 的实现，后者在类型上支持较为丰富一点，这里使用 prometheus metrics 在 task 和 worker 层面设计监控指标，其设计如下表，并采用 worker，task，results 三个主要标签维度进行合理划分，各个类型 metric 的定义和使用详细可见 [Prometheus官网](https://prometheus.io/docs/concepts/metric_types/) 以及对应的 [Python 客户端](https://github.com/prometheus/client_python)。  


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

&emsp;&emsp;获取 Dashboard 模板: 直接在 Grafana 里 import 粘贴 https://grafana.com/grafana/dashboards/9970-celery-metrics/ 即可。


## TODO-LIST
&emsp;&emsp;[TODO-LIST](https://github.com/adrianyoung/CrawlerMonitor/wiki/TODO-LIST) 留给自己。
