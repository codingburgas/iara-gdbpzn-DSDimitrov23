from flask import Blueprint, jsonify, render_template, request, redirect, session
from models import db, User, Vessel, FishingTicket, River, Permit, Inspection, Fine
from sqlalchemy import func
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

bp = Blueprint('main', __name__)

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def json_error(message, status=400):
    return jsonify({'error': message}), status


def parse_json_request():
    data = request.get_json(silent=True)
    if data is None:
        return None, json_error('Invalid JSON payload', 400)
    return data, None


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        username = session.get('username')
        if not username:
            return json_error('Authentication required', 401)

        user = User.query.filter_by(username=username).first()
        if not user:
            session.pop('username', None)
            return json_error('Authentication required', 401)

        return func(*args, current_user=user, **kwargs)
    return wrapper


def authorization_required(target_username, current_user):
    return current_user.username == target_username or current_user.role.lower() == 'admin'


def validate_registration(data):
    if not data.get('username') or not isinstance(data.get('username'), str):
        return 'Потребителското име е задължително.'
    if not data.get('email') or not isinstance(data.get('email'), str) or not EMAIL_REGEX.match(data['email']):
        return 'Въведете валиден имейл адрес.'
    password = data.get('password')
    if not password or not isinstance(password, str) or len(password) < 8:
        return 'Паролата трябва да бъде поне 8 символа.'
    return None


def serialize_user(user):
    return {
        'username': user.username,
        'email': user.email,
        'fullname': user.fullname,
        'phone': user.phone,
        'role': user.role,
        'vessel': user.vessel,
        'permit': user.permit,
        'member_since': user.member_since
    }


@bp.route('/')
def index():
    return redirect('/login')


@bp.route('/dashboard')
def dashboard():
    return render_template('index.html')


@bp.route('/login')
def login_page():
    return render_template('login.html')


@bp.route('/register')
def register_page():
    return render_template('register.html')


@bp.route('/map')
def map_page():
    return render_template('map.html')


@bp.route('/tickets')
def tickets_page():
    return render_template('tickets.html')


@bp.route('/profile')
def profile_page():
    return render_template('profile.html')


@bp.route('/fines')
def fines_page():
    return render_template('fines.html')


@bp.route('/api/tickets')
@require_login
def get_tickets(current_user):
    tickets = FishingTicket.query.order_by(FishingTicket.timestamp.desc()).all()
    return jsonify([
        {
            'id': t.id,
            'ticket_type': t.ticket_type,
            'price': t.price,
            'timestamp': t.timestamp.strftime('%d.%m.%Y %H:%M')
        }
        for t in tickets
    ])


@bp.route('/api/register', methods=['POST'])
def register_user():
    data, error = parse_json_request()
    if error:
        return error

    data['username'] = data['username'].strip() if isinstance(data.get('username'), str) else data.get('username')
    data['email'] = data['email'].strip().lower() if isinstance(data.get('email'), str) else data.get('email')

    validation_error = validate_registration(data)
    if validation_error:
        return json_error(validation_error, 400)

    if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
        return json_error('Потребителското име или имейл вече съществуват.', 400)

    user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=16),
        fullname=data.get('fullname', '—') or '—',
        phone=data.get('phone', '—') or '—',
        role=data.get('role') or 'Любител рибар',
        vessel=data.get('vessel', '—') or '—',
        permit=data.get('permit', '—') or '—'
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'OK'}), 201


@bp.route('/api/login', methods=['POST'])
def login_user():
    data, error = parse_json_request()
    if error:
        return error

    if not data.get('username') or not data.get('password'):
        return json_error('Username and password are required', 400)

    identifier = data['username'].strip()
    user = User.query.filter(
        (User.username == identifier) | (func.lower(User.email) == identifier.lower())
    ).first()
    if not user:
        return json_error('Invalid credentials', 401)

    password_matches = check_password_hash(user.password, data['password'])
    if not password_matches and user.password == data['password']:
        user.password = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=16)
        db.session.commit()
        password_matches = True

    if not password_matches:
        return json_error('Invalid credentials', 401)

    session.clear()
    session['username'] = user.username
    session.permanent = True

    return jsonify({'message': 'OK', 'username': user.username, 'role': user.role})


@bp.route('/api/logout', methods=['POST'])
@require_login
def logout_user(current_user):
    session.clear()
    return jsonify({'message': 'Logged out'})


@bp.route('/api/me')
@require_login
def get_current_user(current_user):
    return jsonify(serialize_user(current_user))


@bp.route('/api/user/<string:username>')
@require_login
def get_user_details(username, current_user):
    if not authorization_required(username, current_user):
        return json_error('Forbidden', 403)

    user = User.query.filter_by(username=username).first()
    if not user:
        return json_error('Not found', 404)

    return jsonify(serialize_user(user))


