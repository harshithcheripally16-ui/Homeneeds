# build_exe.py
import subprocess
import sys
import os
import shutil
import time
import stat


def force_remove_readonly(func, path, excinfo):
    """Error handler for shutil.rmtree to handle read-only and locked files"""
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        func(path)
    except Exception:
        pass


def kill_running_exe():
    """Kill any running HomeNeeds.exe processes"""
    print("  Checking for running HomeNeeds processes...")

    if sys.platform == 'win32':
        try:
            # Find and kill HomeNeeds.exe
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq HomeNeeds.exe', '/FO', 'CSV', '/NH'],
                capture_output=True, text=True, timeout=10
            )

            if 'HomeNeeds.exe' in result.stdout:
                print("  Found running HomeNeeds.exe — killing process...")
                subprocess.run(
                    ['taskkill', '/F', '/IM', 'HomeNeeds.exe'],
                    capture_output=True, text=True, timeout=10
                )
                time.sleep(2)
                print("  ✓ Process terminated")
            else:
                print("  ✓ No running process found")

        except Exception as e:
            print(f"  Warning: Could not check processes: {e}")
            print("  Trying forced kill anyway...")
            try:
                subprocess.run(
                    ['taskkill', '/F', '/IM', 'HomeNeeds.exe'],
                    capture_output=True, text=True, timeout=10
                )
                time.sleep(2)
            except Exception:
                pass
    else:
        # Linux/Mac
        try:
            subprocess.run(['pkill', '-f', 'HomeNeeds'],
                           capture_output=True, timeout=10)
            time.sleep(1)
        except Exception:
            pass


def safe_remove_file(filepath, max_retries=5):
    """Safely remove a file with retries for locked files"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(filepath):
                os.chmod(filepath, stat.S_IWRITE | stat.S_IREAD)
                os.remove(filepath)
                return True
        except PermissionError:
            if attempt < max_retries - 1:
                print(
                    f"  File locked, retrying in 2s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"  ⚠ Could not delete {filepath}")
                print(f"    Please close HomeNeeds.exe manually and try again")
                return False
        except Exception:
            return True
    return False


def safe_remove_dir(dirpath, max_retries=3):
    """Safely remove a directory with retries"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath, onerror=force_remove_readonly)
                return True
        except PermissionError:
            if attempt < max_retries - 1:
                print(
                    f"  Directory locked, retrying in 2s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"  ⚠ Could not fully remove {dirpath}")
                return False
        except Exception:
            return True
    return False


def install_dependencies():
    """Install all required packages including jaraco modules"""
    print("\n📦 Installing / updating dependencies...")

    packages = [
        'pyinstaller',
        'setuptools',
        'packaging',
        'jaraco.text',
        'jaraco.functools',
        'jaraco.context',
        'jaraco.collections',
        'importlib-resources',
        'flask',
        'flask-sqlalchemy',
        'flask-login',
        'flask-mail',
        'werkzeug',
        'sqlalchemy',
    ]

    for pkg in packages:
        print(f"  Installing {pkg}...")
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', pkg],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    print("  ✓ All dependencies installed\n")


def clean_previous_builds():
    """Remove old build artifacts safely"""
    print("🧹 Cleaning previous builds...")

    # STEP 1: Kill any running HomeNeeds.exe first
    kill_running_exe()

    # STEP 2: Try to remove the exe file specifically first
    exe_path = os.path.join('dist', 'HomeNeeds.exe')
    if os.path.exists(exe_path):
        print(f"  Removing {exe_path}...")
        if not safe_remove_file(exe_path):
            print("\n" + "=" * 60)
            print("  ❌ Cannot delete HomeNeeds.exe")
            print("  ")
            print("  Please do ONE of the following:")
            print("  1. Close HomeNeeds.exe from Task Manager")
            print("     (Ctrl+Shift+Esc → find HomeNeeds → End Task)")
            print("  2. Close the browser tab running the app")
            print("  3. Restart your computer")
            print("  ")
            print("  Then run: python build_exe.py")
            print("=" * 60)
            sys.exit(1)
        else:
            print(f"  ✓ Removed {exe_path}")

    # STEP 3: Remove directories
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for d in dirs_to_clean:
        if os.path.exists(d):
            if safe_remove_dir(d):
                print(f"  Removed {d}/")
            else:
                print(f"  ⚠ Partially cleaned {d}/")

    # STEP 4: Remove spec and temp files
    files_to_clean = ['HomeNeeds.spec', 'launcher.py', 'app_bundled.py']
    for f in files_to_clean:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"  Removed {f}")
            except Exception:
                pass

    print("  ✓ Clean complete\n")


