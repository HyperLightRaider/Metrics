import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import db, User

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder=os.path.join(basedir, '..', 'client'), static_url_path='')
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'metrics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app, supports_credentials=True)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Необходимо указать username и password'}), 400

    username = data['username'].strip()
    password = data['password']

    if len(username) < 3 or len(password) < 3:
        return jsonify({'error': 'Логин и пароль должны быть не короче 3 символов'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Имя пользователя уже занято'}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Пользователь создан'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Необходимо указать username и password'}), 400

    username = data['username'].strip()
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401

    login_user(user)
    return jsonify({
        'message': 'Вход выполнен',
        'user': {
            'id': user.id,
            'username': user.username
        }
    }), 200


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Вы вышли из системы'}), 200


@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username
    })

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

from models import db, User, Entry
from analysis import compute_top_correlation
from datetime import datetime, timedelta

@app.route('/api/entries', methods=['POST'])
@login_required
def create_entry():

    data = request.get_json()

    required_fields = [
        "date",
        "sleep",
        "energy",
        "mood",
        "productivity",
        "activity"
    ]

    if not data:
        return jsonify({"error": "Некорректные данные"}), 400

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Некорректные данные: отсутствует {field}"
            }), 400

    try:
        date = datetime.strptime(data["date"], "%Y-%m-%d").date()

        sleep = float(data["sleep"])

        energy = int(data["energy"])
        mood = int(data["mood"])
        productivity = int(data["productivity"])
        activity = int(data["activity"])

        for value in [energy, mood, productivity, activity]:
            if value < 1 or value > 5:
                raise ValueError()

    except:
        return jsonify({
            "error": "Некорректные данные: неверные типы или диапазоны"
        }), 400

    entry = Entry(
        date=date,
        sleep=sleep,
        energy=energy,
        mood=mood,
        productivity=productivity,
        activity=activity,
        user_id=current_user.id
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "message": "Запись добавлена",
        "entry": {
            "id": entry.id,
            "date": str(entry.date),
            "sleep": entry.sleep,
            "energy": entry.energy,
            "mood": entry.mood,
            "productivity": entry.productivity,
            "activity": entry.activity,
            "user_id": entry.user_id
        }
    }), 201

@app.route('/api/entries', methods=['GET'])
@login_required
def get_entries():

    period = request.args.get("period", "all")

    query = Entry.query.filter_by(user_id=current_user.id)

    now = datetime.utcnow().date()

    if period == "week":
        query = query.filter(
            Entry.date >= now - timedelta(days=7)
        )

    elif period == "month":
        query = query.filter(
            Entry.date >= now - timedelta(days=30)
        )

    entries = query.order_by(Entry.date.asc()).all()

    return jsonify({
        "entries": [
            {
                "id": e.id,
                "date": str(e.date),
                "sleep": e.sleep,
                "energy": e.energy,
                "mood": e.mood,
                "productivity": e.productivity,
                "activity": e.activity
            }
            for e in entries
        ]
    }), 200

@app.route('/api/correlation', methods=['GET'])
@login_required
def correlation():

    entries = Entry.query.filter_by(
        user_id=current_user.id
    ).all()

    result = compute_top_correlation(entries)

    if result is None:
        return jsonify({
            "top_correlation": None,
            "message": "Недостаточно данных для аналитики"
        }), 200

    return jsonify({
        "top_correlation": result
    }), 200

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)