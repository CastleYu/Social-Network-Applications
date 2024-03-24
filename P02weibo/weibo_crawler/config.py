from selenium.webdriver.common.by import By

DOC = "微博登录方法"

URL = "url"
LOGIN_NAME = 'login_name'
PWD = 'password'
LOGIN_BUTTON = 'login_button'
QRCODE = 'qr_code'
PRECONDITION = "precondition_click"

LOGIN_METHOD = [
    {
        URL: "https://weibo.com/login.php",
        LOGIN_NAME: {
            By.ID: "loginname",
            By.XPATH: '//*[@id="loginname"]',
            By.CSS_SELECTOR: '#loginname'
        },
        PWD: {
            By.XPATH: '//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input',
            By.CSS_SELECTOR: '#pl_login_form > div > div:nth-child(3) > div.info_list.password > div > input'
        },
        LOGIN_BUTTON: {

        },
        QRCODE: {
            PRECONDITION: [
                {
                    By.XPATH: '//*[@id="pl_login_form"]/div/div[1]/div/a[2]',
                    By.CSS_SELECTOR: '#pl_login_form > div > div.info_header > div > a:nth-child(2)'
                },
            ],
            By.XPATH: '//*[@id="pl_login_form"]/div/div[2]/img',
            By.CSS_SELECTOR: '#pl_login_form > div > div.login_content > img'
        }
    },
    {
        URL: "https://my.sina.com.cn/profile/unlogin/"
    }
]
