import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from config import *


class Browser:
    def __init__(self, profile, delay=3):
        # print(f'创建一个{profile}的Browser')
        self.profile = profile
        self.driver = None
        self.driver: WebDriver
        self.delay = 3

    def __getattr__(self, name):
        # 将对未定义属性或方法的调用委托给浏览器实例
        return getattr(self.driver, name)

    def start(self):
        raise NotImplementedError

    def get(self, url):
        if self.driver:
            self.driver.get(url)

    def set_delay(self, delay):
        self.delay = delay
        if self.driver:
            self.driver.implicitly_wait(self.delay)

    def get_current_url(self):
        if self.driver:
            return self.driver.current_url
        return None

    def get_cookies(self):
        if self.driver:
            return {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
        return None

    def get_cookie_by_name(self, name):
        if self.driver:
            return self.get_cookies().get(name, None)
        return None

    def calculate_loading_time(self):
        if self.driver:
            start_time = self.execute_script("return window.performance.timing.navigationStart;")
            end_time = self.driver.execute_script("return window.performance.timing.loadEventEnd;")
            return end_time - start_time
        return None

    def is_ready(self) -> bool:
        if self.driver:
            ready_state = self.driver.execute_script("return document.readyState;")
            return ready_state == "complete"
        return False

    def maximize_window(self):
        if self.driver:
            self.driver.maximize_window()

    def minimize_window(self):
        if self.driver:
            self.driver.minimize_window()

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close()


class ChromeBrowser(Browser):
    """ChromeSelenium的封装，提供启动、配置等功能。"""
    DEEAULT = 'default'
    USER = 'user'
    TEST = 'test'

    def __init__(self, profile=DEEAULT):
        super().__init__(profile)
        self.options = Options()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def __get_chrome_user_data_dir():
        """获取Chrome用户数据目录的路径"""
        path = BROWSER_USER_PROFILE_PATH_F.get('chrome').format(os.getlogin())
        print(f"正在使用默认配置{path}")
        return path

    def apply_user_data_dir(self):
        """配置Chrome选项"""
        if self.profile == self.USER:
            self.options.add_argument("user-data-dir=" + self.__get_chrome_user_data_dir())
        elif self.profile == self.DEEAULT:
            self.options.add_argument("profile-directory=Default")
        elif self.profile == self.TEST:
            test_path = os.path.join('test', 'profile')
            os.makedirs(test_path, exist_ok=True)
            self.options.add_argument('user-data-dir=' + os.path.abspath(test_path))

    def use_headless(self):
        self.options.add_argument("--headless")

    def start(self):
        if not self.driver:
            try:
                # print(f'以{self.profile}配置文件启动')
                self.apply_user_data_dir()
                self.driver = webdriver.Chrome(options=self.options)
                self.driver.implicitly_wait(self.delay)
            except Exception as e:
                print("Error starting the Chrome WebDriver:", e)


class WaitForCondition:
    def __init__(self, condition_function, *args, **kwargs):
        """
        初始化等待条件类。
        :param condition_function: 需要等待的布尔函数。
        :param args: 传递给布尔函数的位置参数。
        :param kwargs: 传递给布尔函数的关键字参数。
        """
        self.condition_function = condition_function
        self.args = args
        self.kwargs = kwargs

    def __call__(self, driver):
        """
        当被调用时，执行布尔函数并返回其结果。
        :param driver: Selenium WebDriver实例。
        :return: 布尔函数的返回值。
        """
        return self.condition_function(driver, *self.args, **self.kwargs)


# 使用示例
# def url_ends_with(driver, substrings):
#     """
#     自定义的布尔函数，检查当前URL是否以给定的字符串列表中的任一字符串结尾。
#     :param driver: Selenium WebDriver实例。
#     :param substrings: 字符串列表，包含URL可能的结尾。
#     :return: 如果URL以任一给定字符串结尾，返回True；否则返回False。
#     """
#     current_url = driver.current_url
#     return any(current_url.endswith(substring) for substring in substrings)
#
#
# try:
#     # 使用WaitForCondition类等待URL以指定的字符串结尾
#     WebDriverWait(driver, 120).until(WaitForCondition(url_ends_with, ["weibo.com/u/", "weibo.com/"]))
#     print("找到了符合条件的URL。")
# except TimeoutException:
#     print("在指定时间内没有找到符合条件的URL。")
