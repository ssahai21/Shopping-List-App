"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

mydb=mysql.connector.connect(host="localhost", user="root", password="1890644", database="mydatabase")
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS shoplist (item VARCHAR(255), category VARCHAR(255))")

mycursor.execute("SELECT * FROM shoplist")
rows = mycursor.fetchall()


# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app



def fetch_items():
    mycursor.execute("SELECT * FROM shoplist")
    rows = mycursor.fetchall()
    return [{"item": row[0], "category": row[1]} for row in rows]

@app.route('/')
def home():
    items = fetch_items()
    return render_template("home.html",list=items)

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':        
        new_name = request.form.get('item')
        new_category = request.form.get('category')
        
        if new_name and new_category:
            sql = "INSERT INTO shoplist (item, category) VALUES (%s, %s)"
            val = (new_name, new_category)
            mycursor.execute(sql, val)
            mydb.commit()
        return redirect("/")

    return render_template("add.html")

@app.route('/edit/<item_name>', methods=['GET','POST'])
def edit(item_name):
    items = fetch_items()
    item = next((item for item in items if item['item'] == item_name), None)
    
    if request.method == 'POST':
        new_name = request.form['item']
        new_category = request.form['category']
        if item:
            sql = "UPDATE shoplist SET item = %s, category = %s WHERE item = %s"
            val = (new_name, new_category, item_name)
            mycursor.execute(sql, val)
            mydb.commit()
        return redirect("/")
    

    return render_template("edit.html",item=item)

@app.route('/delete/<item_name>', methods=['GET','POST'])
def delete(item_name):
    items = fetch_items()
    item = next((item for item in items if item['item'] == item_name), None)
    if item is None:
        # If the item is not found, redirect to home or show an error message
        return redirect("/")
    if request.method == 'POST':
        sql = "DELETE FROM shoplist WHERE item = %s"
        val = (item_name,)
        mycursor.execute(sql, val)
        mydb.commit()
        return redirect("/")

    return render_template("delete.html",item=item)

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
