# CookiesPool

Cookies池，目前对接了新浪微博，[m.weibo.cn](https://m.weibo.cn)


## 运行

### ProxyPool-master 

进入ProxyPool-master打开代理池并获取随机代理,运行命令:

```
cd ProxyPool-master
python3 run.py
```

## 获取随机代理

利用requests获取方法如下

```python
import requests

PROXY_POOL_URL = 'http://localhost:5555/random'

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None
```

# 启动爬虫

## 导入账号

```
python3 importer.py
```

```
请输入账号密码组, 输入exit退出读入
wbtnmt279641@game.weibo.com----tkwd64604
anqolj010981@game.weibo.com----ifrc77555
pcgxus947873@game.weibo.com----heut19420
awiaeg229174@game.weibo.com----ijnd32834
pznfst800410@game.weibo.com----xoru05279
账号 wbtnmt279641@game.weibo.com 密码 tkwd64604
录入成功
账号 anqolj010981@game.weibo.com 密码 ifrc77555
录入成功
账号 pcgxus947873@game.weibo.com 密码 heut19420
录入成功
......
exit
```

先导入一部分账号之后再运行命令：

```
python3 run.py
```

## 运行之后会先进行微博模拟登录获取cookies,再进入weibo项目启动爬虫脚本

```
Cookies检测进程开始运行
API接口开始运行
Cookies生成进程开始运行
正在测试Cookies 用户名 wbtnmt279641@game.weibo.com
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
Cookies有效 wbtnmt279641@game.weibo.com
Cookies检测完成
正在生成Cookies 账号 anqolj010981@game.weibo.com 密码 ifrc77555
Cookies生成进程开始运行
正在生成Cookies 账号 anqolj010981@game.weibo.com 密码 ifrc77555
成功获取到Cookies {'M_WEIBOCN_PARAMS': 'uicode%3D20000174', 'SUB': '_2A25xgc7HDeRhGeBI41YT9CbNyzuIHXVSjdKPrDV6PUJbktAKLWX2kW1NRnqTbY2d2uotSFTU1kQbD9B7yW_xct-U', 'MLOGIN': '1', 'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WWATo1Wllqm.Dxd94V9blQ05JpX5KzhUgL.Foqc1hBEShnpehM2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMcSonXeoBReK5N', 'SUHB': '06ZVs1zZ5N2PhY', 'SSOLoginState': '1552268951', 'WEIBOCN_FROM': '1110006030', '_T_WM': 'a7709afbe589f30ea3ae289d92c308ad', 'XSRF-TOKEN': 'a1148a'}
成功保存Cookies
......

```
