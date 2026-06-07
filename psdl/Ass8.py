import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'root',
        database = 'school'
    )

def add_student():
    sid = int(input("Enter the student id : "))

    name = input("Enter the name of student : ")

    age = int(input("Enter age : "))

    marks = float(input("Enter the marks : "))

    conn = get_connection()

    cur = conn.cursor()

    query = "INSERT INTO students VALUES (%s, %s, %s, %s)"

    cur.execute(query, (sid,name,age,marks))

    conn.commit()

    print("Added")

    conn.close()

    cur.close()

def search():
    sid = int(input("Enter the student id : "))

    conn = get_connection()

    cur = conn.cursor()

    query = "SELECT * FROM students WHERE sid = %s"

    cur.execute(query, (sid,))

    row = cur.fetchone()

    if row:
        print(row)
    else:
        print("No")

    conn.close()

    cur.close()

def update():
    
    sid = int(input("Enter the student id : "))

    marks = float(input("Enter new marks : "))
    
    conn = get_connection()

    cur = conn.cursor()

    query = "UPDATE students SET marks = %s WHERE sid = %s"

    cur.execute(query, (marks, sid))

    conn.commit()

    print("Updated")

    conn.close()

    cur.close()

def delete():
    sid = int(input("Enter the student id : "))

    conn = get_connection()

    cur = conn.cursor()

    query = "Delete FROM students WHERE sid = %s"

    cur.execute(query, (sid,))

    conn.commit()

    if cur.rowcount:
        print("Record delete successfully")
    else:
        print("Record not found")

    conn.close()

    cur.close()

def display():
    
    conn = get_connection()

    cur = conn.cursor()

    cur.execute("SELECT * FROM students")

    rows = cur.fetchall()

    if rows : 
        for row in rows : 
            print(row)
    else:
        print("no")

    conn.close()

    cur.close()
    
