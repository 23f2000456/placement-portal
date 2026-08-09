from flask import Blueprint, jsonify, request
from backend import db, cache
from backend.models import User, Company, Student, Job, Application
from backend.utils import role_required
from backend.tasks.reminders import send_interview_reminders
from backend.tasks.reports import send_monthly_report
from backend.tasks.export import export_applications_csv

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def clear_cache():
    cache.clear()


@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
@cache.cached(timeout=30)
def dashboard_stats():
    return jsonify({
        "total_students": Student.query.count(),
        "total_companies": Company.query.count(),
        "total_job_postings": Job.query.count(),
        "total_applications": Application.query.count()
    })


@admin_bp.route('/companies', methods=['GET'])
@role_required('admin')
@cache.cached(timeout=60, query_string=True)
def list_companies():
    search = request.args.get('search', '')
    query = Company.query
    if search:
        query = query.filter(
            (Company.company_name.ilike(f'%{search}%')) |
            (Company.industry.ilike(f'%{search}%'))
        )
    companies = query.all()
    return jsonify([{
        "id": c.id,
        "company_name": c.company_name,
        "industry": c.industry,
        "location": c.location,
        "approval_status": c.approval_status,
        "is_blacklisted": c.is_blacklisted
    } for c in companies])


@admin_bp.route('/companies/<int:company_id>/approve', methods=['PATCH'])
@role_required('admin')
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'approved'
    db.session.commit()
    clear_cache()
    return jsonify({"message": f"Company {company.company_name} approved"})


@admin_bp.route('/companies/<int:company_id>/reject', methods=['PATCH'])
@role_required('admin')
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'rejected'
    db.session.commit()
    clear_cache()
    return jsonify({"message": f"Company {company.company_name} rejected"})


@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PATCH'])
@role_required('admin')
def blacklist_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    clear_cache()
    status = "blacklisted" if company.is_blacklisted else "un-blacklisted"
    return jsonify({"message": f"Company {company.company_name} {status}"})

@admin_bp.route('/companies/<int:company_id>/deactivate', methods=['PATCH'])
@role_required('admin')
def deactivate_company(company_id):
    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)
    user.is_active = not user.is_active
    db.session.commit()
    clear_cache()
    status = "deactivated" if not user.is_active else "reactivated"
    return jsonify({"message": f"Company {company.company_name} {status}"})


@admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@role_required('admin')
def remove_company(company_id):
    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)

    # Delete in correct order to avoid constraint errors
    jobs = Job.query.filter_by(company_id=company.id).all()
    for job in jobs:
        Application.query.filter_by(job_position_id=job.id).delete()
        db.session.delete(job)

    db.session.delete(company)
    if user:
        db.session.delete(user)

    db.session.commit()
    clear_cache()
    return jsonify({"message": "Company removed"})


@admin_bp.route('/companies/<int:company_id>/applications', methods=['GET'])
@role_required('admin')
def view_company_applications(company_id):
    company = Company.query.get_or_404(company_id)
    jobs = Job.query.filter_by(company_id=company.id).all()
    return jsonify({
        "company_name": company.company_name,
        "jobs": [{
            "job_id": j.id,
            "job_title": j.job_title,
            "status": j.status,
            "applications": [{
                "application_id": a.id,
                "student_name": a.student.full_name,
                "status": a.status
            } for a in j.applications]
        } for j in jobs]
    })


@admin_bp.route('/jobs', methods=['GET'])
@role_required('admin')
@cache.cached(timeout=60)
def list_jobs():
    jobs = Job.query.all()
    return jsonify([{
        "id": j.id,
        "company_id": j.company_id,
        "company_name": j.company.company_name,
        "job_title": j.job_title,
        "status": j.status,
        "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None
    } for j in jobs])


@admin_bp.route('/jobs/<int:job_id>/approve', methods=['PATCH'])
@role_required('admin')
def approve_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = 'approved'
    db.session.commit()
    clear_cache()
    return jsonify({"message": f"Job '{job.job_title}' approved"})


@admin_bp.route('/jobs/<int:job_id>/reject', methods=['PATCH'])
@role_required('admin')
def reject_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = 'closed'
    db.session.commit()
    clear_cache()
    return jsonify({"message": f"Job '{job.job_title}' closed"})


@admin_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@role_required('admin')
def remove_job(job_id):
    job = Job.query.get_or_404(job_id)
    Application.query.filter_by(job_position_id=job.id).delete()
    db.session.delete(job)
    db.session.commit()
    clear_cache()
    return jsonify({"message": "Job posting removed"})


