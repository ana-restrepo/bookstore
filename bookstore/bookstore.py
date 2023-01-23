# This is an inventory system for a bookstore. 
# It allows the user to enter, update, delete and search books from the store's database.

# ---------------- Import libraries ----------------
import sqlite3
from tabulate import tabulate
import os


# ---------------- Class Definition ----------------
# Definition of Book class.
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
# This function takes no arguments.
def create_database():

    db_created = False

    # Open or create database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object and table books in the open database.
        # If the table exists the program ignores the command.
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books
                       (id INTEGER PRIMARY KEY NOT NULL,
                       title TEXT NOT NULL,
                       author TEXT NOT NULL,
                       qty INTEGER NOT NULL)''')

        # Check if the table is empty. If it is, insert the first records onto the database.
        # Otherwise, skip this step. 
        cursor.execute('''SELECT count(*) FROM books''')

        is_books_empty = cursor.fetchone()

        if is_books_empty == (0,):

            # Insert appropriate information into table.
            # If records exist, ignore insertion to avoid the program failing.
            book_list = [[3001, "A Tale of Two Cities", "Charles Dickens", 30],
                         [3002, "Harry Potter and the Philosopher's Stone", "J.K. Rowling", 40],
                         [3003, "The Lion, the Witch and the Wardrobe", "C. S. Lewis", 25],
                         [3004, "The Lord of the Rings", "J.R.R Tolkien", 37],
                         [3005, "Alice in Wonderland", "Lewis Carroll", 12]]

            cursor.executemany('''INSERT OR IGNORE INTO books (id, title, author, qty)
                                VALUES (?, ?, ?, ?)''', book_list)

            # Commit changes and print a success message.
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


# Function to enter title or author and check the input is correctly formatted.
# This function takes in a string which indicates if the user want to enter a title or an author.
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
            # Return a string with the title or author as appropriate.
            return field_value


# Function to enter an ID and check it is a number with four digits.
# This function takes in no arguments.
def enter_id():

    while True:
        entered_id = input("Please enter ID (####): ")
        if not entered_id.isdigit() or len(entered_id) != 4:
            print("Please enter a 4 digit number as ID.")
            continue
        else:
            # Return a string with th ID, once the formatting had been verified.
            return entered_id


# Function to enter the book quantity and verify that it is a number less than 9999999999.
# This function takes in no arguments.
def enter_qty():

    while True:
        entered_qty = input("Please enter Qty.: ")
        if not entered_qty.isdigit() or len(entered_qty) > 10:
            print("Please enter a number up to 9999999999.")
            continue
        else:
            # Return a string with the quantity entered and verified.
            return entered_qty


# Function to search the database by title, author or ID.
# This function takes in a string indicating which field will be used to do the search.
def search_book(selection):
    
    # Check which field the user wants to search by, call the appropriate function to enter and verify the information.
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
        # Create cursor object.
        cursor = db.cursor()

        # Retrieve and store records with values similar to the information entered. 
        # The column is determined by the field selected by the user.
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

    # This function returns a boolean value indicating the outcome of the operation and a list of search results.
    return operation_success, records


# Function to transform a list of records into a list of cook objects.
# This function takes in a list of strings in the following format: ["id", "title", "author", "qty."]
def create_book_list(records):

    book_objects = []
    for item in records:
        book_objects.append(Book(item[0], item[1], item[2], item[3]))

    # Return a list of Book objects.
    return book_objects


# Function to print a list of book objects in a table format.
# This function takes in a list of Book objects.
def print_table(book_objects):

    # If the list of books has no objects, only the result total is printed, with no results table.
    print(f"\nSearch results:\t{len(book_objects)}")
    if len(book_objects) > 0:
        book_list = []
        for book in book_objects:
            book_list.append([book.book_id, book.title, book.author, book.book_qty])

        print(tabulate(book_list, headers=["ID", "Title", "Author", "Qty."], tablefmt="pretty"))


# Function to delete a record from the database.
# This function takes in a string with the ID of the record to be deleted.
def delete_book(delete_id):

    # Open database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object.
        cursor = db.cursor()
        
        # Delete record with the ID provided, commit changes.
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
    
    # This function returns a boolean value indicating the operation's success or failure.
    return operation_success


# Function to check if a title already exists in the database.
# This to avoid the creating of multiple record for the same book.
# This function takes in a string with the title to check.
def does_title_exist(check_title):

    # Open database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object.
        cursor = db.cursor()

        # Retrieve records with the same title as the one entered and store them in a list.
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

    # This function returns a boolean value of the operation status and a list of records with the same title.
    return operation_success, records


# Function to update the information of an existing record on the database.
# This function takes in a book object.
def update_data(book):

    # Open database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object.
        cursor = db.cursor()

        # Update the information of the record on the database with the same ID as the book object.
        # Commit changes and retrieve the new record.
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

    # Return the record after the changes have been made.
    return record


# Function to enter a new book to the database.
# This function takes in a book object.
def enter_data(book):

    # Open database.
    db = sqlite3.connect("bookstore-db")

    try:
        # Create cursor object.
        cursor = db.cursor()

        # Insert a new line in the books table with the title, author and quantity from the book object.
        # The ID will be autogenerated by the database.
        # Commit changes and retrieve the new record from the database.
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
    
    # This function returns the information of the new book entered into the database.
    return record


# Function to select field of search.
# This function takes in no arguments.
def menu_search():

    # Ask the user to select a option from the menu, according to their selection,
    # call the function to search a book with the value of the option variable as an argument.
    while True:
        option = input("\nWhat field would you like to use for your search: "
                       "\n\tI\t-\tBook ID"
                       "\n\tT\t-\tBook Title"
                       "\n\tA\t-\tBook Author\n").upper()

        correct_options = ["I", "T", "A"]

        if option in correct_options:
            is_successful, results = search_book(option)
            if is_successful:
                # This function returns a list of records which match the search criterion.
                return create_book_list(results)
            else:
                print("Operation failed, please try again.")
        else:
            print("Invalid selection. Please enter one of the options on the menu.")


# Function to search for a record and delete it.
# This function takes in no arguments.
def menu_delete():

    exit_delete = False
    while not exit_delete:

        # Print a message and call the search function to look for a record to be deleted.
        print("Search for the book you would like to delete.")
        search_results = menu_search()

        # If there is only one record which matches the search criterion, delete the record,
        # notify the user and exit the function.
        if len(search_results) == 1:
            selected_id = str(search_results[0].book_id)
            if delete_book(selected_id):
                print(f"Book with ID {selected_id} has been deleted.")
                exit_delete = True
            else:
                print("Operation unsuccessful. Please try again.")

        # If the search returns no results, offer the user the option to search again or exit the function.
        elif len(search_results) == 0:
            while True:
                exit_selection = input("\nNo results found."
                                       "\nEnter 'T' to try again or 'E' to exit: ").upper()
                if exit_selection == "E":
                    exit_delete = True
                    break
                elif exit_selection == "T":
                    break

        # If the search returns multiple records, print them on a table
        # and ask the user if they want to delete one or exit the function.
        else:
            print_table(search_results)
            while True:
                exit_selection = input("\nEnter 'D' to delete a record from the table above or 'E' to exit: ").upper()

                if exit_selection == "E":
                    exit_delete = True
                    break

                # If the user selects "D", ask them to select which result they want to delete by entering the ID.
                # Delete the selected record, print a confirmation message and exit the function.
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


# Function to search for a record to update and enter the new information.
# This function takes in no arguments.
def menu_update():
    exit_loop_1 = False
    exit_loop_2 = False
    update_needed = False
    book_to_change = ""

    # Loop one: search for and select one record to be updated.
    while not exit_loop_1:

        # Call search function.
        print("\nSearch for the book you would like to update.")
        search_results = menu_search()

        # If there is only one result, print it on a table, store it in the book_to_change variable and exit loop 1.
        if len(search_results) == 1:
            print_table(search_results)
            book_to_change = search_results[0]
            print(f"The record above will be updated.")
            break

        # If the search returns no results, ask the user if they want to try again or exit the function.
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

        # If the search returns multiple results, print them on a table
        # and ask the user if they want to update one of them or exit the function.
        else:
            print_table(search_results)
            while True:
                exit_selection = input("\nEnter 'U' to update a record from the table above or 'E' to exit: ").upper()

                if exit_selection == "E":
                    exit_loop_1 = True
                    exit_loop_2 = True
                    break

                # If the user selects "U", ask the user to select the record to be changed by entering its ID.
                # Once,the user selects a valid ID that is inside the results list, identify the record with that ID,
                # store it in the book_to_change variable, print a message and exit loop 1.
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

    # Loop 2: select which field or fields to update and store the new information in the book object.
    while not exit_loop_2:

        # Ask the user which field they want to change.
        field_to_change = input("\nWhat field would you like to update: "
                                "\n\tT\t-\tBook Title"
                                "\n\tA\t-\tBook Author"
                                "\n\tQ\t-\tQuantity"
                                "\n\tALL\t-\tAll Fields\n").upper()

        # If the user selects "T", ask them to enter a new title. Verify that this title does not exist in the database.
        # If it does, offer the user the option to enter a different title or exit the function.
        # Once the user enters a title that doesn't exist on the database,
        # change the title in the book object to match the new information and exit loop 2.
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

        # If the user selects "A", ask them to enter a new author,
        # and change the author in the book object to match the new information and exit loop 2.
        elif field_to_change == "A":
            book_to_change.author = enter_text(field_to_change).title()
            update_needed = True
            exit_loop_2 = True

        # If the user selects "Q", ask them to enter a new quantity,
        # change the quantity in the book object to match the new information and exit loop 2.
        elif field_to_change == "Q":
            book_to_change.book_qty = enter_qty()
            update_needed = True
            exit_loop_2 = True

        # If the user selects "ALL", ask them to enter new information for each of the fields,
        # update the values inside the book object and exit loop 2.
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

    # If the variable update needed has a True value, call the update data function passing the book_to_change,
    # containing the updated information, as an argument.
    # Then, print the updated record on a table with a success message.
    if update_needed:
        new_info = update_data(book_to_change)
        print_table([Book(new_info[0], new_info[1], new_info[2], new_info[3])])
        print("Information has been updated successfully as above.")


# Function to enter new information to create a new record.
# This function takes in no arguments.
def menu_enter():

    exit_enter = False
    while not exit_enter:

        # Ask the user to enter a new title and verify that it does not exist on the database.
        title = enter_text("T").title()
        is_successful, book_record = does_title_exist(title)

        # If the title is new, ask the user to enter an author and a quantity.
        # Store the information in a book object with a placeholder ID,
        # call the function to insert a new record in the database, print the new record on a table
        # and exit the function.
        if is_successful and len(book_record) == 0:
            new_title = title
            new_author = enter_text("A").title()
            new_qty = enter_qty()
            placeholder_id = "placeholder"
            new_book = enter_data(Book(placeholder_id, new_title, new_author, new_qty))
            print(new_book)
            break

        # If the title entered is already in the database, ask the user if they want to try again or exit the function.
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


# Function to export search results to a .txt file.
# This function takes in a list of book objects.
def table_to_file(book_objects):

    # Ask the user if they want to export their search results.
    while True:
        selection = input("Would you like to export your search results to a file? (Y/N): ").upper()

        # If the user selects "Y", add the result total to a string followed by a table with the results' information.
        # Write the string on a .txt file, print a success message and exit the function.
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

        # If the user selects "N", exit the function.
        elif selection == "N":
            print("Search results will not be exported.")
            break

        else:
            print("Invalid selection. Please try again.")


# ---------------- Program Start ----------------
# Print a welcome message and call the function to create the database.
print("\nWelcome to our Bookstore system!")
create_database()

# Ask the user to select an option from the menu.
# According to the option selected, call the appropriate function.
# If the selection is invalid, ask the user to try again.
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
        # Call the function to search the database and print the result on a table.
        # Then, call the function to export the search results.
        result_list = menu_search()
        print_table(result_list)
        table_to_file(result_list)

    elif menu_option == "4":
        menu_delete()

    elif menu_option == "0":
        break

    else:
        print("Invalid selection. Please choose one of the options on the menu.")
