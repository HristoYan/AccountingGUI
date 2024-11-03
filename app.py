import pendulum
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import apology, login_required, get_period_info, expenses_visualization, get_all_expenses, \
    get_criteria_info, db
from models.log_in import UserLog
from models.expense import Expense

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# create_db()
# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///db/accounting.db")
db.execute("CREATE TABLE IF NOT EXISTS "
           "users(id INTEGER UNIQUE,"
           "first_name TEXT, "
           "last_name TEXT, "
           "age INTEGER, "
           "email TEXT, "
           "money INTEGER, "
           "password TEXT, "
           "PRIMARY KEY(id))")

db.execute("CREATE TABLE IF NOT EXISTS "
           "expense(id INTEGER UNIQUE, "
           "user_id INTEGER, "
           "amount INTEGER, "
           "type TEXT, "
           "category TEXT, "
           "time NUMERIC, "
           "PRIMARY KEY(id), "
           "FOREIGN KEY(user_id) REFERENCES users(id))")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Show starting page"""

    return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        age = int(request.form.get("age"))
        email = request.form.get("email")
        money = int(request.form.get("money"))
        password = generate_password_hash(request.form.get("password"))

        # Ensure username was submitted
        if not first_name:
            return apology("must provide First name", 400)

        elif not last_name:
            return apology("must provide Last Name", 400)

        elif not age:
            return apology("must provide Age", 400)

        elif not email:
            return apology("must provide Email", 400)

        elif not money:
            return apology("must provide Money", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide Password", 400)

        # Ensure password and confirmation match
        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        # Ensure that the email is free
        check_email = db.execute("SELECT email FROM users WHERE email=?", email)

        if check_email:
            return apology("This Email is already taken", 400)

        user = UserLog(first_name, last_name, age, email, money, password)

        # Insert username in database
        db.execute("INSERT INTO users (first_name, last_name, age, email, money, password) "
                   "VALUES (?, ?, ?, ?, ?, ?)", user.first_name, user.last_name, user.age,
                   user.email, user.money, user._password)

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # Ensure username was submitted
        if not email:
            return apology("must provide Email", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["first_name"] = rows[0]["first_name"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/add_money", methods=["GET", "POST"])
@login_required
def add_money():
    """Buy shares of stock"""

    if request.method == "POST":
        #  checking for a problem with input info
        try:
            money_to_add = int(request.form.get("money"))

        except ValueError as e:
            return apology(f"The money must be a positive integer. {e}", 400)

        if money_to_add < 1 or money_to_add is None:
            return apology("The money must be a positive integer")

        try:
            money_to_the_bank = db.execute("SELECT money FROM users WHERE id=?", session["user_id"])
            print(money_to_the_bank[0]['money'])
        except ValueError as e:
            return apology(f"The money must be a positive integer. {e}", 400)
        total = money_to_add + int(money_to_the_bank[0]['money'])

        db.execute('UPDATE users SET money=? WHERE id=?', total, session['user_id'])

        print("Successfully added money to your account.")
        return redirect("/")

    else:
        return render_template("add_money.html")


categories = ['Utilities', 'Transportation', 'Loan and interest payments', 'Insurance', 'Gifts', 'Travel expenses',
              'Education', 'Clothing', 'Rent or mortgage', 'Maintenance and repairs', 'Legal expenses',
              'Medical Health', 'Professional services', 'Saving, investing, & debt payments', 'Fun', 'Food']


@app.route("/spend", methods=["GET", "POST"])
@login_required
def spend():
    """Sell shares of stock"""

    money_to_spend = db.execute("SELECT money FROM users WHERE id=?", session['user_id'])[0]['money']

    if request.method == 'POST':

        try:
            category = request.form.get('category')
            try:
                amount = int(request.form.get('amount'))
            except:
                return apology("The amount must be a positive integer", 400)

            if amount < 1:
                return apology("The amount must be a positive integer")

        except:
            return apology('Both fields are required!', 403)

        if amount > money_to_spend:
            return apology("You don't have enough money to spend", 401)

        if amount < 0:
            return apology('Money must be a positive integer', 402)

        total = money_to_spend - amount

        db.execute('UPDATE users SET money=? WHERE id=?', total, session["user_id"])

        if amount < 100:
            expense_type = 'low'
        elif 100 <= amount < 1000:
            expense_type = 'mid'
        else:
            expense_type = 'expensive'
        expense = Expense(amount, expense_type, category)
        db.execute("INSERT INTO expense (user_id, amount, type, category, time) "
                   "VALUES (?, ?, ?, ?, ?)", session['user_id'], expense.spend_amount,
                   expense.type_of_expense, expense.category, expense.time)

        return redirect("/")

    else:
        return render_template("spend.html", categories=categories)


sorting_criteria = ['Date', 'Period', 'Category', 'Max in Category',
                    'Min in Category', 'Max in Period', 'Min in Period', 'Statistics']


@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    """Show history of expenses"""
    print(request.method)

    expense_info = []
    all_info = []
    criteria = 'All'
    if request.method == 'POST':
        criteria = request.form.get('criteria')

        if criteria == 'Date':
            return render_template("date.html")

        elif criteria == 'Period':
            return render_template("period.html")

        elif criteria == 'Category':
            return render_template("category.html", categories=categories)

        elif criteria == 'Max in Category':
            dict_info = get_criteria_info()

            all_info = []
            for cat, expenses in dict_info.items():
                max_expense = max(expenses, key=lambda d: d['amount'])
                all_info.append(max_expense)

        elif criteria == 'Min in Category':
            dict_info = get_criteria_info()

            all_info = []
            for cat, expenses in dict_info.items():
                max_expense = min(expenses, key=lambda d: d['amount'])
                all_info.append(max_expense)
        elif criteria == 'Max in Period':
            return render_template("maxperiod.html", criteria=criteria)

        elif criteria == 'Min in Period':
            return render_template("minperiod.html", criteria=criteria)
        elif criteria == 'Statistics':
            stat_info, total = stats()
            return render_template("statistics.html", stat_info=stat_info, total=total)
        else:
            expense_info = get_all_expenses()
            all_info = expenses_visualization(expense_info)
    else:
        print('IN ELSE: ')
        expense_info = get_all_expenses()

        all_info = expenses_visualization(expense_info)

    return render_template("expenses.html", info=all_info, criteria=sorting_criteria)


@app.route('/date', methods=['GET', 'POST'])
@login_required
def by_date():
    print('In Date: ')
    if request.method == 'POST':
        date = request.form.get('date')
        date_var = get_all_expenses()
        all_info = []
        for row in date_var:
            dtc = pendulum.parse(str(date))
            dtc_str = f'{dtc.year}-{dtc.month}-{dtc.day}'
            row_date = pendulum.parse(str(row['time']))
            row_date_str = f'{row_date.year}-{row_date.month}-{row_date.day}'
            if dtc_str == row_date_str:
                all_info.append(row)

        return render_template("expenses.html", info=all_info, criteria=sorting_criteria)
    else:
        redirect('/date.html')


@app.route('/period', methods=['GET', 'POST'])
@login_required
def by_period(criteria=None):
    print('In Period: ')
    if request.method == 'POST':
        start_date = pendulum.parse(request.form.get('start_date')).timestamp()
        end_date = pendulum.parse(request.form.get('end_date')).add(days=1).timestamp()
        all_info = get_period_info(start_date, end_date)

        return render_template("expenses.html", info=all_info, criteria=sorting_criteria)
    else:
        redirect('/period.html')


@app.route('/category', methods=['GET', 'POST'])
@login_required
def category():
    print('In Category: ')
    if request.method == 'POST':
        category_var = request.form.get('category')
        expense_info = db.execute('SELECT * FROM expense WHERE user_id=? AND category=?',
                                  session['user_id'], category_var)
        all_info = expenses_visualization(expense_info)

        return render_template("expenses.html", info=all_info, criteria=sorting_criteria)
    else:
        redirect('/category.html', categories=categories) # noqa


@app.route('/maxperiod', methods=['GET', 'POST'])
@login_required
def by_maxperiod():
    print('In MaxPeriod: ')
    if request.method == 'POST':
        start_date = pendulum.parse(request.form.get('start_date')).timestamp()
        end_date = pendulum.parse(request.form.get('end_date')).add(days=1).timestamp()
        all_info = get_period_info(start_date, end_date)
        max_info = []
        max_expense = max(all_info, key=lambda d: d['amount'])
        max_info.append(max_expense)
        print(max_info)
        return render_template("expenses.html", info=max_info, criteria=sorting_criteria)
    else:
        redirect('/maxperiod.html')


@app.route('/minperiod', methods=['GET', 'POST'])
@login_required
def by_minperiod():
    print('In MaxPeriod: ')
    if request.method == 'POST':
        start_date = pendulum.parse(request.form.get('start_date')).timestamp()
        end_date = pendulum.parse(request.form.get('end_date')).add(days=1).timestamp()
        all_info = get_period_info(start_date, end_date)
        min_info = []
        min_expense = min(all_info, key=lambda d: d['amount'])
        min_info.append(min_expense)
        print(min_info)
        return render_template("expenses.html", info=min_info, criteria=sorting_criteria)
    else:
        redirect('/minperiod.html')


@app.route('/stats', methods=['post'])
@login_required
def stats():
    all_info = get_all_expenses()
    all_money_spent = sum(info['amount'] for info in all_info)
    print(f"Total money spent: {all_money_spent}")
    category_totals = {}
    cat_total = []
    for info in all_info:
        category = info['category']
        amount = info['amount']

        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

    for category, total in category_totals.items():
        temp = ({'category': category, 'total': total})
        cat_total.append(temp)
    print(cat_total)
    return cat_total, all_money_spent

