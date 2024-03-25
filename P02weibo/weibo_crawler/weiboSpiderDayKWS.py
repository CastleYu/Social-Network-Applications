# -*- coding: utf-8 -*-
import datetime
import io
import re
import time

import cv2
import requests
import xlwt
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from weibo_crawler.browser import ChromeBrowser
from weibo_crawler.config import *

browser = ChromeBrowser("test")
browser.start()
exit(0)
# ********************************************************************************
#                            第一步: 登陆login.sina.com
#                     这是一种很好的登陆方式，有可能有输入验证码
#                          登陆之后即可以登陆方式打开网页
# ********************************************************************************




# def try_find_element(driver: webdriver.Chrome, feature_dict:dict):


def login_weibo(username, password):
    # try:
    # 输入用户名/密码登录
    print('准备登陆Weibo.cn网站...')
    method = LOGIN_METHOD[0]
    url = method.get(URL)
    driver.get(url)
    __preconditional_click(driver, method)
    # driver.find_element(By.CLASS_NAME, "hd_login").click()
    # input()
    # elem_user = driver.find_element(By.NAME, "loginname")
    # elem_user.send_keys(username)  # 用户名
    # elem_pwd = driver.find_element("xpath","/html/body/div[1]/div/div/div[2]/div[2]/form/div[2]/input")
    # elem_pwd.send_keys(password)  # 密码
    # elem_sub = driver.find_element("xpath","/html/body/div[1]/div/div/div[2]/div[2]/button")
    # elem_sub.click()  # 点击登陆 因无name属性
    # 扫码登录
    try:
        __preconditional_click(driver, method.get(QRCODE))
        elem_qrcode = driver.find_element(
            By.XPATH, '//*[@id="pl_login_form"]/div/div[2]/img')
    except NoSuchElementException:
        input("element is not found")
        exit(1)
    image_url = elem_qrcode.get_attribute('src')
    response = requests.get(image_url)
    # 将响应的内容转换为一个NumPy数组
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    # 从NumPy数组解码图像数据
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    # 显示图片
    cv2.imshow('Image', img)
    cv2.waitKey(0)  # 等待按键事件
    cv2.destroyAllWindows()  # 关闭显示窗口

    # 获取Coockie 推荐资料：http://www.cnblogs.com/fnng/p/3269450.html
    print('Crawl in ', driver.current_url)
    print('输出Cookie键值对信息:')
    for cookie in driver.get_cookies():
        print(cookie)
        for key in cookie:
            print(key, cookie[key])
    print('登陆成功...')
    # except Exception as e:
    #     print("Error: ", e)
    # finally:


print('End LoginWeibo!\n')


# ********************************************************************************
#                  第二步: 访问http://s.weibo.com/页面搜索结果
#               输入关键词、时间范围，得到所有微博信息、博主信息等
#                     考虑没有搜索结果、翻页效果的情况
# ********************************************************************************

def get_search_content(key):
    driver.get("http://s.weibo.com/")
    print('搜索热点主题：')

    # 输入关键词并点击搜索
    item_inp = driver.find_element(
        "xpath", '//*[@id="pl_homepage_search"]/div/div[2]/div/input')
    # item_inp = driver.find_element("xpath","//*[@id='pl_homepage_search']/div/div[2]/div/input")
    item_inp.send_keys(key)
    item_inp.send_keys(Keys.RETURN)  # 采用点击回车直接搜索

    time.sleep(5)
    input('等待下一步')
    # 获取搜索词的URL，用于后期按时间查询的URL拼接
    current_url = driver.current_url
    # http://s.weibo.com/weibo/%25E7%258E%2589%25E6%25A0%2591%25E5%259C%25B0%25E9%259C%2587
    current_url = current_url.split('&')[0]

    global start_stamp
    global page

    input('等待下一步')
    # 需要抓取的开始和结束日期，可根据你的实际需要调整时间
    start_date = datetime.datetime(2021, 2, 10)
    end_date = datetime.datetime(2021, 3, 10)
    delta_date = datetime.timedelta(days=1)

    # 每次抓取一天的数据
    start_stamp = start_date
    end_stamp = start_date + delta_date

    global outfile
    global sheet

    outfile = xlwt.Workbook(encoding='utf-8')

    while end_stamp <= end_date:
        page = 1

        # 每一天使用一个sheet存储数据
        sheet = outfile.add_sheet(start_stamp.strftime("%Y-%m-%d-%H"))
        init_xls()

        # 通过构建URL实现每一天的查询
        url = current_url + '&typeall=1&suball=1&timescope=custom:' + start_stamp.strftime(
            "%Y-%m-%d-%H") + ':' + end_stamp.strftime("%Y-%m-%d-%H") + '&Refer=g'
        driver.get(url)

        handle_page()  # 处理当前页面内容

        start_stamp = end_stamp
        end_stamp = end_stamp + delta_date
    input("等待下一步")


