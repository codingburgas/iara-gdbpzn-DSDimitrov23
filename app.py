import os
import json
from flask import Flask
from flask_cors import CORS
from sqlalchemy import inspect, text
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from models import db, User, Vessel, River, Permit, FishingTicket, Inspection, Fine
from routes import bp as main_bp


DEFAULT_RIVER_FISH_RULES = {
    'Язовир Искър': [
        {'name': 'Пъстърва', 'season': '01.05 - 30.09', 'note': 'Извън размножителната забрана.'},
        {'name': 'Костур', 'season': 'Целогодишно', 'note': 'При спазване на дневните норми.'},
        {'name': 'Платика', 'season': '01.06 - 14.04', 'note': 'Забранена през пролетното размножаване.'}
    ],
    'Река Камчия': [
        {'name': 'Шаран', 'season': '01.06 - 14.04', 'note': 'Забранен през пролетното размножаване.'},
        {'name': 'Каракуда', 'season': 'Целогодишно', 'note': 'При спазване на дневните норми.'},
        {'name': 'Бяла риба', 'season': '01.06 - 14.03', 'note': 'Пази се през размножителния период.'}
    ],
    'Река Струма': [
        {'name': 'Пъстърва', 'season': '01.05 - 30.09', 'note': 'Само в разрешения сезон за балканска пъстърва.'},
        {'name': 'Кефал', 'season': '01.06 - 14.04', 'note': 'Най-подходящо през топлите месеци.'},
        {'name': 'Черен мряна', 'season': '01.06 - 14.04', 'note': 'Забранена през пролетното размножаване.'}
    ],
    'Язовир Копринка': [
        {'name': 'Шаран', 'season': '01.06 - 14.04', 'note': 'Забранен през пролетното размножаване.'},
        {'name': 'Щука', 'season': '01.05 - 31.12', 'note': 'Пази се в началото на годината.'},
        {'name': 'Бял амур', 'season': '01.06 - 14.04', 'note': 'При спазване на минимален размер.'}
    ],
    'Езерото Огоста': [
        {'name': 'Костур', 'season': 'Целогодишно', 'note': 'При спазване на дневните норми.'},
        {'name': 'Шаран', 'season': '01.06 - 14.04', 'note': 'Забранен през пролетното размножаване.'},
        {'name': 'Платика', 'season': '01.06 - 14.04', 'note': 'Подходяща след края на пролетната забрана.'}
    ],
    'Язовир Янтра': [
        {'name': 'Костур', 'season': 'Целогодишно', 'note': 'При спазване на дневните норми.'},
        {'name': 'Шаран', 'season': '01.06 - 14.04', 'note': 'Забранен през пролетното размножаване.'},
        {'name': 'Амур', 'season': '01.06 - 14.04', 'note': 'При спазване на минимален размер.'}
    ],
    'Река Арда': [
        {'name': 'Пъстърва', 'season': '01.05 - 30.09', 'note': 'Само в разрешения сезон за пъстървови риби.'},
        {'name': 'Каракуда', 'season': 'Целогодишно', 'note': 'При спазване на дневните норми.'},
        {'name': 'Шаран', 'season': '01.06 - 14.04', 'note': 'Забранен през пролетното размножаване.'}
    ],
    'Река Въча': [
        {'name': 'Пъстърва', 'season': '01.05 - 30.09', 'note': 'Подходяща за мухарски риболов в сезона.'},
        {'name': 'Кефал', 'season': '01.06 - 14.04', 'note': 'Най-подходящо през топлите месеци.'},
        {'name': 'Черен мряна', 'season': '01.06 - 14.04', 'note': 'Забранена през пролетното размножаване.'}
    ],
    'Река Лом': [
        {'name': 'Шаран', 'season': '01.06 - 14.04', 'note': 'Забранен през пролетното размножаване.'},
        {'name': 'Каракуда', 'season': 'Целогодишно', 'note': 'При спазване на дневните норми.'},
        {'name': 'Костур', 'season': 'Целогодишно', 'note': 'При спазване на дневните норми.'}
    ],
}


