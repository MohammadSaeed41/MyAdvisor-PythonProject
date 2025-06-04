import csv
import os
import termcolor
import json

# this function to calculate the cridits of the course
def course_credits(course_code):
    if course_code == "UE":
        return 3
    return int(course_code[5])

# this function to choose the courses for the next semester
def choose_courses(study_plan, max_credits,CourseBrowser):
    not_passed_courses = []

    # Loop over all courses in the study plan and check if they're not passed
    for year_data in study_plan.values():
        for semester_data in year_data.values():
            for course in semester_data:
                if not course['is_passed']:
                    # If the course is not passed, add it to the list of not passed courses
                    not_passed_courses.append(course)

    # Return the first not passed courses that satisfies the max credits requirement
    selected_courses = []
    total_credits = 0
    for course in not_passed_courses:
        credits = int(course_credits(course['course_code']))
        if total_credits + credits <= max_credits:
            # Check in the course exist in the course browser
            for key in CourseBrowser:
                if course['course_code'] in key:
                    selected_courses.append(course['course_code'])
                    total_credits += credits
                    break
        else:
            break
    return selected_courses

# print the study plan after choosing the courses
def print_study_plan(study_plan, selected_courses):
    print("Year\tSemester\tCourses")
    print("......\t........\t.......")
    for year, semesters in study_plan.items():
        for semester, courses in semesters.items():
            courses_str = ', '.join([
                termcolor.colored(c['course_code'], 'green') if c['is_passed'] and c['course_code'] not in selected_courses
                else termcolor.colored(c['course_code'], 'red') if c['course_code'] in selected_courses
                else c['course_code'] for c in courses
            ])
            print(f"{year}\t{semester}\t\t{courses_str}")

# This function to print the schedule of the courses
def print_schedule(selected_courses,CourseBrowser):
    with open(CourseBrowser) as f:
        course_schedule = json.load(f)

    #print("The preferences cannot be achieved, I suggest a course schedule that agrees with the student studying plan but not the preferences.")
    print('Course Schedule\n---------------')
    selected_sections = []
    for course in selected_courses:
        for section_type in ['Lecture', 'Lab']:
            for section_num in range(1, 4):
                section_key = f"{course}-{section_type}-{section_num}"
                if section_key in course_schedule and section_key not in selected_sections:
                    course_info = course_schedule[section_key]
                    instructor = course_info.get('Instructor')
                    days = [day for day in course_info.keys() if day != 'Instructor']
                    times = [course_info[day] for day in days]
                    days_str = '/'.join(days)
                    times_str = ', '.join(times)
                    print(f"{course} {section_type} {section_num} ({days_str}) from {times_str} with {instructor}")
                    selected_sections.append(section_key)
                    break
            else:
                continue
            break
        else:
            print(f"{course} is not offered this semester.")

# Print schedule in the SuggestedCourses.txt file
def print_schedule_on_file(selected_courses, CourseBrowser):
    with open(CourseBrowser) as f:
        course_schedule = json.load(f)

    with open('SuggestedCourses.txt', 'w') as f:
        f.write('Course Schedule\n---------------\n')
        selected_sections = []
        for course in selected_courses:
            for section_type in ['Lecture', 'Lab']:
                for section_num in range(1, 4):
                    section_key = f"{course}-{section_type}-{section_num}"
                    if section_key in course_schedule and section_key not in selected_sections:
                        course_info = course_schedule[section_key]
                        instructor = course_info.get('Instructor')
                        days = [day for day in course_info.keys() if day != 'Instructor']
                        times = [course_info[day] for day in days]
                        days_str = '/'.join(days)
                        times_str = ', '.join(times)
                        f.write(f"{course} {section_type} {section_num} ({days_str}) from {times_str} with {instructor}\n")
                        selected_sections.append(section_key)
                        break
                else:
                    continue
                break
            else:
                f.write(f"{course} is not offered this semester.\n")

study_plan = {}
# Read the data from the file and store it in dictionary
with open('CEStudyPlan.txt') as file:
    reader = csv.DictReader(file)
    for row in reader:
        year = row['Year']
        semester = row['Semster']
        course_code = row['CourseCode']
        prerequisites = row['Prerequisists']
        is_passed = False

        if year not in study_plan:
            study_plan[year] = {}
        if semester not in study_plan[year]:
            study_plan[year][semester] = []
        course = {'course_code': course_code, 'is_passed': is_passed, 'prerequisites': prerequisites}
        study_plan[year][semester].append(course)

# Print the study plan
print('Year\tSemester\tCourses')
print('......\t........\t.......')
for year, semesters in study_plan.items():
    for semester, courses in semesters.items():
        courses_str = ', '.join([c['course_code'] for c in courses])
        print(f'{year}\t{semester}\t\t{courses_str}')


