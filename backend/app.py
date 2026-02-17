# backend/app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from datetime import datetime, timedelta
from config import config_map
from models import db, User, Item, DeletedItem
from auth import mail, generate_verification_code, send_verification_email
import os


def get_project_paths():
    """
    Find template and static folders automatically.
    Works for local dev, Render.com, and any deployment.
    """
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)

    # Priority 1: New structure — frontend/pages/ at project root
    new_templates = os.path.join(project_root, 'frontend', 'pages')
    new_static = os.path.join(project_root, 'frontend')
    if os.path.isdir(new_templates) and os.path.isdir(new_static):
        print(f"[PATHS] Using frontend structure: {new_templates}")
        return new_templates, new_static

    # Priority 2: Templates inside backend/ folder
    local_templates = os.path.join(backend_dir, 'templates')
    local_static = os.path.join(backend_dir, 'static')
    if os.path.isdir(local_templates):
        print(f"[PATHS] Using local structure: {local_templates}")
        return local_templates, local_static

    # Priority 3: Old structure at project root
    old_templates = os.path.join(project_root, 'templates')
    old_static = os.path.join(project_root, 'static')
    if os.path.isdir(old_templates):
        print(f"[PATHS] Using old structure: {old_templates}")
        return old_templates, old_static

    # Fallback
    print(f"[PATHS] WARNING: No template folder found! Tried:")
    print(f"  - {new_templates}")
    print(f"  - {local_templates}")
    print(f"  - {old_templates}")
    return new_templates, new_static


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    template_folder, static_folder = get_project_paths()

    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder
                )

    app.config.from_object(config_map.get(
        config_name, config_map['development']))

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    CORS(app, supports_credentials=True)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Login required'}), 401
        return redirect(url_for('login'))

    with app.app_context():
        db.create_all()

    # ============ HEALTH CHECK ============
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'template_folder': app.template_folder,
            'static_folder': app.static_folder
        })

    # ============ PWA FILES ============
    @app.route('/manifest.json')
    def manifest():
        return app.send_static_file('manifest.json')

    @app.route('/sw.js')
    def service_worker():
        response = app.send_static_file('js/sw.js')
        response.headers['Service-Worker-Allowed'] = '/'
        response.headers['Content-Type'] = 'application/javascript'
        return response

    # ============ AUTH ROUTES ============

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            name = data.get('name', '').strip()
            password = data.get('password', '')
            user = User.query.filter_by(name=name).first()
            if user and user.check_password(password):
                if not user.is_verified:
                    session['verify_user_id'] = user.id
                    code = generate_verification_code()
                    user.verification_code = code
                    user.code_expiry = datetime.utcnow() + timedelta(minutes=10)
                    db.session.commit()
                    send_verification_email(user.email, code)
                    if request.is_json:
                        return jsonify({'success': True, 'redirect': url_for('verify')})
                    return redirect(url_for('verify'))
                login_user(user, remember=True)
                if request.is_json:
                    return jsonify({'success': True, 'redirect': url_for('dashboard')})
                return redirect(url_for('dashboard'))
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid name or password'}), 401
            flash('Invalid name or password', 'error')
        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            dob = data.get('dob', '')
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')

            errors = []
            if not all([name, email, password, confirm_password]):
                errors.append('All fields are required')
            if password != confirm_password:
                errors.append('Passwords do not match')
            if len(password) < 6:
                errors.append('Password must be at least 6 characters')
            if User.query.filter_by(email=email).first():
                errors.append('Email already registered')
            if User.query.filter_by(name=name).first():
                errors.append('Username already taken')

            if errors:
                msg = errors[0]
                if request.is_json:
                    return jsonify({'success': False, 'message': msg}), 400
                flash(msg, 'error')
                return render_template('signup.html')

            user = User(name=name, email=email)
            if dob:
                try:
                    user.dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except ValueError:
                    pass
            user.set_password(password)
            code = generate_verification_code()
            user.verification_code = code
            user.code_expiry = datetime.utcnow() + timedelta(minutes=10)
            db.session.add(user)
            db.session.commit()
            send_verification_email(email, code)
            session['verify_user_id'] = user.id
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('verify')})
            return redirect(url_for('verify'))
        return render_template('signup.html')

    @app.route('/verify', methods=['GET', 'POST'])
    def verify():
        user_id = session.get('verify_user_id')
        if not user_id:
            return redirect(url_for('login'))
        user = User.query.get(user_id)
        if not user:
            return redirect(url_for('login'))
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            code = data.get('code', '').strip()
            if user.code_expiry and datetime.utcnow() > user.code_expiry:
                msg = 'Verification code expired. Please request a new one.'
                if request.is_json:
                    return jsonify({'success': False, 'message': msg}), 400
                flash(msg, 'error')
                return render_template('verify.html', email=user.email)
            if code == user.verification_code:
                user.is_verified = True
                user.verification_code = None
                user.code_expiry = None
                db.session.commit()
                login_user(user, remember=True)
                session.pop('verify_user_id', None)
                add_default_items(user.id)
                if request.is_json:
                    return jsonify({'success': True, 'redirect': url_for('dashboard')})
                return redirect(url_for('dashboard'))
            msg = 'Invalid verification code'
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'error')
        return render_template('verify.html', email=user.email)

    @app.route('/resend-code', methods=['POST'])
    def resend_code():
        user_id = session.get('verify_user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Session expired'}), 400
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 400
        code = generate_verification_code()
        user.verification_code = code
        user.code_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        send_verification_email(user.email, code)
        return jsonify({'success': True, 'message': 'New code sent!'})

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    def add_default_items(user_id):
        if Item.query.filter_by(user_id=user_id).first():
            return
        default_veg = [
            'Tomato', 'Potato', 'Onion', 'Carrot', 'Spinach', 'Broccoli',
            'Capsicum', 'Cucumber', 'Cabbage', 'Cauliflower', 'Green Beans',
            'Peas', 'Corn', 'Lettuce', 'Mushroom', 'Garlic', 'Ginger',
            'Apple', 'Banana', 'Orange', 'Mango', 'Grapes', 'Watermelon',
            'Strawberry', 'Pineapple', 'Papaya', 'Lemon', 'Pomegranate',
            'Guava', 'Kiwi'
        ]
        default_grocery = [
            'Rice', 'Wheat Flour', 'Sugar', 'Salt', 'Cooking Oil', 'Butter',
            'Milk', 'Bread', 'Eggs', 'Tea', 'Coffee', 'Pasta', 'Noodles',
            'Oats', 'Cornflakes', 'Biscuits', 'Jam', 'Honey', 'Ketchup',
            'Soy Sauce', 'Vinegar', 'Pepper', 'Turmeric', 'Cumin',
            'Coriander Powder', 'Chili Powder', 'Cinnamon', 'Cardamom',
            'Dal / Lentils', 'Chickpeas'
        ]
        for name in default_veg:
            db.session.add(
                Item(name=name, category='vegfruit', user_id=user_id))
        for name in default_grocery:
            db.session.add(
                Item(name=name, category='grocery', user_id=user_id))
        db.session.commit()

    # ============ PAGE ROUTES ============

    @app.route('/dashboard')
    @login_required
    def dashboard():
        stats = get_user_stats(current_user.id)
        return render_template('dashboard.html', user=current_user, **stats)

    @app.route('/vegfruits-procure')
    @login_required
    def vegfruits_procure():
        return render_template('vegfruits_procure.html')

    @app.route('/groceries-procure')
    @login_required
    def groceries_procure():
        return render_template('groceries_procure.html')

    @app.route('/vegfruits-list')
    @login_required
    def vegfruits_list():
        return render_template('vegfruits_list.html')

    @app.route('/groceries-list')
    @login_required
    def groceries_list():
        return render_template('groceries_list.html')

    # ============ API ROUTES ============

    @app.route('/api/items/<category>', methods=['GET'])
    @login_required
    def get_items(category):
        if category not in ['vegfruit', 'grocery']:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400
        items = Item.query.filter_by(
            user_id=current_user.id, category=category
        ).order_by(Item.name).all()
        return jsonify([item.to_dict() for item in items])

    @app.route('/api/items', methods=['POST'])
    @login_required
    def add_item():
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        name = data.get('name', '').strip()
        category = data.get('category', '').strip()
        if not name or len(name) > 100:
            return jsonify({'success': False, 'message': 'Invalid item name'}), 400
        if category not in ['vegfruit', 'grocery']:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400
        existing = Item.query.filter_by(
            user_id=current_user.id, name=name, category=category
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Item already exists'}), 400
        item = Item(name=name, category=category, user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()}), 201

    @app.route('/api/items/<int:item_id>/toggle-procure', methods=['PUT'])
    @login_required
    def toggle_procure(item_id):
        item = Item.query.filter_by(
            id=item_id, user_id=current_user.id).first()
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        item.to_procure = not item.to_procure
        if not item.to_procure:
            item.consumed = False
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})

    @app.route('/api/items/<int:item_id>/toggle-consumed', methods=['PUT'])
    @login_required
    def toggle_consumed(item_id):
        item = Item.query.filter_by(
            id=item_id, user_id=current_user.id).first()
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        item.consumed = not item.consumed
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})

    @app.route('/api/items/<int:item_id>', methods=['DELETE'])
    @login_required
    def delete_item(item_id):
        item = Item.query.filter_by(
            id=item_id, user_id=current_user.id).first()
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        deleted = DeletedItem(
            original_id=item.id, name=item.name, category=item.category,
            is_active=item.is_active, to_procure=item.to_procure,
            consumed=item.consumed, user_id=item.user_id
        )
        db.session.add(deleted)
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'deleted_id': deleted.id, 'item_name': deleted.name})

    @app.route('/api/items/undo/<int:deleted_id>', methods=['POST'])
    @login_required
    def undo_delete(deleted_id):
        deleted = DeletedItem.query.filter_by(
            id=deleted_id, user_id=current_user.id
        ).first()
        if not deleted:
            return jsonify({'success': False, 'message': 'Cannot undo'}), 404
        item = Item(
            name=deleted.name, category=deleted.category,
            is_active=deleted.is_active, to_procure=deleted.to_procure,
            consumed=deleted.consumed, user_id=deleted.user_id
        )
        db.session.add(item)
        db.session.delete(deleted)
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})

    @app.route('/api/dashboard-stats', methods=['GET'])
    @login_required
    def dashboard_stats():
        return jsonify(get_user_stats(current_user.id))

    def get_user_stats(user_id):
        return {
            'veg_procure_count': Item.query.filter_by(
                user_id=user_id, category='vegfruit', to_procure=True, consumed=False
            ).count(),
            'grocery_procure_count': Item.query.filter_by(
                user_id=user_id, category='grocery', to_procure=True, consumed=False
            ).count(),
            'total_veg': Item.query.filter_by(user_id=user_id, category='vegfruit').count(),
            'total_grocery': Item.query.filter_by(user_id=user_id, category='grocery').count(),
            'consumed_veg': Item.query.filter_by(
                user_id=user_id, category='vegfruit', consumed=True
            ).count(),
            'consumed_grocery': Item.query.filter_by(
                user_id=user_id, category='grocery', consumed=True
            ).count(),
        }

    # ============ ASSET LINKS (Play Store TWA) ============

    @app.route('/.well-known/assetlinks.json')
    def asset_links():
        return jsonify([{
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": os.environ.get('ANDROID_PACKAGE', 'com.homeneeds.app'),
                "sha256_cert_fingerprints": [
                    os.environ.get('ANDROID_SHA256', 'YOUR_SHA256_HERE')
                ]
            }
        }])

    # ============ ERROR HANDLERS ============

    @app.errorhandler(404)
    def not_found(e):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Not found'}), 404
        return redirect(url_for('dashboard'))

    @app.errorhandler(500)
    def server_error(e):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Server error'}), 500
        return redirect(url_for('dashboard'))

    return app


# Entry point — gunicorn uses this
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
