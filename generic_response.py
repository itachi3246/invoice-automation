import re
class Generic_response:

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
        self.subline=Doc_data["SubLine"]

        self.End_Row=False #status to get final response

    def extract_values(self,data_response): #from the response extracts the data column wise

        line_template=self.line_regex #main line defined structure will get assigned
        subline_template=self.subline #sub line defined structure will get assigned
        sub_row=False
        line_main={} #values gets from main line will appended
        final_respose=[] # final extracted line will get appended 
        sub_list={} #values gets from sub-line will appended here
        line_operations=line_template['values'] #respective document defined line operations will be invoked 
        subline_operations=subline_template['values'] #respective document defined sub-line operations will be invoked 

        for l_index,line in enumerate(data_response): #iterate over the data_response got from extact_row method
            for s_index,ele in enumerate(line): 
                if isinstance(ele,str): #check if row is list(sub-line) or string(main line/single row)
                    data=re.split(line_template['separator'],ele.strip()) #split by space and extra spacing will be removed 
                    data=[i for i in data if len(i)>0] #empty list values will be removed 
                    for opr_dict in line_operations: #predefined operations will be iterated
                        if opr_dict['line_no']==s_index: #compare if subline index and predefined line number
                            if opr_dict['imp']=='required': #check for operation status extracted word is required or not
                                if opr_dict['end_position']: 
                                    if opr_dict['separator']:
                                        if line_main['separator'] in data:
                                                line_main[opr_dict['type']]=[i for i in data.split(opr_dict['separator']) if i][0]
                                        # chech if line contains the separator
                                    else:
                                        if opr_dict['end_position']==-1: 
                                            #get all the elements from list, from start position to end of list
                                            line_main[opr_dict['type']]=' '.join(data[opr_dict['start_position']:])

                                        else:
                                            #get element from start to end
                                            line_main[opr_dict['type']]=' '.join(data[opr_dict['start_position']:opr_dict['end_position']])
                                else:
                                    #gets specific element from list
                                    line_main[opr_dict['type']]=data[opr_dict['start_position']]
                    try:
                        #check for next row
                        if line[s_index+1]:
                            continue
                    except:
                        self.End_Row=True
                else:
                    # extract values from sublist response
                    for sub_index,row in enumerate(ele):
                        row_new=re.split(self.subline['separator'],row.strip())
                        new_row=[i for i in row_new if i]
                        for sopr_dict in subline_operations:
                            if sopr_dict['line_no']==sub_index:
                                if sopr_dict['imp']=='required':
                                    if sopr_dict['end_position']:
                                        if sopr_dict['separator']:
                                            if sopr_dict['separator'] in row:
                                                sub_list[sopr_dict['type']]=[i for i in row.split(sopr_dict['separator']) if i][0].split()[sopr_dict['start_position']:sopr_dict['end_position']][0]
                                        else:
                                            if sopr_dict['end_position']==-1:
                                                sub_list[sopr_dict['type']]=' '.join(new_row[sopr_dict['start_position']:])

                                            else:
                                                sub_list[sopr_dict['type']]=' '.join(new_row[sopr_dict['start_position']:sopr_dict['end_position']])
                                    else:
                                        if sopr_dict['separator']:
                                            if sopr_dict['separator'] in row:
                                                sub_list[sopr_dict['type']]=[i for i in row.split(sopr_dict['separator']) if i][0].strip()
                                        else:
                                            sub_list[sopr_dict['type']]=new_row[sopr_dict['start_position']]
                    sub_row=True

                #subrow is present
                if sub_row:
                    #merge two dictionary to form final row
                    result_merge={**line_main,**sub_list}
                    sub_list={}
                    #appended to final response gets generated
                    final_respose.append(result_merge)
                    result_merge={}
                    sub_row=False

                #all the values gets extracted from lines
                if self.End_Row:
                    final_respose.append(line_main)
                    line_main={}
        return final_respose