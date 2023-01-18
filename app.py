from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_mysqldb import MySQL
from passlib.handlers.sha2_crypt import sha256_crypt
from forms import ApproveAppointmentForm, BookAppointmentForm, LoginForm, RegistrationForm, WorkerForm
from utils import login_required, check_is_admin, check_is_client
from datetime import datetime

app = Flask(__name__)
app.secret_key = "too_secret_to_reveal"
app.static_folder = 'static'

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "scheduling"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Login page
@app.route('/', methods=["GET", "POST"])
def index():
    form = LoginForm(request.form)
    if "logged_in" in session:
        if session['is_client']:
            return redirect(url_for("my_appointments"))
        if session['is_admin']:
            return redirect(url_for("admin_appointments"))
    if request.method == "POST":
        email = form.email.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        query = "SELECT * FROM user WHERE email = %s"
        result_set = cursor.execute(query, (email,))
        if result_set > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered, real_password):
                user_id = data["id"]
                role = data["role"]
                full_name = data["first_name"] + " " + data["last_name"]

                session["logged_in"] = True
                session["user_id"] = user_id
                session["full_name"] = full_name
                session["email"] = email
                session["is_client"] = check_is_client(user_id, mysql)
                session["is_admin"] = check_is_admin(user_id, mysql)

                if role == 'client':
                    cursor.execute("SELECT office FROM client WHERE user_id = %s", (user_id,))
                    session["office"] = cursor.fetchone()["office"]
                    return redirect(url_for("my_appointments"))
                elif role == 'admin':
                    return redirect(url_for("admin_appointments"))
            else:
                flash("Your password is wrong.", "danger")
                return redirect(url_for("index"))
        else:
            flash("There is no such email has been registered.", "danger")
            return redirect(url_for("index"))
    return render_template("login.html", form=form)

# Register page
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if "logged_in" in session and session["is_admin"]:
        pass
    else:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))

    if request.method == "POST" and form.validate():
        role = form.role.data
        office = form.office.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        gender = form.gender.data
        birth_date = form.birth_date.data
        password = sha256_crypt.hash(form.password.data)

        cursor = mysql.connection.cursor()

        query = "SELECT * FROM user WHERE email = %s"
        same_email = cursor.execute(query, (email,)) > 0

        if same_email:
            flash(message="This email has been registered, if you think there was a mistake then contact us.",
                  category="danger")
            cursor.close()
            return redirect(url_for("register"))

        query = "INSERT INTO user(role, email, password, first_name, last_name, gender, birth_date) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (role, email, password, first_name, last_name, gender, birth_date))
        mysql.connection.commit()

        #Insert the created user to admin/client table
        if role == 'admin':
            query = "INSERT INTO admin(user_id) VALUES(%s)"
        elif role == 'client':
            query = "INSERT INTO client(user_id, office) VALUES(%s, %s)"

        cursor.execute(query, (cursor.lastrowid, office))
        mysql.connection.commit()

        cursor.close()
        flash(message="You have been successfully registered. You may login now.", category="success")
        return redirect(url_for("index"))
    else:
        return render_template("register.html", form=form)

# Appointments -> My Appointments
@app.route('/appointments')
@login_required
def my_appointments():
    if not session["is_client"]:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM client WHERE user_id = %s"
    cursor.execute(query, (session["user_id"],))
    client = cursor.fetchone()
    client_id = client["id"]


    query = """ SELECT appointment.*, field_of_work.name as field_of_work_name, 
                CASE
                    WHEN appointment.worker IS NOT NULL THEN CONCAT(worker.last_name, ', ', worker.first_name)
                    ELSE NULL
                END as worker_fullname
                FROM appointment
                INNER JOIN field_of_work
                ON appointment.field_of_work = field_of_work.id
                LEFT JOIN worker
                ON appointment.worker = worker.id
                WHERE (client_id = %s AND date >= CURRENT_DATE() AND (status != 'done' AND status != 'rejected' AND status != 'cancelled') )"""
    cursor.execute(query, (client_id,))
    upcoming_appointments = cursor.fetchall()

    query = """ SELECT appointment.*, field_of_work.name as field_of_work_name, 
                CASE
                    WHEN appointment.worker IS NOT NULL THEN CONCAT(worker.last_name, ', ', worker.first_name)
                    ELSE NULL
                END as worker_fullname
                FROM appointment
                INNER JOIN field_of_work
                ON appointment.field_of_work = field_of_work.id
                LEFT JOIN worker
                ON appointment.worker = worker.id
                WHERE client_id = %s AND (date < CURRENT_DATE() OR (status = 'done' OR status = 'rejected' OR status = 'cancelled')) """
    cursor.execute(query, (client_id,))
    past_appointments = cursor.fetchall()

    query = """SELECT notification.*, 
                    appointment.id as appointment_id, 
                    appointment.status as appointment_status
                FROM notification
                INNER JOIN appointment
                ON notification.appointment_id = appointment.id
                WHERE appointment.client_id = %s
                ORDER BY status DESC
                LIMIT 5"""
    cursor.execute(query, (client_id,))
    notifications = cursor.fetchall()

    cursor.close()
    return render_template("appointments.html", past_appointments=past_appointments,
                         upcoming_appointments=upcoming_appointments, notifications=notifications)

# Appointments -> Book An Appointment
@app.route('/book-an-appointment', methods=["GET", "POST"])
@login_required
def book_an_appointment():
    if not session["is_client"]:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))
    if request.method == "GET":
        form = BookAppointmentForm(request.form)
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM client WHERE user_id = %s"
        cursor.execute(query, (session["user_id"],))
        client = cursor.fetchone()
        client_id = client["id"]

        # month = datetime.today().month
        # day = datetime.today().day
        # year = datetime.today().year

        query = """ SELECT * FROM appointment
                        WHERE (client_id = %s AND date >= CURRENT_DATE() AND status != 'done')"""
        cursor.execute(query, (client_id,))
        upcoming_appointments = cursor.fetchall()

        if upcoming_appointments:
            flash(message="You have an upcoming appointment, you can get another appointment after that one.",
                  category="danger")
            cursor.close()
            return redirect(url_for("my_appointments"))

        query = "SELECT * FROM field_of_work"
        cursor.execute(query)
        fields_of_work = cursor.fetchall()

        form.field_of_work.choices = [(field_of_work["id"], field_of_work["name"]) for field_of_work in fields_of_work]

        return render_template("book-an-appointment.html", form=form)
    else:
        form = BookAppointmentForm(request.form)
        if request.method == "POST":
            cursor = mysql.connection.cursor()
            field_of_work = form.field_of_work.data
            date = form.date.data
            time = form.time.data
            decsription = form.description.data
            estimated_time = form.estimated_time.data
            materials_status  = form.materials_status.data
            today = datetime.today()
            if today.year >= date.year and today.month >= date.month and today.day >= date.day:
                flash(message="You cannot get an appointment for today and the past days.", category="danger")
                return redirect(url_for("book_an_appointment"))

            query = "SELECT * FROM field_of_work WHERE id = %s"
            cursor.execute(query, (field_of_work,))
            field_of_work = cursor.fetchone()
            field_of_work_id = field_of_work["id"]
            query = "SELECT * FROM client WHERE user_id = %s"
            cursor.execute(query, (session["user_id"],))
            client = cursor.fetchone()
            client_id = client["id"]
            query = "INSERT INTO appointment(field_of_work, client_id, date, time, description, estimated_time, materials_status) VALUES(%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (field_of_work_id, client_id, date, time, decsription, estimated_time, materials_status))
            mysql.connection.commit()
            cursor.close()
            flash(message="Your appointment has been successfully booked", category="success")
            return redirect(url_for("my_appointments"))
        else:
            flash(message="Please fulfill the form", category="danger")
            return redirect(url_for("my_appointments"))

# Appointments -> Cancel Appointment
@app.route('/cancel-appointment', methods=["GET","POST"])
@login_required
def cancel_appointment():
    if not session["is_client"]:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))


    cursor = mysql.connection.cursor()
    query = "UPDATE appointment SET status = 'cancelled' WHERE id = %s"
    cursor.execute(query, (request.args.get('param'),))
    mysql.connection.commit()
    
    # query = "INSERT into notification SET appointment_id = %s, client_id = %s, user_id = %s"
    # cursor.execute(query, (request.args.get('param'),))
    # mysql.connection.commit()

    cursor.close()
    flash(message="Appointment cancelled", category="success")
    return redirect(url_for("my_appointments"))

# Appointments -> Done Appointment
@app.route('/done-appointment', methods=["GET","POST"])
@login_required
def done_appointment():
    if not session["is_client"]:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))


    cursor = mysql.connection.cursor()
    query = "UPDATE appointment SET status = 'done' WHERE id = %s"
    cursor.execute(query, (request.args.get('param'),))
    mysql.connection.commit()

    # query = "INSERT into notification SET appointment_id = %s, client_id = %s, user_id = %s"
    # cursor.execute(query, (request.args.get('param'),))
    # mysql.connection.commit()

    cursor.close()
    flash(message="Appointment marked as done", category="success")
    return redirect(url_for("my_appointments"))

# Appointments -> Approve Appointment
@app.route('/approve-appointment', methods=["GET","POST"])
@login_required
def approve_appointment():
    if not session["is_admin"]:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))

    cursor = mysql.connection.cursor()
    query = "UPDATE appointment SET status = 'approved', worker=%s WHERE id = %s"
    cursor.execute(query, (request.args.get('param2'),request.args.get('param1'),))

    query = "INSERT into notification SET appointment_id = %s, user_id = %s"
    cursor.execute(query, (request.args.get('param1'), session["user_id"]))
    mysql.connection.commit()

    cursor.close()
    flash(message="Appointment marked as approved. Client was already notified.", category="success")
    return redirect(url_for("admin_appointments"))

