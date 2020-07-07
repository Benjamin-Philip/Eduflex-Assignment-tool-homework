from requests import Session
from bs4 import BeautifulSoup,Tag,SoupStrainer
import pandas as pd
import numpy as np
from pandas import ExcelWriter


def scrape():    
    #Calling and Autheneticating Eduflex
    with Session() as s:
        site = s.get("https://eduflex.co.in/portal/?_proj=THEDEENS")
        print("Loading Site", end = (40 - len("Loading Site")) * ".")
        beautifulsoup_content = BeautifulSoup(site.content, "html.parser")
        print(" Done")
        print("Authenticating", end = (40 - len("Authenticating")) * ".")
        token = beautifulsoup_content.find("input", {"name":"_FOK"})["value"]
        login_data = {"username":"Benjamin.Jacob","password":"Th3T3mp35t!", "_FOK":token}
        s.post("https://eduflex.co.in/portal/?_proj=THEDEENS",login_data)
        assignments_tab = s.get("https://eduflex.co.in/portal/assignments.jsp")
        print(" Done")
        
    

    #Assigning assignments and finding no. of assignments
    print("Navigating to Assignments", end = (40 - len("Navigating to Assignments")) * ".") 
    soup = BeautifulSoup(assignments_tab.content,"html.parser")
    assignments_container = soup.find('div', id = "collapseExample", class_ = "panel-body")
    number= len(assignments_container.findAll('div', class_ = "panel panel-default"))
    print(" Done")

    #Creating List
    print("Creating List [Homeworks]", end = (40 - len("Creating List [Homeworks]")) * ".")
    homeworks = []
    print(" Done")
    
    print("Extracting Data:")
    #for loop to extract data
    for i in range(0,number,1):

        #div call automation
        hw_string = "hw" + str(i)
        collapse_string = "collapse" + str(i + 1)

        #adding hw to list
        print(f"Adding {hw_string} to list", end = (40 - len("Adding " + hw_string + " to list")) * ".")
        homeworks.append(hw_string)
        print(" Done")

        print(f"Extracting Attributes of {hw_string}:") 
        #title
        print("Extracting Title", end = (40 - len("Extracting Title")) * ".")
        current_assignment_title = assignments_container.find('div',id = hw_string)
        title_container = current_assignment_title.find('h4', class_ = "panel-title")
        title = str(title_container.findAll('a')[1].get_text())
        print(" Done")

        #body
        current_assignment_body = assignments_container.find('div', id = collapse_string)

        #topic
        print("Extarcting Topic", end = (40 - len("Extracting Topic")) * ".")
        topic_container = current_assignment_body.find('div', class_ = "text-danger")
        topic = str(topic_container.get_text())
        print(" Done")

        #description
        print("Extarcting Description", end = (40 - len("Extracting Description")) * ".")
        details_container = current_assignment_body.find('div', class_ = "topic_details")
        description = str(details_container.get_text())
        print(" Done")

        #attachments
        print("Checking for Attachments", end = (40 - len("Checking for Attachments")) * ".")
        attachment_container = current_assignment_body.find('div', class_ = "text-success")
        attachment_container = attachment_container.find('u')
        
        if attachment_container.find('a', href = True):
            print(" Done")
            print("Inputing Attachment list", end = (40 - len("Inputing Attachment list")) * ".")
            attachments = str(attachment_container.findAll('a', href = True))
            print(" Done")
        
        else:
            attachments = False
            print(" Done")
        
        
        print(f"Extracting Attributes of {hw_string}: Done")
        print(f"Adding Attributes of {hw_string}:", end = (40 - len(f"Adding Attributes of {hw_string}:")) * ".")
        print(" Done")
        homeworks[i] = {'title':title, 'Topic':topic, 'Description':description, 'Attachments':attachments,}

    print(f"Extracting Data: Done")
    return homeworks
    

