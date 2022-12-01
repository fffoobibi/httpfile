# _# _coding;utf-8 _*_
# 开发团队：明日科技
# 开发人员：$(USER)
# 开发时间：$(DATE)$(TIME)
# 文件名：$(NAME).py
# 开发工具：$(PRODUCT_NAME)
#导包
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


try:
    op = Options()
    op.add_argument('--proxy-server=http://%s' %
                    '54.177.104.82:20000'
                    # '35.87.179.92:20033'
                    )

    wd = webdriver.Chrome(executable_path=r"C:\Users\admin\Desktop\chromedrivers\chromedriver_107_0_5304_62.exe", chrome_options=op)

    wd.get('https://www.vip-cdkeysales.com/signin')

    element=wd.xxxaaa(By.CSS_SELECTOR,'#pclogin > div.d_register > div > div > div > div > ul > li.clearfix > input')
    element.send_keys('495024719@qq.com\n')

    element=wd.xxxaaa(By.CSS_SELECTOR,'#pclogin > div.d_register > div > div > div > div > ul > li.capital > input')
    element.send_keys('111111\n')

    #time.sleep(2000)
    # wd.find_element(By.CSS_SELECTOR,'#pclogin > div.d_register > div > div > div > div > div > button').click()
    # time.sleep(5)

    time.sleep(5)

    ret=wd.xxxaaa(By.CSS_SELECTOR,'body > header > div.web_top.container > form > div > input')

    ret.send_keys('office\n')
    time.sleep(5)

    element=wd.xxxaaa(By.CSS_SELECTOR,'body > div.bs-example.bs-example-form.search-form.warp_page > div > ul > li:nth-child(1) > a > p.title-one > span').click()


    windows=wd.window_handles
    wd.switch_to.window(windows[-1])
except Exception as e:
    print(e.__class__)
    print(e)

