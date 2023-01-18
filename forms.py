from datetime import date
from wtforms import Form, IntegerField, RadioField, StringField, PasswordField, SelectField, DateField, validators

# Login Form
class LoginForm(Form):
    email = StringField("Email", validators=[validators.length(min=8, max=50),
                                             validators.Email(message="Please enter a valid email")])
    password = PasswordField("Password", validators=[
        validators.data_required(message="Please enter a password")])

# Registration Form
class RegistrationForm(Form):
    role = SelectField("Role", choices=[('admin', 'Admin'), ('client', 'Client')],
                         validators=[validators.data_required(message="Please select your gender")],
                         render_kw={"onclick": "roleSelected()"})
    office = StringField("Office")                     
    email = StringField("Email", validators=[validators.length(min=8, max=50),
                                             validators.Email(message="Please enter a valid email")])
    first_name = StringField("First name", validators=[validators.length(min=2, max=50), validators.data_required(
        message="Please enter your first name")])
    last_name = StringField("Last name", validators=[validators.length(min=2, max=50),
                                                     validators.data_required(message="Please enter your last name")])
    gender = SelectField("Gender", choices=[('female', 'Female'), ('male', 'Male')],
                         validators=[validators.data_required(message="Please select your gender")])
    birth_date = DateField("Birth date", format='%Y-%m-%d',
                           validators=[validators.data_required(message="Please enter your birth date")])
    password = PasswordField("Password", validators=[
        validators.data_required(message="Please type a password"),
        validators.equal_to(fieldname="confirm", message="Passwords not matching")])
    confirm = PasswordField("Re-enter your password")

# Book Appointment Form
class BookAppointmentForm(Form):
    field_of_work = SelectField("Field of Work", validators=[validators.data_required(message="Please select a field of work")])
    date = DateField("Date", format='%Y-%m-%d', default=date.today,
                     validators=[
                         validators.data_required(
                             message="Please enter a starting date to look for an appointment")])
    time = SelectField("Time", choices=[('morning', 'Morning'), ('afternoon', 'Afternoon')], validators=[validators.data_required(message="Please select a time")])
    description = StringField("Specific work to be done", validators=[validators.length(min=2, max=255), validators.data_required(
        message="Please describe the work to be done")])
    estimated_time = IntegerField('Estimated Time (hours) (Optional)')
    materials_status = RadioField('Status of Materials', choices=[('available', 'Available'), ('unavailable', 'Unavailable')], default='available')

# Worker Form
class WorkerForm(Form):
    first_name = StringField("First name", validators=[validators.length(min=2, max=50), validators.data_required(
        message="Please enter your first name")])
    last_name = StringField("Last name", validators=[validators.length(min=2, max=50),
                                                     validators.data_required(message="Please enter your last name")])
    field_of_work = SelectField("Field of Work", validators=[validators.data_required(message="Please select a field of work")]) 

# Approve Form
class ApproveAppointmentForm(Form):
    worker = SelectField("Worker", validators=[validators.data_required(message="Please select a field of work")])                                                    