# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import Question
from django.shortcuts import render_to_response
from django.template import RequestContext
# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone

##IMPORT FILE
# import pandas as pd
import numpy as np
import os
from pandas import Series,DataFrame
import itertools
import datetime as dt
import time
import re

## END IMPORT FILE 
def index(request):
	latest_question_list = Question.objects.order_by('-pub_date')[:5]
	context = {'latest_question_list': latest_question_list}
	return render(request, 'polls/index.html', context)
    
# def detail(request, question_id):
# 	question = get_object_or_404(Question, pk=question_id)
# 	return render(request, 'polls/detail.html', {'question': question})

# def results(request, question_id):
#   #respose = "You're looking at the results of question %s."
# 	return HttpResponse(response, '' )

def vote(request, question_id):
	return HttpResponse("You're voting on question %s." % question_id)
# def submit(request):
# 	info = request.GET['your_name']

def hello(request):
  try:
	direc = request.POST.get(r'input_sheets')
	calc_direc = request.POST.get(r'calculated_sheets')
	output_direc = request.POST.get(r'output_sheets')
	#----------------------------------Setting the directory-----------------------------------------#
    #direc = "C:\\Users\\600018630\\Documents\\OtherProjects\\CromptonDispatchPlanning\\Input_Sheets"
    #----------------------------------Setting the directory-----------------------------------------#
	#direc = "C:\\Users\\600018630\\Documents\\OtherProjects\\CromptonDispatchPlanning\\Input_Sheets"
	os.chdir(direc)
	#print(repr(direc))
	#os.chdir(r'C:\Python27\Dispatc-Planning-Tool\Input_Sheets')
	in_time = time.clock()
	##################################################################################################
	#----------------------------------Reading the input Files---------------------------------------#
	setting = pd.read_csv("Setting.csv")
	print("setting", setting)
	STPO = pd.read_csv("STPO.csv")
	print("STPO", STPO)
	Dispatch_File = pd.read_csv("Dispatch_File.csv")
	Closing_Stock = pd.read_csv("Closing_Stock.csv") 
	Inward = pd.read_csv("Inward.csv")
	Monthly_Plan = pd.read_csv("Monthly_Plan.csv")
	STPO_Prio = pd.read_csv("STPO_Priority.csv")
	Location_master = pd.read_csv("Location_Master.csv")
	Box_list = pd.read_csv("Box_list.csv")
	allocated_df = pd.read_csv("Allocated.csv")
	#Priority = pd.read_csv("Priority.csv")
	###################################################################################################
	#----------------------------Modifying the STPO sheet based on Originating document---------------#
	###################################################################################################
	today_date = dt.datetime.now().day
	STPO.insert(3,column = "STPO_Cut_Off",value = None,allow_duplicates = True)
	STPO_new = pd.merge(STPO,STPO_Prio,how  = "left",left_on = "Originating document",right_on = "STPO Number")
	STPO_new.loc[:,"STPO_Cut_Off"] = STPO_new["Priority"]
	STPO_new.drop(["STPO Number","Priority"],axis = 1,inplace = True)


	###################################################################################################
	#----------------------------Creating the pivot sheets -------------------------------------------#
	###################################################################################################
	#STPO_Pivot = pd.pivot_table(STPO_new,index = ["Material","STPO_Cut_Off"],columns = "Plant",values = "Open quantity",aggfunc = "sum")
	STPO_Pivot = pd.pivot_table(STPO_new,index = ["Material","STPO_Cut_Off"],columns = ["Plant"],values = "Open quantity",aggfunc = "sum")
	Dispatch_File_Pivot = pd.pivot_table(Dispatch_File,index = "Material Code",columns = "Receiving Plant",values = "GIT Qty",aggfunc = "sum")
	Closing_Stock_Pivot = pd.pivot_table(Closing_Stock,index = "Material",values = "Unrestricted",aggfunc = "sum")
	Inward_Pivot = pd.pivot_table(Inward,index = "Material",values = "qty",aggfunc = "sum")

	###################################################################################################
	#--------------------------- Modifying Monthly Plan sheet ----------------------------------------#
	###################################################################################################
	setting_dict = {}
	for i in range(0,setting.shape[0]):
		x = setting["Day.1"][i]
		setting_dict[x] = setting["STOP Cut Off Date"][i]



	M_cols = Monthly_Plan.columns
	M_cols = M_cols[3:len(M_cols)]

	M_cols_new = [y + "Cut_Off" for y in M_cols]
	Monthly_Cutoff = DataFrame(0,index = range(0,Monthly_Plan.shape[0]),columns = M_cols_new)
	ratio_vals = list(setting["Cut off in %"])
	ratio_vals.append(ratio_vals[0])
	ratio_vals_series = Series(ratio_vals*(Monthly_Cutoff.shape[0]/4))

	for j in range(0,Monthly_Cutoff.shape[1]):
		Monthly_Cutoff.iloc[:,j] = Monthly_Plan.iloc[:,j+3]*ratio_vals_series
		
	Monthly_Plan_full = pd.concat([Monthly_Plan,Monthly_Cutoff],axis = 1)
	Monthly_Plan_Cutoff = pd.concat([Monthly_Plan[["Item Name","Date"]],Monthly_Cutoff],axis = 1)
	Monthly_Plan_Cutoff.columns = [zx for zx in Monthly_Plan.columns if zx != "Key"]
	Monthly_Plan_Cutoff.insert(2,column = "Key",value = Monthly_Plan_Cutoff["Item Name"] + "_" + 
							   Monthly_Plan_Cutoff["Date"])

	zzz = list(Monthly_Plan_Cutoff.columns[0:3])
	zzz.extend([(xzz + "_Plan") for xzz in Monthly_Plan_Cutoff.columns[3:]])
	Monthly_Plan_Cutoff.columns = zzz
	###############################################################################################################################
	#--------------------------------------------- Creating STPO Vs Plan Sheet----------------------------------------------------#
	###############################################################################################################################
	locations = list(Location_master["TP/ DC"])
	M_cols_output = [(z + "_Plan",z + "_STPO",z + "_Net") for z in locations]
	M_cols_final = list(itertools.chain.from_iterable(M_cols_output))

	unique_mat = STPO["Material"].unique()
	material_quart = np.repeat(unique_mat,4)

	cut_offs = list(setting["Day.1"])
	cut_offs.append("M+1_7th")
	stpo_cutoffs_list = cut_offs*len(unique_mat)

	STPO_Vs_Plan_sub = DataFrame({"Material":material_quart,"STPO_Cut_Offs":stpo_cutoffs_list})
	Plan_df = DataFrame(index = STPO_Vs_Plan_sub.index,columns = M_cols_final)
	STPO_Vs_Plan_Final = pd.concat([STPO_Vs_Plan_sub,Plan_df],axis = 1)



	STPO_Vs_Plan_Final.insert(2,column = "Key",value = STPO_Vs_Plan_Final["Material"] + "_" + 
							  STPO_Vs_Plan_Final["STPO_Cut_Offs"])

	Plan_list = filter(lambda abc:"Plan" in abc,list(STPO_Vs_Plan_Final.columns))
	STPO_Vs_Plan_Final1 = STPO_Vs_Plan_Final

	for i in Plan_list:
		if i in Monthly_Plan_Cutoff.columns:
			STPO_Vs_Plan_Final1.loc[:,i] = pd.merge(STPO_Vs_Plan_Final[["Key"]],Monthly_Plan_Cutoff[["Key",i]],
								   how = "left",on = "Key")[i]
			
	loc_code_dict = {}        

	for i in range(0,Location_master.shape[0]):
		loc_code_dict[Location_master["Code"][i]] = Location_master["TP/ DC"][i]
		
	STPO_Pivot_new = STPO_Pivot
	STPO_Pivot_new.reset_index(inplace = True)
	STPO_Pivot_new.insert(2,"Key",value = STPO_Pivot_new["Material"] + "_" + STPO_Pivot_new["STPO_Cut_Off"])
	STPO_Pivot_new.rename(columns = loc_code_dict,inplace = True)

	fff = list(STPO_Pivot_new.columns[0:3])  
	ff = [(z + "_STPO") for z in STPO_Pivot_new.columns[3:]]
	fff.extend(ff)
	STPO_Pivot_new.columns = fff

	STPO_list = filter(lambda k:"_STPO" in k,list(STPO_Vs_Plan_Final.columns))

	for i in STPO_list:
		if i in STPO_Pivot_new.columns:
			STPO_Vs_Plan_Final1.loc[:,i] = pd.merge(STPO_Vs_Plan_Final[["Key"]],STPO_Pivot_new[["Key",i]],
								   how = "left",on = "Key")[i]
			
	Net_list = filter(lambda k : "_Net" in k,STPO_Vs_Plan_Final1)
	STPO_Vs_Plan_Final1.fillna(0,inplace = True)

	for i in locations:
		plan_col = i + "_Plan"
		stpo_col = i + "_STPO"
		net_col = i + "_Net"
		
		STPO_Vs_Plan_Final1.loc[:,net_col] = STPO_Vs_Plan_Final[[plan_col,stpo_col]].min(axis = 1)
		

	##############################################################################################
	#----------------------------- Creation of Priority sheet -----------------------------------#
	##############################################################################################  
	Net_require_df = STPO_Vs_Plan_Final1[Net_list]
	for i in range(0,3):
		Net_require_df.insert(i,column = STPO_Vs_Plan_Final1.columns[i],value = STPO_Vs_Plan_Final1.iloc[:,i])

	Priority_df = DataFrame({"TP/DC" : np.repeat(Location_master["TP/ DC"],4)})
	Priority_df["LT"] = pd.merge(Priority_df,Location_master[["TP/ DC","LT from Ambala"]],how = "left",left_on="TP/DC",
			   right_on = "TP/ DC")["LT from Ambala"]
	Priority_df.reset_index(inplace = True,drop = True)
	Priority_df["Date"] = cut_offs*(Priority_df.shape[0]/4)
	Priority_df["Net Requirement"] = None
	Priority_df["Days Remaining"] = None
	Priority_df["Priority"] = None
	deduct_dict = {"M_7th":7,"M_15th":15,"M_25th":25,"M+1_7th":37}

	for i in Net_list:
		coll = i.replace("_Net","")
		Require_M_7th = Net_require_df.loc[Net_require_df["STPO_Cut_Offs"] == "M_7th",i].sum()
		Require_M_15th = Net_require_df.loc[Net_require_df["STPO_Cut_Offs"] == "M_15th",i].sum()
		Require_M_25th = Net_require_df.loc[Net_require_df["STPO_Cut_Offs"] == "M_25th",i].sum()
		Require_M1_7th = Net_require_df.loc[Net_require_df["STPO_Cut_Offs"] == "M+1_7th",i].sum()      
		LT = list(Location_master.loc[Location_master["TP/ DC"] == coll,"LT from Ambala"])[0]
		
		date_ser = Series([Require_M_7th,Require_M_15th,Require_M_25th,Require_M1_7th])
		Priority_df.loc[Priority_df["TP/DC"] == coll,"Net Requirement"] = list(date_ser)
		
		remain_M_7th = (7-today_date) if (7-today_date-LT) > 0 else 0
		remain_M_15th = (15-today_date) if (15-today_date-LT) > 0 else 0
		remain_M_25th = (25-today_date) if (25-today_date-LT) > 0 else 0
		remain_M1_7th = (37-today_date) if (37-today_date-LT) > 0 else 0
		
		remain_ser = Series([remain_M_7th,remain_M_15th,remain_M_25th,remain_M1_7th])
		Priority_df.loc[Priority_df["TP/DC"] == coll,"Days Remaining"] = list(remain_ser)

	Priority_df_sorted = Priority_df.sort_values(by = ["Days Remaining","Net Requirement"],ascending = [True,False])    
	Priority_df_sorted.reset_index(drop = True,inplace = True)
	##############################################################################################
	#--------------------------------Allocation Logic -------------------------------------------#
	##############################################################################################
	allocated_df_new = allocated_df
	allocated_df_new.iloc[:,2:] = allocated_df_new.iloc[:,2:].applymap(lambda x :None)
	Item_list = Net_require_df["Material"].unique()
	for j in range(0,Priority_df_sorted.shape[0]):
		print ("Running Priority number : {} out of {}".format(j+1,Priority_df_sorted.shape[0]))
		Location = Priority_df_sorted["TP/DC"][j]
		colll = Location + "_Net" 
		date_ = Priority_df_sorted["Date"][j]
		
		for v in Item_list:
			requirement = 0
			requirement1 = 0
			stock = 0
			aloc_qty = 0
			Net_require_sub_df = Net_require_df[["Material","STPO_Cut_Offs","Key",colll]]
			Item = list(Net_require_sub_df.loc[Net_require_sub_df["Key"] == (v + "_" + date_),"Material"])[0]
			requirement = list(Net_require_sub_df.loc[Net_require_sub_df["Key"] == (v + "_" + date_),colll])[0]

			inward = Inward_Pivot.loc[v,"qty"] if v in Inward_Pivot.index else 0
			stock = Closing_Stock_Pivot.loc[v,"Unrestricted"] if v in Closing_Stock_Pivot.index else 0
			allocated_sub_df = allocated_df.loc[allocated_df["Item Name"] == Item,:]
			aloc_qty = allocated_sub_df.sum().dropna().values[2:].sum()
			
			allocated_df_new.loc[(allocated_df_new["Item Name"] == Item) & (allocated_df_new["Date"] == date_),
								 Location] = min(inward + stock - aloc_qty,requirement)

	###################################################################################################
	#-----------------------------Other Output sheets ------------------------------------------------#
	###################################################################################################
	allocated_box = allocated_df_new
	allocated_box = pd.merge(allocated_box,Box_list,how = "left",left_on = "Item Name",right_on = "CATREF")
	allocated_box.drop("CATREF",inplace = True,axis = 1)
	allocated_box.iloc[:,2:(allocated_box.shape[1]-1)] = allocated_box.iloc[:,2:(allocated_box.shape[1]-1)].div(allocated_box["BOX"],axis = 0)

	###################################################################################################
	#-------------------------------------------Printing out the calculated sheets--------------------#
	###################################################################################################
	#os.chdir(r'C:\Python27\Dispatc-Planning-Tool\Calculated_Sheets')
	os.chdir(calc_direc)
	#print(repr(calc_direc))
	#os.chdir(r"C:\Users\600018630\Documents\OtherProjects\CromptonDispatchPlanning\Calculated_Sheets")
	STPO_Pivot.to_csv("STPO_Pivot.csv")
	Dispatch_File_Pivot.to_csv("Dispatch_Pivot.csv")
	Closing_Stock_Pivot.to_csv("Closing_Stock_Pivot.csv")
	Inward_Pivot.to_csv("Inward_Pivot.csv")

	###################################################################################################
	#------------------------------------------Printing out the Result sheets ------------------------#
	###################################################################################################
	#os.chdir(r'C:\Python27\Dispatc-Planning-Tool\Output_Sheets')
	os.chdir(output_direc)
	#print(repr(output_direc))
	#os.chdir(r"C:\Users\600018630\Documents\OtherProjects\CromptonDispatchPlanning\Output_Sheets")
	allocated_df_new.to_csv("Allocated.csv",index = False) 
	allocated_box.to_csv("BOX_WISE_Allocation.csv",index = False) 

	out_time = time.clock()
	tot_time  = out_time - in_time

	print ("Total_time taken :{} minutes".format(tot_time/60))
	return render_to_response('polls/hello.html')
	# return HttpResponse("Successfully Done")
  except Exception:
    import traceback
    print traceback.format_exc()
    return HttpResponse("Error")