# -*- coding: utf-8 -*-
"""
Project: Volebni Model CR (Election Model - Czech Republic) - DHondt, HagenbachBishoff
author: sid6336@gmail.com
Python Version: Python 3
Date: 20180930
"""

import pandas as pd
import os as os
import glob
from lib.lib1 import *

##Input - Parameters
#input Path: one level up, /inputFoo
sPathInput = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'inputFoo'))
sPathOutput = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'outputFoo'))
#https://stackoverflow.com/questions/5013532/open-file-by-filename-wildcard
sPathInput = sPathInput #+ '\czvolby_ps2017*.xlsx'
'''
xlsx = glob.glob(sPathInput)

for filename in xlsx:
   filename_woextenstion, file_extension = os.path.splitext(filename)
   if file_extension != 'xlsx':
       exit()

for filename in os.listdir(sPathInput):
   filename_woextenstion, file_extension = os.path.splitext(filename)
   if file_extension <>'xlsx':
       exit()
'''
print (sPathInput)
filename = '\\czvolby_ps2017_20180919.xlsx' #'volbytest.xlsx'
sSheetName = 'DATA_RAW'
iTotalSeats = 200
fKvorum = 0.05

#Grain: CIS_KRAJ, KSTRAN, KANDIDAT
dfInput = fnXlsLoader(sPathInput,filename,sSheetName)
#Aggregate raw data CIS_KRAJ, KSTRANA
dfInputAgg = dfInput.groupby(['CIS_KRAJ','KSTRANA'], as_index = False).mean()

#Get df: Strana Dic(STRANA_NAME, KSTRANA)
dfStranaName = fnDict(dfInput,'KSTRANA','NAZ_STR')
dfKrajName = fnDict(dfInput,'CIS_KRAJ','NAZ_KRAJ')

#Get df: KRAJ, allocated MANDATY
dfKrajMandaty = fnKrajMandaty(dfInputAgg,iTotalSeats)

#Get df: KRAJ,STRANA,SUM(HLASY) for given KVORUM
dfKrajStranaKvorum = fnKrajStranaKvorum(dfInputAgg,fKvorum)

####1.D'Hodnt, Kraje
lOutDhodnt = fnDhondt(fnDfToList(dfKrajStranaKvorum),dfKrajMandaty)
dfOutDhodnt = pd.DataFrame(lOutDhodnt)
dfOutDhodnt.columns = ['CIS_KRAJ','KSTRANA','HLASY','MANDATY']

#dfStranaSeat = dfOutDhodnt.groupby(['KSTRANA'],as_index = False)[['HLASY','MANDATY']].sum()
dfStranaNameSeatDHM = pd.merge(dfOutDhodnt,dfStranaName,on ='KSTRANA', how='inner')
#dfStranaNameSeatDHM = dfStranaNameSeatDHM.sort_values('MANDATY', ascending = False)
dfStranaNameSeatDHM = fnAddColumn(dfStranaNameSeatDHM,'Model','DHM')

####2.D'Hodnt, 1 region
dfStranaHlasy = fnSumGrpCol1(dfKrajStranaKvorum,'KSTRANA','HLASY_x')
lOutDhodnt1 = fnDhondtSingle(dfStranaHlasy.values.tolist(),iTotalSeats)
dfOutDhodnt1 = pd.DataFrame(lOutDhodnt1)
dfOutDhodnt1.columns = ['KSTRANA','HLASY','MANDATY']
dfStranaNameSeatDH1 = pd.merge(dfOutDhodnt1,dfStranaName,on ='KSTRANA', how='inner')
dfStranaNameSeatDH1 = dfStranaNameSeatDH1.sort_values('MANDATY', ascending = False)
dfStranaNameSeatDH1 = fnAddColumn(dfStranaNameSeatDH1,'Model','DH1')

####3.H-B, 1region
dfStranaSeat = fnHagenbachBishoff1 (dfKrajStranaKvorum, iTotalSeats)
dfStranaNameSeatHB1 = pd.merge(dfStranaSeat,dfStranaName,on ='KSTRANA', how='inner')
dfStranaNameSeatHB1 = fnAddColumn(dfStranaNameSeatHB1,'Model','HB1')

####4.H-B, multiregion
dfKrajMandaty = fnKrajMandaty(dfInputAgg,iTotalSeats)
dfKrajStranaSeat = fnHagenbachBishoffMulti(dfKrajStranaKvorum,dfKrajMandaty)
dfStranaNameSeatHBM = pd.merge(dfKrajStranaSeat,dfStranaName,on ='KSTRANA', how='inner')
dfStranaNameSeatHBM = fnAddColumn(dfStranaNameSeatHBM,'Model','HBM')

### All in one sheet
dfFinalOutput = pd.DataFrame([])
lModels = [dfStranaNameSeatDHM,dfStranaNameSeatDH1,dfStranaNameSeatHBM,dfStranaNameSeatHB1]
for model in lModels:
    dfFinalOutput = dfFinalOutput.append(model)
#KRAJ_NAME
dfFinalOutput = pd.merge(dfFinalOutput,dfKrajName,on ='CIS_KRAJ', how='inner')


'''
dfFinalOutput = dfFinalOutput.append(dfStranaNameSeatDHM)
dfFinalOutput = dfFinalOutput.append(dfStranaNameSeatDH1)
'''
####Write to XLSX
#sPathOutput
writer = pd.ExcelWriter(sPathOutput + '\\output.xlsx')

dfFinalOutput.to_excel(writer, 'All', index=False)
dfStranaNameSeatDHM.to_excel(writer, 'KRAJ_DHONDT', index=False)
dfStranaNameSeatDH1.to_excel(writer, '1Reg_DHONDT', index=False)
dfStranaNameSeatHBM.to_excel(writer, 'KRAJ_HB', index=False)
dfStranaNameSeatHB1.to_excel(writer, '1Reg_HB', index=False)

writer.save()
writer.close()
