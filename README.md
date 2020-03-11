#1、get_schools.py
源代码
内含：1、获取所有可以查询到学校信息的城市信息（城市名、拼音）
      2、根据1生成的表格，爬学校信息数据

#2、city.xls
 从学校大全首页爬取的可以查询到学校信息的所有城市表

#3、schools.xls
最终保存抓取信息的表


将这三个文件放同一级目录，执行爬虫脚本就可以了。


#python3环境要求 :
pip install bs4
pip install requests
pip install xlrd
pip install xlutils
pip install re
