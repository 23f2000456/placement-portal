from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from backend import db
from backend.models import User, Company, Student

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),
        role='student'
    )
    db.session.add(user)
    db.session.flush()  

    student = Student(
        user_id=user.id,
        full_name=data['full_name'],
        branch=data.get('branch'),
        cgpa=data.get('cgpa'),
        graduation_year=data.get('graduation_year'),
        phone=data.get('phone')
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"}), 201


@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json()

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),
        role='company'
    )
    db.session.add(user)
    db.session.flush()

    company = Company(
        user_id=user.id,
        company_name=data['company_name'],
        hr_contact=data.get('hr_contact'),
        website=data.get('website'),
        industry=data.get('industry'),
        location=data.get('location')
    )
    db.session.add(company)
    db.session.commit()

    return jsonify({"message": "Company registered. Awaiting admin approval."}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not check_password_hash(user.password, data.get('password', '')):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    if user.role == 'company':
        company = Company.query.filter_by(user_id=user.id).first()
        if company.approval_status != 'approved':
            return jsonify({"error": "Company not yet approved by admin"}), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return jsonify({
        "access_token": token,
        "role": user.role,
        "email": user.email
    }), 200

from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils import role_required

@auth_bp.route('/dashboard/admin', methods=['GET'])
@role_required('admin')
def admin_dashboard():
    return jsonify({"message": "Welcome Admin", "user_id": get_jwt_identity()})


@auth_bp.route('/dashboard/company', methods=['GET'])
@role_required('company')
def company_dashboard():
    return jsonify({"message": "Welcome Company", "user_id": get_jwt_identity()})


@auth_bp.route('/dashboard/student', methods=['GET'])
@role_required('student')
def student_dashboard():
    return jsonify({"message": "Welcome Student", "user_id": get_jwt_identity()})
