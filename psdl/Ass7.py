class Product:


product_list = []

def add_product():
   

    print("Product Added successfully")

def update_product():
    uid = int(input("Enter the product ID to update: "))

    

def search_product():
    sid = int(input("Enter the product ID to search: "))


def delete_product():
    sid = int(input("Enter the product ID to delete: "))

    
    
def display_product():

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
        display_product()

    elif choice == 4:
        update_product()

    elif choice == 5:
        search_product()

    elif choice == 6:
        print("Program Exited.")
        break

    else:
        print("Invalid Choice\n")



