# The application is written to simplify your work with a specific GuideCompanies database.
# (There is code for individual tables, it is possible to automate it, but I did not :)) Enjoy ^_^

# List of required libraries and extensions
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import re
import sys

# Additional functions to simplify.
import additional_funcs as DBhelper


# The class of the start authorization window---------------------------------------------------------------------------


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("Login.ui", self)

        self.my_close = False

        # First connection by postgres. It is necessary for read/write users table with password (not safe)
        try:
            self.connection = psycopg2.connect(user="postgres",
                                               password="root",
                                               host="127.0.0.1",
                                               port="5432",
                                               database="GuideCompanies")

            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()

            # This user is online now
            self.cursor.execute(f'''SELECT CURRENT_USER''')
            global curr_user
            curr_user = self.cursor.fetchall()
            for row in curr_user:

                # Clearing tables for triggers to work correctly (This must be done every time you log in)
                self.cursor.execute(f'''TRUNCATE TABLE "public".current_user_logon;''')
                self.cursor.execute(f'''TRUNCATE TABLE "public".lock_audit;''')
                print("Current user: ", row[0])

            print("Success connect to LOGIN by postgres!")

        # Throw error if bad connection
        except (Exception, Error) as error:
            print("Error connect to LOGIN by postgres!", error)

        self.own_username = "postgres"
        self.own_password = "root"

        # Take the last login user from file to fill the user_name field
        file_last_login = open('lastLogin.txt', 'r')
        self.username.setText(file_last_login.readline())
        file_last_login.close()

        self.loginButton.clicked.connect(self.loginFunction)  # Go to work loginFunction
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)  # Hiding password behind markers
        self.createButton.clicked.connect(lambda: self.gotocreate(self.own_username, self.own_password))  # Go to create form by gotocreate function

    # Verification of entered data during authorization
    def loginFunction(self):
        username = self.username.text()
        password = self.password.text()

        # If field are empty
        if len(username) == 0 or len(password) == 0:
            self.login_error_label.setText("Not all fields are filled in")
        else:  # or...
            self.login_error_label.setText("")
            self.cursor.execute(
                f"""SELECT user_passw FROM "public".users WHERE user_name = \'""" + username + """\';""")  # Take pass from table to verify with entered
            result = self.cursor.fetchall()
            for row in result:
                result_pass = row[0]
                break
            if result_pass == password:
                DBhelper.drop_message_box("Success logged in!")

                # Write the last login user to file for simplify the next connection (do not write user_name next)
                file_last_login = open('lastLogin.txt', 'w')
                file_last_login.write('' + username + '')
                file_last_login.close()

                # Go to next form by go_to_data function
                self.go_to_data(username, password)
            else:
                self.login_error_label.setText("Incorrect password! Try again")

    # Go to create form function
    def gotocreate(self, own_username, own_password):
        createAcc = CreateAccount(own_username, own_password)
        widget.addWidget(createAcc)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        self.cursor.close()
        self.connection.close()
        print("CLose connect to LOGIN by postgres!")

    # Go to data form function
    def go_to_data(self, username, password):
        data = DataForm(username, password)
        widget.addWidget(data)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        self.cursor.close()
        self.connection.close()
        print("CLose connect to LOGIN by postgres!")

# Form for creating a new account with a password-----------------------------------------------------------------------


