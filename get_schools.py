from bs4 import BeautifulSoup
import requests
import re
import sys
import xlwt
import xlrd
from xlutils.copy import copy

# 获取html
def getHtmlText(url, code="GBK"):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return "获取html异常"

# 解析页码
def getPageCode(htext, typeitem):
    try:
        soup = BeautifulSoup(htext, "html.parser")
        s1 = soup.find('a', attrs={'class': 'last'})
        if (s1):
            pat = re.compile(typeitem + r'pn([0-9]+).html')
            if (s1.get('href')):
                code = pat.search(s1.get('href'))
                if (code):
                    return code.group(1)
        else:
            return 0

    except:
        print("getPageCode异常")

# 获取全国城市
def getCitys(htext):
    try:
        cfile = r'city.xls'
        soup = BeautifulSoup(htext, "html.parser")
        sclist = soup.find_all('div', attrs={'class':'city-all'})

        for item in sclist:
            sl = item.find_all('a')
            for city in sl:
                pinyin = city.get('href')[7:-19]
                print(city.text, pinyin)
                if len(pinyin) != 0:
                    saveCity(cfile, city.text, pinyin)

        print("获取成功")
    except:
        print("getCitys 异常")

# 保存到excel
def saveCity(fileAddress, name, pinyin):
    workbook = xlrd.open_workbook(fileAddress, 'w+b')
    sheet = workbook.sheet_by_index(0)
    wb = copy(workbook)
    ws = wb.get_sheet(0)
    rowNum = sheet.nrows
    ws.write(rowNum, 0, name)
    ws.write(rowNum, 1, pinyin)
    wb.save(fileAddress)

# 解析行政区信息
def getAreaList(htext, cityItem):
    try:
        soup = BeautifulSoup(htext, "html.parser")
        tlist = soup.find_all('dl', attrs={'class': 'nobackground'})

        areaDict = {}
        for item in tlist:
            alist = item.find_all('a')
            links = []
            for ainfo in alist:
                areaDict[ainfo.get('href')] = ainfo.text
        print(areaDict)
        return  areaDict
    except:
        print("getAreaList异常")

# 解析类型
def getType(link):
    try:
        if "youeryuan" in link:
            return "幼儿园"
        elif "xiaoxue" in link:
            return "小学"
        elif "chuzhong" in link:
            return "初中"
        elif "gaozhong" in link:
            return "高中"
        elif "daxue" in link:
            return "大学"
        elif "chengren" in link:
            return "机构"
    except:
        print("getType异常")

# 解析学校信息，返回学校名称、地址、电话、网址
def getSchoolList(htext, fileAddress, cityitem, area, type):
    try:
        soup = BeautifulSoup(htext, "html.parser")
        sclist1 = soup.find_all('dl', attrs={'class': 'left'})
        sclist2 = soup.find_all('dl', attrs={'class': 'right'})
        sclist = sclist1 + sclist2

        for item in sclist:
            hInfo = getHtmlText(item.find('p').find('a').get('href'))
            parseSchoolInfo(hInfo, fileAddress, cityitem, area, item, type)
    except:
        print("getSchoolList异常")

def parseSchoolInfo(htext, fileAddress, cityitem, area, cItem, type):
    try:
        schoolDict = {}
        soup = BeautifulSoup(htext, "html.parser")
        sclist = soup.find_all('div', attrs={'class':'detail-xx clearfix'})

        for item in sclist:
            schoolDict['城市'] = cityitem
            schoolDict['行政区'] = area
            schoolDict['类型'] = type
            schoolDict['学校名称'] = cItem.find('p').text
            sl = item.find_all('li')
            for s in sl:
                if "地址" in s.text:
                    schoolDict['地址'] = s.text.lstrip("地址：")
                elif "邮编" in s.text:
                    schoolDict['邮编'] = s.text.lstrip("邮编：")
                elif "电话" in s.text:
                    schoolDict['电话'] = s.text.lstrip("电话：")
                elif "网站" in s.text:
                    schoolDict['网站'] = s.text.lstrip("网站：")
                elif "公交路线" in s.text:
                    schoolDict['公交路线'] = s.text.lstrip("公交路线：")
                elif "附近地标" in s.text:
                    schoolDict['附近地标'] = s.text.lstrip("附近地标：")
                elif "学校性质" in s.text:
                    schoolDict['学校性质'] = s.text.lstrip("学校性质：")
            print(schoolDict)
            savefile(schoolDict, fileAddress)
    except:
        print("parseSchoolInfo异常")


# 保存到excel
def savefile(schoolDict, fileAddress):
    workbook = xlrd.open_workbook(fileAddress, 'w+b')
    sheet = workbook.sheet_by_index(0)
    wb = copy(workbook)
    ws = wb.get_sheet(0)
    rowNum = sheet.nrows
    ws.write(rowNum, 0, schoolDict['城市'])
    ws.write(rowNum, 1, schoolDict['行政区'])
    ws.write(rowNum, 2, schoolDict['类型'])
    ws.write(rowNum, 3, schoolDict['学校名称'])
    ws.write(rowNum, 4, schoolDict['地址'])
    ws.write(rowNum, 5, schoolDict['电话'])
    if "网站" in schoolDict.keys():
        ws.write(rowNum, 6, schoolDict['网站'])
    if "公交路线" in schoolDict.keys():
        ws.write(rowNum, 7, schoolDict['公交路线'])
    if "附近地标" in schoolDict.keys():
        ws.write(rowNum, 8, schoolDict['附近地标'])
    if "学校性质" in schoolDict.keys():
        ws.write(rowNum, 9, schoolDict['学校性质'])
    wb.save(fileAddress)

# 获取城市列表,城市由EXCEL文件存储
def getCityList():
    try:
        cityFileAddress = r'city.xls'
        file = xlrd.open_workbook(cityFileAddress)
        sheet = file.sheet_by_name('city')
        cityDic = {}
        for i in range(sheet.nrows):
            key = sheet.col_values(0)[i]
            value = sheet.col_values(1)[i].lower()
            cityDic[key] = value
        return cityDic
    except:
        print("getCityList失败")


def getAllInfo():
    # 加载所有城市
    cityList = getCityList()
    fileAddress = r'schools.xls'
    for cityitem in cityList:
        # for typeitem in typeList:
        searchUrl = 'http://' + cityList[cityitem] + '.xuexiaodaquan.com'
        htext = getHtmlText(searchUrl)
        #行政区
        areaList = getAreaList(htext, cityitem)
        for link in areaList:
            # 类型
            type = getType(link)
            schoolUrl = searchUrl + link
            stext = getHtmlText(schoolUrl)
            getSchoolList(stext, fileAddress, cityitem, areaList[link], type)
            # 翻页
            pagecode = int(getPageCode(htext, link))
            if pagecode != 0:
                for i in range(2, pagecode + 1):
                    h1text = getHtmlText(searchUrl + link + 'pn' + str(i) + '.html')
                    getSchoolList(h1text, fileAddress, cityitem, areaList[link], type)

if __name__ == '__main__':
    # 获取http://www.xuexiaodaquan.com/下所有可以获得的城市信息表 city.xls
    # url  = "http://www.xuexiaodaquan.com/"
    # htext = getHtmlText(url)
    # getCitys(htext)

    # 获取city.xls下城市所有学校
    getAllInfo()
