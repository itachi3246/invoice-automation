import xml.etree.ElementTree as ET
import os
import subprocess 
import pdfplumber
import platform
import json
def google_response(text,co_ordinates):

    des={}
    co_ordinate=[int(float(x)) for x in co_ordinates]
    points=[(co_ordinate[0],co_ordinate[3]),(co_ordinate[2],co_ordinate[3]),(co_ordinate[2],co_ordinate[1]),(co_ordinate[0],co_ordinate[1])]
    des['description']=text
    # des['vertices']=group(co_ordinate,2)
    des['vertices']=points
    return des

def extract_wordco(text_desc):
    word_bound=[]
    first_text=text_desc[0]
    last_text=text_desc[-1]
    co_ordi_first =[int(float(x)) for x in first_text.attrib['bbox'].split(',')]
    co_ordi_second = [int(float(x)) for x in last_text.attrib['bbox'].split(',')]
    word_bound = [co_ordi_first[0],co_ordi_first[1],co_ordi_second[2],co_ordi_second[3]]
    return word_bound


def extract_utils(path):
    all_words=[]
    tree = ET.parse(path)
    description=[]
    root = tree.getroot()
    description_f=[]
    for page in root:
        for id_ in page.attrib['id']:
            page_point = page.attrib['bbox'].split(',')
            w = (page_point[0],page_point[1])
            h = (page_point[2],page_point[3])
            for textbox in page:
                for textline in textbox:
                    tempstr=[]
                    text_desc=[]
                    for text in textline:
                        if text.tag == 'text':
                            if not text.text.isspace():
                                # print(text.tag, text.attrib)
                                tempstr.append(text.text)
                                co_ordinates = textline.attrib['bbox'].split(',')
                                text_desc.append(text)
                            else:
                                # tempstr.append('')
                                if len(text_desc)>0:
                                    co_ordinates=extract_wordco(text_desc)
                                    all_words.append(google_response(''.join(tempstr),co_ordinates)) 
                                    description.append(''.join(tempstr))
                                    tempstr=[]
                                    text_desc=[]
                    description.append('\n')
            page_cor=page.attrib['bbox'].split(',')
            w=int(float(page_cor[2]))
            h=int(float(page_cor[3]))
        description_f.append(' '.join(description))
    description=' '.join(description_f)
    # print("Description:",description)
    return description,all_words,w,h

def pdf_to_xml(path):
    with open('config/config.json', 'r') as data_file:
        response = json.load(data_file)
    file_path_pdf=response['pdf2txt_path']
    file_path,filename= os.path.split(path)
    newfilename=os.path.splitext(filename)[0]
    file_dest_ext='.xml'
    file_path='Gen_xmls'
    dest = os.path.join(file_path,newfilename+file_dest_ext)
    #IF ERROR GETS AS "NO SUCH FILE/DIRECTORY FOUND, THEN CHANGE COMMAND CODE BELOW TO ANOTHER AND COMMENT PREVIOUS COMMAND
    if platform.system() == 'Linux':
        command = f'pdf2txt.py -o "{dest}" "{path}"'#works in ubuntu
    else:
        command = f'"{file_path_pdf}" pdf2txt.py -o "{dest}" "{path}"'#works in windows
    # print(command)
    subprocess.call(command, shell=True)

    doc_path = dest.replace('\ ', ' ')
    
    description,all_words,w,h = extract_utils(doc_path)
    # print("Data:",[description])
    return description,all_words,w,h,doc_path

# def rectifyCharacterSet(description):
#     """
#     Function to rectify character set of given text
#     """
#     # Change cyrillic characters to latin. As block and column headers are based on latin.
#     cyrList = 'АВЕМСТахУХуОНРеԚԛԜԝҮү•ΕΙр'
#     latList = 'ABEMCTaxyXyOHPeQqWwYy.EIp'
#     table = str.maketrans(cyrList, latList)
#     return description.translate(table)


def main(path):
    dest_path=pdf_to_xml(path)

if __name__ == "__main__":
    pdf_path="/home/kunal/Projects/mj/pdf_xml/docs/REGAL BELOIT Purchase Order# 670061378.pdf"
    dest=pdf_to_xml(pdf_path)
    doc_path = dest.replace('\ ', ' ')


