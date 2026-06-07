class Product:
    def __init__(self, pid, name, price, quantity):
        self.pid = pid
        self.name = name
        self.price = price
        self.quantity = quantity

    def display(self):
        print(f"Product ID : {self.pid}")
        print(f"Product Name: {self.name}")
        print(f"Product Price : {self.price}")
        print(f"Product Quantity : {self.quantity}")

class ElectronicProf(Product):
    def __init__(self, pid, name, price, quantity, brand):
        super().__init__(pid,name,price,quantity)

        self.brand = brand
    
    def display_elec(self):
        self.display()
        print(f"Product Brand : {self.brand}")


product_list = []

def add_product():
    pid = int(input("Enter pid : "))
    name = input("Enter name : ")
    price = float(input("Enter price : "))
    quantity = int(input("Enter quantity: "))

    p = Product(pid, name, price, quantity)

    product_list.append(p)

    print("Product added successfully")

def display_products():
    if len(product_list) == 0:
        print("List is empty")
    else:
        for p in product_list : 
            p.display()

def search_product():
    sid = int(input("Enter ProductID to search : "))

    found = False

    for p in product_list:
        if p.pid == sid:
            print("Product found")
            p.display()
            found = True
            break

    if not found:
        print("Product not found")

def delete_product():
    did = int(input("Enter the pid to delete : "))
    
    found = False

    for p in product_list:
        if p.pid == did: 
            print("Product delete")
            product_list.remove(p)
            found = True
            break

    if not found:
        print("Product not found")

def update_product():
    uid = int(input("Enter the pid to update : "))
    
    found = False

    for p in product_list:
        if p.pid == uid:
            p.price = float(input("Enter new price : "))
            found = True
            break

    if not found:
        print("Product not found")

while True:
    print("1. Add Product")
    print("2. Delete Product")
    print("3. Display Products")
    print("4. Update Product")
    print("5. Search Product")
    print("6. Exit")

    choice = int(input("Enter your choice : "))

    if choice == 1:
        add_product()

    elif choice == 2:
        delete_product()

    elif choice == 3:
        display_products()

    elif choice == 4:
        update_product()

    elif choice == 5:
        search_product()

    elif choice == 6:
        print("Program Exited.")
        break

    else:
        print("Invalid Choice\n")




