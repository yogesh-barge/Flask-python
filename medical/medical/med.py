from flask import Flask, render_template, request, redirect, url_for, make_response,jsonify
import mysql.connector as mysql
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle




from reportlab.lib import colors



app = Flask(__name__)
# Establish a connection to the MySQL database
mydatabase = mysql.connect(
    host="localhost",
    user="root",
    password="Shahjah",
    database="medical_shop_db"
)
cur = mydatabase.cursor()
users = {
    "Admin": "Medical",
    "admin": "medical"
}



# Route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            # Redirect to dashboard or home page upon successful login
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password. Please try again."
    return render_template("login.html", error=error)

# Route for dashboard or home page
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# In-memory data storage
items = []

@app.route("/")
def index():
    return render_template("index.html")

# Route to display all items
@app.route("/items")
def display_items():
    cur = mydatabase.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    print(items)
    cur.close()

    return render_template("items.html",items=items )

# Route to add a new item
@app.route("/items/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":

        data = request.form
        item = {
            "id": len(items) + 1,
            "name": data["name"],
            "price": float(data["price"]),
            "quantity": int(data["quantity"])
        }

        items.append(item)
        cur = mydatabase.cursor()
        cur.execute("INSERT INTO items (name, price, quantity) VALUES (%s, %s, %s)", (data['name'], float(data['price']), int(data['quantity'])))
        mydatabase.commit()
        cur.close()
        return redirect(url_for('display_items'))
    return render_template("add_item.html")

## Route to edit an existing item
@app.route("/items/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    # Establish a cursor to interact with the database
    cur = mydatabase.cursor()

    # If the request method is POST, update the item details in the database
    if request.method == "POST":
        data = request.form
        name = data["name"]
        price = float(data["price"])
        quantity = int(data["quantity"])
        # Execute the SQL UPDATE statement to update the item details
        cur.execute("UPDATE items SET name = %s, price = %s, quantity = %s WHERE id = %s", (name, price, quantity, item_id))
        # Commit the transaction to apply changes
        mydatabase.commit()
        # Close the cursor
        cur.close()
        # Redirect to the display_items route to refresh the items list
        return redirect(url_for('display_items'))

    # If the request method is GET, fetch the item details from the database
    # Execute the SQL SELECT statement to fetch the item details
    cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
    # Fetch the item details from the database
    item = cur.fetchone()
    # Close the cursor
    cur.close()

    # Render the edit_item.html template with the item details
    return render_template("edit_item.html", item=item)

## Route to delete an item
@app.route("/items/delete/<int:item_id>")
def delete_item(item_id):
    # Establish a cursor to interact with the database
    cur = mydatabase.cursor()

    # Execute the SQL DELETE statement to delete the item with the given item_id
    cur.execute("DELETE FROM items WHERE id = %s", (item_id,))

    # Commit the transaction to apply changes
    mydatabase.commit()

    # Close the cursor
    cur.close()

    # Redirect to the display_items route to refresh the items list
    return redirect(url_for('display_items'))

# Function to fetch data from the database
def fetch_data_from_database():
    #conn = mysql.connect('medical_shop_db')
    cursor = mydatabase .cursor()
    cursor.execute('SELECT name, quantity, price FROM items')
    items = cursor.fetchall()
    cursor.close()
    return items

# Function to calculate the total amount
def calculate_total(items):
    total = sum(item[1] * item[2] for item in items)
    return total

# Function to generate PDF bill
def generate_pdf_bill(items, total_amount):
    # Create PDF document
    pdf = SimpleDocTemplate("bill.pdf", pagesize=letter)

    # Define table data
    data = [['Item', 'Quantity', 'Price', 'Total']]
    for item in items:
        data.append([item[0], str(item[1]), str(item[2]), str(item[1] * item[2])])

    # Add total amount to data
    data.append(['', '', '', 'Total Amount: ' + str(total_amount)])

    # Create table
    table = Table(data)

    # Style table
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),
                        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0))])

    table.setStyle(style)

    # Build PDF
    pdf.build([table])

# Route to generate the PDF bill
@app.route('/items/generate_bill')
def generate_pdf_bill_route():
    items = fetch_data_from_database()
    total_amount = calculate_total(items)
    generate_pdf_bill(items, total_amount)

    # Serve the generated PDF
    with open("bill.pdf", "rb") as f:
        response = make_response(f.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=bill.pdf'
        return response
# #
# @app.route('/items/customer', methods=["GET", "POST"])
# def enterdetails():
#      return render_template("enter_customerdetails.html")
#
# # Flask route to add a customer
# @app.route('/items/customer/details', methods=["POST"])
# def add_customer():
#     if request.method == "POST":
#         name = request.form['name']
#         phone = request.form['phone']
#         medname = request.form['medname']
#         cquantity = int(request.form['cquantity'])
#
#         # Insert customer into database
#         cur.execute("INSERT INTO customer (name, phone, medname,cquantity) VALUES (%s, %s, %s,%s)", (name, phone, medname,cquantity))
#         mydatabase.commit()
#         print("Customer added successfully")
#
#         # Fetch item data from the database
#         cur.execute("SELECT quantity, id FROM items WHERE name = %s", (medname,))
#         item_data = cur.fetchone()
#         if len(item_data)>0:
#             item_quantity = item_data[0]
#             item_id = item_data[1]
#             if item_quantity < cquantity:
#                 return "Insufficient quantity available"
#             updated_quantity = item_quantity - cquantity
#             cur.execute("UPDATE items SET quantity = %s WHERE id = %s", (updated_quantity, item_id))
#             mydatabase.commit()
#         else:
#             return "Item not found"
#
#         # Fetch updated item list from the database
#         cur.execute("SELECT * FROM items")
#         items = cur.fetchall()
#         cur.close()
#         return render_template("items.html",items=items)  # Redirect to the display_items route
#
#
#
#




if __name__ == "__main__":
    app.run(debug=True)
