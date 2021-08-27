* 常用于将获取的cookie转为字典
--------------
``` python
def str2dict(dict_str):
    """
    等号分号(= ;)型字符串转字典
    :return: 字典cookie
    """
    json_data = json.dumps(dict_str)
    json_str = json.loads(json_data)
    if ";" not in json_str:
        tmp_list = json_str.split("=", 1)
        cookie = {tmp_list[0]: tmp_list[1]}
    else:
        cookie = dict([item.split("=", 1) for item in json_str.split(";")])
    return cookie
```
