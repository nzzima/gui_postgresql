from PyQt5 import  QtGui
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from psycopg2 import Error


def full_fill_table(table_widget, myTable, new_cursor):
    new_cursor.execute(f'''SELECT column_name FROM information_schema.columns
                            WHERE table_name = \'''' + myTable + '''\'
                            ORDER BY ORDINAL_POSITION;''')
    result_header = new_cursor.fetchall()

    table_widget.setColumnCount(len(result_header))

    i = 0
    for row in result_header:
        for item in row:
            temp = QTableWidgetItem()
            temp.setText(item)
            table_widget.setHorizontalHeaderItem(i, temp)
        i += 1

    if myTable == 'country':
        new_cursor.execute(f'''SELECT * FROM "public".''' + myTable + ''' ORDER BY "Country_ID";''')
    if myTable == 'company':
        new_cursor.execute(f'''select * from return_cursor_company();
                               fetch all from _result;''')
    if myTable == 'region_of_sale':
        new_cursor.execute(f'''SELECT * FROM "public".''' + myTable + ''' ORDER BY "Region_ID";''')
    if myTable == 'client':
        new_cursor.execute(f'''select * from return_t_clients();''')
    if myTable == 'product':
        new_cursor.execute(f'''SELECT * FROM "public".''' + myTable + ''' ORDER BY "Product_ID";''')
    if myTable == 'cheque':
        new_cursor.execute(f'''SELECT * FROM "public".''' + myTable + ''' ORDER BY "Cheque_ID";''')
    if myTable == 'company_and_product':
        new_cursor.execute(f'''SELECT * FROM "public".''' + myTable + ''' ORDER BY "Company_ID";''')
    if myTable == 'users':
        new_cursor.execute(f'''SELECT * FROM "public".''' + myTable + ''';''')
    if myTable == 'audit_user_log':
        new_cursor.execute(f'''SELECT * FROM "public".''' + myTable + ''';''')
    if myTable == 'lock_audit':
        new_cursor.execute(f'''SELECT * FROM "public".''' + myTable + ''';''')
    if myTable == 'current_user_logon':
        new_cursor.execute(f'''SELECT * FROM "public".''' + myTable + ''';''')

    result_table = new_cursor.fetchall()

    for row, form in enumerate(result_table):
        table_widget.insertRow(row)
        for column, item in enumerate(form):
            table_widget.setItem(row, column, QTableWidgetItem(str(item)))


def simple_fill_table(table_widget, result):
    for row, form in enumerate(result):
        table_widget.insertRow(row)
        for column, item in enumerate(form):
            table_widget.setItem(row, column, QTableWidgetItem(str(item)))


def fill_search_boxes(current_table, combo_box1, combo_box2, help, new_cursor):
    help.setText("")
    combo_box1.clear()
    combo_box2.clear()
    if current_table == "country":
        help.setText("Choose range")

        new_cursor.execute(f'''SELECT "Country_ID" FROM "public".country;''')
        result_country_id = new_cursor.fetchall()
        combo_box1.addItems([str(e) for e in range(1, len(result_country_id) + 1)])
        combo_box2.addItems([str(e) for e in range(1, len(result_country_id) + 1)])

    if current_table == "company":
        help.setText("Choose >year and >id")
        combo_box1.addItems(['1950', '1960', '1970', '1980', '1990', '2000', '2010', '2020'])

        new_cursor.execute(f'''SELECT "Company_ID" FROM "public".company;''')
        result_company_id = new_cursor.fetchall()
        combo_box2.addItems([str(e) for e in range(1, len(result_company_id) + 1)])

    if current_table == "client":
        help.setText("Choose >first")

        new_cursor.execute(f'''SELECT "Client_ID" FROM "public".client;''')
        result_client_id = new_cursor.fetchall()
        combo_box1.addItems([str(e) for e in range(1, len(result_client_id) + 1)])

    if current_table == "company_and_product":
        help.setText("Choose Product_ID")

        new_cursor.execute(f'''SELECT "Product_ID" FROM "public".product;''')
        result_product_id = new_cursor.fetchall()
        combo_box1.addItems([str(e) for e in range(1, len(result_product_id) + 1)])

    if current_table == "cheque":
        help.setText("Choose range sum of order")
        combo_box1.addItems(['100', '300', '500', '1000', '2000'])
        combo_box2.addItems(['200', '400', '600', '1100', '2500'])

    if current_table == "region_of_sale":
        help.setText("Choose >first")

        new_cursor.execute(f'''SELECT "Region_ID" FROM "public".region_of_sale;''')
        result_region_id = new_cursor.fetchall()
        combo_box1.addItems([str(e) for e in range(1, len(result_region_id) + 1)])

    if current_table == "product":
        help.setText("Choose Manufacturer and ProductType")
        combo_box1.addItems(['NVIDIA', 'AMD', 'MSI', 'ASUS'])
        combo_box2.addItems(['Video card', 'Motherboard', 'Screen'])


