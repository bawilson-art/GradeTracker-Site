from dataclasses import dataclass
from drafter import *

set_website_title("GradeTracker")

set_site_information(
    "Braden Wilson",
    "A website that helps students track their grades.",
    "Students put in their assignment names and grades to get an average",
    "Plan: Improve website and make it more complex",
    []
)

@dataclass
class Assignment:
    """Tracks information for one assignment."""
    name: str
    score: float
    category: str
    course_name: str

@dataclass
class State:
    """Tracks information between website pages."""
    student_name: str
    course_name: str
    assignments: list[Assignment]
    exams: float
    grade_goal: float
    selected_course: str

def get_course_names(state: State) -> list[str]:
    """Returns a list of course names from assignments"""
    courses = []

    for assignment in state.assignments:
        if assignment.course_name not in courses:
            courses.append(assignment.course_name)

    return courses

def get_course_assignments(state: State, course_name: str) -> list[Assignment]:
    """Returns assignments that belong to a certain course"""
    course_assignments = []

    for assignment in state.assignments:
        if assignment.course_name == course_name:
            course_assignments.append(assignment)

    return course_assignments

def calculate_average(state: State, course_name: str = "") -> float:
    """Calculates the average grade for the courses"""
    total = 0.0
    count = 0

    for assignment in state.assignments:
        if course_name == "" or assignment.course_name == course_name:
            total += assignment.score
            count += 1

    if count == 0:
        return 0.0

    return total / count

def get_letter_grade(average: float) -> str:
    """Converts numbers into letter grades"""
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    else:
        return "F"

@route
def index(state: State) -> Page:
    """Displays the home page"""
    average = calculate_average(state)
    letter = get_letter_grade(average)

    return Page(state, [
        Header("GradeTracker"),
        "Overall Average: " + str(round(average, 2)) + "%",
        "Letter Grade: " + letter,
        "Grade Goal: " + str(state.grade_goal) + "%",
        "Number of Assignments: " + str(len(state.assignments)),
        Button("View Grades", "view_grades"),
        Button("Add an Assignment", "add_grade"),
        Button("Grade Summary", "grade_summary"),
        Button("Profile", "profile"),
        Button("Help", "help")
    ])

@route
def view_grades(state: State) -> Page:
    """Displays assignments with the course and grade"""
    content = [
        Header("My Grades"),
        "Here is a complete list of all your assignments."
    ]

    if len(state.assignments) == 0:
        content.append("You have not added any assignments yet.")

    else:
        for assignment in state.assignments:
            content.append(
                Header(assignment.course_name + " - " + assignment.name, 3)
            )
            content.append("Grade: " + str(assignment.score) + "%")
            content.append("Category: " + assignment.category)
            content.append("")

    content.append(Button("Home", "index"))

    return Page(state, content)

@route
def add_grade(state: State) -> Page:
    """Displays where to enter new assignments"""
    return Page(state, [
        Header("Add a New Assignment"),
        "Enter the course and assignment information below.",
        "Course Name:",
        TextBox("course_name"),
        "\nAssignment Name:",
        TextBox("title_box"),
        "\nGrade Score (0-100):",
        TextBox("grade_box"),
        "\nAssignment Category:",
        SelectBox(
            "category",
            ["Homework", "Quiz", "Exam", "Project"],
            "Homework"
        ),
        "\n",
        Button("Add Assignment", "save_new_grade"),
        Button("Home", "index")
    ])

@route
def save_new_grade(state: State,
                   course_name: str,
                   title_box: str,
                   grade_box: str,
                   category: str) -> Page:
    """Checks and saves new assignments"""

    if course_name.strip() == "" or title_box.strip() == "":
        return Page(state, [
            Header("Input Error"),
            "Please enter both a course name and assignment name.",
            Button("Home", "index")
        ])

    try:
        score = float(grade_box)
    except ValueError:
        return Page(state, [
            "Please enter a valid numerical grade.",
            Button("Home", "index")
        ])

    if score < 0 or score > 100:
        return Page(state, [
            "Grades must be between 0 and 100.",
            Button("Home", "index")
        ])

    for assignment in state.assignments:
        if (assignment.name.lower() == title_box.strip().lower()
                and assignment.course_name.lower()
                == course_name.strip().lower()):
            return Page(state, [
                "That assignment already exists in this course.",
                Button("Home", "index")
            ])

    new_assignment = Assignment(
        title_box.strip(),
        score,
        category,
        course_name.strip()
    )

    state.assignments.append(new_assignment)

    state.course_name = course_name.strip()
    state.selected_course = course_name.strip()

    if category == "Exam":
        state.exams = score

    return Page(state, [
        Header("Assignment Added!"),
        "Your assignment was successfully added.",
        Button("Home", "index")
    ])

