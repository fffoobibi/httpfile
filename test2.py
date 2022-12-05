# _# _coding;utf-8 _*_
# 开发团队：明日科技
# 开发人员：$(USER)
# 开发时间：$(DATE)$(TIME)
# 文件名：$(NAME).py
# 开发工具：$(PRODUCT_NAME)
# 导包
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

wd = webdriver.Chrome(service=Service(executable_path=r"C:\Users\admin\Desktop\chromedrivers\chromedriver_107_0_5304_62.exe"))

wd.get('https://www.vip-cdkeysales.com/signin')

element = wd.find_element(By.CSS_SELECTOR, '#pclogin > div.d_register > div > div > div > div > ul > li.clearfix > input')
element.send_keys('495024719@qq.com\n')

element = wd.find_element(By.CSS_SELECTOR, '#pclogin > div.d_register > div > div > div > div > ul > li.capital > input')
element.send_keys('111111\n')

# time.sleep(2000)
# wd.find_element(By.CSS_SELECTOR,'#pclogin > div.d_register > div > div > div > div > div > button').click()
# time.sleep(5)

time.sleep(5)

ret = wd.find_element(By.CSS_SELECTOR, 'body > header > div.web_top.container > form > div > input')

ret.send_keys('office\n')
time.sleep(5)

element = wd.find_element(By.CSS_SELECTOR, 'body > div.bs-example.bs-example-form.search-form.warp_page > div > ul > li:nth-child(1) > a > p.title-one > span').click()

windows = wd.window_handles
wd.switch_to.window(windows[-1])

element = wd.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/section/div/div/div/div/div[1]/div/div[3]/div/div[2]/span').click()
time.sleep(5)
element = wd.find_element(By.CSS_SELECTOR, 'body > div.main.clearfix > div.web-main.container.shopping-bg.clearfix > div.table-div > ul.table-ul.web_changes > li:nth-child(3) > div > input')
element.send_keys('2222')

# time.sleep(5)
# element = wd.find_element(By.CSS_SELECTOR, 'body > div.main.clearfix > div.web-main.container.shopping-bg.clearfix > div.table-div > ul.table-ul.web_changes > li:nth-child(3) > div > input').send_keys('2')
# element = wd.find_element(By.CSS_SELECTOR, '#buy_now').click()
# time.sleep(500)