# time.sleep(1)

# ********************************************************************************
#                  辅助函数，考虑页面加载完成后得到页面所需要的内容
# ********************************************************************************

# 页面加载完成后，对页面内容进行处理


def handle_page():
    while True:
        # 之前认为可能需要sleep等待页面加载，后来发现程序执行会等待页面加载完毕
        # sleep的原因是对付微博的反爬虫机制，抓取太快可能会判定为机器人，需要输入验证码
        time.sleep(1)
        # 先行判定是否有内容
        if check_content():
            print("getContent")
            get_content()
            # 先行判定是否有下一页按钮
            if check_next():
                input("拿到下一页按钮")
                next_page_btn = driver.find_element(
                    "css_selector", "#pl_feedlist_index > div.m-page > div > a.next")
                next_page_btn.click()
            else:
                print("no Next")
                break
        else:
            print("no Content")
            break


# 判断页面加载完成后是否有内容
def check_content():
    # 有内容的前提是有“导航条”？错！只有一页内容的也没有导航条
    # 但没有内容的前提是有“pl_noresult”
    try:
        driver.find_element(
            "xpath", "//div[@class='card card-no-result s-pt20b40']")
        flag = False
    except:
        flag = True
    return flag


# 判断是否有下一页按钮
def check_next():
    try:
        driver.find_element(
            "css_selector", "#pl_feedlist_index > div.m-page > div > a.next")
        flag = True
    except:
        flag = False
    return flag


# 判断是否有展开全文按钮
def checkqw():
    try:
        driver.find_element(
            "xpath", ".//div[@class='content']/p[@class='txt']/a")
        flag = True
    except:
        flag = False
    return flag


# 在添加每一个sheet之后，初始化字段
def init_xls():
    name = ['博主昵称', '博主主页', '微博认证', '微博达人', '微博内容',
            '发布位置', '发布时间', '微博地址', '微博来源', '转发', '评论', '赞']

    global row
    global outfile
    global sheet

    row = 0
    for i in range(len(name)):
        sheet.write(row, i, name[i])
    row = row + 1
    outfile.save("./微博数据.xls")


# 将dic中的内容写入excel
def write_xls(dic):
    global row
    global outfile
    global sheet

    for k in dic:
        for i in range(len(dic[k])):
            sheet.write(row, i, dic[k][i])
        row = row + 1
    outfile.save("./微博数据.xls")