@route
def save(state: State) -> Page:
    """Displays student's saved grades and profile"""
    return Page(state, [
        Header("Review Grades"),
        "Student: " + state.student_name,
        "Number of assignments: " + str(len(state.assignments)),
        "Overall Average: " + str(
            round(calculate_average(state), 2)
        ) + "%",
        "Grade Goal: " + str(state.grade_goal) + "%",
        Button("Home", "index")
    ])

@route
def help(state: State) -> Page:
    """Explains how to use the website"""
    return Page(state, [
        Header("How to use GradeTracker"),
        "1. Go to Add an Assignment.",
        "2. Enter your course name.",
        "3. Enter the assignment name and grade.",
        "4. Select the assignment category.",
        "5. Click Add Assignment.",
        "6. Visit View Grades to see all your scores.",
        "7. Visit Grade Summary to calculate your average.",
        "\nGrade Information:",
        "A = 90-100",
        "B = 80-89",
        "C = 70-79",
        "D = 60-69",
        "F = Below 60",
        Button("Home", "index")
    ])

@route
def profile(state: State) -> Page:
    """Displays student's name and what their goal grade is"""
    return Page(state, [
        Header("Student Profile"),
        "Student Name:",
        TextBox("student_box", state.student_name),
        "\nDesired Grade Goal:",
        TextBox("goal_box", str(state.grade_goal)),
        "\n",
        Button("Update Profile", "save_profile"),
        Button("Home", "index")
    ])

@route
def save_profile(state: State,
                 student_box: str,
                 goal_box: str) -> Page:
    """Saves the profile that is entered"""

    if student_box.strip() == "":
        return Page(state, [
            "Please enter your name.",
            Button("Home", "index")
        ])

    try:
        goal = float(goal_box)
    except ValueError:
        return Page(state, [
            "Please enter a valid grade goal.",
            Button("Home", "index")
        ])

    if goal < 0 or goal > 100:
        return Page(state, [
            "Your grade goal must be between 0 and 100.",
            Button("Home", "index")
        ])

    state.student_name = student_box.strip()
    state.grade_goal = goal

    return Page(state, [
        Header("Profile Updated!"),
        "Your student information was updated.",
        Button("Home", "index")
    ])

@route
def grade_summary(state: State) -> Page:
    """Calculates and displays course average and letter grade""" 

    if len(state.assignments) == 0:
        return Page(state, [
            Header("Grade Summary"),
            "You have not entered any grades yet.",
            Button("Home", "index")
        ])

    if state.selected_course == "":
        average = calculate_average(state)
        course_label = "All Courses"
    else:
        average = calculate_average(state, state.selected_course)
        course_label = state.selected_course

    letter = get_letter_grade(average)

    if average >= 60:
        passing_message = "Your current grade is passing."
    else:
        passing_message = "Your current grade is failing."

    return Page(state, [
        Header("Grade Summary"),
        "Course: " + course_label,
        "Current Grade: " + str(round(average, 2)) + "%",
        "Letter Grade: " + letter,
        passing_message,
        Button("Home", "index")
    ])

def sample_state() -> State:
    """Sample to test the code"""
    return State(
        "Student",
        "Algebra",
        [
            Assignment("Chapter 1 Test", 84.0, "Exam", "Algebra"),
            Assignment("Homework 2", 92.0, "Homework", "Biology")
        ],
        84.0,
        90.0,
        "Algebra"
    )

assert_has(index(sample_state()), "GradeTrack")
assert_has(view_grades(sample_state()), "Chapter 1 Test")
assert_has(add_grade(sample_state()), "Course Name")

assert_state(
    save_new_grade(
        State("Student", "", [], 0.0, 90.0, ""),
        "Chemistry",
        "Lab 1",
        "88",
        "Project"
    ),
    State(
        "Student",
        "Chemistry",
        [Assignment("Lab 1", 88.0, "Project", "Chemistry")],
        0.0,
        90.0,
        "Chemistry"
    )
)



assert_has(save(sample_state()), "session")
assert_has(help(sample_state()), "How to use GradeTrack")
assert_has(profile(sample_state()), "Student Name")

assert_state(
    save_profile(
        sample_state(),
        "Alex",
        "95"
    ),
    State(
        "Alex",
        "Algebra",
        [
            Assignment("Chapter 1 Test", 84.0, "Exam", "Algebra"),
            Assignment("Homework 2", 92.0, "Homework", "Biology")
        ],
        84.0,
        95.0,
        "Algebra"
    )
)


start_server(
    State(
        "Student",
        "",
        [],
        0.0,
        0.0,
        ""
    )
)
