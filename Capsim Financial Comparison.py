#!/usr/bin/env python
# coding: utf-8

# In[1]:


import matplotlib.pyplot as plt
import openpyxl
import pandas as pd
import numpy as np


# In[43]:


import openpyxl

wb = openpyxl.load_workbook(r'C:\Users\Karlm\Desktop\11.xlsx')

# 获取workbook中所有的表格
sheets = wb.sheetnames
names=['Andrews','Baldwin','Chester','Digby','Erie','Ferris']
print(sheets)
for i in sheets:
    ws = wb[i]
    data=pd.DataFrame(ws.values)
    print(data)
    plt.figure(figsize=(10,7))
    for f in range(0,6):
        print(names[f])
        plt.plot(data[0][1:],data[f+1][1:],label=names[f])
    plt.ylabel(data[0][0],fontsize=20)
    plt.legend(loc="best")
    plt.show()
    plt.close()


# In[ ]:




