from datetime import datetime, timedelta, timezone
from backend import celery, mail, db
from backend.models import Application
from flask_mail import Message


@celery.task(name='backend.tasks.reminders.send_interview_reminders')
def send_interview_reminders():
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)

    upcoming = Application.query.filter(
        Application.interview_datetime >= start,
        Application.interview_datetime <= end,
        Application.status == 'interview'
    ).all()

    for app in upcoming:
        student_email = app.student.user.email
        msg = Message(
            subject="Interview Reminder - Placement Portal",
            recipients=[student_email],
            body=f"""
Hi {app.student.full_name},

This is a reminder that you have an interview scheduled tomorrow.

Company: {app.job_position.company.company_name}
Position: {app.job_position.job_title}
Time: {app.interview_datetime.strftime('%Y-%m-%d %H:%M')}

Best of luck!
Placement Portal Team
            """
        )
        mail.send(msg)

    return f"Sent {len(upcoming)} interview reminders"