def create_launcher_script():
    """Create a wrapper script for PyInstaller - windowed mode, no console"""
    launcher_code = r'''
import sys
import os
import webbrowser
import threading
import time
import logging
import socket

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# Set up logging to file (no console in windowed mode)
log_dir = os.path.join(os.path.expanduser('~'), '.home_needs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Redirect stdout/stderr to log file in windowed mode
if hasattr(sys, '_MEIPASS'):
    try:
        sys.stdout = open(log_file, 'a', encoding='utf-8')
        sys.stderr = open(log_file, 'a', encoding='utf-8')
    except Exception:
        pass

# Set template and static folders
os.environ['FLASK_TEMPLATE_DIR'] = get_resource_path('templates')
os.environ['FLASK_STATIC_DIR'] = get_resource_path('static')

def check_port_available(port):
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except OSError:
        sock.close()
        return False

def find_available_port(start_port=5000):
    """Find an available port"""
    for port in range(start_port, start_port + 100):
        if check_port_available(port):
            return port
    return start_port

if __name__ == '__main__':
    sys.path.insert(0, get_resource_path('.'))
    
    from app_bundled import create_app
    
    app = create_app(
        template_folder=get_resource_path('templates'),
        static_folder=get_resource_path('static')
    )
    
    port = find_available_port(5000)
    logging.info(f"Starting Home Needs on port {port}")
    
    def open_browser():
        time.sleep(2)
        webbrowser.open(f'http://127.0.0.1:{port}')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Suppress Werkzeug logs in windowed mode
    import werkzeug.serving
    werkzeug.serving._log = lambda *args, **kwargs: None
    
    app.run(
        host='127.0.0.1',
        port=port,
        debug=False,
        use_reloader=False
    )
'''

    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_code)

    print("  ✓ Created launcher.py")


