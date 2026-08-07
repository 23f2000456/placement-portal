from flask import Blueprint, jsonify
from backend.models import User, Company, Student, Job, Application
from backend.utils import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard_stats():
    return jsonify({
        "total_students": Student.query.count(),
        "total_companies": Company.query.count(),
        "total_job_postings": Job.query.count(),
        "total_applications": Application.query.count()
    })

from flask import request
from backend import db
from backend.models import User, Company, Student, Job, Application


@admin_bp.route('/companies', methods=['GET'])
@role_required('admin')
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
    return jsonify({"message": f"Company {company.company_name} approved"})


@admin_bp.route('/companies/<int:company_id>/reject', methods=['PATCH'])
@role_required('admin')
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'rejected'
    db.session.commit()
    return jsonify({"message": f"Company {company.company_name} rejected"})


@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PATCH'])
@role_required('admin')
def blacklist_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted  # toggle on/off
    db.session.commit()
    status = "blacklisted" if company.is_blacklisted else "un-blacklisted"
    return jsonify({"message": f"Company {company.company_name} {status}"})


@admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@role_required('admin')
def remove_company(company_id):
    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)
    db.session.delete(company)
    if user:
        db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Company removed"})

@admin_bp.route('/jobs', methods=['GET'])
@role_required('admin')
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
    return jsonify({"message": f"Job '{job.job_title}' approved"})


@admin_bp.route('/jobs/<int:job_id>/reject', methods=['PATCH'])
@role_required('admin')
def reject_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = 'closed'
    db.session.commit()
    return jsonify({"message": f"Job '{job.job_title}' closed"})


@admin_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@role_required('admin')
def remove_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job posting removed"})


@admin_bp.route('/applications', methods=['GET'])
@role_required('admin')
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


@admin_bp.route('/students/<int:student_id>/blacklist', methods=['PATCH'])
@role_required('admin')
def blacklist_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    status = "blacklisted" if student.is_blacklisted else "un-blacklisted"
    return jsonify({"message": f"Student {student.full_name} {status}"})


@admin_bp.route('/students/<int:student_id>/deactivate', methods=['PATCH'])
@role_required('admin')
def deactivate_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = "deactivated" if not user.is_active else "reactivated"
    return jsonify({"message": f"Student {student.full_name} {status}"})

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