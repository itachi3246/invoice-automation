from document import Document
import os
import json
import ast
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    else:
        return obj


if __name__ == "__main__":
    d=Document()
    directory = "Unit Cases/"
    count=0
    Failed=[]
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            print(filename)
            file_split,file_ext =os.path.splitext(filename)
            data_1 = d.identify_doc(directory+filename)
            res = ast.literal_eval(json.dumps(data_1)) 
            suffix='.json'
            json_file =directory+file_split+suffix
            with open(json_file, 'r') as data_file:
                data_2 = json.load(data_file)
            if ordered(res)==ordered(data_2):
                print(True)
                count+=1
            else:
                print(False)
                Failed.append(filename)
    print("Failed files are:{}, Passed count is:{}".format(Failed,count))