@bp.route('/api/user/<string:username>/edit', methods=['PATCH'])
@require_login
def edit_user_profile(username, current_user):
    if not authorization_required(username, current_user):
        return json_error('Forbidden', 403)

    user = User.query.filter_by(username=username).first()
    if not user:
        return json_error('Not found', 404)

    data, error = parse_json_request()
    if error:
        return error

    if 'username' in data:
        new_username = data['username'].strip()
        if not new_username:
            return json_error('Username is required', 400)
        existing_user = User.query.filter(User.username == new_username, User.id != user.id).first()
        if existing_user:
            return json_error('Username already exists', 409)
        user.username = new_username
    if 'fullname' in data:
        user.fullname = data['fullname'].strip() or '—'
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if not EMAIL_REGEX.match(new_email):
            return json_error('Invalid email', 400)
        existing_email = User.query.filter(User.email == new_email, User.id != user.id).first()
        if existing_email:
            return json_error('Email already exists', 409)
        user.email = new_email
    if 'phone' in data:
        user.phone = data['phone'].strip() or '—'
    if 'role' in data:
        user.role = data['role'].strip() or '—'
    if 'vessel' in data:
        user.vessel = data['vessel'].strip() or '—'
    if 'permit' in data:
        user.permit = data['permit'].strip() or '—'
    if 'member_since' in data:
        user.member_since = data['member_since'].strip() or '—'

    db.session.commit()
    return jsonify({'message': 'OK', 'user': serialize_user(user)})


@bp.route('/api/user/<string:username>/password', methods=['PATCH'])
@require_login
def change_password(username, current_user):
    if not authorization_required(username, current_user):
        return json_error('Forbidden', 403)

    user = User.query.filter_by(username=username).first()
    if not user:
        return json_error('Not found', 404)

    data, error = parse_json_request()
    if error:
        return error

    old_password = data.get('old_password')
    new_password = data.get('password')
    if not old_password or not new_password:
        return json_error('Old password and new password are required', 400)
    if not check_password_hash(user.password, old_password):
        return json_error('Current password is incorrect', 401)
    if len(new_password) < 8:
        return json_error('Password must be at least 8 characters long', 400)

    user.password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
    db.session.commit()
    return jsonify({'message': 'OK'})


@bp.route('/api/check_permit/<string:cfr>')
def check_permit(cfr):
    vessel = Vessel.query.filter_by(cfr=cfr.upper()).first()
    if not vessel:
        return json_error('Not found', 404)
    return jsonify({'vessel': vessel.name, 'captain': vessel.captain, 'expires': vessel.valid_until})


@bp.route('/api/issue_ticket', methods=['POST'])
@require_login
def issue_ticket(current_user):
    data, error = parse_json_request()
    if error:
        return error

    ticket_type = data.get('type')
    price = data.get('price')
    if not ticket_type or price is None:
        return json_error('Ticket type and price are required', 400)

    try:
        price_value = float(price)
    except (ValueError, TypeError):
        return json_error('Invalid price', 400)

    ticket = FishingTicket(ticket_type=ticket_type, price=price_value)
    db.session.add(ticket)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': ticket.id}), 201




@bp.route('/api/rivers', methods=['GET'])
def list_rivers():
    rivers = River.query.filter_by(active=True).order_by(River.region).all()
    return jsonify([
        {
            'id': r.id,
            'name': r.name,
            'type': r.type,
            'region': r.region,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'fish': r.fish,
            'fish_rules': r.fish_rules,
            'interesting_facts': r.interesting_facts,
            'description': r.description
        }
        for r in rivers
    ])


@bp.route('/api/river', methods=['POST'])
@require_login
def create_river(current_user):
    data, error = parse_json_request()
    if error:
        return error

    if not data.get('name') or not data.get('type') or not data.get('region'):
        return json_error('Name, type and region are required', 400)

    try:
        latitude = float(data.get('latitude', 0))
        longitude = float(data.get('longitude', 0))
    except (ValueError, TypeError):
        return json_error('Invalid latitude or longitude', 400)

    river = River(
        name=data['name'].strip(),
        type=data['type'].strip(),
        region=data['region'].strip(),
        latitude=latitude,
        longitude=longitude,
        fish=data.get('fish', '').strip(),
        fish_rules=data.get('fish_rules', '').strip(),
        interesting_facts=data.get('interesting_facts', '').strip(),
        description=data.get('description', '').strip()
    )
    db.session.add(river)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': river.id}), 201


@bp.route('/api/river/<int:river_id>', methods=['GET'])
def get_river(river_id):
    river = River.query.get(river_id)
    if not river:
        return json_error('Not found', 404)
    return jsonify({
        'id': river.id,
        'name': river.name,
        'type': river.type,
        'region': river.region,
        'latitude': river.latitude,
        'longitude': river.longitude,
        'fish': river.fish,
        'fish_rules': river.fish_rules,
        'interesting_facts': river.interesting_facts,
        'description': river.description,
        'active': river.active
    })


