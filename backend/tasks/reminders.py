from datetime import datetime, timedelta, timezone
from backend import celery, mail
from backend.models import Job, Application, Student, User
from flask_mail import Message


@celery.task(name='backend.tasks.reminders.send_interview_reminders')
def send_interview_reminders():
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Find jobs with deadline tomorrow
    upcoming_jobs = Job.query.filter(
        Job.application_deadline >= start,
        Job.application_deadline <= end,
        Job.status == 'approved'
    ).all()

    sent = 0

    # Find all students who haven't applied yet and notify them
    for job in upcoming_jobs:
        applied_student_ids = [a.student_id for a in job.applications]
        all_students = Student.query.filter_by(is_blacklisted=False).all()

        for student in all_students:
            if student.id not in applied_student_ids:
                user = User.query.get(student.user_id)
                msg = Message(
                    subject="Application Deadline Reminder - Placement Portal",
                    recipients=[user.email],
                    body=f"""
Hi {student.full_name},

This is a reminder that the application deadline for the following placement drive is tomorrow!

Company: {job.company.company_name}
Position: {job.job_title}
Deadline: {job.application_deadline.strftime('%Y-%m-%d')}

Don't miss out — apply now on the Placement Portal.

Best regards,
Placement Portal Team
                    """
                )
                mail.send(msg)
                sent += 1

    return f"Sent {sent} deadline reminders"