def create_bundled_app():
    """Create a modified app.py for PyInstaller bundling"""
    bundled_code = '''
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from config import Config
from models import db, User, Item, DeletedItem
from auth import mail, generate_verification_code, send_verification_email
import os

def create_app(template_folder=None, static_folder=None):
    kwargs = {}
    if template_folder:
        kwargs['template_folder'] = template_folder
    if static_folder:
        kwargs['static_folder'] = static_folder
    
    app = Flask(__name__, **kwargs)
    app.config.from_object(Config)
    
    db_path = os.path.join(os.path.expanduser('~'), '.home_needs', 'home_needs.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    db.init_app(app)
    mail.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()
    
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
                login_user(user)
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
            if not all([name, email, password, confirm_password]):
                msg = 'All fields are required'
                if request.is_json:
                    return jsonify({'success': False, 'message': msg}), 400
                flash(msg, 'error')
                return render_template('signup.html')
            if password != confirm_password:
                msg = 'Passwords do not match'
                if request.is_json:
                    return jsonify({'success': False, 'message': msg}), 400
                flash(msg, 'error')
                return render_template('signup.html')
            if len(password) < 6:
                msg = 'Password must be at least 6 characters'
                if request.is_json:
                    return jsonify({'success': False, 'message': msg}), 400
                flash(msg, 'error')
                return render_template('signup.html')
            if User.query.filter_by(email=email).first():
                msg = 'Email already registered'
                if request.is_json:
                    return jsonify({'success': False, 'message': msg}), 400
                flash(msg, 'error')
                return render_template('signup.html')
            if User.query.filter_by(name=name).first():
                msg = 'Username already taken'
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
                login_user(user)
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
        existing = Item.query.filter_by(user_id=user_id).first()
        if existing:
            return
        default_veg_fruits = [
            'Tomato', 'Potato', 'Onion', 'Carrot', 'Spinach', 'Broccoli',
            'Capsicum', 'Cucumber', 'Cabbage', 'Cauliflower', 'Green Beans',
            'Peas', 'Corn', 'Lettuce', 'Mushroom', 'Garlic', 'Ginger',
            'Apple', 'Banana', 'Orange', 'Mango', 'Grapes', 'Watermelon',
            'Strawberry', 'Pineapple', 'Papaya', 'Lemon', 'Pomegranate',
            'Guava', 'Kiwi'
        ]
        default_groceries = [
            'Rice', 'Wheat Flour', 'Sugar', 'Salt', 'Cooking Oil', 'Butter',
            'Milk', 'Bread', 'Eggs', 'Tea', 'Coffee', 'Pasta', 'Noodles',
            'Oats', 'Cornflakes', 'Biscuits', 'Jam', 'Honey', 'Ketchup',
            'Soy Sauce', 'Vinegar', 'Pepper', 'Turmeric', 'Cumin',
            'Coriander Powder', 'Chili Powder', 'Cinnamon', 'Cardamom',
            'Dal / Lentils', 'Chickpeas'
        ]
        for item_name in default_veg_fruits:
            db.session.add(Item(name=item_name, category='vegfruit', user_id=user_id))
        for item_name in default_groceries:
            db.session.add(Item(name=item_name, category='grocery', user_id=user_id))
        db.session.commit()
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        veg_procure_count = Item.query.filter_by(
            user_id=current_user.id, category='vegfruit', to_procure=True, consumed=False
        ).count()
        grocery_procure_count = Item.query.filter_by(
            user_id=current_user.id, category='grocery', to_procure=True, consumed=False
        ).count()
        total_veg = Item.query.filter_by(user_id=current_user.id, category='vegfruit').count()
        total_grocery = Item.query.filter_by(user_id=current_user.id, category='grocery').count()
        return render_template('dashboard.html',
            veg_procure_count=veg_procure_count,
            grocery_procure_count=grocery_procure_count,
            total_veg=total_veg,
            total_grocery=total_grocery,
            user=current_user
        )
    
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
    
    @app.route('/api/items/<category>', methods=['GET'])
    @login_required
    def get_items(category):
        items = Item.query.filter_by(
            user_id=current_user.id, category=category
        ).order_by(Item.name).all()
        return jsonify([item.to_dict() for item in items])
    
    @app.route('/api/items', methods=['POST'])
    @login_required
    def add_item():
        data = request.get_json()
        name = data.get('name', '').strip()
        category = data.get('category', '').strip()
        if not name or category not in ['vegfruit', 'grocery']:
            return jsonify({'success': False, 'message': 'Invalid data'}), 400
        existing = Item.query.filter_by(
            user_id=current_user.id, name=name, category=category
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Item already exists'}), 400
        item = Item(name=name, category=category, user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})
    
    @app.route('/api/items/<int:item_id>/toggle-procure', methods=['PUT'])
    @login_required
    def toggle_procure(item_id):
        item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
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
        item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        item.consumed = not item.consumed
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})
    
    @app.route('/api/items/<int:item_id>', methods=['DELETE'])
    @login_required
    def delete_item(item_id):
        item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
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
        deleted = DeletedItem.query.filter_by(id=deleted_id, user_id=current_user.id).first()
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
        veg_procure = Item.query.filter_by(
            user_id=current_user.id, category='vegfruit', to_procure=True, consumed=False
        ).count()
        grocery_procure = Item.query.filter_by(
            user_id=current_user.id, category='grocery', to_procure=True, consumed=False
        ).count()
        total_veg = Item.query.filter_by(user_id=current_user.id, category='vegfruit').count()
        total_grocery = Item.query.filter_by(user_id=current_user.id, category='grocery').count()
        consumed_veg = Item.query.filter_by(
            user_id=current_user.id, category='vegfruit', consumed=True
        ).count()
        consumed_grocery = Item.query.filter_by(
            user_id=current_user.id, category='grocery', consumed=True
        ).count()
        return jsonify({
            'veg_procure': veg_procure, 'grocery_procure': grocery_procure,
            'total_veg': total_veg, 'total_grocery': total_grocery,
            'consumed_veg': consumed_veg, 'consumed_grocery': consumed_grocery
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

    with open('app_bundled.py', 'w', encoding='utf-8') as f:
        f.write(bundled_code)

    print("  ✓ Created app_bundled.py")


def build_exe():
    """Build the application as a Windows .exe file"""

    print("=" * 60)
    print("  🏠 Building Home Needs Application (.exe)")
    print("  Mode: WINDOWED (no console)")
    print("=" * 60)

    # Step 1: Install dependencies
    install_dependencies()

    # Step 2: Clean old builds (now kills process first)
    clean_previous_builds()

    # Step 3: Create helper files
    print("📝 Creating build helper files...")
    create_launcher_script()
    create_bundled_app()
    print()

    # Step 4: Separator
    separator = ';' if sys.platform == 'win32' else ':'

    # Step 5: Hidden imports
    hidden_imports = [
        'flask', 'flask.json', 'flask.templating',
        'flask_sqlalchemy', 'flask_login', 'flask_mail',
        'sqlalchemy', 'sqlalchemy.sql.default_comparator', 'sqlalchemy.ext.baked',
        'werkzeug', 'werkzeug.security', 'werkzeug.serving', 'werkzeug.debug',
        'jinja2', 'jinja2.ext', 'markupsafe', 'itsdangerous',
        'click', 'blinker',
        'email', 'email.mime.multipart', 'email.mime.text',
        'email.mime.base', 'email.utils',
        'smtplib', 'ssl', 'json', 'datetime', 'random', 'string',
        'os', 'sys', 'threading', 'time', 'webbrowser', 'logging', 'socket',
        'jaraco', 'jaraco.text', 'jaraco.functools',
        'jaraco.context', 'jaraco.collections',
        'importlib_resources', 'importlib.resources', 'importlib.metadata',
        'pkg_resources', 'setuptools',
        'packaging', 'packaging.version', 'packaging.specifiers', 'packaging.requirements',
    ]

    collect_packages = [
        'jaraco', 'jaraco.text', 'jaraco.functools',
        'jaraco.context', 'importlib_resources',
    ]

    # Step 6: Build command — WINDOWED
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=HomeNeeds',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--clean',
        f'--add-data=templates{separator}templates',
        f'--add-data=static{separator}static',
        f'--add-data=config.py{separator}.',
        f'--add-data=models.py{separator}.',
        f'--add-data=auth.py{separator}.',
        f'--add-data=app_bundled.py{separator}.',
    ]

    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])

    for pkg in collect_packages:
        cmd.extend(['--collect-all', pkg])

    cmd.extend(['--collect-submodules', 'jaraco'])
    cmd.extend(['--collect-submodules', 'flask'])
    cmd.extend(['--collect-submodules', 'sqlalchemy'])
    cmd.extend(['--collect-submodules', 'werkzeug'])
    cmd.extend(['--collect-submodules', 'pkg_resources'])

    cmd.append('launcher.py')

    print("🔨 Running PyInstaller (windowed mode)...")
    print("   This may take a few minutes...\n")

    try:
        process = subprocess.run(cmd, capture_output=False, text=True)

        if process.returncode != 0:
            print("\n⚠️  Standard build failed. Trying .spec file approach...")
            build_with_spec_file(separator, hidden_imports)
            return

        exe_name = 'HomeNeeds.exe' if sys.platform == 'win32' else 'HomeNeeds'
        exe_path = os.path.join('dist', exe_name)

        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)
            print("\n" + "=" * 60)
            print("  ✅ BUILD SUCCESSFUL!")
            print(f"  📁 Executable: {os.path.abspath(exe_path)}")
            print(f"  📊 Size: {file_size:.1f} MB")
            print("  ")
            print("  ✓ No console window will appear")
            print("  ✓ Browser opens automatically")
            print("  ✓ Logs: ~/.home_needs/app.log")
            print("  ")
            print("  To run: double-click HomeNeeds.exe in dist/")
            print("=" * 60)
        else:
            print("\n❌ Build completed but executable not found.")

    except Exception as e:
        print(f"\n❌ Build error: {e}")
        print("   Trying .spec file method...")
        build_with_spec_file(separator, hidden_imports)


def build_with_spec_file(separator, hidden_imports):
    """Alternative build using .spec file"""

    print("\n📝 Creating custom .spec file (windowed mode)...")

    hidden_imports_str = ',\n        '.join(
        [f"'{imp}'" for imp in hidden_imports])

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

extra_datas = []
extra_binaries = []
extra_hiddenimports = []

for pkg in ['jaraco', 'jaraco.text', 'jaraco.functools', 'jaraco.context',
            'importlib_resources', 'flask', 'sqlalchemy', 'werkzeug']:
    try:
        d, b, h = collect_all(pkg)
        extra_datas.extend(d)
        extra_binaries.extend(b)
        extra_hiddenimports.extend(h)
    except Exception as e:
        print(f"Warning: Could not collect {{pkg}}: {{e}}")

for pkg in ['jaraco', 'flask', 'sqlalchemy', 'werkzeug', 'pkg_resources',
            'email', 'jinja2']:
    try:
        extra_hiddenimports.extend(collect_submodules(pkg))
    except Exception:
        pass

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=extra_binaries,
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('config.py', '.'),
        ('models.py', '.'),
        ('auth.py', '.'),
        ('app_bundled.py', '.'),
    ] + extra_datas,
    hiddenimports=[
        {hidden_imports_str}
    ] + extra_hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HomeNeeds',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
)
'''

    with open('HomeNeeds.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("  ✓ Created HomeNeeds.spec")
    print("\n🔨 Building with .spec file (windowed)...")

    try:
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller',
            '--noconfirm', '--clean', 'HomeNeeds.spec'
        ])

        exe_name = 'HomeNeeds.exe' if sys.platform == 'win32' else 'HomeNeeds'
        exe_path = os.path.join('dist', exe_name)

        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)
            print("\n" + "=" * 60)
            print("  ✅ BUILD SUCCESSFUL! (via .spec file)")
            print(f"  📁 Executable: {os.path.abspath(exe_path)}")
            print(f"  📊 Size: {file_size:.1f} MB")
            print("  ")
            print("  ✓ No console window")
            print("  ✓ Browser opens automatically")
            print("  ✓ Logs: ~/.home_needs/app.log")
            print("=" * 60)
        else:
            print("\n❌ Executable not found after build.")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        print("\n🔧 Try: pip install pyinstaller==5.13.2")


if __name__ == '__main__':
    build_exe()
