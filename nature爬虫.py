import requests, time, os, json, random
from bs4 import BeautifulSoup as bs


def get_page_info(soup):
    ul = soup.find("ul", {"class":"app-article-list-row"})
    li_ls = ul.find_all("li", {"class":"app-article-list-row__item"})
    for li in li_ls:
        a = li.find("a", {"class":"c-card__link u-link-inherit"})
        href = "https://www.nature.com" + a.attrs["href"]
        with open("./nature/url_ls.txt", "at", encoding = 'utf-8') as fo:
            fo.write(href)
            fo.write('\n')
    pass


def process_soup(soup, url):
    article = soup.find("article")
    try:
        title = article.find('h1').string.strip()
    except:
        title = str(article.find('h1'))
        replace_ls = ["<sub>", "</sub>", "<sup>", "</sup>", "<i>", "</i>", "\n"]
        for replace_str in replace_ls:
            title = title.replace(replace_str, '')
        title = title.split('<')[-2].split('>')[-1]
    article_dic = {}
    article_dic[title] = {}
    sections = article.find_all("section")
    for section in sections:
        try:
            data_title = section.attrs["data-title"]
        except:
            continue
        article_dic[title][data_title] = []
        p_ls = section.find_all('p')
        for p in p_ls:
            p_1 = [sup.extract() for sup in soup("sup")]    # 去除p标签中的sup标签
            p_2 = [sup.extract() for sup in soup("sub")]    # 去除p标签中的sub标签
            article_dic[title][data_title].append(str(p).strip('<p>').strip('</p>'))
            # 这一句是从p标签中提取文本
    with open("./nature/thesis.json", "at", encoding = "utf-8") as fo:
        # 所有文献保存在同一个json文件中
        fo.write(json.dumps(article_dic))
        fo.write('\n')
        


def get_thesis():
    with open("./nature/url_ls.txt", "rt", encoding = 'utf-8') as fi:
        for i in fi:
            url = i.strip()
            header = {
                "authority":"www.nature.com",
                "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
            }
            r = requests.get(url, headers = header)
            r.encoding = r.apparent_encoding
            soup = bs(r.text, "html.parser")
            process_soup(soup, url)
            time.sleep(3 + random.random())
    print("文献爬取完成")
    pass


def main(input_string):
    url = "https://www.nature.com/search?q={}".format('+'.join(input_string.split()))
    header = {
        "authority":"www.nature.com",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
    }
    r = requests.get(url, headers = header)
    soup = bs(r.text, "html.parser")
    span = soup.find("div", {"class":"c-list-header"}).find("span", {"class":"u-display-flex"})
    num_of_thesis = int(span.find_all("span")[-1].string.split()[0])   # 这个是文献数量
    get_page_info(soup)   # 直接传入soup获取搜索页面信息
    page = num_of_thesis//50 + 1
    print("\r已完成 1/{}".format(page), end = '')
    if num_of_thesis <= 50:
        return 0
    for i in range(2, page + 1):
        time.sleep(2 + random.random())
        url_i = "https://www.nature.com/search?q={}&page={}".format('+'.join(input_string.split()), i)
        r = requests.get(url_i, headers = header)
        soup = bs(r.text, "html.parser")
        get_page_info(soup)
        print("\r已完成 {}/{}".format(i, page), end = '')
    print('\r获取搜索页面信息已完成')
    get_thesis()
    pass


input_string = input("请输入想搜索的内容：")
# input_string = "Alkane activation"
start = time.time()
main(input_string)
print("耗时 {}s".format(time.time() - start))
