from lxml import etree

from weibo_service import *

if __name__ == "__main__":
    cookie_file_path = 'weibo_cookie.json'

    # 尝试从本地文件读取cookie
    cookie_dict = read_cookie_from_file(cookie_file_path)

    if cookie_dict is None or 'SUB' not in cookie_dict:
        with WeiboService('default') as weibo:
            weibo.start()
            weibo.minimize_window()
            weibo.login()
            sub_cookie = weibo.get_cookie_by_name('SUB')
            if sub_cookie:
                # 假设这里直接获取到了cookie的字典形式
                cookie_dict = {'SUB': sub_cookie}
                save_cookie_to_file(cookie_dict, cookie_file_path)

    cookie = cookie_dict
    param = {
        'q': '赵丽颖'
    }
    url = 'https://s.weibo.com/weibo'
    response = requests.get(url, params=param, cookies=cookie)
    html = etree.HTML(response.text)

    # 使用XPath定位元素
    # 假设我们想要定位页面上所有的<h1>标签
    h1_tags = html.xpath('//*[@id="pl_feedlist_index"]/div[2]')
    elem = h1_tags[0]
    save_element_content_to_file(elem, 'div.html')
    # 遍历找到的元素
    for tag in h1_tags:
        print(tag.text)  # 打印每个<h1>标签的文本内容