def check_and_run_search_boxes(text_box1, text_box2, table_widget, new_cursor):
    file_selected_table = open('selectedTable.txt', 'r')
    my_table = file_selected_table.readline()
    file_selected_table.close()

    new_cursor.execute(f'''SELECT column_name FROM information_schema.columns
                                WHERE table_name = \'''' + my_table + '''\'
                                ORDER BY ORDINAL_POSITION;''')
    result_header = new_cursor.fetchall()
    table_widget.setColumnCount(len(result_header))

    i = 0
    for row in result_header:
        for item in row:
            temp = QTableWidgetItem()
            temp.setText(item)
            table_widget.setHorizontalHeaderItem(i, temp)
        i += 1

    if my_table == 'country':
        new_cursor.execute(f'''SELECT * FROM country_dynamic_search('"Country_ID" BETWEEN '''+text_box1+''' AND '''+text_box2+'''');''')
        user_result = new_cursor.fetchall()
        simple_fill_table(table_widget, user_result)

    if my_table == 'company':
        new_cursor.execute(f'''SELECT * FROM company_dynamic_search('"Year_of_foundation" > '''+text_box1+''' AND "Company_ID" > '''+text_box2+'''');''')
        user_result = new_cursor.fetchall()
        simple_fill_table(table_widget, user_result)

    if my_table == 'client':
        new_cursor.execute(f'''SELECT * FROM "public".'''+my_table+''' 
                        WHERE "Client_ID" > '''+text_box1+''';''')
        user_result = new_cursor.fetchall()
        simple_fill_table(table_widget, user_result)

    if my_table == 'company_and_product':
        new_cursor.execute(f'''SELECT * FROM "public".'''+my_table+''' 
                        WHERE "Product_ID" = '''+text_box1+''';''')
        user_result = new_cursor.fetchall()
        simple_fill_table(table_widget, user_result)

    if my_table == 'cheque':
        new_cursor.execute(f'''SELECT * FROM "public".'''+my_table+''' 
                        WHERE "Order_amount" BETWEEN '''+text_box1+''' AND '''+text_box2+''';''')
        user_result = new_cursor.fetchall()
        simple_fill_table(table_widget, user_result)

    if my_table == 'region_of_sale':
        new_cursor.execute(f'''SELECT * FROM "public".'''+my_table+''' 
                        WHERE "Region_ID" > '''+text_box1+''';''')
        user_result = new_cursor.fetchall()
        simple_fill_table(table_widget, user_result)

    if my_table == 'product':
        new_cursor.execute(f'''SELECT * FROM product_dynamic_search('"Manufacturer" = \'\''''+text_box1+'''\'\' AND "Product_Type" = \'\''''+text_box2+'''\'\'');''')
        user_result = new_cursor.fetchall()
        simple_fill_table(table_widget, user_result)


