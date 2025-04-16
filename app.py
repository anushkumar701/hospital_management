import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'secretkey123'

# Set the absolute path for the database
database_path = os.path.join('C:/DISK D/hospital_management', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(50))  # admin, doctor, receptionist, patient

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    ailment = db.Column(db.String(150), nullable=False)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    date = db.Column(db.String(20), nullable=False)

    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for(f'dashboard_{user.role}'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard_admin')
@login_required
def dashboard_admin():
    if current_user.role != 'admin':
        return "Access Denied"
    return render_template('dashboard_admin.html')

@app.route('/dashboard_doctor')
@login_required
def dashboard_doctor():
    if current_user.role != 'doctor':
        return "Access Denied"
    return render_template('dashboard_doctor.html')

@app.route('/dashboard_receptionist')
@login_required
def dashboard_receptionist():
    if current_user.role != 'receptionist':
        return "Access Denied"
    return render_template('dashboard_receptionist.html')

@app.route('/dashboard_patient')
@login_required
def dashboard_patient():
    if current_user.role != 'patient':
        return "Access Denied"
    return render_template('dashboard_patient.html')

# --- Patient Management ---
@app.route('/admin/patients')
@login_required
def manage_patients():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

@app.route('/admin/patients/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        ailment = request.form['ailment']
        new_patient = Patient(name=name, age=age, gender=gender, ailment=ailment)
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for('manage_patients'))
    return render_template('add_patient.html')

# --- Doctor Management ---
@app.route('/admin/doctors')
@login_required
def manage_doctors():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/admin/doctors/add', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        new_doctor = Doctor(name=name, specialization=specialization)
        db.session.add(new_doctor)
        db.session.commit()
        return redirect(url_for('manage_doctors'))
    return render_template('add_doctor.html')

# --- Appointment Management Routes ---
@app.route('/admin/appointments')
@login_required
def manage_appointments():
    if current_user.role != 'admin' and current_user.role != 'receptionist':
        return redirect(url_for('home'))
    
    appointments = Appointment.query.all()  # Get all appointments
    return render_template('appointments.html', appointments=appointments)

@app.route('/admin/appointments/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    if current_user.role != 'admin' and current_user.role != 'receptionist':
        return redirect(url_for('home'))
    
    patients = Patient.query.all()  # Get all patients
    doctors = Doctor.query.all()  # Get all doctors
    
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        
        new_appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id, date=date)
        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Appointment successfully created!', 'success')  # Flash success message
        return redirect(url_for('manage_appointments'))
    
    return render_template('add_appointment.html', patients=patients, doctors=doctors)

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)