while True:

    last_semester = 0  # To store the number of last semester which exist in the student record

    # Reach to the Student_Records.txt file and read the data from it
    while True:
        file_name = input("Please enter the name of the student records text file (FName.txt): ")
        file_path = input("Please enter the location of the student records text file: ")
        full_path = os.path.join(file_path, file_name)
        try:
            # Read the data from the Student_Records.txt file
            with open(full_path, "r") as file:
                reader = csv.reader(file)
                next(reader)  # skip the header row
                for row in reader:
                    year, semester, course_marks = row[0], row[1], row[2:]
                    last_semester = int(semester) # To store the last semester which exist the student record
                    for course_mark in course_marks:
                        course_code, mark = course_mark.split(":")
                        mark = int(mark)
                        if mark >= 60:
                            for year_data in study_plan.values():
                                for semester_data in year_data.values():
                                    for course in semester_data:
                                        if course['course_code'] == course_code:
                                            course['is_passed'] = True
            break
        except FileNotFoundError:
            print("Error: The file not found. Please enter a valid file name and location.")

    # Print the Study Plan on the screen and identify the passed courses in green color
    print("Year\tSemester\tCourses")
    print("......\t........\t.......")
    for year, semesters in study_plan.items():
        for semester, courses in semesters.items():
            courses_str = ', '.join(
                [termcolor.colored(c['course_code'], 'green') if c['is_passed'] else c['course_code'] for c in courses])
            print(f"{year}\t{semester}\t\t{courses_str}")

    # Ask the user to enter the minimum number of free days per week
    min_free_days = int(input("Enter the minimum number of free days per week: "))

    # Ask the user to enter the maximum number of credits per semester
    max_credits_first_semester = int(input("Enter the maximum number of credits for the first semester (12 to 18): "))
    while max_credits_first_semester < 12 or max_credits_first_semester > 18:
        print("Invalid input. Please enter a number between 12 and 18.")
        max_credits_first_semester = int(
            input("Enter the maximum number of credits for the first semester (12 to 18): "))

    max_credits_second_semester = int(input("Enter the maximum number of credits for the second semester (12 to 18): "))
    while max_credits_second_semester < 12 or max_credits_second_semester > 18:
        print("Invalid input. Please enter a number between 12 and 18.")
        max_credits_second_semester = int(
            input("Enter the maximum number of credits for the second semester (12 to 18): "))

    max_credits_summer_semester = int(input("Enter the maximum number of credits for the summer semester (0 to 9): "))
    while max_credits_summer_semester < 0 or max_credits_summer_semester > 9:
        print("Invalid input. Please enter a number between 0 and 9.")
        max_credits_summer_semester = int(
            input("Enter the maximum number of credits for the summer semester (0 to 9): "))

    # Ask the user about the number of semesters
    while True:
        num_semesters = int(
            input("Enter the number of semesters for which you want to plan the schedule (minimum 1 semester): "))
        if num_semesters > 0:
            break
        else:
            print("Invalid input. The number of semesters should be greater than 0. Please try again.")

    #############################################################
    # Read the data of course browser for the first semester
    with open('CourseBrowser_1.json', 'r') as f:
        CourseBrowser_1 = json.load(f)

    # Read the data of course browser for the second semester
    with open('CourseBrowser_2.json', 'r') as f:
        CourseBrowser_2 = json.load(f)

    # Read the data of course browser for the summer semester
    with open('CourseBrowser_3.json', 'r') as f:
        CourseBrowser_3 = json.load(f)
    #############################################################
    current_semester = last_semester + 1 # To store the number of the current semester
    selected_courses = []

    if current_semester == 1:
        selected_courses = choose_courses(study_plan, max_credits_first_semester,CourseBrowser_1)
    elif current_semester == 2:
        selected_courses = choose_courses(study_plan, max_credits_second_semester,CourseBrowser_2)
    elif current_semester == 3:
        selected_courses = choose_courses(study_plan, max_credits_summer_semester,CourseBrowser_3)
    #########################################################################
    # Print the study plan with the next semester courses in the red color
    print_study_plan(study_plan, selected_courses)
    ########################################
    # Print the Schedule in terms of the semester
    if current_semester == 1:
        print_schedule(selected_courses,"CourseBrowser_1.json")
    elif current_semester == 2:
        print_schedule(selected_courses,"CourseBrowser_2.json")
    elif current_semester == 3:
        print_schedule(selected_courses,"CourseBrowser_3.json")
    #######################################

    flag = False # To do (continue) to the main loop
    # final part,print the data in the file and exit
    while True:
        save_to_file = input("Do you want to save the schedules to a text file? (y/n): ")
        if save_to_file.lower() == 'y':
            # Print the Schedule on the file in terms of the semester
            if current_semester == 1:
                print_schedule_on_file(selected_courses, "CourseBrowser_1.json")
            elif current_semester == 2:
                print_schedule_on_file(selected_courses, "CourseBrowser_2.json")
            elif current_semester == 3:
                print_schedule_on_file(selected_courses, "CourseBrowser_3.json")
            break
        elif save_to_file.lower() == 'n':
            exit_program = input("Do you want to exit the program? (y/n): ")
            if exit_program.lower() == 'y':
                break
            elif exit_program.lower() == 'n':
                flag = True
                break
            else:
                print("Invalid input.")
                break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    if flag:
        continue
    break