class CreateAccount(QDialog):
    def __init__(self, own_username, own_password):
        super(CreateAccount, self).__init__()
        loadUi("Register.ui", self)

        self.my_close = False
        self.own_username = own_username
        self.own_password = own_password
        try:
            self.connection = psycopg2.connect(user=own_username,
                                               password=own_password,
                                               host="127.0.0.1",
                                               port="5432",
                                               database="GuideCompanies")

            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor_cre = self.connection.cursor()

            self.cursor_cre.execute(f'''SELECT CURRENT_USER''')
            global curr_user_cre
            curr_user_cre = self.cursor_cre.fetchall()
            for row in curr_user_cre:
                print("Current user: ", row[0])

            print("Success connect to CREATE by postgres!")

        except (Exception, Error) as error:
            print("Error connect to LOGIN by postgres!", error)

        self.registerButton.clicked.connect(self.createAccFunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.backButton.clicked.connect(self.goback)

    # Create new db account function
    def createAccFunction(self):
        username = self.username.text()

        # Check created accounts for avoiding repetition
        self.cursor_cre.execute(f'''SELECT "user_name" FROM "public".users;''')
        result_names = self.cursor_cre.fetchall()
        for row in result_names:
            if username == row[0]:
                DBhelper.drop_message_box("User with this name is already exist! Try again")
                return  # Drop
            else:
                continue  # Next

        # Confirming username and password (verify pass from table with pass entered and not_empty pass or username)
        if len(username) == 0 or len(self.password.text()) == 0 or len(
                self.confirmPassword.text()) == 0 or self.password.text() != self.confirmPassword.text():
            self.register_error_label.setText("Not all fields are filled in or Passwords don't match")
        else:
            self.register_error_label.setText("")
            password = self.password.text()

            # Add new account to the table after success confirming
            self.cursor_cre.execute(f'''INSERT INTO "public".users (user_name, user_passw) VALUES
                            ('{username}', '{password}'); ''')
            self.cursor_cre.execute(f"CREATE USER {username} WITH PASSWORD \'{password}\';")
            self.cursor_cre.execute(f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ' + username + ';')
            self.cursor_cre.execute(f'REVOKE ALL PRIVILEGES ON TABLE "public".users FROM ' + username + ';')

            DBhelper.drop_message_box("Success registration !")

            print("Success created account!")
            self.sucessGotoLogin()

    # Success creating? Go to login_form
    def sucessGotoLogin(self):
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        self.cursor_cre.close()
        self.connection.close()
        print("Close connect to CREATE by postgres!")

    # Go back without using creating form
    def goback(self):
        go_back = Login()
        widget.addWidget(go_back)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        self.cursor_cre.close()
        self.connection.close()
        print("Close connect to CREATE by postgres!")

# Database data display form--------------------------------------------------------------------------------------------


class DataForm(QDialog):
    def __init__(self, username, password):
        super(DataForm, self).__init__()
        loadUi("DataForm.ui", self)

        # Hide all using elements before you'll choose correct table
        self.my_close = False
        self.editButton.hide()
        self.tableWidget.hide()
        self.searchButton.hide()
        self.table_comboBox1.hide()
        self.table_comboBox2.hide()

        self.username = username
        self.password = password
        try:
            self.connection_user = psycopg2.connect(user=username,
                                                    password=password,
                                                    host="127.0.0.1",
                                                    port="5432",
                                                    database="GuideCompanies")
            self.cursor_user = self.connection_user.cursor()

            self.cursor_user.execute(f'''SELECT CURRENT_USER''')
            global curr_user_DF
            curr_user_DF = self.cursor_user.fetchall()
            for row in curr_user_DF:
                self.cursor_user.execute(f'''INSERT INTO "public".current_user_logon ("username")
                                                                        VALUES (\'{row[0]}\')''')
                self.cursor_user.execute(f'''commit''')
                print("Current user: ", row[0])

            print("Success connect to DATA_FORM " + username + "!")
        except (Exception, Error) as error:
            print("Error connect to DATA_FORM by " + username + "!", error)

        # The prohibition on editing data in table widgets!
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.exploreButton.clicked.connect(self.ShowTablesList)
        self.tables_list.itemClicked.connect(self.FillTableExplore)
        self.searchButton.clicked.connect(self.FillTableSearch)

        self.editButton.clicked.connect(lambda: self.GoToEditForm(username, password))

        file_last_login = open('lastLogin.txt', 'r')
        self.logged_in_username.setText(file_last_login.readline())
        file_last_login.close()

        widget.setFixedWidth(1280)
        widget.setFixedHeight(820)

        self.exitButton.clicked.connect(lambda: widget.close())

    # Show all database tables
    def ShowTablesList(self):
        self.tables_list.clear()
        self.cursor_user.execute(
            f'''SELECT pg_tables.tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';''')
        result_tables = self.cursor_user.fetchall()

        for row in result_tables:
            self.tables_list.addItems(row)

    def FillTableExplore(self):

        # Admin has all functions, user - not :)
        if self.username != 'postgres':
            self.cursor_user.execute(f'''SELECT "lock_info" from "public".lock_audit;''')
            lock_check = self.cursor_user.fetchall()
            if lock_check[0][0] == 'LOCK_TRUE': # Check the marker (TRUE = LOCK TABLE, FALSE = OPEN TABLE)
                pass
            else:
                self.editButton.show()
        else:
            self.editButton.show()

        # Show all elements
        self.tableWidget.show()
        self.searchButton.show()
        self.table_comboBox1.show()
        self.table_comboBox2.show()

        my_table = self.tables_list.currentItem().text()
        self.table_name_label.setText(my_table)
        self.error_permission.setText("")
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

        self.cursor_user.execute(f'''SELECT * FROM check_access_table(\'{my_table}\', \'{curr_user_DF[0][0]}\')''')
        access_bool = self.cursor_user.fetchall()
        print("ACCESS_BOOL =", access_bool[0][0])
        if access_bool[0][0] == 1:
            self.error_permission.setText("Access denied")
            return
        if access_bool[0][0] == 0:
            pass

        # Using search boxes
        DBhelper.fill_search_boxes(my_table, self.table_comboBox1, self.table_comboBox2, self.help_label,
                                   self.cursor_user)
        DBhelper.full_fill_table(self.tableWidget, my_table, self.cursor_user)

        file_selected_table = open('selectedTable.txt', 'w')
        file_selected_table.write('' + my_table + '')
        file_selected_table.close()

    # Filling table widget with correct data after using search box
    def FillTableSearch(self):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

        user_combo_box1 = self.table_comboBox1.currentText()
        user_combo_box2 = self.table_comboBox2.currentText()

        DBhelper.check_and_run_search_boxes(user_combo_box1, user_combo_box2, self.tableWidget, self.cursor_user)

    # To edit form function
    def GoToEditForm(self, username, password):
        edit = EditDataForm(username, password)
        widget.addWidget(edit)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        for row in curr_user_DF:
            self.cursor_user.execute(f'''DELETE FROM "public".current_user_logon WHERE
                                    "username" = \'{row[0]}\'''')
        self.cursor_user.close()
        self.connection_user.close()
        print("Connection in DATA_FORM closed!")

# Change or add data form ----------------------------------------------------------------------------------------------


class EditDataForm(QDialog):
    def __init__(self, username, password):
        super(EditDataForm, self).__init__()
        loadUi("DataEditForm.ui", self)

        self.my_close = False
        self.username = username
        self.password = password
        try:
            self.connection_user = psycopg2.connect(user=username,
                                                    password=password,
                                                    host="127.0.0.1",
                                                    port="5432",
                                                    database="GuideCompanies")
            self.cursor_userEdit = self.connection_user.cursor()

            self.cursor_userEdit.execute(f'''SELECT CURRENT_USER''')
            global curr_user_EDF
            curr_user_EDF = self.cursor_userEdit.fetchall()
            for row in curr_user_EDF:
                self.cursor_userEdit.execute(f'''INSERT INTO "public".current_user_logon ("username")
                                                    VALUES (\'{row[0]}\')''')
                self.cursor_userEdit.execute(f'''commit''')
                print("Current user: ", row[0])

            print("Success connect to EDIT_DATA_FORM by " + username + "!")
        except (Exception, Error) as error:
            print("Error connect to EDIT_DATA_FORM " + username + "!", error)

        # Show all editing elements after success connect
        DBhelper.starting_show_edit_things(self.textEdit1, self.textEdit2, self.textEdit3, self.textEdit4,
                                           self.textEdit5, self.textEdit6, self.box_foreign_points1,
                                           self.box_foreign_points2, self.box_foreign_points3,
                                           self.title_one, self.title_two, self.title_three, self.title_four,
                                           self.title_five, self.title_six, self.title_seven, self.title_eight,
                                           self.title_nine, self.title_ten, self.dateTimeEdit, self.cursor_userEdit,
                                           self.calendarWidget)

        self.tableWidget_editform.clear()
        self.gobackButton_editform.clicked.connect(lambda: self.GoBackToDataForm(username, password))
        self.addButton.clicked.connect(self.AddFunction)

        file_last_login = open('lastLogin.txt', 'r')
        self.logged_in_username_editform.setText(file_last_login.readline())
        file_last_login.close()

        widget.setFixedWidth(1280)
        widget.setFixedHeight(900)

        file_selected_table = open('selectedTable.txt', 'r')
        my_table = file_selected_table.readline()
        self.current_table.setText(my_table)
        file_selected_table.close()

        DBhelper.full_fill_table(self.tableWidget_editform, my_table, self.cursor_userEdit)

        self.tableWidget_editform.cellChanged.connect(self.check_change)
        self.tableWidget_editform.doubleClicked.connect(self.on_click)

    # Function for setting values of selected data and calendar display for changing time data
    def on_click(self):
        global my_table
        global row_index
        global column_name
        global previous_cell
        global point
        my_table = self.current_table.text()
        row_index = self.tableWidget_editform.currentItem().row()
        colum_index = self.tableWidget_editform.currentItem().column()
        column_name = DBhelper.redefinition_column(colum_index, my_table)
        previous_cell = str(self.tableWidget_editform.currentItem().text())
        point = 0

        if column_name == 'Date_of_the_order':
            self.calendarWidget.show()
            self.calendarWidget.clicked.connect(self.updated_date)
            return

        if previous_cell.isdigit():
            point += 2
            self.calendarWidget.hide()
            return

        match_one = re.search('\d+', '' + previous_cell + '')
        if match_one:
            point += 1
            self.calendarWidget.hide()
            return

        else:
            self.calendarWidget.hide()
            point = 0

        self.calendarWidget.hide()

    # Updating date by calendar
    def updated_date(self):
        date = self.calendarWidget.selectedDate()
        my_date = date.toString("yyyy-MM-dd")
        self.tableWidget_editform.currentItem().setText(my_date)

    # Function for checking data integrity using regular expressions.
    # (It is recommended to use triggers or built-in integrity checking functions for more correct operation)
    def check_change(self):
        cell = self.tableWidget_editform.currentItem().text()

        print("\nSelected cell's row: ", row_index)
        print("Selected cell's column ", column_name)
        print("Selected point to check changing: ", point)

        if point == 0:
            match1 = re.fullmatch(r'[a-zA-Z\s]+', r'' + cell + '')
            match2 = re.fullmatch(r'\d{4}-\d{2}-\d{2}', r'' + cell + '')
            print(match2)
            if match1 or match2:
                print('Correct change!')
                DBhelper.update_psql_table(row_index, column_name, my_table, cell, self.cursor_userEdit)
                self.calendarWidget.hide()
            else:
                DBhelper.drop_message_box("Error when changing. There is an invalid character in the table cell!")
                self.tableWidget_editform.currentItem().setText(previous_cell)
                return

        if point == 1:
            match = re.fullmatch(r'[0-9a-zA-Z\s]+', r'' + cell + '')
            if match:
                print('Correct change!')
                DBhelper.update_psql_table(row_index, column_name, my_table, cell, self.cursor_userEdit)
            else:
                DBhelper.drop_message_box("Error when changing. There is an invalid character in the table cell!")
                self.tableWidget_editform.currentItem().setText(previous_cell)
                return

        if point == 2:
            match = re.fullmatch(r'[0-9]+', r'' + cell + '')
            if match:
                print('Correct change!')
                DBhelper.update_psql_table(row_index, column_name, my_table, cell, self.cursor_userEdit)
            else:
                DBhelper.drop_message_box("Error when changing. There is an invalid character in the table cell!")
                self.tableWidget_editform.currentItem().setText(previous_cell)
                return

    # Go back to data form
    def GoBackToDataForm(self, username, password):
        back = DataForm(username, password)
        widget.addWidget(back)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        for row in curr_user_EDF:
            self.cursor_userEdit.execute(f'''DELETE FROM "public".current_user_logon WHERE
                                    "username" = \'{row[0]}\'''')
        self.cursor_userEdit.close()
        self.connection_user.close()
        print("Connection in EDIT_DATA_FORM closed!")

    # Adding new data to table (for each table)
    def AddFunction(self):
        my_table = self.current_table.text()
        if my_table == 'country':
            new_title_country = self.textEdit1.toPlainText()
            self.cursor_userEdit.execute(f'''select add_country_except('{new_title_country}');''')
            print('Added new COUNTRY!')

        if my_table == 'company':
            new_title_company = self.textEdit1.toPlainText()
            new_year = self.textEdit2.toPlainText()
            new_name = self.textEdit3.toPlainText()
            new_number = self.textEdit4.toPlainText()
            new_foreign_key_country = self.box_foreign_points1.currentText()
            f_k = DBhelper.formate_str_from_box(new_foreign_key_country)
            self.cursor_userEdit.execute(f'''INSERT INTO "public".company ("Title", "Year_of_foundation", "Full_name_of_the_founder",
                            "Work_phone_number", "Country_ID")
                            VALUES('{new_title_company}', {new_year}, '{new_name}', {new_number}, 
                            '''+f_k+''');''')
            print('Added new COMPANY!')

        if my_table == 'region_of_sale':
            new_title_region = self.textEdit1.toPlainText()
            new_tax = self.textEdit2.toPlainText()
            self.cursor_userEdit.execute(f'''INSERT INTO "public".region_of_sale ("Title", "Tax")
                                    VALUES('{new_title_region}', {new_tax});''')
            print('Added new REGION!')

        if my_table == 'client':
            new_name = self.textEdit1.toPlainText()
            new_phone = self.textEdit2.toPlainText()
            self.cursor_userEdit.execute(f'''INSERT INTO "public".client ("Full_name", "Telephone")
                                    VALUES('{new_name}', {new_phone});''')
            print('Added new CLIENT!')

        if my_table == 'product':
            new_title_product = self.textEdit1.toPlainText()
            new_series = self.textEdit2.toPlainText()
            new_number = self.textEdit3.toPlainText()
            new_manufacturer = self.textEdit4.toPlainText()
            new_certification = self.textEdit5.toPlainText()
            new_product_type = self.textEdit6.toPlainText()
            new_foreign_key_region = self.box_foreign_points1.currentText()
            f_k = DBhelper.formate_str_from_box(new_foreign_key_region)
            self.cursor_userEdit.execute(f'''INSERT INTO "public".product ("Title", "Series", "Number", "Manufacturer",
                                    "Certification", "Product_Type", "Region_ID")
                                    VALUES('{new_title_product}', {new_series}, {new_number}, '{new_manufacturer}', 
                                    {new_certification}, '{new_product_type}', '''+f_k+''');''')
            print('Added new PRODUCT!')

        if my_table == 'company_and_product':
            new_foreign_key_company = self.box_foreign_points1.currentText()
            f_k1 = DBhelper.formate_str_from_box(new_foreign_key_company)

            new_foreign_key_product = self.box_foreign_points2.currentText()
            f_k2 = DBhelper.formate_str_from_box(new_foreign_key_product)

            self.cursor_userEdit.execute(f'''INSERT INTO "public".company_and_product ("Company_ID", "Product_ID")
                                    VALUES('''+f_k1+''', '''+f_k2+''');''')
            print('Added new COMPANY_AND_PRODUCT!')

        if my_table == 'cheque':
            new_order = self.textEdit1.toPlainText()
            new_foreign_key_client_id = self.box_foreign_points1.currentText()
            f_k1 = DBhelper.formate_str_from_box(new_foreign_key_client_id)

            new_foreign_key_company_id = self.box_foreign_points2.currentText()
            f_k2 = DBhelper.formate_str_from_box(new_foreign_key_company_id)

            new_foreign_key_product_id = self.box_foreign_points3.currentText()
            f_k3 = DBhelper.formate_str_from_box(new_foreign_key_product_id)

            new_date_time = self.dateTimeEdit.text()
            self.cursor_userEdit.execute(f'''INSERT INTO "public".cheque ("Date_of_the_order", 
                                    "Order_amount", "Client_ID", "Company_ID", "Product_ID")
                                    VALUES('{new_date_time}', {new_order}, '''+f_k1+''', 
                                            '''+f_k2+''', '''+f_k3+''');''')
            print('Added new CHEQUE!')
        self.cursor_userEdit.execute(f'''commit''')


app = QApplication(sys.argv)
startWindow = Login()
widget = QtWidgets.QStackedWidget()
widget.addWidget(startWindow)
widget.setWindowTitle("PSQL GUI")
widget.setWindowIcon(QtGui.QIcon('snake.png'))
widget.setFixedWidth(800)
widget.setFixedHeight(700)
widget.show()
app.exec_()