DEFAULT_RIVER_FACTS = {
    'Язовир Искър': [
        'Най-големият язовир в България по воден обем и важен водоизточник за София.',
        'Бреговете му имат много различни риболовни зони - плитчини, стръмни брегове и заливи.',
        'При промяна на нивото рибата често се мести към старите речни корита и подводни тераси.'
    ],
    'Река Камчия': [
        'Камчия образува една от най-интересните крайречни гори в България - лонгозната гора край устието.',
        'Реката сменя характера си: по-спокойна в долното течение и по-бърза в горните участъци.',
        'В долното течение има смесване на сладководни и крайморски влияния, което прави риболова разнообразен.'
    ],
    'Река Струма': [
        'Струма извира от Витоша и пресича Югозападна България преди да продължи към Егейско море.',
        'По течението й има участъци с бързи прагове, вирове и по-широки спокойни места.',
        'Топлите долини около реката правят сезона активен по-рано от много планински водоеми.'
    ],
    'Язовир Копринка': [
        'Под водите на язовира остава част от района на древния тракийски град Севтополис.',
        'Копринка е известен с разнообразен риболов - от шаранови места до участъци за хищни риби.',
        'Сутрешните и вечерните часове около заливите често са най-резултатни за активна риба.'
    ],
    'Езерото Огоста': [
        'Огоста е сред големите язовири в Северозападна България и е важен за района на Монтана.',
        'Има дълбоки части и просторни брегове, което позволява различни стилове на риболов.',
        'При вятър рибата често се събира по подветрените брегове, където храната се натрупва.'
    ],
    'Язовир Янтра': [
        'Водоемът е свързан с басейна на Янтра - една от значимите реки в Северна България.',
        'Подходящ е за кратки излети, защото има сравнително достъпни брегове.',
        'Костурът често се търси около подводни неравности и каменисти участъци.'
    ],
    'Река Арда': [
        'Арда е една от най-живописните родопски реки и минава през райони със стръмни скали и меандри.',
        'Водата в планинските участъци е по-хладна, което я прави интересна за пъстървов риболов.',
        'След дъжд реката може да променя нивото си бързо, затова изборът на място е важен.'
    ],
    'Река Въча': [
        'Въча е родопска река с чисти, студени участъци и силно планинско влияние.',
        'По течението й има язовири и по-бързи речни места, което създава различни риболовни условия.',
        'Пъстървата обича сенчести участъци, кислородна вода и места след бързеи.'
    ],
    'Река Лом': [
        'Река Лом е част от Дунавския водосбор и носи типичен северозападен речен характер.',
        'В по-спокойните участъци често се търсят шаранови риби, а около прагове - по-активна дребна риба.',
        'След спадане на висока вода остават добри вирове и хранителни петна по завоите.'
    ],
}


def ensure_river_schema():
    columns = {column['name'] for column in inspect(db.engine).get_columns('river')}
    if 'fish_rules' not in columns:
        db.session.execute(text('ALTER TABLE river ADD COLUMN fish_rules TEXT'))
        db.session.commit()
    if 'interesting_facts' not in columns:
        db.session.execute(text('ALTER TABLE river ADD COLUMN interesting_facts TEXT'))
        db.session.commit()


def seed_river_fish_rules():
    for name, rules in DEFAULT_RIVER_FISH_RULES.items():
        river = River.query.filter_by(name=name).first()
        if river and not river.fish_rules:
            river.fish_rules = json.dumps(rules, ensure_ascii=False)
    db.session.commit()


def seed_river_facts():
    for name, facts in DEFAULT_RIVER_FACTS.items():
        river = River.query.filter_by(name=name).first()
        if river:
            river.interesting_facts = json.dumps(facts, ensure_ascii=False)
    db.session.commit()


def remove_hidden_water_spots():
    River.query.filter_by(name='Езерото Пясъчник').delete()
    db.session.commit()


