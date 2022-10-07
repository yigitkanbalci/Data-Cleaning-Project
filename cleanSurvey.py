import os
import csv
import copy
import string
import pandas as pd
import numpy as np
import glob
import sys
import math
import nltk
from nltk.corpus import stopwords
import re
from pathlib import Path


class Prompt:
    def __init__(self, text):
        self.text = text
        self.title = ''


## TODO:
## Students and answers not matching : assigning -999 for all the empty response cells and all 0s where there is not a name in a cell.
## Raw And Reversed flip the answers for the reversed version of the raw prompts.
## develop algorithm to score prompts against the survey dictionary values.

def Name_Encryption(fname, lname, course_code):
    if type(fname) == float:
        return 'N/A'
    fname = fname.lower()
    lname = lname.lower()

    alphabet = string.ascii_lowercase
    alphabet = list(alphabet)
    numbers = ["%.2d" % i for i in range(1,27)]
    index = pd.DataFrame(columns = alphabet)
    index.loc[0] = numbers

    try:
        encryp_Name = index.at[0, fname[0]]
    except IndexError:
        encryp_Name += '00'

    try:
        encryp_Name += index.at[0, fname[1]]
    except IndexError:
        encryp_Name += '00'

    try:
        encryp_Name += index.at[0, lname[0]]
    except IndexError:
        encryp_Name += '00'

    try:
        encryp_Name += ((index.at[0,lname[1]]) + '-' + course_code)
    except IndexError:
        encryp_Name += '00' + '-' + course_code

    return encryp_Name


def is_nan(x):
    return x != x


def get_nan_indexes(df):
    indexes = []
    for i in range(len(df)):
        val = df[i]
        if type(val) == float:
            indexes.append(i)
        i += 1
    return indexes


def create_unique_themes(prompts):
    unique_themes = []
    for prompt in prompts:
        if prompt.title.lower() not in unique_themes:
            unique_themes.append(prompt.title)
    return unique_themes


def clear_null_entry_names(df, indexes):
    first_names = []
    for i in range(len(df)):
        if i != indexes[0]:
            first_names.append(df[i])
        else:
            indexes.pop(0)
    first_names_ndarray = np.array(first_names)
    return first_names_ndarray


def group_titles(unique_themes, prompts):
    new_prompts = []
    for theme in unique_themes:
        for prompt in prompts:
            if prompt.title.lower() == theme.lower():
                new_prompts.append(prompt)
    return new_prompts


def get_prompt_title(prompts):

    for prompt in prompts:
        highest_score = 0
        title = ''
        prompt_text = prompt.text
        for key, values in surdict.items():
            for val in values:
                words1 = prompt_text.lower().split(" ")
            words2 = val.lower().split(" ")
            score = len(list(set(words1) & set(words2)))
            if score > highest_score:
                highest_score = score
                title = title.replace(title, key)
        prompt.title = prompt.title + title
    return prompts


def Data_Cleaning(df, first_names, last_names, course_code, prompts, flag):
    encrypted_Names = [' ', 'Student ID']

    dataframes = []
    run_flag = 1
    null_entries = []
    prompts = get_prompt_title(prompts)
    themes = create_unique_themes(prompts)
    prompts = group_titles(themes, prompts)
    for prompt in prompts:
        df_object = []
        df_object.append(prompt.title)
        df_object.append(prompt.text)
        answer_list = df[prompt.text].values.tolist()
        null_firsts = get_nan_indexes(first_names)

        flag = 1
        for i in range(len(answer_list)):
            if is_nan(answer_list[i]):
                flag = 0
                if run_flag == 1:
                    null_entries.append(i)
            else:
                if type(answer_list[i]) != str:
                    if is_nan(answer_list[i][0]):
                        flag = 0
                        if run_flag == 1:
                            null_entries.append(i)
                    else:
                        val = int(answer_list[i][0])
                else:
                    val = int(answer_list[i])

            if not flag:
                pass
            elif i == null_firsts[0]:
                null_firsts.pop(0)
            else:
                df_object.append(val)
            flag = 1
        run_flag = 0
        prompt_df = pd.DataFrame(df_object)
        dataframes.append(prompt_df)
    first_names = clear_null_entry_names(first_names, null_entries)
    first_names = first_names[~pd.isnull(first_names)]
    last_names = last_names[~pd.isnull(last_names)]

    for i in range(0, len(first_names)):
        encrypted_Names.append(Name_Encryption(first_names[i], last_names[i], course_code))

    names_df = pd.DataFrame(encrypted_Names)
    arrays = [names_df] + dataframes

    merged_df = pd.concat(arrays, axis=1)
    merged_df.to_excel('output.xlsx', index=False, header=False)
    return


