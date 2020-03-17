import json
import re 
import string
import difflib
import requests
import extract_fromxml as ex
import copy

class Get_Custable:

    def __init__(self,Doc_data):
        self.line_regex=Doc_data["Line"]
        """
        works on the subline or multiple liner rows.
        extracts the data column wise
        type: Column name
        imp: required or not
        start_position: index of word list
        end_position: end index of word list
        separator: string by which list is checked 
        line_no: line number on which the word exists 
        """

        self.End_Row=False #status to get final response
    
    
    def extract_ingersol_data(self,data_response): #from the response extracts the data column wise

        line_items={
            
            "Item Number":'',
            "Description":'',
            "Unit Price":'',
            "UOM":'',
            "Quantity":'',
            # "Need By":'',
            "Amount":'',
            # "Supplier Item":'',
        }
        subrow=False
        sublist={}
        line_items={}
        final_respose=[]
        for l_index, line in enumerate(data_response):
            for s_index,ele in enumerate(line):
                if isinstance(ele,str):
                    data=[i for i in ele.split(' ') if len(i)>0]
  
                    if "Promised:" in data:
                        index=data.index("Needed:")
                        line_items["Item Number"]=data[1]
                        line_items["Description"]=data[-1]
                        line_items["Unit Price"]=data[8]
                        line_items["UOM"]=data[7]
                        line_items["Quantity"] = data[6]
                        # line_items["Need By"] = data[index+1]
                        line_items["Amount"] = data[index-1]
                      
                    elif ("Needed:" in data) and ("Promised:" not in data):
                        index=data.index("Needed:")
                        line_items["Item Number"]=data[1]
                        line_items["Description"]=data[-1]
                        line_items["Unit Price"]=data[8]
                        line_items["UOM"]=data[7]
                        line_items["Quantity"] = data[6]
                        # line_items["Need By"] = data[index+1]
                        line_items["Amount"] = data[-2]
                        self.End_Row=True
                    else:
                        print(ele)
                        line_items["Item Number"]=data[1]
                        line_items["Description"]=data[-1]
                    
                else:
                    print("Sub",ele)
                    try:
                        data_sub=[i.split(" ") for i in ele if "Needed:" in i if i][0]
                    except:
                        data_sub=''
                        try:
                            #check for next row
                            if line[s_index+1]:
                                continue
                        except:
                            subrow=True
                            

                    if ("Needed:" in data_sub) and ("Promised:" not in data_sub):
                        index=data_sub.index("Needed:")
                        sublist["Unit Price"]=data_sub[-3]
                        sublist["UOM"]=data_sub[index+3]
                        sublist["Quantity"] = data_sub[index+2]
                        sublist["Need By"] = data_sub[index+1]
                        sublist["Amount"] = data_sub[-1]

                        try:
                            if line[s_index+1]:
                                subrow=True
                        except:
                            subrow=True
                    
                if subrow:
                    result_merge={**line_items,**sublist}
                    sublist={}
                    final_respose.append(result_merge)
                    result_merge={}
                    sub_row=False

                try:
                    #check for next row
                    if line[l_index+1]:
                        continue
                except:
                    break

        return final_respose
    

    def extract_sl_data(self,data_response):
        line_items={
            
            "Item Number":'',
            "Description":'',
            "Unit Price":'',
            "UOM":'',
            "Quantity":'',
            # "Need By":'',
            "Amount":'',
            # "Supplier Item":'',
        }
        subrow=False
        sublist={}
        line_items={}
        final_respose=[]
        for l_index, line in enumerate(data_response):
            for s_index,ele in enumerate(line):
                if isinstance(ele,str):
                    line_items["Description"]=ele

                else:
                    subrow=True
                if subrow:
                    data=[i.split(" ") for i in ele if i][0]
                    line_items["Item Number"] = str(ele[0].split(" ")[0][5:])+str("".join(ele[1].split(" ")[0:2]))
                    line_items["Unit Price"]=data[2]
                    line_items["UOM"]=ele[1].split(" ")[2]
                    line_items["Quantity"] = data[1]
                    line_items["Need By"] = data[-1]
                    line_items["Amount"] = data[-2]
                    subrow=False
            final_respose.append(line_items)
            line_items={
            
            "Item Number":'',
            "Description":'',
            "Unit Price":'',
            "UOM":'',
            "Quantity":'',
            # "Need By":'',
            "Amount":'',
            # "Supplier Item":'',
            }  
        
        return final_respose