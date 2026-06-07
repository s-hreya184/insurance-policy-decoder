import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "root",
        database = "school" 
    )

def insert():
    sid = int(input("Enter the student id : "))

    name = input("Enter the name of student : ")

    age = int(input("Enter age : "))

    marks = float(input("Enter the marks : "))

    conn = get_connection()

    cur = conn.cursor()

    query = "Insert into students (sid, name, age, marks) values (%s, %s, %s, %s)"

    cur.execute(query, (sid, name, age, marks))

    conn.commit()

    print(f"Record inserted successfully. Rows affected :{cur.rowcount}")

    cur.close()

    conn.close()


def update():
    update_sid = int(input("Enter the student ID to update : "))

    new_marks = float(input("Enter the new marks : "))

    conn = get_connection()

    cur = conn.cursor()

    query = "update students set marks = %s where sid = %s"

    cur.execute(query, (new_marks, update_sid))

    conn.commit()

    if cur.rowcount:
        print(f"Record updated successfully")
    else:
        print("Record not found")

    cur.close()

    conn.close()

def delete_record():

    delete_sid = int(input("Enter the student ID to delete : "))

    conn = get_connection()

    cur = conn.cursor()

    query = "Delete from students where sid = %s"

    cur.execute(query, (delete_sid,))

    conn.commit()

    if cur.rowcount:
        print("Record delete successfully")
    else:
        print("Record not found")

    cur.close()

    conn.close()

def search():

    search_sid = int(input("Enter the student ID to search : "))

    conn = get_connection()

    cur = conn.cursor()

    query = "Select * from students where sid = %s"

    cur.execute(query, (search_sid,))

    row = cur.fetchone()

    if row:
        print("Record found successfully")
        print(row)
    else:
        print("Record not found")

    cur.close()

    conn.close()

def display_all():
    conn = get_connection()

    cur = conn.cursor()

    query = "select * from students"

    cur.execute(query)

    rows = cur.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No record found")

    cur.close()

    conn.close()

while True:
    print("1. Insert Record")
    print("2. Update Record")
    print("3. Delete Record")
    print("4. Search Record")
    print("5. Display All Records")
    print("6. Exit")

    choice = int(input("Enter number : "))

    if choice == 1: insert()
    elif choice == 2: update()
    elif choice == 3: delete_record()
    elif choice == 4: search()
    elif choice == 5: display_all()
    elif choice == 6: print("Exit!"); break
    else: print("Invalid choice. Try again.")
      