def main():
    if len(sys.argv) != 2:
        print('Not enough command line arguments to run. Please pass a mode of operation')
        print('\nUsage: python cleanSurvey.py -csv/-xlsx')
        return

    path_name = os.getcwd()
    path_name += '\\'
    filename = input("Type filename ending with its extension (.csv, .xlsx): ")
    path_name += filename

    # parse the method of running the program (either for csv or for excel)
    if sys.argv[1] == '-csv':
        read_file = pd.read_csv(path_name, header=0)
    elif sys.argv[1] == '-xlsx':
        read_file = pd.read_excel(path_name, header=0)
    else:
        print('Please enter a mode of operation (-csv or -xlsx)')
        return

    fields = ['science', 'technology', 'engineering', 'mathematics']
    course = input("Enter course field (Science / Technology / Engineering / Mathematics): ")
    if course.lower() not in fields:
        print('Please enter one of the related STEM fields corresponding to the course (Science, Technology, Engineering or Mathematics')
        return
    course_code = course[0].upper()
    school_name = input("Enter name of University or Institution (i.e. Purdue University): ")
    year = input("Enter year of the course (i.e. 2022): ")
    tokens = nltk.word_tokenize(school_name)
    school_name_words = [w for w in tokens if not w.lower() in stopwords.words('english')]
    first_letters = [x[0] for x in school_name_words]
    abbreviation = "".join(first_letters)
    student_code = year[-2:] + abbreviation + course_code
    new_header = read_file.iloc[0]  # grab the first row for the header
    df = read_file[2:]  # take the data less the header row
    df.columns = new_header  # set the header row as the df header
    first_names = df["First name"].to_numpy()
    last_names = df["Last name"].to_numpy()
    column_list = df.columns.values.tolist()
    prompts_idx_start = column_list.index('Please write the name of your course instructor')
    prompts_idx_end = column_list.index('What is your current GPA?')
    prompts = column_list[prompts_idx_start + 1: prompts_idx_end]
    prompts_data = []
    for text in prompts:
        prompt = Prompt(text)
        prompts_data.append(prompt)

    Data_Cleaning(df, first_names, last_names, student_code, prompts_data, 1)
    return



surdict = {'Self Efficacy': ['I believe I will receive an excellent grade in this course.',
                             'I am confident I can understand the most complex material presented by the instructor in this course.',
                             'I am confident I can do an excellent job on the assignments and tests in this course.',
                             'I am certain I can master the skills being taught in this course.',
                             'Considering the difficulty of this course, the teacher, and my skills, I think I will do well in this class.'],

           'Task Value': ['I think I will be able to use what I learn in this course in other courses.',
                          'It is important for me to learn the course material in this class.',
                          'I am very interested in the content area of this course.',
                          'I think the course material in this class is useful for me to learn.',
                          'I like the subject matter of this course.',
                          'Understanding the subject matter of this course is very important to me.'],

           'Meta cognitive self-regulation': ['During my courses, I often miss important points because I am thinking of other things.',
                                              'When I become confused about some concepts that I am studying, I go back and try to figure it out.',
                                              'If course materials are difficult to understand, I change the way I study the material.',
                                              'I askmyself questions to make sure I understand the material I have been studying.',
                                              'When studying for courses, I try to determine which concepts I do not understand well.',
                                              'When I study for courses, I set goals for myself in order to direct my activities in each study period.',
                                              'If I get confused taking notes in class, I make sure I sort it out afterwards.'],

           'Time Study Environment': ['I usually study in a place where I can concentrate on my course work.',
                                      'I generally make good use of my study time for my courses.',
                                      'I find it hard to stick to a study schedule.',
                                      'I make sure that I keep up with the weekly readings and assignments in my courses.',
                                      'I attend my classes regularly.',
                                      'I often find that I do not spend very much time on my courses because of other activities.',
                                      'In my previous courses, I rarely find time to review my notes or readings before an exam.',
                                        ],

           'Mastery Approach': ['I am striving to understand the content as thoroughly as possible.',
                                'My goal is to learn as much as possible.',
                                'My aim is to completely master the material presented in this class.'],

           'Performance Approach': ['My goal is to perform better than the other students do.',
                                    'My aim is to perform well relative to other students.',
                                    'I am striving to do well compared to other students.'],

           'Performance Avoidance': ['My aim is to avoid doing worse than other students do.',
                                     'I am striving to avoid performing worse than others do.',
                                     'My goal is to avoid performing poorly compared to others.'],

           'Behavioral': ['I stay focused in science classes.',
                          'I put effort into learning science.',
                          'I keep trying even if something is hard in science.',
                          'I complete my science homework assignments on time.',
                          'I do other things when I am supposed to be paying attention in science classes.',
                          'If I do not understand a task in science, I give up right away.',
                          ],
           'Emotional': ['I look forward to science class.',
                         'I enjoy learning new things about science.',
                         'I feel good when I am in science classes.',
                         'I think that science classes are boring.',
                         'I do not want to be in science classes.',
                         'I often feel down when I am in science classes.',
                            ],

           'Social': ["I think about others' ideas and add my opinion in science classes.",
                      "I try to understand other people's ideas in science classes.",
                      'I work with classmates to come up with ways to solve problems in science classes.',
                      "I do not care about other people's ideas in science assignments.",
                      'When working with others in science, I do not share my ideas.',
                      'I do not like working with my classmates in science classes.',
                      ],

           'Cognitive': ["I go through the work that I do for science classes and make sure that it's right.",
                         'I try to connect what I am learning in science classes to things I have learned before.',
                         'I try to understand my mistakes when I get something wrong in science classes.',
                         'I would rather be told the answer in science than have to figure it out myself.',
                         'When work is hard in science, I only study the easy parts.',
                         "I don't think that hard when I am doing work for science classes.",
                         ]}


if __name__ == "__main__":
    main()
