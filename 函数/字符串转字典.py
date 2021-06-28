def str2dict(dict_str):
    """
    等号分号(= ;)型字符串转字典
    :return: 字典cookie
    """
    json_data = json.dumps(dict_str)
    json_str = json.loads(json_data)
    cookie = dict([item.split("=", 1) for item in json_str.split(";")])
    return cookie


def escape2dict(es_str, escapes='\n'):
    """
    将下面两种形式的字符串分割为字典
    '会员时长\n5 天'
    '可用流量\n37.84 GB\n今日已用: 29.03MB'
    :param es_str: 字符串
    :param escapes: 转义符类型
    :return:
    """
    split_ret = [id.split(':', 1) for id in es_str.split('{}'.format(escapes))]
    ret_dict = {}
    flag = True
    for i, s in enumerate(split_ret):
        if len(s) == 2:
            ret_dict[str(s[0]).strip()] = s[1].strip()
            flag = True
        elif not flag:
            flag = True
        else:
            ret_dict[str(s[0]).strip()] = split_ret[i+1][0].strip()
            flag = False
    return ret_dict