REAL_RIVERS = [
    {
        'name': 'Язовир Искър',
        'type': 'Язовир',
        'region': 'София',
        'latitude': 42.450,
        'longitude': 23.550,
        'fish': ['Пъстърва', 'Костур', 'Платика'],
        'description': 'Най-големият язовир в България по воден обем, използван за водоснабдяване, туризъм и риболов.',
        'fish_rules': [
            {'name': 'Пъстърва', 'season': '01.05 - 30.09', 'note': 'Разрешена извън размножителната забрана.'},
            {'name': 'Костур', 'season': 'Целогодишно', 'note': 'При спазване на дневните норми.'},
            {'name': 'Платика', 'season': '01.06 - 14.04', 'note': 'Забранена през пролетното размножаване.'}
        ],
        'facts': [
            'Водоемът е основен водоизточник за София.',
            'Бреговете му предлагат заливи, плитчини и стари речни корита.',
            'При промяна на нивото рибата често се премества към подводни тераси.'
        ]
    },
    {
        'name': 'Река Камчия',
        'type': 'Река',
        'region': 'Варна',
        'latitude': 43.020,
        'longitude': 27.880,
        'fish': ['Шаран', 'Каракуда', 'Бяла риба'],
        'description': 'Река с разнообразни участъци и смесено сладководно и крайморско влияние в долното течение.',
        'fish_rules': [
            {'name': 'Шаран', 'season': '01.06 - 14.04', 'note': 'Забранен през пролетното размножаване.'},
            {'name': 'Каракуда', 'season': 'Целогодишно', 'note': 'При спазване на дневните норми.'},
            {'name': 'Бяла риба', 'season': '01.06 - 14.03', 'note': 'Пази се през размножителния период.'}
        ],
        'facts': [
            'Камчия е известна с лонгозната гора край устието.',
            'Долното течение предлага по-спокойни риболовни места.',
            'Реката е чувствителна към сезонни валежи и промени в нивото.'
        ]
    },
    {
        'name': 'Язовир Копринка',
        'type': 'Язовир',
        'region': 'Стара Загора',
        'latitude': 42.450,
        'longitude': 25.100,
        'fish': ['Шаран', 'Щука', 'Бял амур'],
        'description': 'Популярен язовир с достъпни брегове, лагери и условия за риболов на мирни и хищни риби.',
        'fish_rules': [
            {'name': 'Шаран', 'season': '01.06 - 14.04', 'note': 'Забранен през пролетното размножаване.'},
            {'name': 'Щука', 'season': '01.05 - 31.12', 'note': 'Пази се в началото на годината.'},
            {'name': 'Бял амур', 'season': '01.06 - 14.04', 'note': 'При спазване на минимален размер.'}
        ],
        'facts': [
            'Под водите на язовира остава част от древния Севтополис.',
            'Заливите са резултатни в ранните сутрешни часове.',
            'Подходящ е за кратки проверки заради добрия достъп.'
        ]
    },
    {
        'name': 'Река Струма',
        'type': 'Река',
        'region': 'Югозапад',
        'latitude': 42.000,
        'longitude': 23.150,
        'fish': ['Пъстърва', 'Кефал', 'Черен мряна'],
        'description': 'Голяма река с планински и равнинни участъци, използвана активно за любителски риболов.',
        'fish_rules': [
            {'name': 'Пъстърва', 'season': '01.05 - 30.09', 'note': 'Само в разрешения сезон.'},
            {'name': 'Кефал', 'season': '01.06 - 14.04', 'note': 'Най-активен през топлите месеци.'},
            {'name': 'Черен мряна', 'season': '01.06 - 14.04', 'note': 'Забранена през размножителния период.'}
        ],
        'facts': [
            'Струма извира от Витоша и продължава към Егейско море.',
            'Има участъци с бързеи, вирове и спокойни места.',
            'Топлите долини около реката отварят сезона по-рано.'
        ]
    }
]


