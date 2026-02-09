import os
import pandas as pd
from flask import Flask, render_template, request, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "library_secret"

# ---------- EXCEL AUTO CREATE ----------
def create_register():
    if not os.path.exists('register.xlsx'):
        pd.DataFrame(columns=[
            "Username", "Password", "Role"
        ]).to_excel('register.xlsx', index=False)

def create_forgot():
    if not os.path.exists('forgot_password.xlsx'):
        pd.DataFrame(columns=[
            "Username", "Old Password", "New Password", "Date"
        ]).to_excel('forgot_password.xlsx', index=False)


def create_library():
    if not os.path.exists('library.xlsx'):
        pd.DataFrame(
            columns=["Book ID", "Title", "Author", "Quantity"]
        ).to_excel('library.xlsx', index=False)

def create_users():
    if not os.path.exists('users.xlsx'):
        pd.DataFrame({
            "username": ["admin", "student"],
            "password": ["admin123", "stud123"],
            "role": ["admin", "student"]
        }).to_excel('users.xlsx', index=False)

def create_issue_history():
    if not os.path.exists('issue_history.xlsx'):
        pd.DataFrame(
            columns=["Book ID", "Book Name", "User", "Issue Date", "Return Date"]
        ).to_excel('issue_history.xlsx', index=False)

create_library()
create_users()
create_issue_history()
create_register()
create_forgot()


# ---------- LOGIN ----------

# ---------- ROUTES ----------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        df = pd.read_excel('register.xlsx')

        df.loc[len(df)] = [
            request.form['username'],
            request.form['password'],
            request.form['role']
        ]

        df.to_excel('register.xlsx', index=False)

        # also add to users.xlsx (for login)
        users = pd.read_excel('users.xlsx')
        users.loc[len(users)] = [
            request.form['username'],
            request.form['password'],
            request.form['role']
        ]
        users.to_excel('users.xlsx', index=False)

        return redirect('/')

    return render_template('register.html')
@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method == 'POST':
        users = pd.read_excel('users.xlsx')
        uname = request.form['username']
        new_pass = request.form['new_password']

        old_pass = users.loc[users.username==uname, 'password'].values[0]

        users.loc[users.username==uname, 'password'] = new_pass
        users.to_excel('users.xlsx', index=False)

        log = pd.read_excel('forgot_password.xlsx')
        log.loc[len(log)] = [
            uname, old_pass, new_pass, datetime.now()
        ]
        log.to_excel('forgot_password.xlsx', index=False)

        return redirect('/')

    return render_template('forgot_password.html')


@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        users = pd.read_excel('users.xlsx')
        u = request.form['username']
        p = request.form['password']
        user = users[(users.username==u) & (users.password==p)]
        if not user.empty:
            session['user'] = u
            session['role'] = user.iloc[0]['role']
            return redirect('/admin' if session['role']=='admin' else '/student')
        return "Invalid Login"
    return render_template('login.html')


@app.route('/admin')
def admin():
    return render_template('dashboard_admin.html')


@app.route('/student')
def student():
    return render_template('dashboard_student.html')


@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        df = pd.read_excel('library.xlsx')
        df.loc[len(df)] = [
            request.form['id'],
            request.form['title'],
            request.form['author'],
            request.form['qty']
        ]
        df.to_excel('library.xlsx', index=False)
        return redirect('/books')
    return render_template('add_book.html')


@app.route('/books')
def books():
    df = pd.read_excel('library.xlsx')
    return render_template(
        'view_books.html',
        books=df.to_dict(orient='records')
    )


@app.route('/issue', methods=['GET','POST'])
def issue():
    if request.method == 'POST':
        df = pd.read_excel('library.xlsx')
        bid = int(request.form['id'])
        df.loc[df['Book ID']==bid, 'Quantity'] -= 1
        df.to_excel('library.xlsx', index=False)
        return redirect('/books')
    return render_template('issue_book.html')


@app.route('/return', methods=['GET','POST'])
def return_book():
    if request.method == 'POST':
        df = pd.read_excel('library.xlsx')
        bid = int(request.form['id'])
        df.loc[df['Book ID']==bid, 'Quantity'] += 1
        df.to_excel('library.xlsx', index=False)
        return redirect('/books')
    return render_template('return_book.html')


@app.route('/issue-history')
def issue_history():
    df = pd.read_excel('issue_history.xlsx')
    return render_template(
        'issue_history.html',
        data=df.to_dict(orient='records')
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

