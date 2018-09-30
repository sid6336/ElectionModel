# -*- coding: utf-8 -*-
"""
Project: Library for Volebni_Model
author: sid6336@gmail.com
Python Version: Python 3
Date: 20180930
"""

import pandas as pd
import numpy as np

def fnSumCol1(dfs,ind_col):
    return dfs[ind_col].sum()

def fnSumGrpCol1(dfs,grp_col,ind_col):
    return dfs.groupby([grp_col],as_index = False)[[ind_col]].sum()

def fnSumGrp2Col1(dfs,grp_col1,grp_col2,ind_col,agg_fn,ascending_in):
    dfs = dfs.groupby([grp_col1,grp_col2], as_index = False).agg({ind_col: agg_fn})
    return dfs.sort_values(ind_col, ascending = ascending_in)

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

def fnAllocateSeatRemnat (df,grain,divider,totalSeats):   #grain: 'KSTRANA'
    df['NUMBER_SEAT'] = df['HLASY'] / divider
    df['NUMBER_FULL_SEAT'] = (df['HLASY'] / divider).apply(np.floor)
    df['NUMBER_SEAT_REMNANT'] = df['NUMBER_SEAT']- df['NUMBER_FULL_SEAT']
    df = df.sort_values('NUMBER_SEAT_REMNANT',ascending = False)

    #allocate mandaty nerozd
    iSeatNotAllo = int(totalSeats - fnSumCol1(df,'NUMBER_FULL_SEAT')) #3

    dfSeatNotAllo = df.head(iSeatNotAllo)
    dfSeatNotAllo['NUMBER_FULL_SEAT_2NDALLO'] = dfSeatNotAllo['NUMBER_FULL_SEAT'] + 1

    #Merge: original DF and dfSeatNotAllo (not allocated seats)
    df = pd.merge(df,dfSeatNotAllo, on = grain, how = 'left')
    df['NUMBER_SEAT_FINAL'] = np.where(df['NUMBER_FULL_SEAT_2NDALLO'].isnull() == False, df['NUMBER_FULL_SEAT_2NDALLO'], df['NUMBER_FULL_SEAT_x'])
    df = df[[grain,'HLASY_x','NUMBER_SEAT_FINAL']].sort_values('HLASY_x', ascending = False)

    return df


def fnHagenbachBishoff1 (dfKrajStranaKvorum, iTotalSeats):

    dfStranaHlasy = fnSumGrpCol1(dfKrajStranaKvorum,'KSTRANA','HLASY_x')
    dfStranaHlasy.columns = ['KSTRANA','HLASY']
    dfStranaHlasy = dfStranaHlasy.sort_values('HLASY',ascending = False)

    fHB = fnTotalHlasy(dfStranaHlasy) / iTotalSeats

    dfStranaSeat = fnAllocateSeatRemnat(dfStranaHlasy,'KSTRANA',fHB,iTotalSeats)
    #output.column['KSTRANA','HLASY','MANDATY']
    dfStranaSeat = dfStranaSeat[['KSTRANA','HLASY_x','NUMBER_SEAT_FINAL']]
    dfStranaSeat.columns = ['KSTRANA','HLASY','MANDATY']
    return dfStranaSeat #dfStranaSeat

def fnHagenbachBishoffMulti(dfKrajStranaKvorum,dfKrajMandaty):
   #input: lKrajStranaHlasy=[[CIS_KRAJ,KSTRANA,HLASY]], dfKrajMandaty=[CIS_KRAJ,Mandaty]
   lkraj = fnListUniqueKraj(fnDfToList(dfKrajStranaKvorum))
   dfOutput = pd.DataFrame([])
   for kraj in lkraj:
       dfInput = dfKrajStranaKvorum.ix[dfKrajStranaKvorum['CIS_KRAJ']==kraj]
       #iTotalSeats = fnMandatForKraj(dfMandatyKraj,kraj)
       iTotalSeats = dfKrajMandaty.loc[dfKrajMandaty['CIS_KRAJ']==kraj,'NUMBER_SEAT_FINAL'].item()
       dfForOutput = fnHagenbachBishoff1(dfInput,iTotalSeats)
       dfForOutput['CIS_KRAJ'] = kraj
       dfOutput = dfOutput.append(dfForOutput)

   #dfStranaSeat = dfKrajStrana.groupby(['KSTRANA'],as_index = False)[['HLASY','MANDATY']].sum()
   #dfStranaSeat = dfStranaSeat[['KSTRANA','HLASY','NUMBER_SEAT_FINAL']]
   #dfStranaSeat.columns = ['KSTRANA','HLASY','MANDATY']
   #dfStranaSeat = dfStranaSeat.sort_values('MANDATY', ascending = False)

   return dfOutput #df kraj,strana,seats

