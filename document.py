import json
import pdfplumber
from get_table import Get_table 
from generic_response import Generic_response 
from extract_fromxml import pdf_to_xml
import Lines_ocr as pf
import os
from get_custable import Get_Custable
class Document:
    """
    Describe the template according to create lines for value extractions
    eg. Start_Line: starting of the table
        End_Line: end of the table
        Start_sub_Line: if row is divided into multiple lines so second static word will be start of subrow
        End_sub_Line:if row is divided into multiple lines so last line static word will be end of subrow
        Ignore_Line:if page seperator or any line to ignore can be defined here
    """
    def __init__(self):

        self.main_data=None
        with open('config/main.json', 'r') as data_file:
            self.main_data = json.load(data_file)

        """
        works on the line or single liner rows.
        extracts the data column wise
        type: Column name
        imp: required or not
        start_position: index of word list
        end_position: end index of word list
        separator: string by which list is checked 
        line_no: line number on which the word exists 
        """
        self.doc_identifier_words=self.main_data["Doc_identifier"]
        self.doc_name=None #name of document
        self.doc_type=None


    def identify_doc(self,path): #extracts the text from the document
        pdf = pdfplumber.open(path)
        text=[]
        tables=[]
        
        try:
            for page in pdf.pages:
                text.append(page.extract_text()) #text from pdf
        except Exception as e:
            print(e)

        for name,des in self.doc_identifier_words.items():
            if all(word in text[0] for word in des):
                self.doc_name=name
        
        Doc_data=self.main_data[self.doc_name]
        self.doc_type=Doc_data["Extract_Table"]

        text=[i for t in text for i in t.splitlines()] #split the text into lines  
        gt=Get_table(self.doc_type,Doc_data["Other_details"])
        pdf_text=gt.extract_text(text)  #from the text extracts the table rows


        description,all_words,w,h,doc_path = pdf_to_xml(path)
        try:
            lines,data_test = pf.main(doc_path)
            other_details=gt.extract_details(pdf_text)
        except:
            other_details=gt.extract_details(pdf_text)

        try:

            try:
                address_line=gt.extract_address(lines)
                address,address_status,cust_id=gt.api_address_custid(address_line)
            except:
                address="Not found"
                address_status=False

            if address_status == False :
                try:
                    address_text = gt.api_address(description)
                except:
                    address_text = gt.api_address(pdf_text)
                address,address_status,cust_id=gt.api_address_custid(address_text)
            
        except:
            if address == "Not found" or not address :
                address="Not present in DB"
                cust_id = "Not found"

        os.remove(doc_path)
        print("File Removed!")

        data_response=gt.extract_rows(pdf_text)#from table creates the response of list of list
        print(data_response)
        gc = Get_Custable(Doc_data["Table_Lines"])
        gr = Generic_response(Doc_data["Table_Lines"])
        # print(gr)

        if self.doc_name =="INGERSOL":
            final_response = gc.extract_ingersol_data(data_response)
        elif self.doc_name == "SLWORLD":
            final_response = gc.extract_sl_data(data_response)
        else:
            final_response = gr.extract_values(data_response)#from the response extracts the data column wise

        self.doc_type=Doc_data["Extract_Table"]
        text=[i for t in text for i in t.splitlines()] #split the text into lines
        gt=Get_table(self.doc_type,Doc_data["Other_details"])
        pdf_text=gt.extract_text(text)
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
        final_res=[]
        for item_dic in final_response:
            for key,value in item_dic.items():
                if key in line_items:
                    line_items[key]=value
            final_res.append(line_items)
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
        final_list={
            "Customer ID":cust_id,
            "Shipping Address":address,
            "Invoice ID":other_details['Invoice ID'],
            "Order_Date":other_details['Order_Date'],
            "Purchase order":other_details['Purchase no'],
            "Line Items":final_res
        }
        print(json.dumps(final_list))
        pdf.close()
        # print(final_list)
        return final_list
    


if __name__ == "__main__":
    import sys
    try:
        path = sys.argv[1]
    except:
        path ='E:\\current\\PAYABLES ENTRY SAMPLES - new\\amco & entec\\AP1-453613 Amco 0000175314.pdf'
    d = Document()
    d.identify_doc(path) #extracts the text from the document