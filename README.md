# 成都购房通最新开盘通知
## 用法
1. 安装nodejs
2. 配置钉钉通知地址
```python
DING_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxx"  # 配置钉钉webhook地址
```
3. 配合crontab或者死循环使用
```python
# 死循环
while True:
  get_list()
  time.sleep(100)
```
