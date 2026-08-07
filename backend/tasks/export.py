import csv
import os
from datetime import datetime, timezone
from backend import celery, mail, db
from backend.models import Application, Student
from flask_mail import Message


@celery.task(name='backend.tasks.export.export_applications_csv', bind=True)
def export_applications_csv(self, student_id):
    student = Student.query.get(student_id)
    apps = Application.query.filter_by(student_id=student_id).all()

    filename = f"applications_student_{student_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.csv"
    filepath = os.path.join('/tmp', filename)

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Application Date'])
        for a in apps:
            writer.writerow([
                student.id,
                a.job_position.company.company_name,
                a.job_position.job_title,
                a.status,
                a.application_date.strftime('%Y-%m-%d') if a.application_date else ''
            ])

    # Email the CSV to the student
    student_email = student.user.email
    msg = Message(
        subject="Your Application History Export",
        recipients=[student_email],
        body=f"Hi {student.full_name}, your application history CSV is attached."
    )
    with open(filepath, 'rb') as f:
        msg.attach(filename, 'text/csv', f.read())
    mail.send(msg)

    os.remove(filepath)
    return {"status": "done", "file": filename}