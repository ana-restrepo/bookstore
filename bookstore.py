#

# ---------------- Import libraries ----------------
import sqlite3
from tabulate import tabulate
import os


# ---------------- Class Definition ----------------
# Definition of book object.
class Book:

    # Definition of instance variables, one for each column of the database book table.
    def __init__(self, book_id, title, author, book_qty):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.book_qty = book_qty

    # Function to get object attributes as a list.
    def get_str(self):
        return [self.book_id, self.title, self.author, self.book_qty]


# ---------------- Function Definition ----------------

# Function to create and populate the database.
# If the tables exist and contain the following information, the program ignores it to avoid failing.
# This function takes no arguments.
def create_database():

    db_created = False

    # Open or create database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object and table books in the open database.
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books
                       (id INTEGER PRIMARY KEY NOT NULL,
                       title TEXT NOT NULL,
                       author TEXT NOT NULL,
                       qty INTEGER NOT NULL)''')

        cursor.execute('''SELECT count(*) FROM books''')

        is_books_empty = cursor.fetchone()

        if is_books_empty == (0,):

            # Insert appropriate information into table.
            # If records exist, ignore insertion to avoid the program failing. See Source 1.
            book_list = [[3001, "A Tale of Two Cities", "Charles Dickens", 30],
                         [3002, "Harry Potter and the Philosopher's Stone", "J.K. Rowling", 40],
                         [3003, "The Lion, the Witch and the Wardrobe", "C. S. Lewis", 25],
                         [3004, "The Lord of the Rings", "J.R.R Tolkien", 37],
                         [3005, "Alice in Wonderland", "Lewis Carroll", 12]]

            cursor.executemany('''INSERT OR IGNORE INTO books (id, title, author, qty)
                                VALUES (?, ?, ?, ?)''', book_list)

            # Commit changes.
            db.commit()

        print("\nDatabase is ready.")

        db_created = True

    # If there is an exception during the creating and populating of the database, raise it and rollback changes.
    except Exception as e:
        db.rollback()
        raise e

    # Regardless of operation outcome, close database and return database status.
    finally:

        db.close()
        return db_created


def enter_text(selection):

    if selection == "T":
        field = "title"
    else:
        field = "author"

    while True:
        field_value = input(f"Please enter the book {field}: ")
        if len(field_value) > 256:
            print(f"{field.title()} is too long. Please enter up to 256 characters.")
        elif len(field_value) == 0:
            print(f"{field.title()} is too short. Please enter at least one character.")
        else:
            return field_value


def enter_id():

    while True:
        entered_id = input("Please enter ID (####): ")

        # If the ID is not in the right format, re-start the loop.
        if not entered_id.isdigit() or len(entered_id) != 4:
            print("Please enter a 4 digit number as ID.")
            continue

        else:
            return entered_id


def enter_qty():

    while True:
        entered_qty = input("Please enter Qty.: ")

        # If the Qty. is not in the right format, re-start the loop.
        if not entered_qty.isdigit() or len(entered_qty) > 10:
            print("Please enter a number up to 9999999999.")
            continue

        else:
            return entered_qty


def search_book(selection):

    if selection == "I":
        search_value = str("%" + enter_id() + "%")
        field = "id"
    elif selection == "T":
        search_value = str("%" + enter_text(selection) + "%")
        field = "title"
    else:
        search_value = str("%" + enter_text(selection) + "%")
        field = "author"

    # Open database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object and table books in the open database.
        cursor = db.cursor()

        # Retrieve records with titles similar to the entry in the database and store them in a list.
        cursor.execute('''SELECT * FROM books WHERE ''' + field + ''' LIKE ? ''', (search_value,))

        records = cursor.fetchall()
        operation_success = True

    # If any exceptions occur, rollback any changes and raise the exception.
    except Exception as e:
        records = []
        operation_success = False
        print(e)

    # Close database.
    finally:
        db.close()

    return operation_success, records


def create_book_list(records):

    book_objects = []

    for item in records:
        book_objects.append(Book(item[0], item[1], item[2], item[3]))

    return book_objects


def print_table(book_objects):

    print(f"\nSearch results:\t{len(book_objects)}")

    if len(book_objects) > 0:
        book_list = []

        for book in book_objects:
            book_list.append([book.book_id, book.title, book.author, book.book_qty])

        print(tabulate(book_list, headers=["ID", "Title", "Author", "Qty."], tablefmt="pretty"))


def delete_book(delete_id):

    # Open database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object and table books in the open database.
        cursor = db.cursor()

        cursor.execute('''DELETE FROM books WHERE id=? ''', (delete_id,))
        db.commit()

        operation_success = True

    # If any exceptions occur, rollback any changes and raise the exception.
    except Exception as e:
        operation_success = False
        print(e)

    # Close database.
    finally:
        db.close()

    return operation_success


def does_title_exist(check_title):

    # Open database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object and table books in the open database.
        cursor = db.cursor()

        # Retrieve records with titles similar to the entry in the database and store them in a list.
        cursor.execute('''SELECT * FROM books WHERE title=? ''', (check_title,))

        records = cursor.fetchall()

        operation_success = True

    # If any exceptions occur, rollback any changes and raise the exception.
    except Exception as e:
        records = []
        operation_success = False
        print(e)

    # Close database.
    finally:
        db.close()

    return operation_success, records


def update_data(book):

    # Open database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object and table books in the open database.
        cursor = db.cursor()

        # Retrieve records with titles similar to the entry in the database and store them in a list.
        cursor.execute('''UPDATE books SET title=?, author=?, qty=? WHERE id=? ''',
                       (book.title, book.author, book.book_qty, book.book_id))
        db.commit()
        cursor.execute('''SELECT * FROM books WHERE id=?''', (book.book_id,))
        record = cursor.fetchone()

    # If any exceptions occur, rollback any changes and raise the exception.
    except Exception as e:
        record = []
        print(e)

    # Close database.
    finally:

        db.close()

    return record


def enter_data(book):

    # Open database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object and table books in the open database.
        cursor = db.cursor()

        # Retrieve records with titles similar to the entry in the database and store them in a list.
        cursor.execute('''INSERT INTO books (title, author, qty) VALUES (?, ?, ?) ''',
                       (book.title, book.author, book.book_qty))

        db.commit()

        new_id = cursor.lastrowid

        cursor.execute('''SELECT * FROM books WHERE id=?''', (str(new_id),))

        record = cursor.fetchone()

    # If any exceptions occur, rollback any changes and raise the exception.
    except Exception as e:
        record = []
        print(e)

    # Close database.
    finally:
        db.close()

    return record


def menu_search():

    while True:
        option = input("\nWhat field would you like to use for your search: "
                       "\n\tI\t-\tBook ID"
                       "\n\tT\t-\tBook Title"
                       "\n\tA\t-\tBook Author\n").upper()

        correct_options = ["I", "T", "A"]

        if option in correct_options:
            is_successful, results = search_book(option)
            if is_successful:
                return create_book_list(results)
            else:
                print("Operation failed, please try again.")

        else:
            print("Invalid selection. Please enter one of the options on the menu.")


def menu_delete():
    exit_delete = False

    while not exit_delete:

        print("Search for the book you would like to delete.")

        search_results = menu_search()

        if len(search_results) == 1:
            selected_id = str(search_results[0].book_id)
            if delete_book(selected_id):
                print(f"Book with ID {selected_id} has been deleted.")
                exit_delete = True
            else:
                print("Operation unsuccessful. Please try again.")
        elif len(search_results) == 0:
            while True:
                exit_selection = input("\nNo results found."
                                       "\nEnter 'T' to try again or 'E' to exit: ").upper()
                if exit_selection == "E":
                    exit_delete = True
                    break
                elif exit_selection == "T":
                    break
        else:
            print_table(search_results)
            while True:
                exit_selection = input("\nEnter 'D' to delete a record from the table above or 'E' to exit: ").upper()

                if exit_selection == "E":
                    exit_delete = True
                    break

                elif exit_selection == "D":
                    id_list = [str(book.book_id) for book in search_results]
                    while True:
                        selected_id = enter_id()
                        if selected_id not in id_list:
                            print("ID not in result list. Please try again.")
                            continue
                        else:
                            if delete_book(selected_id):
                                print(f"Book with ID {selected_id} has been deleted.")
                                exit_delete = True
                                break
                            else:
                                print("Operation unsuccessful. Please try again.")
                                break
                    break

                else:
                    print("Invalid selection. Please try again.")


def menu_update():
    exit_loop_1 = False
    exit_loop_2 = False
    update_needed = False
    book_to_change = ""

    while not exit_loop_1:

        print("\nSearch for the book you would like to update.")

        search_results = menu_search()

        if len(search_results) == 1:
            print_table(search_results)
            book_to_change = search_results[0]
            print(f"The record above will be updated.")
            break

        elif len(search_results) == 0:
            while True:
                exit_selection = input("\nNo results found."
                                       "\nEnter 'T' to try again or 'E' to exit: ").upper()
                if exit_selection == "E":
                    exit_loop_1 = True
                    exit_loop_2 = True
                    break
                elif exit_selection == "T":
                    break
        else:
            print_table(search_results)
            while True:
                exit_selection = input("\nEnter 'U' to update a record from the table above or 'E' to exit: ").upper()

                if exit_selection == "E":
                    exit_loop_1 = True
                    exit_loop_2 = True
                    break

                elif exit_selection == "U":
                    id_list = [str(book.book_id) for book in search_results]
                    while True:
                        selected_id = enter_id()
                        if selected_id not in id_list:
                            print("ID not in result list. Please try again.")
                            continue
                        else:
                            for book in search_results:
                                if str(book.book_id) == selected_id:
                                    book_to_change = book
                            print(f"Book with ID {selected_id} will be updated.")
                            exit_loop_1 = True
                            break
                    break

                else:
                    print("Invalid selection. Please try again.")

    while not exit_loop_2:

        field_to_change = input("\nWhat field would you like to update: "
                                "\n\tT\t-\tBook Title"
                                "\n\tA\t-\tBook Author"
                                "\n\tQ\t-\tQuantity"
                                "\n\tALL\t-\tAll Fields\n").upper()

        if field_to_change == "T":
            while True:
                title = enter_text(field_to_change).title()
                is_successful, book_record = does_title_exist(title)
                if is_successful and len(book_record) == 0:
                    book_to_change.title = title
                    update_needed = True
                    exit_loop_2 = True
                    break

                elif is_successful and len(book_record) > 0:
                    while True:
                        exit_selection = input("\nA book with this name already exists in the database."
                                               "\nEnter 'T' to try again or 'E' to exit: ").upper()
                        if exit_selection == "E":
                            exit_loop_2 = True
                            update_needed = False
                            break
                        elif exit_selection == "T":
                            break

                else:
                    continue

        elif field_to_change == "A":
            book_to_change.author = enter_text(field_to_change).title()
            update_needed = True
            exit_loop_2 = True

        elif field_to_change == "Q":
            book_to_change.book_qty = enter_qty()
            update_needed = True
            exit_loop_2 = True

        elif field_to_change == "ALL":
            while True:
                title = enter_text("T").title()
                is_successful, book_record = does_title_exist(title)
                if is_successful and len(book_record) == 0:
                    book_to_change.title = title
                    break
            book_to_change.author = enter_text("A").title()
            book_to_change.book_qty = enter_qty()
            update_needed = True
            exit_loop_2 = True

        else:
            print("Invalid selection. Please try again.")

    if update_needed:
        new_info = update_data(book_to_change)
        print_table([Book(new_info[0], new_info[1], new_info[2], new_info[3])])
        print("Information has been updated successfully as above.")


def menu_enter():

    exit_enter = False

    while not exit_enter:
        title = enter_text("T").title()
        is_successful, book_record = does_title_exist(title)
        if is_successful and len(book_record) == 0:
            new_title = title
            new_author = enter_text("A").title()
            new_qty = enter_qty()
            placeholder_id = "placeholder"
            new_book = enter_data(Book(placeholder_id, new_title, new_author, new_qty))
            print(new_book)
            break

        elif is_successful and len(book_record) > 0:
            while True:
                exit_selection = input("\nA book with this name already exists in the database."
                                       "\nEnter 'T' to try again or 'E' to exit: ").upper()
                if exit_selection == "E":
                    exit_enter = True
                    break
                elif exit_selection == "T":
                    break

        else:
            continue


def table_to_file(book_objects):

    while True:
        selection = input("Would you like to export your search results to a file? (Y/N): ").upper()

        if selection == "Y":

            file_header = f"\nSearch results:\t{len(book_objects)}\n"

            book_list = []

            for book in book_objects:
                book_list.append([book.book_id, book.title, book.author, book.book_qty])

            table = (tabulate(book_list, headers=["ID", "Title", "Author", "Qty."], tablefmt="pretty"))

            with open("results.txt", "w") as file:
                file.write(file_header + table)

            print(f"Exported file 'results.txt' an be found in: {os.getcwd()}")
            break

        elif selection == "N":
            print("Search results will not be exported.")
            break

        else:
            print("Invalid selection. Please try again.")


# ---------------- Program Start ----------------

print("\nWelcome to our Bookstore system!")

create_database()

while True:
    menu_option = input("\nPlease select one of the following options:"
                        "\n\t1\t-\tEnter New Book."
                        "\n\t2\t-\tUpdate Existing Book."
                        "\n\t3\t-\tSearch Books."
                        "\n\t4\t-\tDelete Book."
                        "\n\t0\t-\tExit.\n")

    if menu_option == "1":
        menu_enter()

    elif menu_option == "2":
        menu_update()

    elif menu_option == "3":
        search_results = menu_search()
        print_table(search_results)
        table_to_file(search_results)

    elif menu_option == "4":
        menu_delete()

    elif menu_option == "0":
        break

    else:
        print("Invalid selection. Please choose one of the options on the menu.")
