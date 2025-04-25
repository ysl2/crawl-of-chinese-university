

# 获取大学名字的代码
###排名
# //*[@id="content-box"]/div[2]/table/tbody/tr[1]/td[1]/div(清华)
# //*[@id="content-box"]/div[2]/table/tbody/tr[2]/td[1]/div(北大)

###地区
# //*[@id="content-box"]/div[2]/table/tbody/tr[1]/td[3](清华大学——北京)
# //*[@id="content-box"]/div[2]/table/tbody/tr[2]/td[3](北京大学——北京)

###双一流？(到176为止)
####地区
# //*[@id="content-box"]/div[2]/table/tbody/tr[1]/td[3](清华大学——北京)
# //*[@id="content-box"]/div[2]/table/tbody/tr[2]/td[3](北京大学——北京)

###办学类型
# //*[@id="content-box"]/div[2]/table/tbody/tr[1]/td[4]( 清华)
# //*[@id="content-box"]/div[2]/table/tbody/tr[2]/td[4](北京大学)

###总分
# //*[@id="content-box"]/div[2]/table/tbody/tr[1]/td[5](清华)
# //*[@id="content-box"]/div[2]/table/tbody/tr[2]/td[5](北大)

##办学层次
# //*[@id="content-box"]/div[2]/table/tbody/tr[1]/td[6](清华)
# //*[@id="content-box"]/div[2]/table/tbody/tr[2]/td[6](北大)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree
import time
import json
import pandas as pd

def get_data(html, xpath):
    datas = html.xpath(xpath)
    if len(datas) != 0:
        return [d.strip() for d in datas][0] if datas else ""
    else:
        return ""

def get_university(content, rank):
    html = etree.HTML(content)

    result = {
        "排名": get_data(html, f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[1]/div/text()"),
        "大学名称": get_data(html, f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[2]/div/div[1]/a/text()") or
                  get_data(html, f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[2]/div/div[1]/img/@alt"),
        "所在地区": get_data(html, f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[3]/text()"),
        "办学计划": get_data(html, f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[2]/div/div[2]/p/text()"),
        "办学类型": get_data(html, f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[4]/text()"),
        "总分": get_data(html, f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[5]/text()"),
        "层次": get_data(html, f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[6]/text()")
    }

    return result

if __name__ == "__main__":
    # 配置 Chrome 无头浏览器
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # 使用 webdriver_manager 自动管理 ChromeDriver 版本
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)

    url = 'http://www.shanghairanking.cn/rankings/bcur/2025'
    browser.get(url)

    # 使用显式等待确保页面加载完成
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='content-box']/div[2]/table"))
    )

    data_list = []

    # 手动设置总页数为20页（根据实际情况调整）
    total_pages = 20
    print(f"总页数设置为: {total_pages}")

    for page in range(1, total_pages + 1):
        # 等待表格加载
        time.sleep(2)
        page_source = browser.page_source

        # 获取当前页的大学数量
        rows = len(etree.HTML(page_source).xpath("//*[@id='content-box']/div[2]/table/tbody/tr"))

        for i in range(1, rows + 1):
            university = get_university(page_source, i)
            if university["大学名称"]:  # 只添加有数据的大学
                data_list.append(university)

        print(f"第{page}页已加载，共{rows}条数据")

        if page < total_pages:
            try:
                # 尝试定位下一页按钮（使用更精确的定位方式）
                next_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(@class,'ant-pagination-next')]/a"))
                )
                browser.execute_script("arguments[0].click();", next_button)

                # 等待新页面加载
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='content-box']/div[2]/table"))
                )
            except Exception as e:
                print(f"翻页时出错: {str(e)}")
                # 如果点击下一页失败，尝试直接访问下一页URL
                next_url = f"{url}?page={page+1}"
                browser.get(next_url)
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='content-box']/div[2]/table"))
                )

    browser.quit()

    # 保存数据
    with open("中国大学.json", "w", encoding='utf-8') as fp:
        json.dump(data_list, fp, ensure_ascii=False, indent=2)

    # 转换为Excel
    df = pd.DataFrame(data_list)
    df.replace('', pd.NA, inplace=True)  # 将空字符串替换为NA
    df.dropna(how='all', inplace=True)  # 删除全为空的行
    df.to_excel("中国大学.xlsx", index=False)

    print(f"数据爬取完成，共爬取{len(data_list)}条数据，已保存到中国大学.json和中国大学.xlsx")
