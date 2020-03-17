import json
import re
import difflib
import copy
from line_algorithm.document import Document
from extract_fromxml import extract_utils
## Version 7.2.2 - 2018-12-05

DEBUG = False
DEV_ENV = False


class PaystubDetails:
    """
    Class to read lines from a document
    """

    def __init__(self):
        self.result = {}
        self.description = ''
        self.data_val = []
    def checkRule(self, rule_name):
        """
        Function to check if a rule exists by given name, if yes, return boolean value of that rule
        :param rule_name: Rule name that has to be checked in rules dictionary
        :return: Boolean value
        """
        try:
            for sublist in self.rules:
                if sublist[0] == rule_name:
                    if sublist[1]['val'] == 'True':
                        return True
                    return False
            return False
        except:
            return False
    def change_co(self,all_words):
        max_val=max(all_words, key=lambda x: x['vertices'][0][1])['vertices'][0][1]
        for key, x in enumerate(all_words):
            for key1, y in enumerate(x['vertices']):
                all_words[key]['vertices'][key1]=(y[0],max_val-y[1])
        return all_words

    def readPaystub(self, path):
        """
        Function which takes document path as input, and gives final results as output.

        :param path: Document path that has to be read [Only jpg and png images are allowed]
        :return: Final processed data, text description, complete GCV output
        """
        

        self.description,all_words,self.width,height=extract_utils(path)
        all_mod_words=self.change_co(all_words)
        # update all float of type \d\n,\d to \d ,\d
        self.description = re.sub('\\n,',' ,',self.description)

        # Create an object of Document to get lines of data
        input_param = {'ignore_digits':['1.5','2.0','401']}
        d_obj = Document(self.width, height, input=input_param)

        # Update character set of description
        self.description = d_obj.rectifyCharacterSet(self.description)

        data_test,OCRSpaces, hl, sl, rl, self.result, self.words_dict, self.digits_dict = d_obj.arrangeTextWithCoordinates(
            self.description, all_mod_words)

        hl, sl = d_obj.calculateModeRotate(rl, hl, sl)
        mode_slant = d_obj.calculateModeSlant(sl)
        mode_height = d_obj.calculateModeHeight(hl)
        
        lines, SpecificWords = d_obj.rectifyData(mode_slant)
        
        return lines,data_test
 


# To run this program manually. [Used only for development purpose]
def main(path):
# if __name__ == "__main__":
    import subprocess
    import os
    import sys
    import cv2
    sys.path.insert(0,'../')
    # sys.path.insert(0,'../api/')

    # Make DEBUG true in development environment
    DEBUG = True

    # Make DEV_ENV true in development environment
    DEV_ENV = True

    # create instance of paystub_gcv class that is used for reading paystub details
    pt = PaystubDetails()
 
    doc_path = path.replace('\ ', ' ')

    return pt.readPaystub(doc_path)
