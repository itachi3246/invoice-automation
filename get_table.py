import json
import re 
import string
import difflib
import requests
import extract_fromxml as ex
import copy


class Get_table:

    def __init__(self,doctype=None,other_details=None):
        self.row_startno=None  #line number from where the table is extracted
        self.doctype=doctype #template of document
        self.row_endno=None #table end line number
        self.End_Row=False #status to get final response
        self.doc_po_date=other_details

        with open('config/states.json', 'r', encoding='utf-8') as data_file:
            self.state_name = json.load(data_file)
        with open('config/city.json', 'r', encoding='utf-8') as data_file:
            self.city_name = json.load(data_file)

    def extract_text(self,pdf_text): #from the text extracts the table rows
        
        for index,row in enumerate(pdf_text):  
            remove_space=row.replace(" ","") #from spaces from rows
            if any((difflib.SequenceMatcher(None,i,row).ratio()*100) > 60 for i in self.doctype["Start_Line"]):
            # if any(i in remove_space for i in self.doctype["Start_Line"] ):
                if not self.row_startno:
                    self.row_startno=index #updates the table start line number
                else:
                    if any(i in row for i in self.doctype["Ignore_Line"] ):
                        pass
                    else:
                        self.row_startno=index
        # (difflib.SequenceMatcher(None, state[1],val).ratio()*100) > 60
        for index,row in  reversed(list(enumerate(pdf_text))):  
            remove_space=row.replace(" ","")
            # if any((difflib.SequenceMatcher(None,i,row).ratio()*100) > 80 for i in self.doctype["End_Line"]):
            if any(i in remove_space for i in self.doctype["End_Line"]):
                if not self.row_endno:
                    self.row_endno=index #updates the table start line number
                else:
                    if any(i in row for i in self.doctype["Ship To:"] ):
                        pass
                    else:
                        self.row_endno=index
                # self.row_endno=index #updates the table end line number
                break
        # list_response=self.extract_rows(pdf_text)
        return pdf_text

    def extract_details(self,pdf_text):
        PO_details=self.doc_po_date["PO"]
        Date_details=self.doc_po_date["Date"]
        InvoiceID_details = self.doc_po_date["Invoice ID"]
        po_status=True
        date_status=True
        invid_status=True
        other_details={
            "Purchase no":'',
            "Order_Date":'',
            "Invoice ID":''
        }
        for l_index,line in enumerate(pdf_text):
            if PO_details['word'] in line:
                if po_status:               
                    data_line=pdf_text[l_index+PO_details["line"]].split(PO_details["word"])
                    # data_line=[x for x in data_line if x]
                    if PO_details["direction"] =="right":
                        other_details["Purchase no"]=data_line[1].split()[PO_details["index"]]
                        po_status=False
                    elif PO_details["direction"] =="down":
                        other_details["Purchase no"]=data_line[0].split()[PO_details["index"]]
                        po_status=False
            if Date_details["word"] in line:
                if date_status:
                    data_line=pdf_text[l_index+Date_details["line"]].split(Date_details["word"])
                    if Date_details["direction"] =="right":
                        other_details["Order_Date"]=data_line[1].split()[Date_details["index"]]
                        date_status=False
                    elif Date_details["direction"] =="down":
                        other_details["Order_Date"]=data_line[0].split()[Date_details["index"]]
                        date_status=False
            if InvoiceID_details["word"] in line:
                if invid_status:
                    data_line=pdf_text[l_index+InvoiceID_details["line"]].split(InvoiceID_details["word"])
                    if InvoiceID_details["direction"] =="right":
                        other_details["Invoice ID"]=data_line[1].split()[InvoiceID_details["index"]]
                        invid_status=False
                    elif InvoiceID_details["direction"] =="down":
                        other_details["Invoice ID"]=data_line[0].split()[InvoiceID_details["index"]]
                        invid_status=False
        return other_details

    def extract_podetails(self,lines):
        PO_details=self.doc_po_date["PO"]
        Date_details=self.doc_po_date["Date"]
        InvoiceID_details = self.doc_po_date["Invoice ID"]
        po_status=True
        date_status=True
        invid_status=True
        item_status=False
        other_details={
            "Purchase no":'',
            "Order_Date":'',
            "Invoice ID":''
        }
        po=''
        date=''
        invid=''
        sno_list=[]
        for l_index, line in enumerate(lines):
            for w_index, word in enumerate(line):
                if invid_status:
                    if InvoiceID_details["word"] in word[0]:
                        if InvoiceID_details["direction"] =="right":
                            data=lines[l_index]
                            w_index = lines[l_index].index(word)
                            try:
                                invid = lines[l_index][w_index+1]
                                other_details['Invoice ID']=invid[0]
                            except:
                                invid = lines[l_index][w_index][0]
                                other_details['Invoice ID']=invid.split(InvoiceID_details['word'])[1].strip()
                            invid_status=False
                        elif InvoiceID_details["direction"] =="down":
                            invid = min(enumerate(lines[l_index + InvoiceID_details["line"]]),
                                                        key=lambda x: abs(word[1][0][0] - x[1][1][0][0]) if x[1][1][1][0] > word[1][0][0] else float('inf'))
                            other_details['Invoice ID']=invid[1][0].split()[InvoiceID_details["index"]]
                            invid_status=False
                if po_status:
                    if PO_details['word'] in word[0]:
                        if PO_details["direction"] =="right":
                            data=lines[l_index]
                            w_index = lines[l_index].index(word)
                            try:
                                po = lines[l_index][w_index+1]
                                other_details['Purchase no']=po[0]
                            except:
                                po = lines[l_index][w_index][0]
                                other_details['Purchase no']=po.split(PO_details['word'])[1].strip()
                            po_status=False
                        elif PO_details["direction"] =="down":
                            po = min(enumerate(lines[l_index+PO_details["line"]]),
                                                        key=lambda x: abs(word[1][0][0] - x[1][1][0][0]) if x[1][1][1][0] > word[1][0][0] else float('inf'))
                            other_details['Purchase no']=po[1][0].split()[PO_details["index"]]
                            po_status=False
                if date_status:
                    if Date_details["word"] in word[0]:
                        if Date_details["direction"] =="right":
                            data=lines[l_index]
                            w_index = lines[l_index].index(word)
                            try:
                                date = lines[l_index][w_index+1]
                                other_details['Order_Date']=date[0]
                            except:
                                date = lines[l_index][w_index][0]
                                other_details['Order_Date']=date.split(Date_details['word'])[1].strip()
                            date_status=False
                        elif Date_details["direction"] =="down":
                            date = min(enumerate(lines[l_index + Date_details["line"]]),
                                                        key=lambda x: abs(word[1][0][0] - x[1][1][0][0]) if x[1][1][1][0] > word[1][0][0] else float('inf'))
                            other_details['Order_Date']=date[1][0].split()[Date_details["index"]]
                            date_status=False
                if self.doc_po_date["line_item_word"] in word[0]:
                    item_no=min(enumerate(lines[l_index]),key=lambda x: abs(word[1][0][0] - x[1][1][0][0]) if x[1][1][1][0] > word[1][0][0] else float('inf'))
                    sno_list.append(item_no[1])
                    item_status=True
                elif item_status:
                    remove_space=word[0].replace(" ","")
                    if sno_list[0][1][1][0] >= word[1][1][0]:
                        sno_list.append(word)
                        
                    elif self.doctype['End_Line'][0] in remove_space :
                        item_status=False
                        break

        # print(sno_list)
        return other_details
 

    def extract_rows(self,pdf_text): #from table creates the response of list of list
        lines=[] #main line will get appended here
        data_response=[] # final row will appended in here
        sublist=[] #subline will get appended here
        sub_start_row=False #status when sub row is detected
        header=False
        count=0
        map_count=1
        if not self.row_endno:
            table=pdf_text[self.row_startno+1:]
        else:
            table=pdf_text[self.row_startno+1:self.row_endno]
        template=self.doctype #respected template will be called according to document name
        for index,row in enumerate(table):
            if any(i in row for i in template["Start_sub_Line"]): #check for the subline
                sub_start_row=True
                sublist.append(row)
            elif header:
                count=template["header_footer_Count"]
                if count == map_count:
                    map_count=0
                    header=False
                    continue
                else:
                    map_count+=1
            elif sub_start_row: #adds the sublines 
                if any(i in row for i in template["End_sub_Line"]): #checks for end of sublines
                    sub_start_row=False
                    sublist.append(row)
                    try:
                        if table[index+1]: #found end of subline will check for next line 
                            if any(i in table[index+1] for i in template["Start_sub_Line"]): #will check for another sub-line
                                self.Start_Row=True
                                lines.append(sublist)
                                sublist=[]
                            elif any(i in row for i in template["Ignore_Line"]): #will check for lines to be ignored. 
                                continue
                            else:
                                lines.append(sublist) #all sublines will get appended to lines and sublist will get empty 
                                sublist=[]
                                self.End_Row=True #
                    except:
                        lines.append(sublist) #no next line found then, sublines will get appended to line
                        self.End_Row=True
                elif any(i in row for i in template["Ignore_Line"]): #if subline will check for lines to ignored
                    try:
                        if table[index+1]: #check after ignoreline any another line exists 
                            continue
                    except:
                        lines.append(sublist) #no line append sublines to lines
                        sublist=[]
                        self.End_Row=True
                else:
                    sublist.append(row)
                    try:
                        if table[index+1]: 
                            continue
                    except:
                        lines.append(sublist) #no line append sublines to lines
                        sublist=[]
                        self.End_Row=True
            elif any(i in row for i in template["Ignore_Line"]): #if no subline, ignore line occurs
                    try:
                        if table[index+1]: 
                            continue
                    except:
                        self.End_Row=True
            elif any(i in row for i in template["Header_Footer"]):
                try:
                    if table[index+1]:
                        header=True 
                        continue
                except:
                    self.End_Row=True

            elif (len(template["Start_sub_Line"])==0 and len(template["End_sub_Line"])!=0): 
                #In template subline start word is not given and end subline word is given, subrow is not present 
                sub_start_row=True
                lines.append(row)
            elif (len(template["Start_sub_Line"])==0 and len(template["End_sub_Line"])==0) :
                #In template subline start word and end subline word is not given, row are single liner
                lines.append(row)
                # try:
                #         if table[index+1]: 
                #             continue
                #     except:
                #         self.End_Row=True
                self.End_Row=True
            else: #lines will get appended till next start subline is found
                lines.append(row)
                if len(lines)>1: # if multiple lines are found then it will joined
                    lines=[' '.join(lines)]
                try:    
                    if table[index+1]: #check for end of table
                        continue
                except:
                    self.End_Row=True
            if self.End_Row: # End of tables found reponse is generated 
                if len(lines)!=0: #check if lines are empty list till not append to final response
                    data_response.append(lines)
                lines=[]
                self.End_Row=False
        return data_response

    
    def split(self,delimiters, string, maxsplit=0):
        import re
        regexPattern = '|'.join(map(re.escape, delimiters))
        return re.split(regexPattern, string, maxsplit)
    

    def api_address(self,text=None):#address is extracted from address db using api and mapped with text from pdf
        Address_details =  self.doc_po_date['Address']
        start_word = Address_details['Start']
        line_address= Address_details['line']
        if isinstance(text, str) :
            lines=text.splitlines()
        else:
            lines=text
        tempp_add=[]
        found_address =False
        if line_address >=0:
            for line in lines:
                if start_word in line:
                    found_address=True
                if found_address:
                    tempp_add.append(line)
                    if self.get_state_name(line):
                        found_address=False
                        break
                    elif self.get_city_name(line):
                        found_address= False
                        break
        else:
            for line in reversed(lines):
                if start_word in line:
                    found_address=True
                if found_address:
                    tempp_add.append(line)
                    if self.get_state_name(line):
                        found_address=False
                        break
                    elif self.get_city_name(line):
                        found_address= False
                        break
                # print(line)
        final_address = ''.join([x for x in tempp_add])
        final_Add=final_address.split(start_word)[1].strip()
        return final_Add
    def get_state_name(self,word):
        """
        Function to get state name and its co-ordinates from given word
        :param word:
        :return:
        """
        state_name = self.state_name['state']
        state_list = [x.lower() for x in state_name]
        check_word = copy.deepcopy(word)
        check_word = check_word.lower()
        check_word =  check_word.replace(" ","")
       
        probable_state_list=[]
        for x in state_list:
            temp=x.replace(" ","")
            if temp in check_word:
                probable_state_list.append(x)

        # probable_state_list = list(filter(lambda x: x.startswith(check_word.split()[0][:-1]), state_list))
        for prob in probable_state_list:
            prob=prob.replace(" ","")
            if prob in check_word:
                return True
        return False

    def get_city_name(self,word):
        """
        Function to get state name and its co-ordinates from given word
        :param word:
        :return:
        """
        state_name = self.city_name['city']
        state_list = [x.lower() for x in state_name]
        check_word = copy.deepcopy(word)
        check_word = check_word.lower()
        check_word =  check_word.replace(" ","")
       
        probable_state_list=[]
        for x in state_list:
            temp=x.replace(" ","")
            if temp in check_word:
                probable_state_list.append(x)

        # probable_state_list = list(filter(lambda x: x.startswith(check_word.split()[0][:-1]), state_list))
        for prob in probable_state_list:
            prob=prob.replace(" ","")
            if prob in check_word:
                return True
        return False

    def extract_address(self,lines):#from xml->lines address is extracted based on start word and line no. till states is not matched
        address_keys=self.doc_po_date['Address']
        text_val=[]
        keys=[]
        values=[]
        height_list=[]
        slanted_list=[]
        rotated_list=[]
        first_word={'word':"","L-index":""}
        next_word={'word':"","R-index":""}
        first_word_state=True
        next_word_state=True
        for l_index, line in enumerate(lines):
            for w_index, word in enumerate(line):
                if first_word_state or next_word_state:
                    if 'Start' in address_keys:
                        if address_keys['Start'] in word[0]:
                            if address_keys['line']>0:
                                first_word['word'] = min(enumerate(lines[l_index +address_keys['line']]),
                                                            key=lambda x: abs(word[1][0][0] - x[1][1][0][0]) if x[1][1][1][0] > word[1][0][0] else float('inf'))
                                first_word['L-index']=l_index
                                first_word_state=False
                            else:
                                first_word['word'] = min(enumerate(lines[l_index + address_keys['line']]),
                                                            key=lambda x: abs(word[1][0][0] - x[1][1][0][0]) if x[1][1][1][0] > word[1][0][0] else float('inf'))
                                first_word['L-index']=l_index
                                first_word_state=False
    

                    if 'R-side' in address_keys:
                        if address_keys['R-side'] in word[0]:
                            next_word['word'] = min(enumerate(lines[l_index]),
                                                        key=lambda x: abs(word[1][0][0] - x[1][1][0][0]) if x[1][1][1][0] > word[1][0][0] else float('inf'))
                            next_word['R-index']=l_index
                            next_word_state=False
                else:
                    break


        Addres_lines=[]
        address_state=True
        address_city = True
        if address_keys['line']>=0:
            for l_index, line in enumerate(lines[first_word['L-index']: self.row_startno]):
                for w_index, word in enumerate(line):
                    if address_state:
                        if 'R-side' in address_keys:
                            if next_word['word'][1][1][0][0] >= word[1][1][0] >= first_word['word'][1][1][0][0]:
                                Addres_lines.append(word)
                                if self.get_state_name(word[0]):
                                    address_state=False
                                    break
                                elif self.get_city_name(word[0]):
                                    address_city= False
                                    address_state=False
                                    break
                        else:
                            if word[1][1][0] >= first_word['word'][1][1][0][0]:
                                Addres_lines.append(word)
                                if self.get_state_name(word[0]):
                                    address_state=False
                                    break
                                elif self.get_city_name(word[0]):
                                    address_city= False
                                    address_state=False
                                    break
        else:
            for l_index, line in enumerate(lines[:first_word['L-index']]):
                for w_index, word in enumerate(line):
                    if address_state:
                        if 'R-side' in address_keys:
                            if next_word['word'][1][1][0][0] >= word[1][1][0] >= first_word['word'][1][1][0][0]:
                                Addres_lines.append(word)
                                if self.get_state_name(word[0]):
                                    address_state=False
                                    break
                                elif self.get_city_name(word[0]):
                                    address_city= False
                                    address_state=False
                                    break
                        else:
                            if word[1][1][0] >= first_word['word'][1][1][0][0]:
                                Addres_lines.append(word)
                                if self.get_state_name(word[0]):
                                    address_state=False
                                    break
                                elif self.get_city_name(word[0]):
                                    address_city= False
                                    address_state=False
                                    break

        final_Add=" ".join(list(map(lambda x:x[0], Addres_lines)))
        try:
            final_Add=final_Add.split(address_keys['Start'])[1].strip()
        except:
            final_Add=final_Add

        return final_Add

    def api_address_custid(self,final_Add):
        address_keys=self.doc_po_date['Address']
        
        try:
            with open('config/config.json', 'r') as data_file:
                response = json.load(data_file)
            json_data={
                        "customerIdArray":address_keys['cust_id']
                    }
            response_d = requests.request(response['type'], response['address_api'],json=json_data,timeout=10)

            response_data = json.loads(response_d.text)

            Address_data=response_data
        except:

            Address_data = "Not found"


        address_status=False
        cust_id="Not present in DB"

        count = 0
        add_list=[]
        try:
            if len(final_Add) != 0: 
                for add in Address_data:
                    for key,value in add.items():
                        if key!='id' and value is not None:
                            value_n=value.replace(" ","").lower()
                            final_Add_n=final_Add.replace(" ","").lower()
                            if value_n in final_Add_n:
                                count += 1

                    if count>=2:
                        cust_id=add['id']
                        final_Add=" ".join([val for key,val in add.items() if key!='id' and val])
                        address_status = True
                        break
        except:
            final_Add=final_Add
            
        print(cust_id)
        return final_Add,address_status,cust_id
    

if __name__ == "__main__":
    gt = Get_table()
    gt.api_address()