@bp.route('/api/vessels', methods=['GET'])
@require_login
def list_vessels(current_user):
    vessels = Vessel.query.order_by(Vessel.name).all()
    return jsonify([
        {
            'id': v.id,
            'cfr': v.cfr,
            'name': v.name,
            'captain': v.captain,
            'valid_until': v.valid_until,
            'active': v.active
        }
        for v in vessels
    ])


@bp.route('/api/vessel', methods=['POST'])
@require_login
def create_vessel(current_user):
    data, error = parse_json_request()
    if error:
        return error

    if not data.get('cfr') or not data.get('name'):
        return json_error('CFR and vessel name are required', 400)
    if Vessel.query.filter_by(cfr=data['cfr']).first():
        return json_error('Vessel with this CFR already exists', 400)

    vessel = Vessel(
        cfr=data['cfr'].strip().upper(),
        name=data['name'].strip(),
        captain=data.get('captain', '').strip() or '—',
        valid_until=data.get('valid_until', '2026-12-31')
    )
    db.session.add(vessel)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': vessel.id}), 201


@bp.route('/api/vessel/<int:vessel_id>', methods=['PATCH'])
@require_login
def update_vessel(vessel_id, current_user):
    vessel = Vessel.query.get(vessel_id)
    if not vessel:
        return json_error('Not found', 404)

    data, error = parse_json_request()
    if error:
        return error

    if data.get('name'):
        vessel.name = data['name']
    if data.get('captain'):
        vessel.captain = data['captain']
    if data.get('valid_until'):
        vessel.valid_until = data['valid_until']
    if 'active' in data:
        vessel.active = bool(data['active'])

    db.session.commit()
    return jsonify({'message': 'OK'})


@bp.route('/api/permits', methods=['GET'])
@require_login
def list_permits(current_user):
    permits = Permit.query.order_by(Permit.valid_until.desc()).all()
    return jsonify([
        {
            'id': p.id,
            'owner': p.owner,
            'vessel_cfr': p.vessel_cfr,
            'permit_no': p.permit_no,
            'valid_from': p.valid_from,
            'valid_until': p.valid_until,
            'active': p.active
        }
        for p in permits
    ])


@bp.route('/api/permit', methods=['POST'])
@require_login
def create_permit(current_user):
    data, error = parse_json_request()
    if error:
        return error

    if not data.get('owner') or not data.get('vessel_cfr') or not data.get('permit_no'):
        return json_error('Owner, vessel CFR and permit number are required', 400)
    if Permit.query.filter_by(permit_no=data['permit_no']).first():
        return json_error('Permit number already exists', 400)

    permit = Permit(
        owner=data['owner'].strip(),
        vessel_cfr=data['vessel_cfr'].strip().upper(),
        permit_no=data['permit_no'].strip(),
        valid_from=data.get('valid_from', datetime.utcnow().strftime('%Y-%m-%d')),
        valid_until=data.get('valid_until', '2026-12-31'),
        active=bool(data.get('active', True))
    )
    db.session.add(permit)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': permit.id}), 201


@bp.route('/api/permit/<int:permit_id>/status', methods=['PATCH'])
@require_login
def update_permit_status(permit_id, current_user):
    permit = Permit.query.get(permit_id)
    if not permit:
        return json_error('Not found', 404)

    data, error = parse_json_request()
    if error:
        return error

    if 'active' not in data:
        return json_error('active field is required', 400)

    permit.active = bool(data['active'])
    db.session.commit()
    return jsonify({'message': 'OK'})


@bp.route('/api/inspection', methods=['POST'])
@require_login
def record_inspection(current_user):
    data, error = parse_json_request()
    if error:
        return error

    if not data.get('inspector') or not data.get('target_type') or not data.get('target_id'):
        return json_error('Inspector, target type and target id are required', 400)

    inspection = Inspection(
        inspector=data['inspector'].strip(),
        target_type=data['target_type'].strip(),
        target_id=data['target_id'].strip(),
        location=data.get('location', '').strip(),
        notes=data.get('notes', '').strip()
    )
    db.session.add(inspection)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': inspection.id}), 201


@bp.route('/api/inspections', methods=['GET'])
@require_login
def get_inspections(current_user):
    inspections = Inspection.query.order_by(Inspection.timestamp.desc()).limit(100).all()
    return jsonify([
        {
            'id': i.id,
            'inspector': i.inspector,
            'target_type': i.target_type,
            'target_id': i.target_id,
            'location': i.location,
            'notes': i.notes,
            'timestamp': i.timestamp.strftime('%d.%m.%Y %H:%M')
        }
        for i in inspections
    ])


