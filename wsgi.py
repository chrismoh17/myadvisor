import click, pytest, sys
import csv
from flask import Flask
from flask.cli import with_appcontext, AppGroup
""" 
# add more courses, 
# populate student course history 10courses 
add courses to program
offered courses
"""

from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( 
    create_user, 
    get_all_users_json, 
    get_all_users, 
    create_program,
    get_all_OfferedCodes,
    get_core_credits,
    create_course,
    get_course_by_courseCode,
    get_prerequisites,
    get_all_courses,
    create_programCourse,
    addSemesterCourses,
    create_student,
    get_program_by_name,
    get_all_programCourses,
    addCoursetoHistory,
    getCompletedCourseCodes,
    get_allCore,
    addCourseToPlan,
    get_student_by_id,
    generator
    )

test1 = ["COMP1600",  "COMP1601", "COMP1602", "COMP1603", "COMP1604", "MATH1115", "INFO1600", "INFO1601",  "FOUN1101", "FOUN1105", "FOUN1301", "COMP3605", "COMP3606", "COMP3607", "COMP3608",]

file_path = "/Users/jerrellejohnson/Desktop/softEng2/flaskmvc/testData/test.txt"


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)


# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bobpass')
    create_course('testData/courseData.csv')
    create_program("Computer Science Major", 69, 15, 9)
    create_student(816, "boo", "testing", "Computer Science Major")

    for c in test1:
        addCoursetoHistory(816, c)
    print('Student course history updated')

    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            line = line.strip()
            if i ==0:
                programName = line
            else:
                course = line.split(',')
                create_programCourse(programName, course[0],int(course[1]))
    
    file_path1='/Users/jerrellejohnson/Desktop/softEng2/flaskmvc/testData/test2.txt'
    with open(file_path1, 'r') as file:
        for i, line in enumerate(file):
            line = line.strip()
            addSemesterCourses(line)



    
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli


# ... (previous code remains the same)

'''
Student
'''
student_cli = AppGroup("student", help="Student object commands")

# Define the student create command
@student_cli.command("create", help="Creates a student")
@click.argument("student_id", type=str)
@click.argument("password", type=str)
@click.argument("name", type=str)
@click.argument("programName", type=str)
def create_student_command(student_id, password, name, programname):
    create_student(student_id, password, name, programname)

@student_cli.command("addCourse", help="Student adds a completed course to their history")
@click.argument("student_id", type=str)
@click.argument("code", type=str)
def addCourse(student_id, code):
    addCoursetoHistory(student_id, code)

@student_cli.command("getCompleted", help="Get all of a student completed courses")
@click.argument("student_id", type=str)
def completed(student_id):
    comp = getCompletedCourseCodes(student_id)
    for c in comp:
        print(f'{c}')

@student_cli.command("addCourseToPlan", help="Adds a course to a student's course plan")
def courseToPlan():
    student = get_student_by_id("816")
    addCourseToPlan(student, "COMP2611")

@student_cli.command("generate", help="Generates a course plan based on what they request")
@click.argument("command", type=str)
def generatePlan(command):
    student = get_student_by_id("816")
    courses = generator(student, command)
    for c in courses:
        print(c)


app.cli.add_command(student_cli)

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)
#################################################################

'''
Program Commands
'''

program = AppGroup('program', help = 'Program object commands')

@program.command('create', help='Create a new program')
@click.argument('name', type=str)
@click.argument('core', type=int)
@click.argument('elective', type=int)
@click.argument('foun', type=int)
def create_program_command(name, core, elective, foun):
    program = create_program(name, core, elective, foun)
    

@program.command('core', help='Get program core courses')
#@click.argument('programname', type=str)
def get_CoreCourses():
    create_programCourse("Computer Science Major", "COMP2611", 1)
    create_programCourse("Computer Science Major", "COMP3605", 1)
    create_programCourse("Computer Science Major", "COMP3610", 2)
    core = get_allCore("Computer Science Major")
    for c in core:
        print({c.code})

@program.command('corecredits', help='Get program core courses')
@click.argument('programname', type=str)
def get_CoreCredits(programname):
    credits = get_core_credits(programname)
    print(f'Total Core Credits = {credits}') if credits else print(f'error')

@program.command('allcourses', help='Get all courses')
@click.argument('programname', type=str)
def allCourses(programname):
    all = get_all_courses(programname)
    print(f'All courses are = {all}') if credits else print(f'error')

@program.command('getprogram', help='Get a program by name')
@click.argument('programname', type=str)
def getProgram(programname):
   program = get_program_by_name(programname)
   print(f'{program.id}')

@program.command('addCourse', help='Add a course to a program')
@click.argument('programname', type=str)
@click.argument('code', type=str)
@click.argument('type', type=int)
def addProgramCourse(programname, code, type):
   create_programCourse(programname, code, type)

@program.command('getprogramCourses', help='Get all courses of a program')
@click.argument('programname', type=str)
def addProgramCourse(programname):
   courses = get_all_programCourses(programname)
   for c in courses:
       print(f'{c.code}')

app.cli.add_command(program)
#################################################################

'''
Course Commands
'''

course = AppGroup('course', help = 'Program object commands')

@course.command('create', help='Create a new course')
@click.argument('file_path')
def create_course_command(file_path):  
    newcourse = create_course(file_path)
    print(f'Course created with course code "{newcourse.courseCode}", name "{newcourse.courseName}", credits "{newcourse.credits}", ratings "{newcourse.rating}" and prerequites "{newcourse.prerequisites}"')


@course.command('prereqs', help='Create a new course')
@click.argument('code', type=str)
def create_course_command(code):  
    prereqs = get_prerequisites(code)
    print(f'These are the prerequisites for {code}: {prereqs}') if prereqs else print(f'error')

@course.command('getcourse', help='Get a course by course code')
@click.argument('code', type=str)
def get_course(code):  
    course = get_course_by_courseCode(code)
    print(f'Course Name: {course.courseName}') if course else print(f'error')

@course.command('getprereqs', help='Get all prerequistes for a course')
@click.argument('code', type=str)
def get_course(code):  
    prereqs = get_prerequisites(code)
    for r in prereqs:
        print(f'{r.prereq_courseCode}')

@course.command('nextsem', help='Add a course to offered courses')
@click.argument('code', type=str)
def add_course(code):
    course = addSemesterCourses(code)
    print(f'Course Name: {course.courseName}') if course else print(f'error')

@course.command('getNextSemCourses', help='Get all the courses offered next semester')
def allSemCourses():
    courses = get_all_OfferedCodes()

    if courses:
        for c in courses:
            print({c})
    else:
        print("empty")
    

app.cli.add_command(course)

###########################################################

'''
Course Plan Commands
'''

coursePlan = AppGroup('plan', help = 'Course Plan object commands')

# @coursePlan.command('remaining', help='Get remaining program courses')
# @click.argument('programname', type=str)
# def remaining(programname):  

#     # required = get_all_courses(programname)
#     # completed = ['COMP1600']
#     # newRemaining = getRemainingCourses(completed, required)
#     # print(f'Remaining courses are: {newRemaining}')


app.cli.add_command(coursePlan)