def seed_real_operational_data():
    if River.query.count() == 0 or River.query.filter(River.name.like('%Ð%')).first():
        River.query.delete()
        for item in REAL_RIVERS:
            db.session.add(River(
                name=item['name'],
                type=item['type'],
                region=item['region'],
                latitude=item['latitude'],
                longitude=item['longitude'],
                fish=json.dumps(item['fish'], ensure_ascii=False),
                fish_rules=json.dumps(item['fish_rules'], ensure_ascii=False),
                interesting_facts=json.dumps(item['facts'], ensure_ascii=False),
                description=item['description']
            ))

    if not User.query.filter_by(username='admin').first() and User.query.count() == 0 and Vessel.query.count() == 0:
        db.session.add(User(
            username='admin',
            email='admin@iara.local',
            password=generate_password_hash('Admin123!', method='pbkdf2:sha256', salt_length=16),
            fullname='ИАРА Администратор',
            phone='+359 2 123 4567',
            role='admin',
            vessel='—',
            permit='—'
        ))

    vessels = [
        ('BGR001', 'Black Sea Hunter', 'Иван Иванов', '2026-12-31'),
        ('BGR014', 'Св. Никола', 'Георги Петров', '2026-10-15'),
        ('BGR027', 'Дунав 7', 'Мария Стоянова', '2027-03-20'),
    ]
    for cfr, name, captain, valid_until in vessels:
        if not Vessel.query.filter_by(cfr=cfr).first():
            db.session.add(Vessel(cfr=cfr, name=name, captain=captain, valid_until=valid_until, active=True))

    permits = [
        ('Иван Иванов', 'BGR001', 'PRM-2026-001', '2026-01-01', '2026-12-31'),
        ('Георги Петров', 'BGR014', 'PRM-2026-014', '2026-02-10', '2026-10-15'),
        ('Мария Стоянова', 'BGR027', 'PRM-2026-027', '2026-03-01', '2027-03-20'),
    ]
    for owner, vessel_cfr, permit_no, valid_from, valid_until in permits:
        if not Permit.query.filter_by(permit_no=permit_no).first():
            db.session.add(Permit(owner=owner, vessel_cfr=vessel_cfr, permit_no=permit_no, valid_from=valid_from, valid_until=valid_until, active=True))

    if FishingTicket.query.count() == 0:
        ticket_rows = [
            ('Стандартен годишен билет', 25.00, 150),
            ('Стандартен годишен билет', 25.00, 96),
            ('Под 14г. / Пенсионер', 10.00, 64),
            ('Стандартен годишен билет', 25.00, 32),
            ('Инвалид с ТЕЛК', 0.00, 12),
            ('Стандартен годишен билет', 25.00, 2),
        ]
        for ticket_type, price, days_ago in ticket_rows:
            db.session.add(FishingTicket(ticket_type=ticket_type, price=price, timestamp=datetime.utcnow() - timedelta(days=days_ago)))

    if Inspection.query.count() == 0:
        inspection_rows = [
            ('инсп. Димитров', 'кораб', 'BGR001', 'Пристанище Варна', 'Проверени документи и разрешително.', 35),
            ('инсп. Николова', 'водоем', 'Язовир Искър', 'София област', 'Проверка за спазване на забранени зони.', 11),
            ('инсп. Георгиев', 'кораб', 'BGR014', 'Несебър', 'Установено съответствие с риболовния дневник.', 3),
        ]
        for inspector, target_type, target_id, location, notes, days_ago in inspection_rows:
            db.session.add(Inspection(
                inspector=inspector,
                target_type=target_type,
                target_id=target_id,
                location=location,
                notes=notes,
                timestamp=datetime.utcnow() - timedelta(days=days_ago)
            ))

    if Fine.query.count() == 0:
        db.session.add(Fine(inspection_id=1, amount=150.00, issued_to='Петър Петров', paid=False, issued_at=datetime.utcnow() - timedelta(days=9)))

    db.session.commit()


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    db.init_app(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        ensure_river_schema()
        
        # Add sample vessel
        if not Vessel.query.filter_by(cfr="BGR001").first():
            sample_vessel = Vessel(
                cfr="BGR001",
                name="Black Sea Hunter",
                captain="Ivan Ivanov",
                valid_until="2026-12-31"
            )
            db.session.add(sample_vessel)
            db.session.commit()
        
        # Add Bulgarian rivers
        if not River.query.first():
            rivers_data = [
                River(
                    name='Язовир Искър',
                    type='Язовир',
                    region='София',
                    latitude=42.450,
                    longitude=23.550,
                    fish='["Пъстърва", "Костур", "Платика"]',
                    description='Силно зарибен язовир с туристическа зона и обширни рибарски места.'
                ),
                River(
                    name='Река Камчия',
                    type='Река',
                    region='Варна',
                    latitude=43.020,
                    longitude=27.880,
                    fish='["Шаран", "Каракуда", "Бяла риба"]',
                    description='Течаща река с различни дълбочини и много добри места за шаранова атака.'
                ),
                River(
                    name='Река Струма',
                    type='Река',
                    region='Югозапад',
                    latitude=42.000,
                    longitude=23.150,
                    fish='["Пъстърва", "Кефал", "Черен мряна"]',
                    description='Хладна планинска река, подходяща за мухарски риболов.'
                ),
                River(
                    name='Язовир Копринка',
                    type='Язовир',
                    region='Стара Загора',
                    latitude=42.450,
                    longitude=25.100,
                    fish='["Шаран", "Щука", "Бял амур"]',
                    description='Голям водоем с бавна вода и множество риболовни лагери.'
                ),
                River(
                    name='Езерото Огоста',
                    type='Езеро',
                    region='Монтана',
                    latitude=43.237,
                    longitude=23.189,
                    fish='["Костур", "Шаран", "Платика"]',
                    description='Малко езеро с лесен достъп и отлични условия за семейни риболовци.'
                ),
                River(
                    name='Язовир Янтра',
                    type='Язовир',
                    region='Велико Търново',
                    latitude=43.170,
                    longitude=25.580,
                    fish='["Костур", "Шаран", "Амур"]',
                    description='Популярен язовир за риболов на щука и шаран.'
                ),
                River(
                    name='Река Арда',
                    type='Река',
                    region='Югоизток',
                    latitude=41.591,
                    longitude=25.574,
                    fish='["Пъстърва", "Каракуда", "Шаран"]',
                    description='Планинска река с бързо течение и чудесни места за мухарски риболов.'
                ),
                River(
                    name='Река Въча',
                    type='Река',
                    region='Родопи',
                    latitude=41.900,
                    longitude=24.170,
                    fish='["Пъстърва", "Кефал", "Черен мряна"]',
                    description='Кристално река с перфектни условия за мухарски риболов.'
                ),
                River(
                    name='Река Лом',
                    type='Река',
                    region='Северозапад',
                    latitude=43.757,
                    longitude=23.211,
                    fish='["Шаран", "Каракуда", "Костур"]',
                    description='Спокойна река с лесен достъп и много риболовни брегове.'
                ),
            ]
            for river in rivers_data:
                db.session.add(river)
            db.session.commit()
        remove_hidden_water_spots()
        seed_river_fish_rules()
        seed_river_facts()
        seed_real_operational_data()

    return app


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app = create_app()
    app.run(debug=debug_mode)