def update_psql_table(row_ind, column_name, updating_table, updating_info, new_cursor):
    row_ind = row_ind + 1
    if updating_table == 'country':
        try:
            new_cursor.execute(f'BEGIN;')
            new_cursor.execute(f'SELECT * FROM "public".{updating_table} FOR UPDATE NOWAIT;')
            new_cursor.execute(f'''UPDATE "public".{updating_table} SET "{column_name}" = '{updating_info}' 
                    WHERE "Country_ID" = {row_ind};''')
            new_cursor.execute(f'''commit''')
        except (Exception, Error) as error:
            drop_message_box("Oops, someone is already updating this table. Just wait...")
            print("Oops, someone is already updating this table. Just wait...", error)

    if updating_table == 'company':
        try:
            new_cursor.execute(f'BEGIN;')
            new_cursor.execute(f'SELECT * FROM "public".{updating_table} FOR UPDATE NOWAIT;')
            new_cursor.execute(f'''UPDATE "public".{updating_table} SET "{column_name}" = '{updating_info}' 
                    WHERE "Company_ID" = {row_ind};''')
            new_cursor.execute(f'''commit''')
        except (Exception, Error) as error:
            drop_message_box("Oops, someone is already updating this table. Just wait...")
            print("Oops, someone is already updating this table. Just wait...", error)

    if updating_table == 'region_of_sale':
        try:
            new_cursor.execute(f'BEGIN;')
            new_cursor.execute(f'SELECT * FROM "public".{updating_table} FOR UPDATE NOWAIT;')
            new_cursor.execute(f'''UPDATE "public".{updating_table} SET "{column_name}" = '{updating_info}' 
                    WHERE "Region_ID" = {row_ind};''')
            new_cursor.execute(f'''commit''')
        except (Exception, Error) as error:
            drop_message_box("Oops, someone is already updating this table. Just wait...")
            print("Oops, someone is already updating this table. Just wait...", error)

    if updating_table == 'product':
        try:
            new_cursor.execute(f'BEGIN;')
            new_cursor.execute(f'SELECT * FROM "public".{updating_table} FOR UPDATE NOWAIT;')
            new_cursor.execute(f'''UPDATE "public".{updating_table} SET "{column_name}" = '{updating_info}' 
                    WHERE "Product_ID" = {row_ind};''')
            new_cursor.execute(f'''commit''')
        except (Exception, Error) as error:
            drop_message_box("Oops, someone is already updating this table. Just wait...")
            print("Oops, someone is already updating this table. Just wait...", error)

    if updating_table == 'client':
        try:
            new_cursor.execute(f'BEGIN;')
            new_cursor.execute(f'SELECT * FROM "public".{updating_table} FOR UPDATE NOWAIT;')
            new_cursor.execute(f'''UPDATE "public".{updating_table} SET "{column_name}" = '{updating_info}' 
                    WHERE "Client_ID" = {row_ind};''')
            new_cursor.execute(f'''commit''')
        except (Exception, Error) as error:
            drop_message_box("Oops, someone is already updating this table. Just wait...")
            print("Oops, someone is already updating this table. Just wait...", error)

    if updating_table == 'cheque':
        try:
            new_cursor.execute(f'BEGIN;')
            new_cursor.execute(f'SELECT * FROM "public".{updating_table} FOR UPDATE NOWAIT;')
            new_cursor.execute(f'''UPDATE "public".{updating_table} SET "{column_name}" = '{updating_info}' 
                        WHERE "Cheque_ID" = {row_ind};''')
            new_cursor.execute(f'''commit''')
        except (Exception, Error) as error:
            drop_message_box("Oops, someone is already updating this table. Just wait...")
            print("Oops, someone is already updating this table. Just wait...", error)


