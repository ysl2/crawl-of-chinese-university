

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
from selenium.webdriver.chrome.options import Options
from lxml import etree
import time
import json
import pandas as pd

# 获取页面数据/元素
def get_data(html, xpath):
    xpath_data = xpath
    datas = html.xpath(xpath_data)
    if len(datas) != 0:
        return [d.strip() for d in datas][0]
    else:
        return [d.strip() for d in datas]

# 解析大学信息
def get_university(content, rank):
    # 解析得到源码
    html = etree.HTML(content)

    # 提取排名信息
    xpath_university_ranks = f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[1]/div/text()"
    ranks = get_data(html, xpath_university_ranks)
    # 提取大学名称
    xpath_university_name = f"//*[@id='content-box']//div[2]/table/tbody/tr[{rank}]/td[2]/div/div[1]/img/@alt"
    name = get_data(html, xpath_university_name)
    # 提取所在地区
    xpath_university_district = f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[3]/text()"
    district = get_data(html, xpath_university_district)
    # 提取办学计划
    xpath_university_Plan = f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[2]/div/div[2]/p/text()"
    plan = get_data(html, xpath_university_Plan)
    # 提取办学类型
    xpath_university_type = f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[4]/text()"
    UtyOfType = get_data(html, xpath_university_type)
    # 提取总分
    xpath_university_score = f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[5]/text()"
    score = get_data(html, xpath_university_score)
    # 提取办学层次
    xpath_university_layer = f"//*[@id='content-box']/div[2]/table/tbody/tr[{rank}]/td[6]/text()"
    layer = get_data(html, xpath_university_layer)

    # 构建结果字典
    result = {
        "排名": ranks,
        "大学名称": name,
        "所在地区": district,
        "办学计划": plan,
        "办学类型": UtyOfType,
        "总分": score,
        "层次": layer
    }

    return result

if __name__ == "__main__":
        # 配置 Chrome 无头浏览器
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    chrome_options.binary_location = path

        # 启动 Chrome 浏览器
    browser = webdriver.Chrome(options=chrome_options)
    url = 'http://www.shanghairanking.cn/rankings/bcur/2023'
    browser.get(url)

    time.sleep(1)

    data_list = []
    for page in range(1+1, 21 + 1):
        page_source = browser.page_source
        for i in range(0, 30):
            university = get_university(page_source, i + 1)
            data_list.append(university)

        print(f"第{page - 1}页已经加载：")

        if page == 21:
            browser.save_screenshot("测试page20.png")
        else:
            # 模拟滚动到页面底部
            js_bottom = "document.documentElement.scrollTop=100000"
            browser.execute_script(js_bottom)
            # 等待2秒，确保页面加载完成
            time.sleep(2)
            #点击下一页
            nextPage = browser.find_element_by_link_text(f"{page}")
            nextPage.click()
            # 等待2秒，确保下一页加载完成
            time.sleep(2)

    browser.quit()

    # 将 Python 对象列表写入 JSON 文件
    with open("中国大学.json", "w", encoding='utf-8') as fp:
        json.dump(data_list, fp, ensure_ascii=False)

    # 读取 JSON 文件
    with open("中国大学.json", "r", encoding='utf-8') as fp:
        data_list = json.load(fp)

    # 将数据转为 DataFrame
    df = pd.DataFrame(data_list)

    # 将 DataFrame 写入 Excel 文件
    df.to_excel("中国大学.xlsx", index=False)

    # 读取 Excel 文件
    df1 = pd.read_excel("中国大学.xlsx")

    # 去除无效字符 '[]'
    df1.replace('[]', '',  inplace=True)

    # 将处理后的 DataFrame 写回 Excel 文件
    df1.to_excel("中国大学.xlsx", index=False)