@admin_bp.route('/applications', methods=['GET'])
@role_required('admin')
@cache.cached(timeout=60)
def list_applications():
    apps = Application.query.all()
    return jsonify([{
        "id": a.id,
        "student_id": a.student_id,
        "student_name": a.student.full_name,
        "job_id": a.job_position_id,
        "job_title": a.job_position.job_title,
        "status": a.status,
        "application_date": a.application_date.isoformat() if a.application_date else None
    } for a in apps])


@admin_bp.route('/students', methods=['GET'])
@role_required('admin')
@cache.cached(timeout=60, query_string=True)
def list_students():
    search = request.args.get('search', '')
    query = Student.query
    if search:
        query = query.filter(
            (Student.full_name.ilike(f'%{search}%')) |
            (Student.phone.ilike(f'%{search}%')) |
            (Student.id == search if search.isdigit() else False)
        )
    students = query.all()
    return jsonify([{
        "id": s.id,
        "full_name": s.full_name,
        "branch": s.branch,
        "cgpa": s.cgpa,
        "phone": s.phone,
        "is_blacklisted": s.is_blacklisted
    } for s in students])


@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@role_required('admin')
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    apps = Application.query.filter_by(student_id=student.id).all()
    return jsonify({
        "id": student.id,
        "full_name": student.full_name,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "graduation_year": student.graduation_year,
        "skills": student.skills,
        "phone": student.phone,
        "is_blacklisted": student.is_blacklisted,
        "applications": [{
            "application_id": a.id,
            "company_name": a.job_position.company.company_name,
            "job_title": a.job_position.job_title,
            "status": a.status,
            "application_date": a.application_date.isoformat() if a.application_date else None
        } for a in apps]
    })


@admin_bp.route('/students/<int:student_id>/blacklist', methods=['PATCH'])
@role_required('admin')
def blacklist_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    clear_cache()
    status = "blacklisted" if student.is_blacklisted else "un-blacklisted"
    return jsonify({"message": f"Student {student.full_name} {status}"})


@admin_bp.route('/students/<int:student_id>/deactivate', methods=['PATCH'])
@role_required('admin')
def deactivate_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    user.is_active = not user.is_active
    db.session.commit()
    clear_cache()
    status = "deactivated" if not user.is_active else "reactivated"
    return jsonify({"message": f"Student {student.full_name} {status}"})


@admin_bp.route('/trigger/reminders', methods=['POST'])
@role_required('admin')
def trigger_reminders():
    task = send_interview_reminders.delay()
    return jsonify({
        "message": "Interview reminder job triggered.",
        "task_id": task.id
    }), 202


@admin_bp.route('/trigger/monthly-report', methods=['POST'])
@role_required('admin')
def trigger_monthly_report():
    task = send_monthly_report.delay()
    return jsonify({
        "message": "Monthly report generation triggered.",
        "task_id": task.id
    }), 202


@admin_bp.route('/trigger/export/<int:student_id>', methods=['POST'])
@role_required('admin')
def trigger_student_export(student_id):
    student = Student.query.get_or_404(student_id)
    task = export_applications_csv.delay(student.id)
    return jsonify({
        "message": f"CSV export triggered for {student.full_name}.",
        "task_id": task.id
    }), 202


@admin_bp.route('/task-status/<task_id>', methods=['GET'])
@role_required('admin')
def task_status(task_id):
    from backend import celery
    task = celery.AsyncResult(task_id)
    return jsonify({
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    })

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def placement_stats():
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    total_selected = Application.query.filter(
        Application.status.in_(['selected', 'placed'])
    ).count()
    total_shortlisted = Application.query.filter_by(status='shortlisted').count()
    approved_companies = Company.query.filter_by(approval_status='approved').count()
    pending_companies = Company.query.filter_by(approval_status='pending').count()
    approved_jobs = Job.query.filter_by(status='approved').count()
    pending_jobs = Job.query.filter_by(status='pending').count()

    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_selected": total_selected,
        "total_shortlisted": total_shortlisted,
        "approved_companies": approved_companies,
        "pending_companies": pending_companies,
        "approved_jobs": approved_jobs,
        "pending_jobs": pending_jobs,
        "placement_rate": round((total_selected / total_applications * 100), 1) if total_applications > 0 else 0
    })