def redefinition_column (column, table):
    if table == 'country':
        if column == 0:
            redef_col = 'Country_ID'
        if column == 1:
            redef_col = 'Title'
    if table == 'region_of_sale':
        if column == 0:
            redef_col = 'Region_ID'
        if column == 1:
            redef_col = 'Title'
        if column == 2:
            redef_col = 'Tax'
    if table == 'company_and_product':
        if column == 0:
            redef_col = 'Company_ID'
        if column == 1:
            redef_col = 'Product_ID'
    if table == 'company':
        if column == 0:
            redef_col = 'Company_ID'
        if column == 1:
            redef_col = 'Title'
        if column == 2:
            redef_col = 'Year_of_foundation'
        if column == 3:
            redef_col = 'Full_name_of_the_founder'
        if column == 4:
            redef_col = 'Work_phone_number'
        if column == 5:
            redef_col = 'Country_ID'
    if table == 'product':
        if column == 0:
            redef_col = 'Product_ID'
        if column == 1:
            redef_col = 'Title'
        if column == 2:
            redef_col = 'Series'
        if column == 3:
            redef_col = 'Number'
        if column == 4:
            redef_col = 'Manufacturer'
        if column == 5:
            redef_col = 'Certification'
        if column == 6:
            redef_col = 'Product_Type'
        if column == 7:
            redef_col = 'Region_ID'
    if table == 'cheque':
        if column == 0:
            redef_col = 'Cheque_ID'
        if column == 1:
            redef_col = 'Date_of_the_order'
        if column == 2:
            redef_col = 'Order_amount'
        if column == 3:
            redef_col = 'Client_ID'
        if column == 4:
            redef_col = 'Company_ID'
        if column == 5:
            redef_col = 'Product_ID'
    if table == 'client':
        if column == 0:
            redef_col = 'Client_ID'
        if column == 1:
            redef_col = 'Full_name'
        if column == 2:
            redef_col = 'Telephone'

    return redef_col