def fnMandatForKraj(dfMandatyKraj,iCisKraj):
    #input: original dfInput
    #fKrajMandaty: df(CIS_KRAJ,POCEET_MANDATY_FINAL) for given pocet_mandat(allocation proportionally based on HLASY)
    #dfMandatyKraj = fnKrajMandaty(df,pocet_mandatu)
    #output: for given kraj (iCisKraj)
    #return dfMandatyKraj.ix[dfMandatyKraj['CIS_KRAJ']==iCisKraj]['NUMBER_SEAT_FINAL']
    return int(dfMandatyKraj.loc[dfMandatyKraj['CIS_KRAJ']==iCisKraj]['NUMBER_SEAT_FINAL'])

def fnKrajMandaty(dfInputAgg,iTotalSeats):
    #input: dfInputAgg, iTotalSeats
    #function: fnRMC, fnSumCol1
    #group by CIS_KRAJ,SUM(Hlasy)
    dfKraj = dfInputAgg.groupby(['CIS_KRAJ'],as_index = False)['HLASY'].sum()

    RMC = fnTotalHlasy(dfKraj) / iTotalSeats
    output = fnAllocateSeatRemnat(dfKraj,'CIS_KRAJ',RMC,iTotalSeats)

    #output: df(CIS_KRAJ,POCET_MANDATY_FINAL)
    return output #dfKrajSeat

def fnKrajStranaKvorum(dfKrajStrana,fKvorum):
    #input: df(KRAJ,STRANA,HLASY); fKvorum e.g. 5%
    iTotalHlasy = fnTotalHlasy(dfKrajStrana)
    fKvorumHlasy = iTotalHlasy * fKvorum

    #dfStrana: SUM(HLASY) by KSTRANA
    dfStrana = fnSumGrpCol1(dfKrajStrana,'KSTRANA','HLASY')
    #Kvorum Test (x% of Total Hlasy)
    dfStrana['KVORUM_TEST'] = np.where(dfStrana['HLASY']>=fKvorumHlasy, 'Y','N')
    dfStranaKvorum = dfStrana.ix[dfStrana['KVORUM_TEST']=='Y']

    #merge: dfKrajStrana & dfStranaKvorum
    dfKrajStrana = fnSumGrp2Col1(dfKrajStrana,'CIS_KRAJ','KSTRANA','HLASY','sum', False)
    dfKrajStranaKvorum = pd.merge (dfKrajStrana,dfStranaKvorum, on ='KSTRANA', how='inner')
    dfKrajStranaKvorum = dfKrajStranaKvorum[['CIS_KRAJ','KSTRANA','HLASY_x']]
    return  dfKrajStranaKvorum

def fnRemoveRow(dfs,ind_col,row_value):
    dfs = dfs.dropna()
    return dfs[dfs[ind_col]!=row_value]

def fnTotalHlasy(df):
    return fnSumCol1(df,"HLASY")

def fnDict(dfInput,par1,par2):
    dfOutput = dfInput[[par1,par2]].drop_duplicates()
    #dfOutput = dfInput[['KSTRANA','NAZ_STR']].drop_duplicates()
    #return fnRemoveRow(dfOutput,par2, '(blank)')
    return dfOutput

def fnDfToList(df):
    #input: CIS_KRAJ, KSTRANA, Hlasy to LIST [[x,y,z]]
    return df.values.tolist()

def fnListUniqueKraj(lKrajStranaHlasy):
    lOutput = []
    for i in range(len(lKrajStranaHlasy)):
        lOutput.append(lKrajStranaHlasy[i][0])
    return list(set(lOutput))

def fnXlsWriter(df,sOutputName,sSheetName):
    writer = pd.ExcelWriter(sOutputName)
    df.to_excel(writer,sSheetName)
    #writer.save()

def fnXlsLoader(sFolderName,sFileName,sSheetName):
    #Function: Read and load XLSx data to DataFrame
    sFilePath = sFolderName + sFileName
    return pd.read_excel(sFilePath, sheetname=sSheetName)

def fnListToDF (lInput):
    return pd.DataFrame(lInput)

def fnAddColumn(df,sColumnName,sColumnValue):
    df[sColumnName] = sColumnValue
    return df
