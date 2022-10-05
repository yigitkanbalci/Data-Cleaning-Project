import os
import csv
import copy
import string
import pandas as pd
import numpy as np

def Name_Encryption(fname, lname, course):
    fname = fname.lower()
    lname = lname.lower()

    alphabet = string.ascii_lowercase
    alphabet = list(alphabet)
    numbers = ["%.2d" % i for i in range(1,27)]
    index = pd.DataFrame(columns = alphabet)
    index.loc[0] = numbers

    encryp_Name = index.at[0,fname[0]]
    encryp_Name += index.at[0,fname[1]]
    encryp_Name += index.at[0,lname[0]]
    encryp_Name += (index.at[0,lname[1]] + '-' + course)

    return encryp_Name
# END FUNCTION

def Data_Cleaning(df, course, reverse_ques):
    encrypted_Names = []
    unique_Themes = []
    output_cols = []
    reverse_col = []
    print(df)
    return
    # For-loop to encrypt each student name
    t = 1
    for x in range(2, len(df)):
        print(t)
        encrypted_Names.append(Name_Encryption(df[x][0], df[x][1], course))
        t += 1
    #end for-loop
    encrypted_Names = np.transpose(encrypted_Names)
    df_output = []

    # For-loop to create a list of unique themes
    for x in range(2, len(df[0])):
        if df[0][x] not in unique_Themes:
            unique_Themes.append(df[0][x])
    # end for-loop

    for x in unique_Themes: # x is a string that represents a theme
        for y in range(2, len(df[0])): # y is the column number of current theme
            if x == df[0][y]:
                output_cols.append(x)
                col = [df[1][y]]
                for z in range(2,len(df)): # z is the row #
                    if np.isnan(df[z][y]):
                        df[z][y] = -999
                    col.append(df[z][y])
                if len(df_output) != 0:
                    df_output = np.column_stack((df_output, col))
                    index = len(df_output[0]) - 1
                    if df_output[0][index] in reverse_ques:
                        reverse_col.append(df_output[0][index] + " (Reversed)")
                        for q in range(1, len(df_output)):
                            if df_output[q][index] == "6":
                                reverse_col.append("1")
                            elif df_output[q][index] == "5":
                                reverse_col.append("2")
                            elif df_output[q][index] == "4":
                                reverse_col.append("3")
                            elif df_output[q][index] == "3":
                                reverse_col.append("4")
                            elif df_output[q][index] == "2":
                                reverse_col.append("5")
                            elif df_output[q][index] == "1":
                                reverse_col.append("6")
                            else:
                                reverse_col.append("-999")
                        df_output = np.column_stack((df_output, reverse_col))
                        output_cols.append(x)
                        reverse_col = []
                else:
                    df_output = copy.deepcopy(col)
                    if df_output[0] in reverse_ques:
                        reverse_col.append(df_output[0] + " (Reversed)")
                        for q in range(1, len(df_output)):
                            if str(df_output[q]) == "6":
                                reverse_col.append("1")
                            elif str(df_output[q]) == "5":
                                reverse_col.append("2")
                            elif str(df_output[q]) == "4":
                                reverse_col.append("3")
                            elif str(df_output[q]) == "3":
                                reverse_col.append("4")
                            elif str(df_output[q]) == "2":
                                reverse_col.append("5")
                            elif str(df_output[q]) == "1":
                                reverse_col.append("6")
                            else:
                                reverse_col.append("-999")
                        df_output = np.column_stack((df_output, reverse_col))
                        output_cols.append(x)
                        reverse_col = []

    output_ques = df_output[0]
    output_vals = np.delete(df_output,0,0)
    output_vals = output_vals.astype(np.float64)

    pandas_output = pd.DataFrame(output_vals, columns = [output_cols, output_ques], index = encrypted_Names)
    nameKey_output = np.column_stack((encrypted_Names, df[2:,0], df[2:,1]))
    nameKey_pandas = pd.DataFrame(nameKey_output, columns = ['ID', 'First Name', 'Last Name'])

    nameKey_pandas.to_excel("Name_Key.xlsx", index = False)
    pandas_output.to_excel("Output.xlsx")
# END function

path_name = os.getcwd()
print(path_name)
path_name += "/"
print(path_name)
excel_name = input("Type Excel file name ending with '.xlsx': ")
path_name += excel_name
course = input("Input course info: ")

# Read Excel file
xls = pd.ExcelFile(path_name)
df = pd.read_excel(xls, header=None)
reverse_ques = pd.read_excel(xls, header=None)
df = df.to_numpy()
reverse_ques = reverse_ques.to_numpy()

Data_Cleaning(df, course, reverse_ques)
