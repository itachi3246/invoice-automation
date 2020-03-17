import re

class Utils:
    def __init__(self,debug_flag=False):
        self.debug_flag = debug_flag

    def customPrint(self, *arg):
        """
        Function to print data for debugging

        :param arg: Data which has to be printed
        :return: None
        """
        if self.debug_flag:
            print(arg)

    def isFloat(self, s):
        """
        Function to check if string is a float. (Custom function built specific to OCR requirements)

        :param s: String which has to be checked
        :return: Boolean value
        """
        # check if word is of type phone number
        if bool(re.search('(\(\d{3}\))',s)):
            return False
        try:
            if s[-3] == ',' or s[-3] == ';':
                s = s[:-3] + "." + s[-2:]
        except:
            pass
        s = s.replace('B', '8')
        s = s.replace('S', '5')
        s = s.replace(',', '.')
        s = s.replace(' ', '.')
        # s = re.sub('[*$€\-–)(—;] ?', '', s)
        s = re.sub('[*$€;] ?', '', s)
        s = s.replace('.', '', s.count('.') - 1)
        s = re.sub('[\-–—] ?', '-', s)
        x = re.sub('[\-)(] ?', '', s)
        try:
            int(x)
            return False
        except:
            try:
                float(x)
                return s
            except ValueError:
                return False

    def isFloatOrInt(self, s):
        """
        Function to check if string is Float or Integer value.

        :param s: String which has to be checked
        :return: Boolean value
        """
        try:
            if s[-3] == ',':
                k = s.rfind(",")
                s = s[:k] + "." + s[k + 1:]
        except:
            pass
        s = s.replace('B', '8')
        s = s.replace('S', '5')
        s = s.replace(';', '.')
        s = s.replace(' ', '.')
        s = re.sub('[*,$€\-/–)(—] ?|to|To', '', s)
        s = s.replace('.', '', s.count('.') - 1)
        try:
            int(s)
            return True
        except:
            try:
                float(s)
                return True
            except ValueError:
                return False

    def finalFloat(self, s, c_type='General'):
        """
        Function to return final float value that has to be displayed and used for calculations.

        :param s: String having float value
        :param c_type: Default type is 'General' which takes only two decimal places.
            For 'Rate' type it considers four decimal places
        :return: Corrected float value
        """
        if s == '':
            return s
        s = s.replace('B', '8')
        s = s.replace('S', '5')
        if bool(re.search(r'\)',s)) and bool(re.search(r'\(',s)):
            s = '#'+s
        s = re.sub('[s,;$€)(] ?', '', s)
        if c_type != 'Rate':
            try:
                if s[-4] == '.':
                    s = s[:-1]
                elif s[-5] == '.' and (s[-2] == '1' or s[-1] == '1'):
                    s = s[:-2]
            except:
                pass
            s = s.replace('.', '')
            s = s[:-2] + '.' + s[-2:]
        return s