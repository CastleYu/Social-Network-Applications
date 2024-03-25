from weibo_service import *
from config import *

def main():
    wc = WeiboService()
    while True:
        wc.start()