def starting_show_edit_things(form1, form2, form3, form4, form5, form6, combo_box1, combo_box2, combo_box3,
                              title1, title2, title3, title4, title5, title6, title7, title8, title9, title10,
                              date_time_form, new_cursor, calendar):
    form1.hide()
    form2.hide()
    form3.hide()
    form4.hide()
    form5.hide()
    form6.hide()
    combo_box1.hide()
    combo_box2.hide()
    combo_box3.hide()
    date_time_form.hide()
    calendar.hide()

    file_selected_table = open('selectedTable.txt', 'r')
    my_table = file_selected_table.readline()
    file_selected_table.close()

    if my_table == 'country':
        form1.show()
        title1.setText("Title")

    if my_table == 'company':
        form1.show()
        form2.show()
        form3.show()
        form4.show()

        combo_box1.show()
        new_cursor.execute(f'''SELECT "Country_ID" FROM "public".country;''')
        result_country_id = new_cursor.fetchall()
        new_cursor.execute(f'''SELECT "Title" FROM "public".country;''')
        result_country_name = new_cursor.fetchall()

        result = [str(e) for e in range(1, len(result_country_id) + 1)]

        i = 0
        while i < len(result_country_id):
            for row in result_country_name:
                result[i] += " ("
                result[i] += row[0]
                result[i] += ")"
                i += 1

        combo_box1.addItems(result)

        title1.setText("Title")
        title2.setText("Year_of_foundation")
        title3.setText("Full_name_of_the_founder")
        title4.setText("Phone_number")
        title7.setText("Country_ID")

    if my_table == 'client':
        form1.show()
        form2.show()
        title1.setText("Full_name")
        title2.setText("Telephone")

    if my_table == 'cheque':
        date_time_form.show()
        date_time_form.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        form1.show()

        combo_box1.show()
        new_cursor.execute(f'''SELECT "Client_ID" FROM "public".client;''')
        result_client_id = new_cursor.fetchall()
        new_cursor.execute(f'''SELECT "Full_name" FROM "public".client;''')
        result_client_name = new_cursor.fetchall()

        result = [str(e) for e in range(1, len(result_client_id) + 1)]

        i = 0
        while i < len(result_client_id):
            for row in result_client_name:
                result[i] += " ("
                result[i] += row[0]
                result[i] += ")"
                i += 1

        combo_box1.addItems(result)

        combo_box2.show()
        new_cursor.execute(f'''SELECT "Company_ID" FROM "public".company;''')
        result_comp_id = new_cursor.fetchall()
        new_cursor.execute(f'''SELECT "Title" FROM "public".company;''')
        result_comp_title = new_cursor.fetchall()

        result = [str(e) for e in range(1, len(result_comp_id) + 1)]

        i = 0
        while i < len(result_comp_id):
            for row in result_comp_title:
                result[i] += " ("
                result[i] += row[0]
                result[i] += ")"
                i += 1

        combo_box2.addItems(result)

        combo_box3.show()
        new_cursor.execute(f'''SELECT "Product_ID" FROM "public".product;''')
        result_prod_id = new_cursor.fetchall()
        new_cursor.execute(f'''SELECT "Title" FROM "public".product;''')
        result_prod_title = new_cursor.fetchall()

        result = [str(e) for e in range(1, len(result_prod_id) + 1)]

        i = 0
        while i < len(result_prod_id):
            for row in result_prod_title:
                result[i] += " ("
                result[i] += row[0]
                result[i] += ")"
                i += 1

        combo_box3.addItems(result)

        title10.setText("Date_and_time")
        title1.setText("Order_amount")
        title7.setText("Client_ID")
        title8.setText("Company_ID")
        title9.setText("Product_ID")

    if my_table == 'region_of_sale':
        form1.show()
        form2.show()
        title1.setText("Title")
        title2.setText("Tax")

    if my_table == 'product':
        form1.show()
        form2.show()
        form3.show()
        form4.show()
        form5.show()
        form6.show()

        combo_box1.show()
        new_cursor.execute(f'''SELECT "Region_ID" FROM "public".region_of_sale;''')
        result_region_id = new_cursor.fetchall()
        new_cursor.execute(f'''SELECT "Title" FROM "public".region_of_sale;''')
        result_region_title = new_cursor.fetchall()

        result = [str(e) for e in range(1, len(result_region_id) + 1)]

        i = 0
        while i < len(result_region_id):
            for row in result_region_title:
                result[i] += " ("
                result[i] += row[0]
                result[i] += ")"
                i += 1

        combo_box1.addItems(result)

        title1.setText("Title")
        title2.setText("Series")
        title3.setText("Number")
        title4.setText("Manufacturer")
        title5.setText("Certification")
        title6.setText("Product_Type")
        title7.setText("Region_ID")

    if my_table == 'company_and_product':
        combo_box1.show()
        new_cursor.execute(f'''SELECT "Company_ID" FROM "public".company;''')
        result_company_id = new_cursor.fetchall()
        new_cursor.execute(f'''SELECT "Title" FROM "public".company;''')
        result_company_title = new_cursor.fetchall()

        result = [str(e) for e in range(1, len(result_company_id) + 1)]

        i = 0
        while i < len(result_company_id):
            for row in result_company_title:
                result[i] += " ("
                result[i] += row[0]
                result[i] += ")"
                i += 1

        combo_box1.addItems(result)

        combo_box2.show()
        new_cursor.execute(f'''SELECT "Product_ID" FROM "public".product;''')
        result_product_id = new_cursor.fetchall()
        new_cursor.execute(f'''SELECT "Title" FROM "public".product;''')
        result_product_title = new_cursor.fetchall()

        result = [str(e) for e in range(1, len(result_product_id) + 1)]

        i = 0
        while i < len(result_product_id):
            for row in result_product_title:
                result[i] += " ("
                result[i] += row[0]
                result[i] += ")"
                i += 1

        combo_box2.addItems(result)

        title7.setText("Company_ID")
        title8.setText("Product_ID")


def formate_str_from_box(in_str):
    var = in_str.partition(' ')[0]
    return var


def drop_message_box(info_text):
    msg = QMessageBox()
    msg.setWindowTitle("INFO")
    msg.setWindowIcon(QtGui.QIcon("info.png"))
    msg.setText(info_text)
    msg.exec()