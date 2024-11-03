import pendulum
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from functools import wraps

db = SQL("sqlite:///db/accounting.db")


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_all_expenses():
    """Returning user's all expenses"""
    return db.execute('SELECT * FROM expense WHERE user_id=?', session['user_id'])


def expenses_visualization(rows: list[dict]):
    all_info = []
    for row in rows:
        info = {'amount': row['amount'], 'type': row['type'], 'category': row['category'], 'time': row['time']}

        all_info.append(info)

    return all_info


def get_criteria_info():
    all_expenses = get_all_expenses()
    dict_info = {}

    for expense in all_expenses:
        temp = expense['category']
        if temp not in dict_info:
            dict_info[temp] = [expense]
        else:
            dict_info[temp].append(expense)

    return dict_info


def get_period_info(start_date, end_date):
    date_var = get_all_expenses()
    all_info = []
    for row in date_var:
        row_date = pendulum.parse(row['time']).timestamp()
        if start_date <= row_date <= end_date:
            all_info.append(row)

    return all_info