def sort(extracted_homeworks):
    #Personally I would call this func JANFU clean up but
    #It is sort because that is more sensible

    print("Sorting Data:")
    for i in range(len(extracted_homeworks)):
        current_assignment = extracted_homeworks[i]
        
        #Title
        print("Sorting Title", end = (40 - len("Sorting Title")) * ".")
        title = current_assignment["title"]
        
        #Assigning values
        set_string = title.split(" - ")[0]
        subject_string = title.split(" - ")[1]
        due_string = title.split(" - ")[2]

        #Set Date
        set_date = set_string.split(" : ")[-1]
        
        #Subject
        subject_string = subject_string.split("\n")[1]
        subject = subject_string.split(" ")[-1]

        #Due Date 
        due_date  = due_string.split(" : ")[-1]


        #Removing title
        del current_assignment["title"]

        #Adding new attributes
        current_assignment["Set-Date"] =  pd.to_datetime(set_date)
        current_assignment["Subject"] = subject
        current_assignment["Due-Date"] =  pd.to_datetime(due_date)
        print(" Done")

        #Topic
        print("Sorting Topic", end = (40 - len("Sorting Topic")) * ".")
        current_assignment["Topic"] = current_assignment["Topic"].split(" : ")[-1]
        print(" Done")

    print("Sorting Data: Done")

    return extracted_homeworks


def make_sheets():
    with ExcelWriter(r'D:/Benjamin/Studies/Homework-and-Assignments.xlsx',date_format = "DD-MM-YYYY") as writer:

        print('Writing Homework-and-Assignments.xlsx', end = (40 - len('Writing Homework-and-Assignments.xlsx')) * ".")
        active_sheet = pd.DataFrame()
        expired_sheet = pd.DataFrame()
        active_sheet.to_excel(writer, sheet_name = "ActiveSheet")
        expired_sheet.to_excel(writer, sheet_name = "ExpiredSheet")
        writer.save()
        print(" Done")

def add_assignments(homeworks):
    #Adds assignments to Active-Homework

    #Checking if File exixts.

    try:
        pd.read_excel(r"D:/Benjamin/Studies/Homework-and-Assignments.xlsx")
    except FileNotFoundError:
        make_sheets()
    
    #Opening assignment sheet             

    print(f"Opening ActiveSheet", end = (40 - len(f"Opening ActiveSheet")) * ".")
    active_sheet = pd.read_excel(r"D:/Benjamin/Studies/Homework-and-Assignments.xlsx",sheet_name = "ActiveSheet")
 
    print(" Done")

    #Merging Data
    print("Merging Dataframes", end = (40 - len("Merging Dataframes")) * ".")
    new_homework = pd.DataFrame(homeworks)
    active_sheet = active_sheet.append(new_homework, ignore_index = True)

    #Adding Columns
    active_sheet["Status"] = "Pending"
    active_sheet["Date-of-Completion"] = np.nan

    #Re-ordeing data
    active_sheet = active_sheet[["Subject","Topic","Description","Attachments","Set-Date","Due-Date","Status","Date-of-Completion"]]


    #Checking for Duplicates
    if active_sheet.duplicated(subset = None).any():
        active_sheet.drop_duplicates(subset = None, keep = "first", inplace = True)
    print(" Done")

    #Printing Active Data
    for key,value in active_sheet.iterrows():
        print(key,value)
        print()

    return active_sheet
    

def check_for_expired_assignments(active_sheet):

    print("Checking for expired assignments", end = (40 - len("Checking for expired assignments")) * ".")
    today = pd.to_datetime("today")
    expired_assignments = list([])
    expiredsheet = pd.read_excel(r"D:/Benjamin/Studies/Homework-and-Assignments.xlsx", sheet_name = "ExpiredSheet")

    for i in range(len(active_sheet)):
        current_row_date = active_sheet.iloc[i].at["Due-Date"]
        active_sheet.copy

        if current_row_date < today:
            expired_assignments.append(i)

    temp_df0 = pd.DataFrame(active_sheet.drop(expired_assignments))
    non_expired_assignments = list(active_sheet.index.values)

    for ele in sorted(expired_assignments, reverse = True):
        del non_expired_assignments[ele]

    temp_df0["ActiveSheet-Refrence"] = non_expired_assignments

    print(" Done")
    return temp_df0, expired_assignments, expiredsheet

