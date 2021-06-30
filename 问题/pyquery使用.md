1. lxml安装
```
在系统中安装python-lxml而不是直接使用pip安装lxml
```
2. xml解析
* 使用 ```doc = pq(response.text)```
```
ValueError: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
```
* 使用 ```doc = pq(response.content)``` 或 ```doc = pq(response.text.encode("UTF-8"))```
``` 
不能使用doc('li')获取信息
```
* 使用 ```doc = pq(response.content, parser="html")``` 或 ```doc = pq(response.text.encode("UTF-8", parser="html"))```
``` 
可以
```
