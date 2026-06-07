from flask import Blueprint, jsonify, render_template, request, redirect
from models import db, User, Vessel, FishingTicket, Catch, Permit, Inspection, Fine
from sqlalchemy import func
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    return redirect('/login')

@bp.route("/dashboard")
def dashboard():
    return render_template("index.html")

@bp.route("/login")
def login_page():
    return render_template("login.html")

@bp.route("/register")
def register_page():
    return render_template("register.html")

@bp.route("/map")
def map_page():
    return render_template("map.html")

@bp.route("/tickets")
def tickets_page():
    return render_template("tickets.html")

@bp.route("/profile")
def profile_page():
    return render_template("profile.html")

@bp.route("/fines")
def fines_page():
    return render_template("fines.html")

@bp.route("/api/tickets")
def get_tickets():
    tickets = FishingTicket.query.order_by(FishingTicket.timestamp.desc()).limit(20).all()
    return jsonify([
        {"id": t.id, "ticket_type": t.ticket_type, "price": t.price, "timestamp": t.timestamp.strftime("%d.%m.%Y %H:%M")} for t in tickets
    ])

@bp.route("/api/register", methods=["POST"])
def register_user():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Exists"}), 400
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        fullname=data.get('fullname', '—') if data.get('fullname') else '—',
        phone=data.get('phone', '—') if data.get('phone') else '—',
        role=data.get('role', 'Любител Рибар'),
        vessel=data.get('vessel', '—') if data.get('vessel') else '—',
        permit=data.get('permit', '—') if data.get('permit') else '—'
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "OK"}), 201

@bp.route("/api/login", methods=["POST"])
def login_user():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({"message": "OK", "username": user.username}), 200
    return jsonify({"error": "Invalid"}), 401

@bp.route("/api/user/<string:username>")
def get_user_details(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "username": user.username,
        "email": user.email,
        "fullname": user.fullname,
        "phone": user.phone,
        "role": user.role,
        "vessel": user.vessel,
        "permit": user.permit,
        "member_since": user.member_since
    })

@bp.route("/api/user/<string:username>/edit", methods=["POST"])
def edit_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Not found"}), 404
    data = request.json
    user.fullname = data.get('fullname', user.fullname)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    db.session.commit()
    return jsonify({"message": "OK"})

@bp.route("/api/user/<string:username>/password", methods=["POST"])
def change_password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Not found"}), 404
    data = request.json
    user.password = data.get('password')
    db.session.commit()
    return jsonify({"message": "OK"})

@bp.route("/api/check_permit/<string:cfr>")
def check_permit(cfr):
    v = Vessel.query.filter_by(cfr=cfr.upper()).first()
    if not v:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"vessel": v.name, "captain": v.captain, "expires": v.valid_until})

@bp.route('/api/issue_ticket', methods=['POST'])
def issue_ticket():
    data = request.json
    t = FishingTicket(ticket_type=data['type'], price=float(data['price']))
    db.session.add(t)
    db.session.commit()
    return jsonify({"message": "OK"}), 201

@bp.route('/api/save_catch', methods=['POST'])
def save_catch():
    data = request.json
    c = Catch(fish_type=data['fish_type'], location=data['location'])
    db.session.add(c)
    db.session.commit()
    return jsonify({"message": "OK"}), 201

@bp.route('/api/vessels', methods=['GET'])
def list_vessels():
    vessels = Vessel.query.order_by(Vessel.name).all()
    return jsonify([{"id": v.id, "cfr": v.cfr, "name": v.name, "captain": v.captain, "valid_until": v.valid_until, "active": v.active} for v in vessels])

@bp.route('/api/vessel', methods=['POST'])
def create_vessel():
    data = request.json
    if Vessel.query.filter_by(cfr=data.get('cfr')).first():
        return jsonify({'error': 'exists'}), 400
    v = Vessel(cfr=data.get('cfr'), name=data.get('name'), captain=data.get('captain'), valid_until=data.get('valid_until', '2026-12-31'))
    db.session.add(v)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': v.id}), 201

@bp.route('/api/permits', methods=['GET'])
def list_permits():
    perms = Permit.query.order_by(Permit.valid_until.desc()).all()
    return jsonify([{"id": p.id, "owner": p.owner, "vessel_cfr": p.vessel_cfr, "permit_no": p.permit_no, "valid_from": p.valid_from, "valid_until": p.valid_until, "active": p.active} for p in perms])

@bp.route('/api/permit', methods=['POST'])
def create_permit():
    data = request.json
    if Permit.query.filter_by(permit_no=data.get('permit_no')).first():
        return jsonify({'error': 'exists'}), 400
    p = Permit(owner=data.get('owner'), vessel_cfr=data.get('vessel_cfr'), permit_no=data.get('permit_no'), valid_from=data.get('valid_from', datetime.utcnow().strftime('%Y-%m-%d')), valid_until=data.get('valid_until', '2026-12-31'), active=True)
    db.session.add(p)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': p.id}), 201

@bp.route('/api/inspection', methods=['POST'])
def record_inspection():
    data = request.json
    ins = Inspection(inspector=data.get('inspector'), target_type=data.get('target_type'), target_id=data.get('target_id'), location=data.get('location'), notes=data.get('notes', ''))
    db.session.add(ins)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': ins.id}), 201

@bp.route('/api/inspections', methods=['GET'])
def get_inspections():
    ins = Inspection.query.order_by(Inspection.timestamp.desc()).limit(100).all()
    return jsonify([{"id": i.id, "inspector": i.inspector, "target_type": i.target_type, "target_id": i.target_id, "location": i.location, "notes": i.notes, "timestamp": i.timestamp.strftime('%d.%m.%Y %H:%M')} for i in ins])

@bp.route('/api/dashboard_stats')
def dashboard_stats():
    total_vessels = Vessel.query.count()
    active_permits = Permit.query.filter_by(active=True).count()
    total_tickets = FishingTicket.query.count()
    total_inspections = Inspection.query.count()
    total_fines = Fine.query.count()
    total_revenue = db.session.query(func.coalesce(func.sum(FishingTicket.price), 0)).scalar() or 0
    last_ticket = FishingTicket.query.order_by(FishingTicket.timestamp.desc()).first()

    operations = []
    for ticket in FishingTicket.query.order_by(FishingTicket.timestamp.desc()).limit(5):
        operations.append({
            'title': f"Издаден билет: {ticket.ticket_type}",
            'subtitle': f"Цена: {ticket.price:.2f} €",
            'timestamp': ticket.timestamp.strftime('%d.%m.%Y %H:%M'),
            'status': ticket.price == 0 and 'Безплатен' or 'Платен'
        })
    for inspection in Inspection.query.order_by(Inspection.timestamp.desc()).limit(5):
        operations.append({
            'title': f"Инспекция: {inspection.target_type} {inspection.target_id}",
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
        'recent_operations': operations
    })

@bp.route('/api/issue_fine', methods=['POST'])
def issue_fine():
    data = request.json
    f = Fine(
        inspection_id=data.get('inspection_id'),
        amount=float(data.get('amount', 0)),
        issued_to=data.get('issued_to')
    )
    db.session.add(f)
    db.session.commit()
    return jsonify({'message': 'OK', 'id': f.id}), 201

@bp.route('/api/fines', methods=['GET'])
def list_fines():
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

@bp.route('/api/fine/pay', methods=['POST'])
def pay_fine():
    data = request.json
    fine = Fine.query.filter_by(id=data.get('id')).first()
    if not fine:
        return jsonify({'error': 'Not found'}), 404
    fine.paid = True
    db.session.commit()
    return jsonify({'message': 'OK'})
