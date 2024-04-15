from datetime import date, datetime, timedelta

from lxml.cssselect import CSSSelector

from time_util import convert_time_desc_to_datetime
from weibo_service import *
from xls_writer import *


def get_cookie(try_from_file=True):
    cookie_file_path = 'weibo_cookie.json'
    cookie_dict = None
    if try_from_file:
        cookie_dict = read_cookie_from_file(cookie_file_path)

    if cookie_dict is None or 'SUB' not in cookie_dict:
        with WeiboCookieService(WeiboCookieService.DEEAULT) as weibo:
            weibo.start()
            weibo.minimize_window()
            weibo.login()
            sub_cookie = weibo.get_cookie_by_name('SUB')
            if sub_cookie:
                cookie_dict = {'SUB': sub_cookie}
                save_cookie_to_file(cookie_dict, cookie_file_path)

    return cookie_dict


def handel_feed(feed_content):
    blog_id = feed.attrib.get('mid')
    blogger_info = CSSSelector('div.card > div.card-feed > div.content > div.info > div:nth-child(2) > a')(
        feed)
    if blogger_info:
        blogger_name = blogger_info[0].get('nick-name')
        blogger_url = blogger_info[0].get('href').lstrip('//')
        blogger_url = "https://" + blogger_url.replace("?refer_flag=1001030103_", '')
    else:
        blogger_name = ''
        blogger_url = ''
    verified = CSSSelector('div.card > div.card-feed > div.avator > a > span')(feed)
    verified_type = verified[0].get('title') if verified else ''

    is_weibo_vip = CSSSelector(
        'div.card > div.card-feed > div.content > div.info > div:nth-child(2) > div > img')(
        feed)
    if is_weibo_vip:
        is_weibo_vip = '是'
    else:
        is_weibo_vip = '否'

    blog_content = CSSSelector('div.card > div.card-feed > div.content > p')(feed)
    blog_content = blog_content[0].xpath('string()').strip() if blog_content else ''

    post_time = CSSSelector('div.card > div.card-feed > div.content > div.from > a:nth-child(1)')(feed)
    post_time = post_time[0].text.strip() if post_time else ''
    post_time = convert_time_desc_to_datetime(post_time, now)

    blog_from = CSSSelector('div.card > div.card-feed > div.content > div.from > a:nth-child(2)')(feed)
    blog_from = blog_from[0].text.strip() if blog_from else ''

    repost_count = CSSSelector('div.card > div.card-act > ul > li:nth-child(1) > a > span')(feed)
    repost_count = repost_count[0].tail.strip() if repost_count else -1
    if repost_count == '转发':
        repost_count = 0
    comment_count = CSSSelector('div.card > div.card-act > ul > li:nth-child(2) > a > span')(feed)
    comment_count = comment_count[0].tail.strip() if comment_count else -1
    if comment_count == '评论':
        comment_count = 0
    like_count = CSSSelector(
        'div.card > div.card-act > ul > li:nth-child(3) > a > button > span.woo-like-count')(feed)
    like_count = like_count[0].text.strip() if like_count else -1
    if like_count == '赞':
        like_count = 0
    return [blog_id, blogger_name, blogger_url, verified_type, is_weibo_vip, blog_content, post_time,
            blog_from, repost_count, comment_count, like_count]


def raise_for_banned(head, _url):
    if head.get("SERVER", None) == 'nginx' or "need_login" in _url:
        raise NotImplementedError("You are banned from nginx")


if __name__ == "__main__":

    cookie = get_cookie()
    name = ['微博id', '博主昵称', '博主主页', '微博认证', '微博会员', '微博内容', '发布时间', '微博来源', '转发',
            '评论', '赞']
    query_content = input("输入你要搜索的内容:")
    # query_content = "泛式"

    current_date = date(2024, 4, 14)
    items_cnt = 0

    step = STEP
    while items_cnt <= 10000:
        with XlsWriter(f"{query_content}_微博数据.xlsx", name) as wr:
            for i in range(1, 51):
                former_date = current_date - timedelta(days=step)
                param = {
                    'q': query_content,
                    'page': i,
                    "typeall": 1,
                    "suball": 1,
                    "timescope": f"custom:{former_date.strftime("%Y-%m-%d")}:{current_date.strftime("%Y-%m-%d")}"
                }
                url = 'https://s.weibo.com/weibo'
                try:
                    resp = requests.get(url, params=param, cookies=cookie)
                except requests.exceptions.RequestException as e:
                    print("网络连接出现问题:{e}")
                    continue

                # 检查 cookie 是否失效
                try:
                    raise_for_banned(resp.headers, resp.url)
                except NotImplementedError:
                    print("Cookie失效")
                    cookie = get_cookie(try_from_file=False)
                    resp = requests.get(url, params=param, cookies=cookie)

                # 构建文档树
                now = datetime.now()
                all_content = etree.HTML(resp.text)
                feed_list_items = all_content.xpath('//*[@action-type="feed_list_item"]')

                # 检查页码超标
                page_checker = CSSSelector('#pl_feedlist_index > div.m-page > div > span > a')(all_content)
                if page_checker:
                    page = page_checker[0].text.strip(' 第页')
                    if int(page) != i:
                        # print("寻找到末尾，页码为{}".format(i - 1))
                        break
                else:
                    no_result = CSSSelector('#pl_feedlist_index > div.card-wrap > div')(all_content)
                    if no_result:
                        # print("未找到更多内容")
                        break
                items_cnt += len(feed_list_items)
                for feed in feed_list_items:
                    content = handel_feed(feed)
                    print(f'\r [items_cnt={items_cnt}] [index={i}] {content[6]} ', end='')
                    wr.add_item(content)
        current_date = current_date - timedelta(days=step + 1)