# 在页面有内容的前提下，获取内容
def get_content():
    # 寻找到每一条微博的class
    try:
        nodes = driver.find_element(
            "xpath", "//div[@class='card-wrap']/div[@class='card']")
    except Exception as e:
        print(e)

    # 在运行过程中微博数==0的情况，可能是微博反爬机制，需要输入验证码
    if len(nodes) == 0:
        input("请在微博页面输入验证码！")
        url = driver.current_url
        driver.get(url)
        get_content()
        return

    dic = {}

    global page
    print(start_stamp.strftime("%Y-%m-%d-%H"))
    print('页数:', page)
    page = page + 1
    print('微博数量', len(nodes))

    for i in range(len(nodes)):
        dic[i] = []
        try:
            BZNC = nodes[i].find_element(
                "xpath", ".//div[@class='content']/p[@class='txt']").get_attribute("nick-name")
        except:
            BZNC = ''
        print('博主昵称:', BZNC)
        dic[i].append(BZNC)

        try:
            BZZY = nodes[i].find_element(
                "xpath", ".//div[@class='content']/div[@class='info']/div[2]/a").get_attribute("href")
        except:
            BZZY = ''
        print('博主主页:', BZZY)
        dic[i].append(BZZY)
        # 微博官方认证，没有爬取
        try:
            WBRZ = nodes[i].find_element(
                "xpath", ".//div[@class='info']/div/a[contains(@title,'微博')]").get_attribute('title')  # 若没有认证则不存在节点
        except:
            WBRZ = ''
        print('微博认证:', WBRZ)
        dic[i].append(WBRZ)

        try:
            WBDR = nodes[i].find_element(
                "xpath", ".//div[@class='feed_content wbcon']/a[@class='ico_club']").get_attribute(
                'title')  # 若非达人则不存在节点
        except:
            WBDR = ''
        print('微博达人:', WBDR)
        dic[i].append(WBDR)

        # 判断展开全文和网页链接是否存在
        try:
            nodes[i].find_element(
                "xpath", ".//div[@class='content']/p[@class='txt']/a[@action-type='fl_unfold']").is_displayed()
            flag = True
        except:
            flag = False
        # 获取微博内容
        try:
            if flag:
                nodes[i].find_element(
                    "xpath", ".//div[@class='content']/p[@class='txt']/a[@action-type='fl_unfold']").click()
                time.sleep(1)
                WBNR = nodes[i].find_element(
                    "xpath", ".//div[@class='content']/p[2]").text.replace("\n", "")
                # 判断发布位置是否存在
                try:
                    nodes[i].find_element(
                        "xpath", ".//div[@class='content']/p[@class='txt']/a/i[@class='wbicon']").is_displayed()
                    flag = True
                except:
                    flag = False
                # 获取微博发布位置
                try:
                    if flag:
                        pattern = nodes[i].find_element(
                            "xpath", ".//div[@class='content']/p[2]/a[i[@class='wbicon']]")
                        if isinstance(pattern, list):
                            text = [p.text for p in pattern]
                            FBWZ = [loc for loc in [re.findall(
                                '^2(.*$)', t) for t in text] if len(loc) > 0][0][0]
                        else:
                            text = pattern.text
                            FBWZ = re.findall('^2(.*$)', text)[0]
                    else:
                        FBWZ = ''
                except:
                    FBWZ = ''
            else:
                WBNR = nodes[i].find_element(
                    "xpath", ".//div[@class='content']/p[@class='txt']").text.replace("\n", "")
                # 判断发布位置是否存在
                try:
                    nodes[i].find_element(
                        "xpath", ".//div[@class='content']/p[@class='txt']/a/i[@class='wbicon']").is_displayed()
                    flag = True
                except:
                    flag = False
                # 获取微博发布位置
                try:
                    if flag:
                        pattern = nodes[i].find_element(
                            "xpath", ".//div[@class='content']/p[@class='txt']/a[i[@class='wbicon']]")
                        if isinstance(pattern, list):
                            text = [p.text for p in pattern]
                            FBWZ = [loc for loc in [re.findall(
                                '^2(.*$)', t) for t in text] if len(loc) > 0][0][0]
                        else:
                            text = pattern.text
                            FBWZ = re.findall('^2(.*$)', text)[0]
                    else:
                        FBWZ = ''
                except:
                    FBWZ = ''
        except:
            WBNR = ''
        print('微博内容:', WBNR)
        dic[i].append(WBNR)

        print('发布位置:', FBWZ)
        dic[i].append(FBWZ)

        try:
            FBSJ = nodes[i].find_element(
                "xpath", ".//div[@class='content']/p[@class='from']/a[1]").text
        except:
            FBSJ = ''
        print('发布时间:', FBSJ)
        dic[i].append(FBSJ)

        try:
            WBDZ = nodes[i].find_element(
                "xpath", ".//div[@class='content']/p[@class='from']/a[1]").get_attribute("href")
        except:
            WBDZ = ''
        print('微博地址:', WBDZ)
        dic[i].append(WBDZ)

        try:
            ZF_TEXT = nodes[i].find_element(
                "xpath", ".//a[@action-type='feed_list_forward']").text
            if ZF_TEXT == '转发':
                ZF = 0
            else:
                ZF = int(ZF_TEXT.split(' ')[1])
        except:
            ZF = 0
        print('转发:', ZF)
        dic[i].append(ZF)
        print('\n')

    # 写入Excel
    write_xls(dic)


# *******************************************************************************
#                                程序入口
# *******************************************************************************
if __name__ == '__main__':
    # 定义变量
    username = ""  # 输入你的用户名
    password = ""  # 输入你的密码

    # 操作函数
    login_weibo(username, password)  # 登陆微博
    # 搜索热点微博爬取评论
    # 关键词请根据实际需要进行替换
    # 请搜索和疫情有关的一些非敏感关键词
    # 注意：如果输入的是“疫情”“武汉”“中国”这样的敏感词汇，微博不会返回给你任何结果
    # 请尽量输入疫情相关又不会敏感的词汇，可以输入一些疫情支援人员的姓名试试看
    key = '#赵丽颖#'
    get_search_content(key)