from backend import db
from datetime import datetime, timezone

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin company student
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(150))
    approval_status = db.Column(db.String(20), default="pending")
    is_blacklisted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='company_profile')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    graduation_year = db.Column(db.Integer)
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    is_blacklisted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='student_profile')

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)
    skills_required = db.Column(db.Text)
    salary = db.Column(db.Float)
    eligible_branches = db.Column(db.String(255))
    min_cgpa = db.Column(db.Float, default=0.0)
    eligible_year = db.Column(db.Integer)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending  approved  closed
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    company = db.relationship('Company', backref='job_positions')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_position_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)    
    application_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    status = db.Column(db.String(20), default="applied")  # applied  shortlisted  selected  rejected

    __table_args__= (db.UniqueConstraint('student_id', 'job_position_id'),)

    student = db.relationship('Student', backref='applications')
    job_position = db.relationship('Job', backref='applications')

class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    position = db.Column(db.String(150))
    final_salary = db.Column(db.Float)
    joining_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    application = db.relationship('Application', backref=db.backref('placement', uselist=False))