def change_status(active_sheet):
    temp_df0, expired_assignments, expiredsheet = check_for_expired_assignments(active_sheet)
    choice0 = "nan"
    no0 = False
    updated = False
    
    while no0 != True:
        choice0 = input("Would you like to change status?(y/n)")
        
        if choice0 == "y":

            choice1 = input("ActiveSheet or ExpiredSheet?(0/1)")

            if choice1 == "0":
                print(temp_df0)
                ans0 = "nan"
                yes0 = False

                while yes0 != True:
                    nos = input("Please enter the index no. of the assignments to update:")
                    updated = True
                    selection = nos.split(",")

                    for i in range(len(selection)):
                        current_iteration = selection[i]
                        selection[i] = int(current_iteration)

                    print(selection)

                    ans0 = input("Done?(y/n)")
                    if ans0 == "y":
                        yes0 = True
                    elif ans0 == "n":
                        pass
                    else:
                        print("Unrecognised choice")
                    
                    for i in range(len(selection)):
                        expired_assignments.append(selection[i])
                
                print(f"Making Changes", end = (40 - len("Making Changes")) * ".")
                
                
                for i in range(len(selection)):
                    counter = temp_df0.at[selection[i], "ActiveSheet-Refrence"]
                    active_sheet.loc[counter, "Date-of-Completion"] = pd.to_datetime("today")
                    active_sheet.loc[counter, "Status"] = "Completed"
                    expiredsheet = expiredsheet.append(active_sheet.iloc[counter], ignore_index = True)
                
                for i in range(len(expired_assignments)):
                    current_assignment_no = active_sheet.iloc[expired_assignments]
                    expiredsheet = expiredsheet.append(current_assignment_no, ignore_index = True)
                
                active_sheet.drop(expired_assignments, axis = 0, inplace = True)

                print(" Done")

            elif choice1 == "1":
                yes1 = False
                if expiredsheet.duplicated(subset = ["Description"]).any():
                    expiredsheet.drop_duplicates(subset = ["Description"], keep = "first", inplace = True)

                #Calling pending homeworks
                incomplete_df = expiredsheet.query('Status == "Pending"')
                expired_sheet_refrence_array = expiredsheet.query('Status == "Pending"').index.tolist()
                incomplete_df = incomplete_df.assign(Refrence= expired_sheet_refrence_array)

                while yes1 == False:

                    if len(incomplete_df) == 0:
                        print("No expired pending homework. Please re-check the sheet-location of the Homework to update")
                    else:

                        if expiredsheet.duplicated(subset = ["Description"]).any():
                            expiredsheet.drop_duplicates(subset = ["Description"], keep = "first", inplace = True)

                        print(incomplete_df)
                        finished_homework = []
                        nos = input("Please enter index no.s of the assignments to update:")
                        selection = nos.split(",")
                
                        for i in range(len(selection)):
                            selection[i] = int(selection[i])

                        for i in range(len(selection)):
                            finished_homework.append(selection[i])
                        print(finished_homework)
                        ans1 = input("Done?(y/n)")

                    if ans1 == "y":
                        yes1 = True

                    elif ans1 == "n":
                        pass
                    else:
                        print("Unrecognised choice")

                print("Making Changes", end = (40 - len("Making Changes")) * ".")
                for i in range(len(finished_homework)):
                    temp = incomplete_df.iloc[i]
                    current_assignment_no = temp.at["Refrence"]
                    expiredsheet.loc[current_assignment_no, "Status"] = "Completed"
                    expiredsheet.loc[current_assignment_no, "Date_of_Completion"] = pd.to_datetime("today")
                
                print( "Done")

            else:
                print("Unrecognised Command")
                
        elif choice0 == "n":
            no0 = True

            if updated == False:
                for i in range(len(expired_assignments)):
                    current_assignment_no = active_sheet.iloc[expired_assignments[i]]
                    expiredsheet = expiredsheet.append(current_assignment_no, ignore_index = True)
        
                for i in range(len(expired_assignments)):
                    active_sheet = active_sheet.drop([expired_assignments[i]], axis = 0)

            if expiredsheet.duplicated(subset = ["Description"]).any():
                expiredsheet.drop_duplicates(subset = ["Description"], keep = "first", inplace = True)
        
        else :
            print("Unrecognized choice")
    
    print("Updating Sheets", end = (40 - len("Updating Sheets")) * ".")
    writer = ExcelWriter(r"D:/Benjamin/Studies/Homework-and-Assignments.xlsx", date_format = "DD-MM-YYYY")
    active_sheet.set_axis([*range(len(active_sheet))], axis = 0, inplace = True)
    expiredsheet.set_axis([*range(len(expiredsheet))], axis = 0, inplace = True)
    active_sheet.to_excel(writer, sheet_name = "ActiveSheet")
    
    try:
        expiredsheet = expiredsheet[["Topic", "Subject", "Description","Attachments","Set-Date","Due-Date","Status","Date-of-Completion"]]
        expiredsheet.to_excel(writer, sheet_name = "ExpiredSheet")
    
    except NameError:
        pass
    
    writer.save()
    print(" Done")


if __name__ == "__main__":
    extracted_homeworks = scrape()
    extracted_homeworks = sort(extracted_homeworks)
    active_sheet = add_assignments(extracted_homeworks)
    change_status(active_sheet)