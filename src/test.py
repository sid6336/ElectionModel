# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 10:30:23 2018

@author: miro.gregorovic
"""
import pandas as pd
import os as os
from lib.lib1 import *


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

dfInputAgg = dfInput.groupby(['CIS_KRAJ','KSTRANA'], as_index = False).mean()

#Get df: Strana Dic(STRANA_NAME, KSTRANA)
dfStranaName = fnDict(dfInput,'KSTRANA','NAZ_STR')
dfKrajName = fnDict(dfInput,'CIS_KRAJ','NAZ_KRAJ')

#Get df: KRAJ, allocated MANDATY
dfKrajMandaty = fnKrajMandaty(dfInputAgg,iTotalSeats)

#Get df: KRAJ,STRANA,SUM(HLASY) for given KVORUM
dfKrajStranaKvorum = fnKrajStranaKvorum(dfInputAgg,fKvorum)
#dfKrajStranaKvorum = dfKrajStranaKvorum.loc[dfKrajStranaKvorum['CIS_KRAJ'] ==7]
#iTotalMandaty = 8
####1.D'Hodnt, Kraje

lKrajStranaHlasy = fnDfToList(dfKrajStranaKvorum)

  #input: lKrajStranaHlasy=[[CIS_KRAJ,KSTRANA,HLASY]], dfKrajMandaty=[CIS_KRAJ,Mandaty] 
lKraj = fnListUniqueKraj(lKrajStranaHlasy) 
output = []
for i in lKraj:
    newinput = []     
    iMandatForKraj = fnMandatForKraj(dfKrajMandaty,i)   
    for j in range(len(lKrajStranaHlasy)):         
        if lKrajStranaHlasy[j][0] == i:
            newinput.append(lKrajStranaHlasy[j])             
          #print ("{} and {}".format(i,kraj_strana_hlasy[j][0]))
    #print (newinput)

    #lDhondt = fnDhondtSingle(newinput,iMandatForKraj)
    #for kraj in lDhondt:
    #    output.append(kraj)
    #iMandatForKraj = int(iMandatForKraj)
    for mandat in range(iMandatForKraj):
        print (mandat)
        
#print (output)

'''
    temp=[]
    #Hlasy position in the list j=2:[CIS_KRAJ,KSTRANA,HLASY,MANDATY], j=1:[KSTRANA,HLASY,MANDATY] 
    j = len(lKrajStranaHlasy[0]) - 1
      
      #expand kraj_strana_hlasy for #of seats = 0  
    for i in lKrajStranaHlasy:
        i.append(0) 
      #temp - vote input to d'hondt    
    for i in range(len(lKrajStranaHlasy)):
        temp.append(lKrajStranaHlasy[i][j])
        hlasy = temp      
        mandaty = [0 for H in hlasy]
        quotients = [float(H) for H in hlasy]
    for mandat in range(iMandatForKraj):
        assigned = quotients.index(max(quotients))
        mandaty[assigned] += 1
        quotients[assigned] = hlasy[assigned] / float(mandaty[assigned] + 1)
          #transform assigned: 0 ->[0][[3]], 1-> [1][3]            
        lKrajStranaHlasy[assigned][j+1] +=1  
print (lKrajStranaHlasy)
'''

'''
def fnDhondt(lKrajStranaHlasy,dfKrajMandaty):
  #input: lKrajStranaHlasy=[[CIS_KRAJ,KSTRANA,HLASY]], dfKrajMandaty=[CIS_KRAJ,Mandaty] 
  lKraj = fnListUniqueKraj(lKrajStranaHlasy) 
  output = []
  for i in lKraj:
      newinput = []     
      iMandatForKraj = fnMandatForKraj(dfKrajMandaty,i)
      for j in range(len(lKrajStranaHlasy)):         
          if lKrajStranaHlasy[j][0] == i:
              newinput.append(lKrajStranaHlasy[j])             
              #print ("{} and {}".format(i,kraj_strana_hlasy[j][0]))
      lDhondt = fnDhondtSingle(newinput,iMandatForKraj)
      for kraj in lDhondt:
          output.append(kraj)
  return output #[[]]
 
def fnDhondtSingle(lKrajStranaHlasy, iTotalMandaty):
  #input: lKrajStranaHlasy=[CIS_KRAJ,KSTRANA,HLASY], iTotalMandaty  
  temp=[]
  #Hlasy position in the list j=2:[CIS_KRAJ,KSTRANA,HLASY,MANDATY], j=1:[KSTRANA,HLASY,MANDATY] 
  j = len(lKrajStranaHlasy[0]) - 1
  
  #expand kraj_strana_hlasy for #of seats = 0  
  for i in lKrajStranaHlasy:
      i.append(0)
     
  #temp - vote input to d'hondt    
  for i in range(len(lKrajStranaHlasy)):
      temp.append(lKrajStranaHlasy[i][j])
  hlasy = temp      
  mandaty = [0 for H in hlasy]
  quotients = [float(H) for H in hlasy]
  for mandat in range(iTotalMandaty):
    assigned = quotients.index(max(quotients))
    mandaty[assigned] += 1
    quotients[assigned] = hlasy[assigned] / float(mandaty[assigned] + 1)
    #transform assigned: 0 ->[0][[3]], 1-> [1][3]            
    lKrajStranaHlasy[assigned][j+1] +=1  
  return lKrajStranaHlasy
  
  '''