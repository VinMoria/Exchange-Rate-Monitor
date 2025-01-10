# 新币汇率监控

## 定期从中国银行网页上爬取数据，当汇率满足条件时，会发送邮件

目前的规则为：初始浮动阈值 = 固定阈值，当汇率低于浮动阈值时，发送邮件，并同时将浮动阈值设为 (当前汇率-0.01)。当汇率高于固定阈值时，浮动阈值重置为固定阈值。

## 运行
1. 将 config-template.json 复制一份为 config.json，并填写相关内容。（关于发送者的邮箱，目前outlook和gmail已经不再支持授权码登录，可以使用qq邮箱，或尝试其他邮箱服务）
2. 运行main.py.

## Docker
镜像文件在 docker hub 上，在服务器端可执行以下命令来部署运行

```Shell
docker pull redcomet720/currency:latest

docker run -d -v [filepath]/config.json:/app/config.json redcomet720/currency:latest 
#请提前准备好配置文件，执行此命令后，服务开始运行

# 以下是日志查看
docker ps # 查看运行中的容器的id
docker logs [容器 id] # 查看运行时日志 

```