import io
import re
import difflib
import copy
import os
from line_algorithm.utils import Utils
import statistics

util_obj = Utils(True)

class Document:

    def __init__(self, width, height, **kwargs):
        """
        Update parameters that are to be used for this line generation algorithm
        """

        self.width = width
        self.height = height

        self.imp_words_w_spaces=[]
        
        # Full stop words when found, stop concatenating other words
        self.full_stop_words = []

        # Half stop words when found, minimize space width for further concatenation
        self.half_stop_words = []

        # List of OCR words (word + co-ordinates) whose assigned line number is to be found
        self.find_ocr_words = []

        # List of digits to be ignored from digits list
        self.ignore_digits = []

        # Flag to check if compressed text
        self.compressed_text = False

        # Flag to check Large text
        self.large_text = False

        self.output_flags = {'WordsDict':False,'DigitsDict':False,'OCRSpaces':False,'SpecificWords':False}

        if kwargs is not None:
            if 'output' in kwargs:
                for key in kwargs['output']:
                    try:
                        self.output_flags[key] = bool(kwargs['output'][key])
                    except:
                        pass
            if 'input' in kwargs:
                if 'full_stop_words' in kwargs['input']:
                    self.full_stop_words = kwargs['input']['full_stop_words']
                if 'half_stop_words' in kwargs['input']:
                    self.half_stop_words = kwargs['input']['half_stop_words']
                if 'find_ocr_words' in kwargs['input']:
                    self.find_ocr_words = kwargs['input']['find_ocr_words']
                if 'ignore_digits' in kwargs['input']:
                    self.ignore_digits = kwargs['input']['ignore_digits']
                if 'imp_words_w_spaces' in kwargs['input']:
                    self.imp_words_w_spaces = kwargs['input']['imp_words_w_spaces']
                if 'compressed_text' in kwargs['input']:
                    self.compressed_text = kwargs['input']['compressed_text']
                if 'large_text' in kwargs['input']:
                    self.large_text = kwargs['input']['large_text']
        return
    
    def updateInitParams(self, **kwargs):
        """
        Function to update init parameters that are to be used for this line generation algorithm
        """
        if kwargs is not None:
            if 'output' in kwargs:
                for key in kwargs['output']:
                    try:
                        self.output_flags[key] = bool(kwargs['output'][key])
                    except:
                        pass
            if 'input' in kwargs:
                if 'full_stop_words' in kwargs['input']:
                    self.full_stop_words = kwargs['input']['full_stop_words']
                if 'half_stop_words' in kwargs['input']:
                    self.half_stop_words = kwargs['input']['half_stop_words']
                if 'find_ocr_words' in kwargs['input']:
                    self.find_ocr_words = kwargs['input']['find_ocr_words']
                if 'ignore_digits' in kwargs['input']:
                    self.ignore_digits = kwargs['input']['ignore_digits']
                if 'imp_words_w_spaces' in kwargs['input']:
                    self.imp_words_w_spaces = kwargs['input']['imp_words_w_spaces']
                if 'compressed_text' in kwargs['input']:
                    self.compressed_text = kwargs['input']['compressed_text']
                if 'large_text' in kwargs['input']:
                    self.large_text = kwargs['input']['large_text']
        return

    def removeJunkAndMergeFloatWords(self,line_list):
        """
        Function to remove junk sequences and merge all float values into one word.
        As per Google OCR, we get special characters in distinct words, i.e 1,003.56 is broken in five
        different words such as [1 , 003 . 56]. We need to merge these into one word

        :param line_list: Line list having words that are not merged
        :return: Line list having merged float values
        """

        for k, line in enumerate(line_list):
            line_list[k] = sorted(line, key=lambda x: x[1][0][0])
            line = line_list[k]
            pop_elements = []

            last_word = ['', []]
            junk_char_seq = []
            junk_char = ''
            probable_values = []
            for w_index, word in enumerate(line):
                if word[0] == last_word[0] or (word[0] == ',' and last_word[0] == '.') or (
                        word[0] == '.' and last_word[0] == ','):
                    if word[1][0][0] < last_word[1][1][0]:
                        pop_elements.append(w_index)
                        last_word = copy.deepcopy(word)
                        continue
                    if word[0] in (',', '.', '/', '-', '–', '—', '%', '.', ';'):
                        junk_char_seq.append(w_index - 1)
                        junk_char = word[0]
                        continue
                if junk_char_seq:
                    line_list[k][junk_char_seq[0] - 1][0] = line_list[k][junk_char_seq[0] - 1][0].replace(junk_char, '')
                    for v in junk_char_seq:
                        if v not in pop_elements:
                            pop_elements.append(v)
                    pop_elements.append(junk_char_seq[-1] + 1)
                    junk_char_seq = []
                    junk_char = ''
                last_word = copy.deepcopy(word)
                if bool(re.search(r'[\d\-+,.$)(]', word[0])):
                    if abs(last_word[1][1][0] - word[1][0][0]) > (3 * abs(last_word[1][1][1] - last_word[1][2][1])):
                        probable_values = []
                    for i, p in enumerate(probable_values):
                        if list(filter(lambda x: x.startswith(p[0] + word[0]), self.digits_dict)):
                            probable_values[i][0] = p[0] + word[0]
                            if probable_values[i][0] in self.digits_dict:
                                try:
                                    if bool(re.search(r'[\d,)*]', line_list[k][w_index + 1][0])) and abs(
                                            word[1][1][0] - line_list[k][w_index + 1][1][0][0]) < (
                                            3 * abs(word[1][1][1] - word[1][2][1])):
                                        if not (line_list[k][w_index + 1][0] == last_word[0] and
                                                line_list[k][w_index + 1][1][0][0] < last_word[1][1][0]):
                                            continue
                                except:
                                    pass
                                word_index = probable_values[i][2]
                                line_list[k][word_index][0] = probable_values[i][0]
                                line_list[k][word_index][1] = [probable_values[i][1][0], word[1][1], word[1][2],
                                                               probable_values[i][1][3]]
                                for s in range(word_index + 1, w_index + 1):
                                    if s not in pop_elements:
                                        pop_elements.append(s)
                                probable_values = []
                                break
                        elif list(filter(lambda x: x.startswith(p[0] + ' ' + word[0]), self.digits_dict)):
                            probable_values[i][0] = p[0] + ' ' + word[0]
                            if probable_values[i][0] in self.digits_dict:
                                try:
                                    if bool(re.search(r'[\d,)*]', line_list[k][w_index + 1][0])) and abs(
                                            word[1][1][0] - line_list[k][w_index + 1][1][0][0]) < (
                                            3 * abs(word[1][1][1] - word[1][2][1])):
                                        if not (line_list[k][w_index + 1][0] == last_word[0] and
                                                line_list[k][w_index + 1][1][0][0] < last_word[1][1][0]):
                                            continue
                                except:
                                    pass
                                word_index = probable_values[i][2]
                                line_list[k][word_index][0] = probable_values[i][0]
                                line_list[k][word_index][1] = [probable_values[i][1][0], word[1][1], word[1][2],
                                                               probable_values[i][1][3]]
                                for s in range(word_index + 1, w_index + 1):
                                    if s not in pop_elements:
                                        pop_elements.append(s)
                                probable_values = []
                                break
                        else:
                            probable_values[i][0] = 'XXXX'
                    if list(filter(lambda x: x.startswith(word[0]), self.digits_dict)):
                        probable_values.append(copy.deepcopy(word))
                        probable_values[-1].append(w_index)
                    probable_values = list(filter(lambda w: w[0] != 'XXXX', probable_values))
                else:
                    probable_values = []

            if junk_char_seq:
                line_list[k][junk_char_seq[0] - 1][0] = line_list[k][junk_char_seq[0] - 1][0].replace(junk_char, '')
                for v in junk_char_seq:
                    if v not in pop_elements:
                        pop_elements.append(v)
                pop_elements.append(junk_char_seq[-1] + 1)
                junk_char_seq = []
                junk_char = ''

            for i in reversed(sorted(pop_elements)):
                line_list[k].pop(i)

        # Return updated list
        return line_list

    def getSlopeIntercept(self, X, Y):
        """
        Function to find slope and intercept of line based on given list of X, Y points

        :param X: List of X co-ordinates
        :param Y: List of Y co-ordinates
        :return: Y-intercept, slope of line
        """

        xbar = sum(X) / len(X)
        ybar = sum(Y) / len(Y)
        n = len(X)  # or len(Y)

        numer = sum(xi * yi for xi, yi in zip(X, Y)) - n * xbar * ybar
        denum = sum(xi ** 2 for xi in X) - n * xbar ** 2

        try:
            b = numer / denum
            a = ybar - b * xbar
        except:
            return 0, 0

        return a, b

    def checkWordWithBoundary(self,word,line,boundaries):
        """
        Function to check whether a <<word>> is eligible to be part of a <<line>> as per <<boundaries>>
        """

        if not boundaries:
            return True
        
        # Check if word's entry changes standard deviation of line significantly
        if statistics.stdev(line['y_points']+word[2:]) < 3:
            return True

        # positive delta allowed
        pos_delta_x = int(self.mode_height * 0.5)
        pos_delta_y = int(self.mode_height * 1.0)

        # negative delta allowed
        neg_delta_x = -int(self.mode_height * 0.5)
        neg_delta_y = -int(self.mode_height * 1.0)
        
        # Check word's position w.r.to given boundaries
        is_bounded = False
        right_bounded = False
        left_bounded = False
        right_x2 = None
        left_x1 = None

        # extended flags to be used for checking extended boundaries
        extended_right = False
        extended_left = False

        try:
            # check if word is bounded by right boundary on left side
            right_x2 = min(enumerate(filter(lambda x: (x[1][1]+neg_delta_y<=word[2]<=x[1][2]+pos_delta_y and word[1]>=x[1][0]+neg_delta_x),enumerate(boundaries['right']))), key=lambda x: word[1]-x[1][1][0])
            right_bounded = True

            # check if it is not bounded because of extended boundary
            if not right_x2[1][1][1] <= word[2] <= right_x2[1][1][2]:
                extended_right = True
                
            # check if no left boundary found closer than right boundary on left side of word
            left_x2 = min(enumerate(filter(lambda x: (x[1][1]+neg_delta_y<=word[2]<=x[1][2]+pos_delta_y and word[1]>=x[1][0]),enumerate(boundaries['left']))), key=lambda x: word[1]-x[1][1][0])
            if word[1] - left_x2[1][1][0] < pos_delta_x or left_x2[1][1][0] < right_x2[1][1][0]:
                is_bounded = True
            else:
                right_bounded = False
        except:
            if right_bounded:
                is_bounded = True


        try:
            # check if word is bounded by left boundary on right side
            left_x1 = min(enumerate(filter(lambda x: (x[1][1]+neg_delta_y<=word[2]<=x[1][2]+pos_delta_y and word[0]<=x[1][0]+pos_delta_x),enumerate(boundaries['left']))), key=lambda x: x[1][1][0]-word[0])
            left_bounded = True

            # check if it is not bounded because of extended boundary
            if not left_x1[1][1][1] <= word[2] <= left_x1[1][1][2]:
                extended_left = True

            # check if no right boundary found closer than left boundary on right side of word
            right_x1 = min(enumerate(filter(lambda x: (x[1][1]+neg_delta_y<=word[2]<=x[1][2]+pos_delta_y and word[0]<=x[1][0]),enumerate(boundaries['right']))), key=lambda x: x[1][1][0]-word[0])
            if right_x1[1][1][0] - word[0] < pos_delta_x or right_x1[1][1][0] > left_x1[1][1][0]:
                is_bounded = True
            else:
                left_bounded = False
        except:
            if left_bounded:
                is_bounded = True

        # if word is not bounded, let line allocation happen as per normal condition
        if not is_bounded:
            return True

        # Check line's position w.r.to given boundaries
        l_is_bounded = False
        l_right_bounded = False
        l_left_bounded = False
        right_l = None
        left_l = None

        # Check if given line is bounded by same boundaries, if not, given line is not eligible for given word 
        if min(line['x_points']) > word[1]:
            # if line is on right side of word, check right bounded of line
            check_word = [line['x_points'][0]] + line['y_points'][0:2]
        elif max(line['x_points']) < word[0]:
            # if line is on left side of word, check left bounded
            check_word = [line['x_points'][-1]] + line['y_points'][-2:]
        else:
            return True
    
        try:
            # check if line is bounded by right boundary on left side
            right_l = min(enumerate(filter(lambda x: (x[1][1]+neg_delta_y<=check_word[1]<=x[1][2]+pos_delta_y and check_word[0]>=x[1][0]+neg_delta_x),enumerate(boundaries['right']))), key=lambda x: check_word[0]-x[1][1][0])
            l_right_bounded = True

            # check if it is not bounded because of extended boundary
            if not right_l[1][1][1] <= check_word[1] <= right_l[1][1][2]:
                extended_right = True

            # check if no left boundary found closer than right boundary on left side of check_word
            temp = min(enumerate(filter(lambda x: (x[1][1]+neg_delta_y<=check_word[1]<=x[1][2]+pos_delta_y and check_word[0]>=x[1][0]),enumerate(boundaries['left']))), key=lambda x: check_word[0]-x[1][1][0])
            if check_word[0] - temp[1][1][0] < pos_delta_x or temp[1][1][0] < right_l[1][1][0]:
                l_is_bounded = True
            else:
                l_right_bounded = False
        except:
            if l_right_bounded:
                l_is_bounded = True


        try:
            # check if check_word is bounded by left boundary on right side
            left_l = min(enumerate(filter(lambda x: (x[1][1]+neg_delta_y<=check_word[1]<=x[1][2]+pos_delta_y and check_word[0]<=x[1][0]+pos_delta_x),enumerate(boundaries['left']))), key=lambda x: x[1][1][0]-check_word[0])
            l_left_bounded = True

            # check if it is not bounded because of extended boundary
            if not left_l[1][1][1] <= check_word[1] <= left_l[1][1][2]:
                extended_left = True

            # check if no right boundary found closer than left boundary on right side of check_word
            temp = min(enumerate(filter(lambda x: (x[1][1]+neg_delta_y<=check_word[1]<=x[1][2]+pos_delta_y and check_word[0]<=x[1][0]),enumerate(boundaries['right']))), key=lambda x: x[1][1][0]-check_word[0])
            if temp[1][1][0] - check_word[0] < pos_delta_x or temp[1][1][0] > left_l[1][1][0]:
                l_is_bounded = True
            else:
                l_left_bounded = False
        except:
            if l_left_bounded:
                l_is_bounded = True

        # if Word is bounded and line is not bounded, return False 
        if not l_is_bounded:
            return False
        
        
        if (right_bounded or l_right_bounded) and not extended_right:
            # if either word or line is not right bounded
            if not (right_bounded and l_right_bounded):
                return False
            # if both are not bounded to same right boundary
            elif right_x2[1][1] != right_l[1][1]:
                return False
        
        if (left_bounded or l_left_bounded) and not extended_left:
            # if either word or line is not right bounded
            if not (left_bounded and l_left_bounded):
                return False
            # if both are not bounded to same right boundary
            elif left_x1[1][1] != left_l[1][1]:
                return False

        return True

    def get_lines_and_state_lines(self, res, mode_slant, boundaries=False):
        """
        Function to create a line list having words falling in that line.
        Idea is to create a virtual copy of original document.

        :param res: Sorted list of words as per x and y axis
        :param mode_slant: Standard Model slant
        :return: List of lines having words (Un-arranged), lines having state in it
        """

        # Initialise state lines and list of lines
        state_lines = []
        line_list = []

        # initialise all values for reading first word of document to start algorithm
        prev_word = res[0]
        mod_ht = abs(res[0][1][0][1] - res[0][1][3][1])
        line_details = [
            {'intercept': 0, 'slope': 0, 'x_points': [], 'y_points': [], 'heights': [mod_ht], 'mod_ht': mod_ht},
            {'intercept': 0, 'slope': 0, 'x_points': [], 'y_points': []},
            {'intercept': 0, 'slope': 0, 'x_points': [], 'y_points': []}]
        cx_1 = res[0][1][0][0]
        cy_1 = res[0][1][0][1]
        cx_2 = res[0][1][1][0]
        cy_2 = res[0][1][1][1]
        line_details[-3]['x_points'].extend([cx_1, cx_2])
        line_details[-3]['y_points'].extend([cy_1, cy_2])

        cx_3 = res[0][1][2][0]
        cy_3 = res[0][1][2][1]
        cx_4 = res[0][1][3][0]
        cy_4 = res[0][1][3][1]
        line_details[-2]['x_points'].extend([cx_3, cx_4])
        line_details[-2]['y_points'].extend([cy_3, cy_4])

        # Referene point 1 for word is at half height, quarter width
        cx_5 = int(res[0][1][0][0] + ((res[0][1][1][0] - res[0][1][0][0]) * 0.25))
        cy_5 = int((res[0][1][0][1] + res[0][1][3][1]) / 2)
        # Referene point 2 for word is at half height, 3/4th width
        cx_6 = int(res[0][1][0][0] + ((res[0][1][1][0] - res[0][1][0][0]) * 0.75))
        cy_6 = int((res[0][1][1][1] + res[0][1][2][1]) / 2)
        line_details[-1]['x_points'].extend([cx_5, cx_6])
        line_details[-1]['y_points'].extend([cy_5, cy_6])

        line_list.append([[res[0][0], res[0][1]]])

        # Check if first word is a state word, if yes add it to state list
        if res[0] in self.find_ocr_words:
            state_lines.append([res[0], 0])

        # Final fit list for checking index of finalised line
        final_fit = [-1, -2, -3]

        # Multipliers for allowed height difference and allowed slant difference
        if self.compressed_text:
            height_diff_multiplier = 1
            slant_diff_multiplier = 0.5
        else:
            height_diff_multiplier = 0.72
            slant_diff_multiplier = 0.45

        """
        Line of Best Fit (Least Square Method)
        """
        for i, values in enumerate(res[1:]):
            if prev_word[0] == values[0] and ((values[1][0][0] <= prev_word[1][0][0] <= values[1][1][0]) or \
                                              (prev_word[1][0][0] <= values[1][0][0] <= prev_word[1][1][0])):
                continue
            prev_word = values
            cx_1 = values[1][0][0]
            cy_1 = values[1][0][1]
            cx_2 = values[1][1][0]
            cy_2 = values[1][1][1]

            cx_3 = values[1][2][0]
            cy_3 = values[1][2][1]
            cx_4 = values[1][3][0]
            cy_4 = values[1][3][1]

            # if word co-ordinates are slanted, normalize word by increasing and decreasing y-axis values
            iter_no = 1
            while abs(cy_1 - cy_2) > (2 * mode_slant):
                if cy_1 < cy_2:
                    if iter_no % 2 != 0:
                        cy_1 += 1
                    else:
                        cy_2 -= 1
                else:
                    if iter_no % 2 != 0:
                        cy_1 -= 1
                    else:
                        cy_2 += 1
                iter_no += 1

            iter_no = 1
            while abs(cy_4 - cy_3) > (2 * mode_slant):
                if cy_4 < cy_3:
                    if iter_no % 2 != 0:
                        cy_4 += 1
                    else:
                        cy_3 -= 1
                else:
                    if iter_no % 2 != 0:
                        cy_4 -= 1
                    else:
                        cy_3 += 1
                iter_no += 1

            # Referene point 1 for word is at half height, quarter width
            cx_5 = int(cx_1 + ((cx_2 - cx_1) * 0.25))
            cy_5 = int((cy_1 + cy_4) / 2)
            # Referene point 2 for word is at half height, 3/4th width
            cx_6 = int(cx_1 + ((cx_2 - cx_1) * 0.75))
            cy_6 = int((cy_2 + cy_3) / 2)

            
            line_num = -1
            line_num2 = -2
            line_num3 = -3

            # Ideally word should be added to last line, for that document should not be too much slanted
            if mode_slant < 0.5 and abs(sum(line_details[-3]['y_points'][-2:]) +
                                        sum(line_details[-2]['y_points'][-2:]) +
                                        sum(line_details[-1]['y_points'][-2:]) -
                                        sum(list([cy_1, cy_2, cy_3, cy_4, cy_5, cy_6]))) < 5:
                line_list[-1].append([values[0], values[1]])
                line_added_to = -1
            else:

                # Update intercept and slope of last three lines
                line_details[line_num]['intercept'], line_details[line_num]['slope'] = self.getSlopeIntercept(
                    line_details[line_num]['x_points'], line_details[line_num]['y_points'])
                line_details[line_num2]['intercept'], line_details[line_num2]['slope'] = self.getSlopeIntercept(
                    line_details[line_num2]['x_points'], line_details[line_num2]['y_points'])
                line_details[line_num3]['intercept'], line_details[line_num3]['slope'] = self.getSlopeIntercept(
                    line_details[line_num3]['x_points'], line_details[line_num3]['y_points'])

                if abs(values[1][0][1] - values[1][2][1]) != line_details[line_num3]['mod_ht']:
                    line_details[line_num3]['mod_ht'] = max(set(line_details[line_num3]['heights']),
                                                            key=line_details[line_num3]['heights'].count)

                # Check error of proximity of both reference points with last 3 lines using slope intercept equation.
                # delta = (mx + c) - y, where m is slope and c is intercept
                y_fits = []
                try:
                    line_1_delta = line_2_delta = line_3_delta = 100
                    line_1_delta += abs((line_details[-3]['slope'] * cx_1 + line_details[-3]['intercept']) - cy_1)
                    line_1_delta += abs((line_details[-3]['slope'] * cx_2 + line_details[-3]['intercept']) - cy_2)
                    line_1_delta += abs((line_details[-2]['slope'] * cx_3 + line_details[-2]['intercept']) - cy_3)
                    line_1_delta += abs((line_details[-2]['slope'] * cx_4 + line_details[-2]['intercept']) - cy_4)
                    line_1_delta += abs((line_details[-1]['slope'] * cx_5 + line_details[-1]['intercept']) - cy_5)
                    line_1_delta += abs((line_details[-1]['slope'] * cx_6 + line_details[-1]['intercept']) - cy_6)
                    y_fits.append((line_1_delta - 100) / 6)

                    line_2_delta += abs((line_details[-6]['slope'] * cx_1 + line_details[-6]['intercept']) - cy_1)
                    line_2_delta += abs((line_details[-6]['slope'] * cx_2 + line_details[-6]['intercept']) - cy_2)
                    line_2_delta += abs((line_details[-5]['slope'] * cx_3 + line_details[-5]['intercept']) - cy_3)
                    line_2_delta += abs((line_details[-5]['slope'] * cx_4 + line_details[-5]['intercept']) - cy_4)
                    line_2_delta += abs((line_details[-4]['slope'] * cx_5 + line_details[-4]['intercept']) - cy_5)
                    line_2_delta += abs((line_details[-4]['slope'] * cx_6 + line_details[-4]['intercept']) - cy_6)
                    y_fits.append((line_2_delta - 100) / 6)

                    line_3_delta += abs((line_details[-9]['slope'] * cx_1 + line_details[-9]['intercept']) - cy_1)
                    line_3_delta += abs((line_details[-9]['slope'] * cx_2 + line_details[-9]['intercept']) - cy_2)
                    line_3_delta += abs((line_details[-8]['slope'] * cx_3 + line_details[-8]['intercept']) - cy_3)
                    line_3_delta += abs((line_details[-8]['slope'] * cx_4 + line_details[-8]['intercept']) - cy_4)
                    line_3_delta += abs((line_details[-7]['slope'] * cx_5 + line_details[-7]['intercept']) - cy_5)
                    line_3_delta += abs((line_details[-7]['slope'] * cx_6 + line_details[-7]['intercept']) - cy_6)
                    y_fits.append((line_3_delta - 100) / 6)
                except:
                    pass

                # point with lowest delta is closest to that line
                index_min = min(range(len(y_fits)), key=y_fits.__getitem__)

                start_new_line = True

                # delta should be lower 40% of mod height of finalised line
                if abs(abs(cy_2 - cy_3) - line_details[final_fit[index_min] * 3]['mod_ht']) <= round( \
                        line_details[final_fit[index_min] * 3]['mod_ht'] * height_diff_multiplier) and y_fits[index_min] < ( \
                                line_details[final_fit[index_min] * 3]['mod_ht'] * slant_diff_multiplier):
                    # check if word and finalised lines are bounded by same boundaries
                    if self.checkWordWithBoundary([cx_1,cx_2,cy_1,cy_2],line_details[final_fit[index_min] * 3],boundaries):
                        # add word to finalized line
                        line_added_to = line_num = final_fit[index_min]
                        line_list[line_num].append([values[0], values[1]])

                        # line_num for line_details updation
                        line_num3 = line_num * 3
                        line_num2 = line_num3 + 1
                        line_num = line_num3 + 2

                        start_new_line = False
                    else:
                        # check if any other line other than current minimum is eligible for this word
                        
                        # update current min with max value
                        y_fits[index_min] = max(y_fits)

                        # find new min value
                        index_min = min(range(len(y_fits)), key=y_fits.__getitem__)
                        
                        # delta should be lower 40% of mod height of finalised line
                        if abs(abs(cy_2 - cy_3) - line_details[final_fit[index_min] * 3]['mod_ht']) <= round( \
                            line_details[final_fit[index_min] * 3]['mod_ht'] * height_diff_multiplier) and y_fits[index_min] < ( \
                                line_details[final_fit[index_min] * 3]['mod_ht'] * slant_diff_multiplier) and self.checkWordWithBoundary([cx_1,cx_2,cy_1,cy_2],line_details[final_fit[index_min] * 3],boundaries):
                            # add word to finalized line
                            line_added_to = line_num = final_fit[index_min]
                            line_list[line_num].append([values[0], values[1]])

                            # line_num for line_details updation
                            line_num3 = line_num * 3
                            line_num2 = line_num3 + 1
                            line_num = line_num3 + 2

                            start_new_line = False

                if start_new_line:
                    line_list.append([[values[0], values[1]]])
                    line_details.append({'intercept': 0, 'slope': 0, 'x_points': [], 'y_points': [], 'heights': [],
                                         'mod_ht': abs(values[1][0][1] - values[1][3][1])})
                    line_details.append({'intercept': 0, 'slope': 0, 'x_points': [], 'y_points': []})
                    line_details.append({'intercept': 0, 'slope': 0, 'x_points': [], 'y_points': []})

                    # line number where word has finally been added
                    line_added_to = line_num = -1
                    line_num2 = -2
                    line_num3 = -3

            # Update line details of the line where word was added
            # Update reference points list of that line

            line_details[line_num3]['x_points'].extend([cx_1, cx_2])
            line_details[line_num3]['y_points'].extend([cy_1, cy_2])

            line_details[line_num2]['x_points'].extend([cx_3, cx_4])
            line_details[line_num2]['y_points'].extend([cy_3, cy_4])

            line_details[line_num]['x_points'].extend([cx_5, cx_6])
            line_details[line_num]['y_points'].extend([cy_5, cy_6])

            # Update height list of that line
            line_details[line_num3]['heights'].append(abs(values[1][0][1] - values[1][3][1]))

            # If word is a state word, update state line list
            if values in self.find_ocr_words:
                state_lines.append([values, len(line_list) + line_added_to])

        # For all lines having only one word, check next line for that word and see if it fits there.
        pop_lines = []
        for index, line in enumerate(line_list[:-1]):
            if len(line) > 1:
                continue
            k = index * 3
            if line[0][0] == 'Check' or line[0][0] == 'Rate':
                pop_lines.append(index)
                continue
            [cx_1, cx_2] = line_details[k]['x_points']
            [cy_1, cy_2] = line_details[k]['y_points']

            # check delta with next line of that word and see if it fits there.
            y_fits = []
            try:
                y_fits.append(abs((line_details[k + 3]['slope'] * cx_1 + line_details[k + 3]['intercept']) - cy_1))
                y_fits.append(abs((line_details[k + 3]['slope'] * cx_2 + line_details[k + 3]['intercept']) - cy_2))
            except:
                continue
            if min(y_fits) < (line_details[k + 3]['mod_ht'] / 3):
                line_list[index + 1].append(line[0])
                pop_lines.append(index)
        # For all lines that are to be removed, update state line number accordingly
        for i in reversed(pop_lines):
            line_list.pop(i)
            for k, s in enumerate(state_lines):
                if s[1] > i:
                    state_lines[k][1] -= 1

        return line_list, state_lines

    def rejectAndSortWords(self, mode_slant):
        """
        Function used in rectifying data.
        It takes list of words as input and rejects all words above or below permissible height and slant and
        sort words with respect to x-axis for each small range of y-axis

        :param mode_slant: Mode of all word's slant value, will be used for generating lines of code
        :return: Sorted list of words as per x and y axis & average character size in document
        """

        # sort all words as per y-axis of its first element
        res = sorted(self.result, key=lambda x: x[1][0][1])

        half_width = round(max(enumerate(res), key=lambda x: x[1][1][1][0])[1][1][1][0] / 2)

        # Create upper and lower limit for permissible heights
        if self.large_text:
            max_height = self.mode_height * 2.8
        else:
            max_height = self.mode_height * 2.35
        min_height = self.mode_height * 0.5

        # Create permissible slant limit
        slant_reject = round(mode_slant + (self.mode_height / 2.5))

        final_res = []

        # Define a range size for each bucket and create a limit for first bucket
        range_size = round(self.mode_height * 0.22)
        neg_range_size = round(range_size * 0.5)
        upto_y = res[0][1][0][1] + range_size
        half_range_size = round(range_size * 2) if round(range_size * 2) > 0 else 1

        # Define variables to store final sorted word list, and range buckets
        range_bucket = []

        # For each word, reject words as per defined limits, and sort words of each buckets
        for values in res:
            # If word size is not in permissible heights limits, reject it
            if abs(values[1][0][1] - values[1][3][1]) > max_height or abs(
                    values[1][0][1] - values[1][3][1]) < min_height:
                # util_obj.customPrint('Rejected word ', values)
                continue

            # If word slant is not in permissible slant limits, reject it
            # if abs(values[1][0][1] - values[1][1][1]) > slant_reject:
            #     util_obj.customPrint('Rejected word because of improper alignment', values)
            #     continue

            # If word is a part of current bucket range, add it to the bucket

            if values[1][0][1] <= upto_y:
                range_bucket.append(values)
            else:
                # Define new range for upcoming words                
                upto_y = values[1][0][1] + range_size if values[1][0][0] < half_width else values[1][0][1] + half_range_size
                neg_y = values[1][0][1] - neg_range_size

                # remove words upto neg range from previous bucket
                remove_words = list(filter(lambda x: x[1][0][1] >= neg_y,range_bucket))
                if remove_words:
                    range_bucket = [x for x in range_bucket if x not in remove_words]
                
                # sort bucket as per x-axis, and add it to final output.
                range_bucket = sorted(range_bucket, key=lambda x: x[1][0][0])
                final_res.extend(range_bucket)
                
                # start new bucket
                range_bucket = [values]
                if remove_words:
                    range_bucket.extend(remove_words)


        # Sort final bucket as per x-axis, and add it to final output
        range_bucket = sorted(range_bucket, key=lambda x: x[1][0][0])
        final_res.extend(range_bucket)

        return final_res

    def mergeHalfWords(self,line_list):
        for l_index, line in enumerate(line_list):
            for w_index, word in enumerate(line):
                half_c = list(filter(lambda x: x.startswith(word[0].lower()), self.imp_words_w_spaces))
                if half_c and not difflib.get_close_matches(word[0].lower(),half_c,cutoff=0.95):
                    # util_obj.customPrint('half word ', half_c)
                    y_axis = word[1][3][1]
                    try:
                        curr_l_index = l_index
                        while(True):
                            n_word = min(enumerate(line_list[curr_l_index + 1]),
                                            key=lambda x: abs(word[1][0][0] - x[1][1][0][0]) if x[1][1][1][0] >
                                                                                                word[1][0][
                                                                                                    0] else float(
                                                'inf'))
                            if n_word[1][1][1][0] > word[1][0][0] and abs(n_word[1][1][0][1] - y_axis)\
                                    <= int(abs(word[1][0][1]-word[1][2][1])/3 + 1):
                                if list(filter(lambda x: x.startswith(word[0].lower()+n_word[1][0].lower()),
                                                        half_c)):
                                    line_list[l_index][w_index][0] = word[0] + n_word[1][0]
                                    y_axis = n_word[1][1][3][1]
                                    n_index = line_list[curr_l_index + 1].index(n_word[1])
                                    line_list[curr_l_index + 1][n_index][0] = '-'
                                    # If complete word has become a column header, update current word
                                    if difflib.get_close_matches(word[0].lower(), half_c,
                                                                    cutoff=0.95):
                                        break
                                    else:
                                        curr_l_index += 1
                                elif list(filter(lambda x: x.startswith(word[0].lower()+' '+n_word[1][0].lower()),half_c)):
                                    line_list[l_index][w_index][0] = word[0]+' '+n_word[1][0]
                                    y_axis = n_word[1][1][3][1]
                                    n_index = line_list[curr_l_index + 1].index(n_word[1])
                                    line_list[curr_l_index + 1][n_index][0] = '-'
                                    # If complete word has become a column header, update current word
                                    if difflib.get_close_matches(word[0].lower(), half_c,
                                                                    cutoff=0.95):
                                        break
                                    else:
                                        curr_l_index += 1
                                else:
                                    # If merged word is not column header
                                    break
                            else:
                                break
                    except:
                        pass
        return line_list

    def rectifyData(self, mode_slant, boundaries = None):
        """
        Function to sort list of words and characters to create a list of lines having words and their co-ordinates.

        :param mode_slant: Mode of all word's slant value, will be used for generating lines of code
        :return: Complete line list, lines having state codes of address
        """

        # Reject improper words and sort words by x and y axis
        res = self.rejectAndSortWords(mode_slant)

        # Get list of lines (Un-arranged), along with lines having state words in it.
        line_list, state_lines = self.get_lines_and_state_lines(res, mode_slant, boundaries)

        # Remove junk sequences and merge float values words
        line_list = self.removeJunkAndMergeFloatWords(line_list)

        decimal_value = False

        # Use google description to merge words in next step
        desc = self.description
        # util_obj.customPrint(desc)

        # Line numbers that are to be removed
        pop_lines = []

        # For each line merge words as per document
        for k, line in enumerate(line_list):
            line = line_list[k]
            # if len(line) == 0:
            #     pop_lines.append(k)
            #     continue
            pop_elements = []
            word_end = 0
            space_width = 0
            new_line_start = True

            spaces = []
            word_val = ''

            for w_index, word in enumerate(line):
                if word[0] in ('|', 'USD', '=', '>', ':', 'less', 'equals', ''):
                    pop_elements.append(w_index)
                    continue

                special_char = False
                word_diff = abs(word_end - word[1][0][0])
                # word_height = abs(word[1][0][1] - word[1][2][1])

                # check word without space
                d = word_val + word[0]
                d1 = word_val + ' ' + word[0]

                # if new word is very close to the previous word
                # or d1.lower() in ['new york']:
                if (word_diff <= round(space_width) and not new_line_start) or d1.lower() in ['new york']:
                    if word[0] not in (',', '.', '/', '-', '–', '—', '%','(','K',')'):
                        if util_obj.isFloat(word_val):
                            if not util_obj.isFloatOrInt(word[0]) \
                                    and word[0].lower() not in ['jan', 'january', 'feb', 'february', 'mar', 'march',
                                                                'apr', 'april', 'may', 'jun', 'june',
                                                                'jul', 'july', 'aug', 'august', 'sep', 'sept',
                                                                'september', 'oct', 'october', 'nov', 'november', 'dec',
                                                                'december']:
                                line_list[k][w_index] = word

                                # space_width = abs(word[1][2][0]-word[1][3][0])/len(word[0]) * 2.5
                                spaces = []
                                space_width = abs(word[1][2][0] - word[1][3][0]) / len(word[0]) * 2.75
                                spaces.append(space_width / 2.75)

                                word_end = word[1][2][0]
                                word_val = word[0]
                                prev_index = w_index
                                check_word = word
                                continue
                            elif len(word[0]) == 2:
                                if '.' not in word_val and not (
                                        '/' in word_val or '-' in word_val or '–' in word_val or '—' in word_val):
                                    d = word_val + '.' + word[0]
                                    decimal_value = True
                                if word_val[-1] == '.':
                                    d = word_val + word[0]
                                    decimal_value = True
                                    space_width = 0
                            elif word[0] in self.digits_dict:
                                line_list[k][w_index] = word

                                # space_width = abs(word[1][2][0]-word[1][3][0])/len(word[0]) * 2.5
                                spaces = []
                                space_width = abs(word[1][2][0] - word[1][3][0]) / len(word[0]) * 2.75
                                spaces.append(space_width / 2.75)

                                word_end = word[1][2][0]
                                word_val = word[0]
                                prev_index = w_index
                                check_word = word
                                continue
                        # specifically for Paycor paystubs:
                        # elif word_val == 'NET' and bool(re.search(r'\d', word[0])):
                        elif word[0] in self.digits_dict:
                            line_list[k][w_index] = word

                            # space_width = abs(word[1][2][0]-word[1][3][0])/len(word[0]) * 2.5
                            spaces = []
                            space_width = abs(word[1][2][0] - word[1][3][0]) / len(word[0]) * 2.75
                            spaces.append(space_width / 2.75)

                            word_end = word[1][2][0]
                            word_val = word[0]
                            prev_index = w_index
                            check_word = word
                            continue
                    else:
                        if not (util_obj.isFloatOrInt(word_val) or bool(re.search(
                                r'(401|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)',
                                word_val.lower()))):
                            # check if next word is a digit
                            try:
                                # if util_obj.isFloatOrInt(line[w_index + 1][0]):
                                if line[w_index + 1][0] in self.digits_dict:
                                    line_list[k][w_index] = word

                                    # space_width = abs(word[1][2][0]-word[1][3][0])/len(word[0]) * 2.5
                                    spaces = []
                                    space_width = abs(word[1][2][0] - word[1][3][0]) / len(word[0]) * 2.75
                                    spaces.append(space_width / 2.75)

                                    word_end = word[1][2][0]
                                    word_val = word[0]
                                    prev_index = w_index
                                    check_word = word
                                    continue
                            except:
                                pass
                        special_char = True
                    if d in desc or decimal_value:
                        if d1 in desc:
                            try:
                                if list(filter(lambda x: x.startswith(d1 + ' ' + line[w_index + 1][0]),
                                               self.words_dict)):
                                    # use d1 in desc block
                                    pass
                                else:
                                    raise Exception('Go to exception')
                            except:
                                decimal_value = False
                                line_list[k][prev_index][0] = d
                                line_list[k][prev_index][1] = [check_word[1][0], word[1][1], word[1][2],
                                                               check_word[1][3]]
                                # remove current word from line list
                                pop_elements.append(w_index)

                                # if word belongs to column header, no further word should be added in it.
                                col_word = difflib.get_close_matches(d.lower(), self.full_stop_words, cutoff=0.95)
                                try:
                                    if col_word and not line[w_index + 1][0] == ')':
                                        # util_obj.customPrint('we are here making space width zero ', word)
                                        space_width = 0
                                except:
                                    pass
                                word_val = d
                                word_end = word[1][2][0]
                                continue
                        else:
                            decimal_value = False
                            line_list[k][prev_index][0] = d
                            line_list[k][prev_index][1] = [check_word[1][0], word[1][1], word[1][2], check_word[1][3]]
                            # remove current word from line list
                            pop_elements.append(w_index)

                            # if word belongs to column header, no further word should be added in it.
                            col_word = difflib.get_close_matches(d.lower(), self.full_stop_words, cutoff=0.95)
                            try:
                                if col_word and not line[w_index + 1][0] == ')':
                                    # util_obj.customPrint('we are here making space width zero ', word)
                                    space_width = 0
                            except:
                                pass
                            word_val = d
                            word_end = word[1][2][0]
                            continue

                    if d1 in desc:
                        # check if combined word is a column header
                        if list(filter(lambda x: x.startswith(d1.lower()), self.full_stop_words)):
                            col_word = difflib.get_close_matches(d1.lower(), self.full_stop_words, cutoff=0.95)
                            if col_word:
                                # util_obj.customPrint('we are here making space width zero ', word)
                                space_width = 0
                            elif difflib.get_close_matches(d1.lower(), self.half_stop_words,
                                                           cutoff=0.95):
                                space_width = word_diff * 1.75 if word_diff < 10 else word_diff * 1.5

                                # try:
                                #     if d1.lower() in ['period start', 'period begin', 'period ending', 'period end',
                                #                       'period starting', 'period beginning', 'pay start', 'pay begin',
                                #                       'earns begin', 'pay end', 'earns end']:
                                #         if line[w_index + 1][0].lower() not in ['date']:
                                #             space_width = 0
                                # except:
                                #     pass
                            else:
                                spaces.append(word_diff)
                                if len(word[0]) > 2:
                                    spaces.append(abs(word[1][2][0] - word[1][3][0]) / len(word[0]))
                                space_width = sum(spaces) / len(spaces) * 2

                                # space_width = word_diff * space_wise_multiplier

                        else:
                            # check if prev word and next word are column headers
                            if list(filter(lambda x: x.startswith(word[0].lower()), self.full_stop_words)) \
                                    and difflib.get_close_matches(word_val.lower(),self.full_stop_words,cutoff=0.95):
                                line_list[k][w_index] = word

                                # space_width = abs(word[1][2][0]-word[1][3][0])/len(word[0]) * 2.5
                                spaces = []
                                space_width = abs(word[1][2][0] - word[1][3][0]) / len(word[0]) * 2.75
                                spaces.append(space_width / 2.75)

                                word_end = word[1][2][0]
                                word_val = word[0]
                                prev_index = w_index
                                check_word = word
                                continue
                            elif difflib.get_close_matches(d1.lower(), self.half_stop_words,
                                                           cutoff=0.95):
                                space_width = word_diff * 1.75 if word_diff < 10 else word_diff * 1.5

                                try:
                                    if d1.lower() in ['period start', 'period begin', 'period ending', 'period end',
                                                      'period starting', 'period beginning', 'pay start', 'pay begin',
                                                      'earns begin', 'pay end', 'earns end']:
                                        if line[w_index + 1][0].lower() not in ['date']:
                                            space_width = 0
                                except:
                                    pass
                            # define space width
                            elif not special_char and word_diff > 5:
                                spaces.append(word_diff)
                                if len(word[0]) > 2:
                                    spaces.append(abs(word[1][2][0] - word[1][3][0]) / len(word[0]))
                                space_width = sum(spaces) / len(spaces) * 2

                                # space_width = word_diff * space_wise_multiplier if word_diff < 9 else word_diff * 2.1

                        line_list[k][prev_index][0] = d1
                        line_list[k][prev_index][1] = [check_word[1][0], word[1][1], word[1][2], check_word[1][3]]
                        # remove current word from line list
                        pop_elements.append(w_index)
                        word_val = d1
                        word_end = word[1][2][0]
                        continue

                    # add this word without space to previous word if its a special character
                    if special_char:
                        line_list[k][prev_index][0] = d
                        line_list[k][prev_index][1] = [check_word[1][0], word[1][1], word[1][2], check_word[1][3]]
                        # remove current word from line list
                        pop_elements.append(w_index)
                        word_val = d
                        word_end = word[1][2][0]
                        continue
                    line_list[k][w_index] = word

                    # space_width = abs(word[1][2][0]-word[1][3][0])/len(word[0]) * 2.5

                    spaces = []
                    space_width = abs(word[1][2][0] - word[1][3][0]) / len(word[0]) * 2.75
                    spaces.append(space_width / 2.75)

                    word_end = word[1][2][0]
                    word_val = word[0]
                    prev_index = w_index
                    check_word = word
                else:
                    new_line_start = False
                    line_list[k][w_index] = word

                    # space_width = abs(word[1][2][0]-word[1][3][0])/len(word[0]) * 2.5
                    spaces = []
                    space_width = abs(word[1][2][0] - word[1][3][0]) / len(word[0]) * 2.75
                    if len(word[0]) == 1:
                        space_width = space_width * 2
                    spaces.append(space_width / 2.75)

                    word_end = word[1][2][0]
                    word_val = word[0]
                    prev_index = w_index
                    check_word = word
            for i in reversed(pop_elements):
                line_list[k].pop(i)

        # For all imp words with spaces, check if half word is on next line
        line_list = self.mergeHalfWords(line_list)
    
        # remove all unwanted words from line list, and lines if they become empty after this operation
        for k, line in enumerate(line_list):
            pop_elements = []
            for w_index, word in enumerate(line):
                if word[0] in (',', '.', '/', '-', '–', '—', '%'):
                    pop_elements.append(w_index)
                    continue
            for i in reversed(pop_elements):
                line_list[k].pop(i)
            if len(line_list[k]) == 0:
                pop_lines.append(k)

        # For all lines that are to be removed, update state line number accordingly
        for i in reversed(pop_lines):
            line_list.pop(i)
            for k, s in enumerate(state_lines):
                if s[1] > i:
                    state_lines[k][1] -= 1

        return line_list, state_lines

    def getDocumentStructure(self):
        # Check for text words
        text_result = copy.deepcopy(self.result)
        word_buckets = []
        digit_buckets = []
        check_words = list( set(self.words_dict) - set(self.full_stop_words) - set(['yes','no','Yes','No']))
        for i, value in enumerate(text_result):
            if bool(re.search('([A-Z])\w+|401',value[0])) and list(filter(lambda x: x.startswith(value[0]),check_words)):
                try:
                    min_word = min(enumerate(word_buckets), key=lambda x: abs((float(sum(x[1][0])/len(x[1][0])))-value[1][0][0]))
                    if (abs((float(sum(min_word[1][0])/len(min_word[1][0]))) - value[1][0][0]) < self.mode_height/2) and \
                        (abs(min_word[1][1][-1][1][3][1] - value[1][0][1]) < self.mode_height * 5): 
                        word_buckets[min_word[0]][1].append(value)
                        word_buckets[min_word[0]][0].append(value[1][0][0])
                    else:
                        word_buckets.append([[value[1][0][0]],[value]])
                except:
                    word_buckets.append([[value[1][0][0]],[value]])
            elif bool(re.search('\d{2}',value[0])) and list(filter(lambda x: x.endswith(value[0]), self.digits_dict)):
                try:
                    min_word = min(enumerate(digit_buckets), key=lambda x: abs((float(sum(x[1][0])/len(x[1][0])))-value[1][1][0]))
                    if (abs((float(sum(min_word[1][0])/len(min_word[1][0]))) - value[1][1][0]) < self.mode_height/2) and \
                        (abs(min_word[1][1][-1][1][3][1] - value[1][0][1]) < self.mode_height * 10): 
                        digit_buckets[min_word[0]][1].append(value)
                        digit_buckets[min_word[0]][0].append(value[1][1][0])
                    else:
                        digit_buckets.append([[value[1][1][0]],[value]])
                except:
                    digit_buckets.append([[value[1][1][0]],[value]])
        # get word start lines
        word_columns = list(filter(lambda x:len(x[0]) > 4, word_buckets))
        word_points = []
        if len(word_columns) > 1:
            for c in word_columns:
                word_points.append([round(sum(c[0])/len(c[0])) , min(enumerate(c[1]),key=lambda x:x[1][1][0][1])[1][1][0][1], max(enumerate(c[1]),key=lambda x:x[1][1][3][1])[1][1][3][1]])
        word_columns = list(filter(lambda x:len(x[0]) > 6, word_buckets))
        
        # get digit end lines
        digit_columns = list(filter(lambda x:len(x[0]) > 4, digit_buckets))
        digit_points = []
        if len(digit_columns) > 1:
            for c in digit_columns:
                digit_points.append([round(sum(c[0])/len(c[0])) , min(enumerate(c[1]),key=lambda x:x[1][1][0][1])[1][1][0][1], max(enumerate(c[1]),key=lambda x:x[1][1][3][1])[1][1][3][1]])
        
        return word_points, digit_points

    def checkOverlappingLines(self, l1_start, l1_end, l2_start, l2_end):
        return (l2_start<=l1_start<=l2_end or l2_start<=l1_end<=l2_end or l1_start<=l2_start<=l1_end or l1_start<=l2_end<=l1_end)

    def getBoundaries(self,word_points,digit_points):
        """
        Function to get proper right & left check boundaries of a document, based on given words and digit line
        """
        boundaries = {'right':[],'left':[]}
        merge_lines = sorted(word_points+digit_points,key=lambda x: x[0])
        allow_right_line = True
        locked_index = None
        first_left_line = True
        for line in merge_lines:
            # if line of type right, i.e. word line
            if line in word_points:
                if allow_right_line or not self.checkOverlappingLines(boundaries['right'][-1][1],boundaries['right'][-1][2],line[1],line[2]) or ((line[0]-boundaries['right'][-1][0]) > (20 * self.mode_height) or (line[0]-boundaries['right'][-1][0]) <= 5):
                    boundaries['right'].append(line)
                    allow_right_line = False
                    # check y-overlap of left boundary before locking it
                    if len(boundaries['left']) > 0 and self.checkOverlappingLines(boundaries['left'][-1][1],boundaries['left'][-1][2],line[1],line[2]):
                        locked_index = len(boundaries['left']) - 1
            # if line of type left, i.e. digit line
            else:
                # add first left line without any checks
                if first_left_line:
                    boundaries['left'].append(line)
                    first_left_line = False
                elif locked_index == len(boundaries['left']) - 1:
                    boundaries['left'].append(line)
                # add line at last index, if it is not locked
                else:
                    boundaries['left'][-1] = line
                allow_right_line = True
        return boundaries
                            
    def calculateModeRotate(self, rotate_angle_list, height_list, slant_list):
        """
        Function to calculate rotation angle of document, and take action if it is flipped

        :param rotate_angle_list: List containing rotate angle of all words in a document
        :return: Height list updated, slant list updated, state points updated.
        """
        mode_rotate = max(set(rotate_angle_list), key=rotate_angle_list.count)
        # if mode_rotate != 0:
            # Image is rotated by either 90, 180 or 270 degrees. Rotate the document virtually to make it straight
            # height_list, slant_list = self.changeCoordinates(mode_rotate)
        
        return height_list, slant_list
    
    def changeCoordinates(self, mode_rotate):
        """
        Function to virtually rotate an image by transposing entire x,y co-ordinate graph to make it work with our system.

        :param mode_rotate: Degrees by which it needs to be rotated, [90, 180 or 270]
        :return: Height list updated, slant list updated, state points updated.
        """

        width, height = self.width, self.height

        # Save original result in temp variable
        text_result = copy.deepcopy(self.result)

        new_result = []
        new_points = []

        slanted_list = []
        height_list = []

        # If image is rotated by 90 degrees, rotate each vertex where [x = old y , y = width - x]
        if mode_rotate == 90:
            for v in text_result:
                for i in range(4):
                    v[1][i] = (v[1][i][1], width - v[1][i][0])
                # if self.compressed_text or bool(re.search(r'\d{2,}', v[0])):
                height_list.append(abs(v[1][0][1] - v[1][3][1]))
                if len(v[0]) > 2:
                    slanted_list.append(abs(v[1][0][1] - v[1][1][1]))
                new_result.append(v)
            for p in self.find_ocr_words:
                for i in range(4):
                    p[1][i] = (p[1][i][1], width - p[1][i][0])
                new_points.append(p)
        # Elif image is rotated by 270 degrees, rotate each vertex where [x = height - y , y = old x]
        elif mode_rotate == 270:
            for v in text_result:
                for i in range(4):
                    v[1][i] = (height - v[1][i][1], v[1][i][0])
                # if self.compressed_text or !bool(re.search(r'\d{2,}', v[0])):
                height_list.append(abs(v[1][0][1] - v[1][3][1]))
                if len(v[0]) > 2:
                    slanted_list.append(abs(v[1][0][1] - v[1][1][1]))
                new_result.append(v)
            for p in self.find_ocr_words:
                for i in range(4):
                    p[1][i] = (height - p[1][i][1], p[1][i][0])
                new_points.append(p)
        # Elif image is rotated by 180 degrees, rotate each vertex where [x = width - x , y = height - y]
        elif mode_rotate == 180:
            for v in text_result:
                for i in range(4):
                    v[1][i] = (width - v[1][i][0], height - v[1][i][1])
                # if self.compressed_text or !bool(re.search(r'\d{2,}', v[0])):
                height_list.append(abs(v[1][0][1] - v[1][3][1]))
                if len(v[0]) > 2:
                    slanted_list.append(abs(v[1][0][1] - v[1][1][1]))
                new_result.append(v)
            for p in self.find_ocr_words:
                for i in range(4):
                    p[1][i] = (width - p[1][i][0], height - p[1][i][1])
                new_points.append(p)

        # Update result with new transposed values result
        self.result = new_result
        self.find_ocr_words = new_points
        return height_list, slanted_list

    def calculateModeSlant(self, slant_list):
        """
        Function to calculate mode of slant of document

        :param slant_list: List containing slant of all words in document
        :return: Mode slant of entire document
        """
        # Calculate mode slant using slant list values
        sl_count = len(slant_list)
        sl_checked = 0
        slant_sum = 0
        # We consider slant value only if there are considerable amount of words having
        while sl_checked < sl_count:
            ms = max(set(slant_list), key=slant_list.count)
            ms_count = slant_list.count(ms)
            if ms_count < 4:
                break
            slant_sum += ((ms+1) * ms_count)
            sl_checked += ms_count
            slant_list = list(filter(lambda a: a != ms, slant_list))
        mode_slant = (slant_sum / sl_checked) - 1
        return mode_slant

    def calculateModeHeight(self, height_list):
        # Calculate mode height using list of all words heights
        hl_count = len(height_list)
        hl_checked = 0
        height_sum = 0
        # We consider only half list, as it is enough to get better understanding. We start
        # by taking initial list and reduce the list until we get to half count of original list
        while hl_checked < hl_count / 2:
            # get mode of height from given remaining height list
            mh = max(set(height_list), key=height_list.count)
            mh_count = height_list.count(mh)
            if mh_count < 5:
                break
            # height sum will be height of words multiplied by no. of words having that height
            height_sum += (mh * height_list.count(mh))
            hl_checked += height_list.count(mh)
            # Reduce list by removing used heights
            height_list = list(filter(lambda a: a != mh, height_list))
        # Final mode height is height sum (calculated above) divided by checked elements
        self.mode_height = height_sum / hl_checked
        return self.mode_height
    
    def rectifyCharacterSet(self,description):
        """
        Function to rectify character set of given text
        """
        # Change cyrillic characters to latin. As block and column headers are based on latin.
        cyrList = 'АВЕМСТахУХуОНРеԚԛԜԝҮү•ΕΙр'
        latList = 'ABEMCTaxyXyOHPeQqWwYy.EIp'
        table = str.maketrans(cyrList, latList)
        return description.translate(table)

    def arrangeTextWithCoordinates(self,description,all_words):

        self.description = description

        # Create a words dict and float values dict exclusive of each other, out of given words
        desc = self.description
        self.words_dict = desc.split('\n')
        self.digits_dict = list(filter(lambda w: bool(re.search(r'[+-]?([0-9]*[,\s]*[0-9]*[.][0-9]+)', w)), self.words_dict))
        # Look for words that has text and float val, or two different float val separated by space
        digits_w_spaces = list(filter(lambda w: bool(re.search(r'[ ]', w)), self.digits_dict))
        # Fetch float value from such words, remove the entire word and just add float to float values dict
        for d in digits_w_spaces:
            new_d = re.findall(r'(([(|\-|+|*|$]+)?\d+(\s?\,?\.?\s?\d{3})*\,?\.?(\d+)?[*)]?)', d)
            self.digits_dict.remove(d)
            for val in new_d:
                if re.search(r'\d+\.\d+', val[0]):
                    self.digits_dict.append(val[0])
        # For specific case, where 1.5 is not float value instead it is a word. (e.g. Overtime 1.5)
        try:
            self.words_dict = list(set(self.words_dict) - set(self.digits_dict))
            self.digits_dict = list(filter(lambda a: a not in ['1.5','2.0'], self.digits_dict))
            # self.digits_dict = list(filter(lambda a: a != '1.5', self.digits_dict))
        except:
            pass

        # Height list having heights of all digit values
        height_list = []
        # Slant list having slant value of each word
        slanted_list = []
        # Rotate list having orientation of each word
        rotated_list = []

        text_val = []
        keys = []
        values = []

        # Create a list of all words and its respective co-ordinates
        for word in all_words:
            text_val.append(word['description'])
            vertices = [vertex for vertex in word['vertices']]
            # create key-value pair of word and its vertices
            keys.append(word['description'])
            values.append(vertices)

            # Update height, slant and rotate list
            # if self.compressed_text or !bool(re.search(r'\d{2,}', word['description'])):
            height_list.append(abs(vertices[0][1] - vertices[3][1]))
            if len(word['description']) > 2:
                slanted_list.append(abs(vertices[0][1] - vertices[1][1]))
            if vertices[0][1] > vertices[2][1] and vertices[1][1] > vertices[3][1]:
                rotated_list.append(180)
            elif vertices[0][1] > vertices[2][1]:
                rotated_list.append(270)
            elif vertices[1][1] > vertices[3][1]:
                rotated_list.append(90)
            else:
                rotated_list.append(0)
        # height_list =[max(height_list)-x if max(height_list) != x else x  for x in height_list ]
        # Translate all cyrillic characters to latin in key list (list of words)
        keys = [self.rectifyCharacterSet(s) for s in keys]
        # Zip keys and values together to create a list of word and its vertices
        self.result = zip(keys, values)
        # Create a space separated word data that is useful for regex.
        data = " ".join(map(str, text_val))
        data_test = description.replace('\n',' ')
        return data_test,data, height_list, slanted_list, rotated_list, self.result, self.words_dict, self.digits_dict

    def getLines(self,description,all_words):
        OCRSpaces, hl, sl, rl, _, _, _ = self.arrangeTextWithCoordinates(description,all_words)
        hl, sl = self.calculateModeRotate(rl, hl, sl)
        mode_slant = self.calculateModeSlant(sl)
        mode_height = self.calculateModeHeight(hl)
        lines, SpecificWords = self.rectifyData(mode_slant)
        WordsDict = self.words_dict
        DigitsDict = self.digits_dict
        for key in self.output_flags:
            if self.output_flags[key]:
                self.output_flags[key] = eval(key)
        return lines, self.output_flags
        

if __name__ == '__main__':
    path = 'All Paystubs/ADP/Type1/ADP ABCO Refrgeration Supply Corp 011418.jpg' #sys.argv[1]
    print(path)


