import pprint


def wr_cls(obj):
    if isinstance(obj, dict):
        data = dict(obj)
    else:
        data = obj.__dict__

    # 创建 PrettyPrinter 对象
    pp = pprint.PrettyPrinter(indent=4, width=40, depth=2)

    # 使用 pformat 获取格式化的字符串
    formatted_data = pp.pformat(data)

    # 将格式化的数据写入文件
    with open('output.txt', 'w') as file:
        file.write(formatted_data)
