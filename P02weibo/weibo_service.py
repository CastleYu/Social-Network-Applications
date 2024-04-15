from selenium.common import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from browser import *
from config import *
from utils import *


class WeiboCookieService(ChromeBrowser):
    def __init__(self, profile='test'):
        super().__init__(profile)

    def precondition_click(self, precondition_list: list):
        """前置条件点击"""
        for feature_dict in precondition_list:
            for by, value in feature_dict.items():
                try:
                    elem = self.driver.find_element(by, value)
                    try:
                        elem.click()
                        elem.click()
                        return True
                    except Exception as e:
                        print(e)
                        print("When processing precondition click:")
                        print("\tElement founded, but error occurred when trying to click")
                        if input('Press Enter to Finish Precondition Click') == '':
                            return False
                        else:
                            continue
                except NoSuchElementException:
                    continue
        else:
            raise KeyError("There is a precondition click, but no element founded")

    def find_element_by_dict(self, feature_dict: dict):
        """根据{By:Value}获取到目标元素"""
        # 处理前置条件点击，并且记录Flag-是否处理预点击队列
        precondition = feature_dict.pop(PRECONDITION, None)
        if precondition:
            pre_did = self.precondition_click(precondition)
        else:
            pre_did = True

        # 遍历寻找可用的键值对来寻找元素
        for by, value in feature_dict.items():
            try:
                elem = self.driver.find_element(by, value)
                return elem
            except NoSuchElementException:
                continue
        else:  # 未寻得报错
            if pre_did:
                raise KeyError("No element founded")
            else:
                raise KeyError("No element founded, and no precondition click")

    def login(self, username=None, password=None, use_qr_code=True):
        success = False
        index = 0
        while not success:
            success = self.try_login(index, username, password, use_qr_code)
            index += 1

    def try_login(self, index=0, username=None, password=None, use_qr_code=True):
        method = LOGIN_METHODS[index]
        url = method.get(URL)
        self.get(url)
        try:
            WebDriverWait(self.driver, 5).until(EC.url_contains("weibo.com/login"))
        except TimeoutException as e:
            print("未跳转")
            if self.get_current_url().endswith('weibo.com/'):
                print("已登录")
                return True

        # 二维码登录
        if use_qr_code:
            feature_dict = method.get(QRCODE)
            element = self.find_element_by_dict(feature_dict)
            WebDriverWait(self.driver, 10).until(lambda driver: element.get_attribute('src') != 'about:blank;',
                                                 f"[超时]等待元素属性")
            img_url = element.get_attribute('src')
            event = threading.Event()
            show_image_by_url(img_url, event)
            print("已显示图片")
            try:
                # 等待直到URL变为weibo.com 或者 weibo.com/u/
                pattern = r".*weibo\.com/(u/.*)?$"
                WebDriverWait(self.driver, 120).until(EC.url_matches(pattern))
                event.set()
                return True
            except TimeoutException:
                print("[超时]URL没有变化")
                input('暂停操作, Press any key to continue...')
        else:
            raise Exception("由于验证码机制和安全性考虑，暂不启用账户密码登录")
        return False


class WeiboService:
    def __init__(self):
        self.content = None
