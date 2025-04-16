from werkzeug.security import generate_password_hash
from app import app, db, User

with app.app_context():
    db.create_all()  # This will create the tables in the database

    # Check if the users already exist to avoid duplication
    if not User.query.filter_by(username='admin1').first():
        admin = User(username='admin1', password=generate_password_hash('admin123'), role='admin')
        doctor = User(username='drjohn', password=generate_password_hash('doc123'), role='doctor')
        receptionist = User(username='reception', password=generate_password_hash('rec123'), role='receptionist')
        patient = User(username='patient1', password=generate_password_hash('pat123'), role='patient')

        db.session.add_all([admin, doctor, receptionist, patient])
        db.session.commit()
        print("✅ Users and database created successfully!")
    else:
        print("Database already contains users.")