# Appointments -> Reject Appointment
@app.route('/reject-appointment', methods=["GET","POST"])
@login_required
def reject_appointment():
    if not session["is_admin"]:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))


    cursor = mysql.connection.cursor()
    query = "UPDATE appointment SET status = 'rejected' WHERE id = %s"
    cursor.execute(query, (request.args.get('param1'),))

    query = "INSERT into notification SET appointment_id = %s, user_id = %s"
    cursor.execute(query, (request.args.get('param1'), session["user_id"]))
    mysql.connection.commit()

    cursor.close()
    flash(message="Appointment marked as rejected. Client was already notified.", category="success")
    return redirect(url_for("admin_appointments"))

# Admin Appointment
@app.route('/admin-appointments')
@login_required
def admin_appointments():
    if not session["is_admin"]:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))

    form = ApproveAppointmentForm(request.form)
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM client"
    cursor.execute(query,)


    query = """ SELECT appointment.*, 
                        CONCAT(user.last_name, ', ', user.first_name) as user_fullname,                      
                        client.office as client_office,
                        field_of_work.id as field_of_work_id,
                        field_of_work.name as field_of_work_name, 
                CASE
                    WHEN appointment.worker IS NOT NULL THEN CONCAT(worker.last_name, ', ', worker.first_name)
                    ELSE NULL
                END as worker_fullname
                FROM appointment
                INNER JOIN client
                ON appointment.client_id = client.id
                INNER JOIN user
                ON client.user_id = user.id
                INNER JOIN field_of_work
                ON appointment.field_of_work = field_of_work.id
                LEFT JOIN worker
                ON appointment.worker = worker.id
                WHERE (date >= CURRENT_DATE() AND (status != 'done' AND status != 'rejected' AND status != 'cancelled') )"""
    cursor.execute(query,)
    upcoming_appointments = cursor.fetchall()

    query = """ SELECT appointment.*, 
                        CONCAT(user.last_name, ', ', user.first_name) as user_fullname,
                        client.office as client_office,
                        field_of_work.id as field_of_work_id,
                        field_of_work.name as field_of_work_name, 
                CASE
                    WHEN appointment.worker IS NOT NULL THEN CONCAT(worker.last_name, ', ', worker.first_name)
                    ELSE NULL
                END as worker_fullname
                FROM appointment
                INNER JOIN client
                ON appointment.client_id = client.id
                INNER JOIN user
                ON client.user_id = user.id
                INNER JOIN field_of_work
                ON appointment.field_of_work = field_of_work.id
                LEFT JOIN worker
                ON appointment.worker = worker.id
                WHERE (date < CURRENT_DATE() OR (status = 'done' OR status = 'rejected' OR status = 'cancelled')) """
    cursor.execute(query,)
    past_appointments = cursor.fetchall()

    query = "SELECT * FROM worker"
    cursor.execute(query)
    workers = cursor.fetchall()

    # form.worker.choices = [(worker["id"], worker["last_name"] + ', '+ worker["first_name"]) for worker in workers]

    cursor.close()
    return render_template("admin-appointments.html", past_appointments=past_appointments,
                         upcoming_appointments=upcoming_appointments, form=form, workers=workers, include_script=True)

# Workers
@app.route('/workers')
@login_required
def workers():
    if not session["is_admin"]:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))
    cursor = mysql.connection.cursor()

    query = """ SELECT worker.*, field_of_work.name as field_of_work_name FROM worker
                INNER JOIN field_of_work
                ON worker.field_of_work = field_of_work.id"""
    cursor.execute(query)
    workers = cursor.fetchall()
    print(workers)
    cursor.close()
    return render_template("workers.html", workers=workers)

# Worker
@app.route('/worker', methods=['GET', 'POST'])
def worker():
    form = WorkerForm(request.form)
    if "logged_in" in session and session["is_admin"]:
        pass
    else:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        field_of_work = form.field_of_work.data
        last_name = form.last_name.data
        first_name = form.first_name.data
        cursor = mysql.connection.cursor()

        query = "SELECT * FROM field_of_work WHERE id = %s"
        cursor.execute(query, (field_of_work,))
        field_of_work = cursor.fetchone()
        field_of_work_id = field_of_work["id"]
        query = "INSERT INTO worker(field_of_work, first_name, last_name) VALUES(%s, %s, %s)"
        cursor.execute(query, (field_of_work_id, first_name, last_name))
        mysql.connection.commit()

        cursor.close()
        flash(message="Worker added successfully.", category="success")
        return redirect(url_for("workers"))
    else:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM field_of_work"
        cursor.execute(query)
        fields_of_work = cursor.fetchall()

        form.field_of_work.choices = [(field_of_work["id"], field_of_work["name"]) for field_of_work in fields_of_work]

        return render_template("worker.html", form=form)

# Notification Read
@app.route('/read-notification', methods=["GET","POST"])
@login_required
def read_notification():
    if not session["is_client"]:
        flash("You are not authorized!", "danger")
        return redirect(url_for("index"))


    cursor = mysql.connection.cursor()
    query = "UPDATE notification SET status = 'read' WHERE id = %s"
    cursor.execute(query, (request.args.get('param'),))
    mysql.connection.commit()

    cursor.close()
    return redirect(url_for("my_appointments"))

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run()

