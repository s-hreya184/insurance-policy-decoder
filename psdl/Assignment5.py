employees = [
{"name": "Aman", "salary": 50000},
{"name": "Riya", "salary": 65000},
{"name": "Karan", "salary": 45000},
{"name": "Sneha", "salary": 70000}
]

from functools import reduce

def totalPay(stu):
    return reduce(lambda x, y : x + y["salary"], stu, 0)

print(totalPay(employees))

def incSal(stu):
    return list(map(lambda x : {" name" : x["name"], "salary" : x["salary"]*1.10}, stu))

print(incSal(employees))

def richEmp(students):
    return list(filter(lambda x : x["salary"] >= 60000, students))

print(richEmp(employees))