@bp.route('/api/dashboard_stats')
@require_login
def dashboard_stats(current_user):
    total_vessels = Vessel.query.count()
    active_permits = Permit.query.filter_by(active=True).count()
    total_tickets = FishingTicket.query.count()
    total_inspections = Inspection.query.count()
    total_fines = Fine.query.count()
    total_revenue = db.session.query(func.coalesce(func.sum(FishingTicket.price), 0)).scalar() or 0
    last_ticket = FishingTicket.query.order_by(FishingTicket.timestamp.desc()).first()

    today = datetime.utcnow()
    month_series = []
    current_month = datetime(today.year, today.month, 1)
    for offset in range(5, -1, -1):
        month_start = current_month
        for _ in range(offset):
            month_start = (month_start - timedelta(days=1)).replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        tickets_count = FishingTicket.query.filter(
            FishingTicket.timestamp >= month_start,
            FishingTicket.timestamp < next_month
        ).count()
        inspections_count = Inspection.query.filter(
            Inspection.timestamp >= month_start,
            Inspection.timestamp < next_month
        ).count()
        month_series.append({
            'label': month_start.strftime('%m.%Y'),
            'tickets': tickets_count,
            'inspections': inspections_count,
            'total': tickets_count + inspections_count
        })

    max_month_value = max([item['total'] for item in month_series] + [1])
    for item in month_series:
        item['value'] = round((item['total'] / max_month_value) * 100) if item['total'] else 8

    operations = []
    for ticket in FishingTicket.query.order_by(FishingTicket.timestamp.desc()).limit(5):
        operations.append({
            'title': f'Издаден билет: {ticket.ticket_type}',
            'subtitle': f'Цена: {ticket.price:.2f} €',
            'timestamp': ticket.timestamp.strftime('%d.%m.%Y %H:%M'),
            'status': 'Безплатен' if ticket.price == 0 else 'Платен'
        })
    for inspection in Inspection.query.order_by(Inspection.timestamp.desc()).limit(5):
        operations.append({
            'title': f'Инспекция: {inspection.target_type} {inspection.target_id}',
            'subtitle': inspection.location,
            'timestamp': inspection.timestamp.strftime('%d.%m.%Y %H:%M'),
            'status': 'Завършена'
        })
    operations.sort(key=lambda item: datetime.strptime(item['timestamp'], '%d.%m.%Y %H:%M'), reverse=True)
    operations = operations[:6]

    return jsonify({
        'total_vessels': total_vessels,
        'active_permits': active_permits,
        'total_tickets': total_tickets,
        'total_inspections': total_inspections,
        'total_fines': total_fines,
        'total_revenue': float(total_revenue),
        'last_ticket': last_ticket.timestamp.strftime('%d.%m.%Y %H:%M') if last_ticket else '—',
        'monthly_overview': month_series,
        'recent_operations': operations
    })

@bp.route('/api/issue_fine', methods=['POST'])
@require_login
def issue_fine(current_user):
    data, error = parse_json_request()
    if error:
        return error

    if data.get('inspection_id') is None or data.get('issued_to') is None:
        return json_error('Inspection ID and issued_to are required', 400)

    try:
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        return json_error('Invalid amount', 400)

    fine = Fine(
        inspection_id=data['inspection_id'],
        amount=amount,
        issued_to=data['issued_to']
    )
    db.session.add(fine)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': fine.id}), 201


@bp.route('/api/fines', methods=['GET'])
@require_login
def list_fines(current_user):
    fines = Fine.query.order_by(Fine.issued_at.desc()).all()
    return jsonify([
        {
            'id': fine.id,
            'inspection_id': fine.inspection_id,
            'amount': fine.amount,
            'issued_to': fine.issued_to,
            'paid': fine.paid,
            'issued_at': fine.issued_at.strftime('%d.%m.%Y %H:%M')
        }
        for fine in fines
    ])


@bp.route('/api/fine/<int:fine_id>/pay', methods=['POST'])
@require_login
def pay_fine(fine_id, current_user):
    fine = Fine.query.get(fine_id)
    if not fine:
        return json_error('Not found', 404)
    fine.paid = True
    db.session.commit()
    return jsonify({'message': 'OK'})


@bp.route('/api/fine/pay', methods=['POST'])
@require_login
def pay_fine_legacy(current_user):
    data, error = parse_json_request()
    if error:
        return error

    fine_id = data.get('id')
    if fine_id is None:
        return json_error('Fine id is required', 400)

    fine = Fine.query.get(fine_id)
    if not fine:
        return json_error('Not found', 404)

    fine.paid = True
    db.session.commit()
    return jsonify({'message': 'OK'})

