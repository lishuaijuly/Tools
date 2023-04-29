import camelot
tables = camelot.read_pdf('进展公告.pdf') #类似于Pandas打开CSV文件的形式
print(len(tables))
tables[0].df # get a pandas DataFrame!
tables.export('foo.csv', f='csv', compress=True) # json, excel, html, sqlite，可指定输出格式
tables[0].to_csv('foo.csv') # to_json, to_excel, to_html, to_sqlite， 导出数据为文件
#tables
