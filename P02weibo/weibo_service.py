from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from browser import *
from config import *
from utils import *


class WeiboService(ChromeBrowser):
    def __init__(self, profile='test'):
        super().__init__(profile)

    def preconditional_click(self, precondition_list: list):
        """前置条件点击"""
        for feature_dict in precondition_list:
            for by, value in feature_dict.items():
                try:
                    elem = self.driver.find_element(by, value)
                    try:
                        elem.click()
                        return True
                    except Exception as e:
                        print(e)
                        print("When processing preconditional click:")
                        print("\tElement founded, but error occurred when trying to click")
                        if input('Press Enter to Finish Preconditional Click') == '':
                            return False
                        else:
                            continue
                except NoSuchElementException:
                    continue
        else:
            raise KeyError("There is a preconditional click, but no element founded")

    def find_elemnet_by_dict(self, feature_dict: dict):
        # 处理前置条件点击，并且记录Flag-是否处理
        precondition = feature_dict.pop(PRECONDITION, None)
        if precondition:
            prec_did = self.preconditional_click(precondition)
        else:
            prec_did = True

        # 遍历寻找可用的键值对来寻找元素
        for by, value in feature_dict.items():
            try:
                elem = self.driver.find_element(by, value)
                return elem
            except NoSuchElementException:
                continue
        else:  # 未寻得报错
            if prec_did:
                raise KeyError("No element founded")
            else:
                raise KeyError("No element founded, and no preconditional click")

    # def monitor_page_change(self, initial_url='', to_be_url=''):
    #     if initial_url and to_be_url:
    #         return ValueError('Provide both initial_url and to_be_url')
    #     pass

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
        WebDriverWait(self.driver, 5).until(EC.url_contains("weibo.com/login"))
        if use_qr_code:
            feature_dict = method.get(QRCODE)
            element = self.find_elemnet_by_dict(feature_dict)
            WebDriverWait(self.driver, 10).until(lambda driver: element.get_attribute('src') != 'about:blank;',
                                                 f"[超时]等待元素属性")
            img_url = element.get_attribute('src')
            event = threading.Event()
            show_image_by_url(img_url, event)
            try:
                # 等待直到URL变为特定值
                WebDriverWait(self.driver, 120).until(EC.url_contains("weibo.com/u/"))
                event.set()
                return True
            except TimeoutException:
                print("[超时]URL没有变化")
                input('暂停操作, Press any key to continue...')
        else:
            raise Exception("由于验证码机制和安全性考虑，暂不启用账户密码登录")
        return False
