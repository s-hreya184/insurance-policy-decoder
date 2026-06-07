students = {}

def add_students():

    sid = int(input("Enter student ID : "))

    if sid in students:
        print("Student already exists")
        return
    
    name = input("Enter name : ")
    age = int(input("Enter age : "))
    marks = float(input("Enter marks : "))

    students[sid] = {
        "Name" : name,
        "Age" : age,
        "Marks" : marks
    }

    print("student added") 

def display():
    if not students:
        print("Empty")
        return
    
    for sid, details in students.items():
        print("\nID:", sid)

        for key, value in details.items():
            print(key, value)

def search():
    sid = int(input("Enter the student ID : "))

    if sid in students:
        print(students[sid])

    else:
        print("not found")

def update():
    sid = int(input("Enter the student ID : "))

    if sid in students:

        students[sid]["Marks"] = int(input("Enter the new marks : "))

        print("updated")

    else:
        print("not found")


def delete():
    sid = int(input("Enter the student ID : "))

    if sid in students:

        del students[sid]

        print("deleted")

    else:
        print("not found")

def good_students():
    for sid, details in students.items():
        if details["Marks"] > 75:
            print(details)

def topper():
    if not students:
        print("No record")
        return
    topper = max(students, key = lambda x : students[x]["Marks"])

    print(students[topper])

add_students()
display()
search()
update()
good_students()
topper()
delete()