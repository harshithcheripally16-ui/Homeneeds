# setup.py
"""
Home Needs - Project Setup Script
Handles both initial setup and restructuring.
"""
import subprocess
import sys
import os
import shutil


def setup():
    print("=" * 60)
    print("  🏠 Home Needs - Project Setup")
    print("=" * 60)

    # Detect which structure we're in
    is_new_structure = os.path.exists('backend') and os.path.exists('frontend')
    is_old_structure = os.path.exists('templates') and os.path.exists('static')

    if is_old_structure and not is_new_structure:
        print("\n📂 Detected OLD project structure")
        print("   Would you like to restructure for Play Store deployment?")
        answer = input(
            "   Type 'yes' to restructure, or 'no' to keep current: ").strip().lower()

        if answer == 'yes':
            restructure_project()
        else:
            setup_old_structure()
            return
    elif is_new_structure:
        print("\n📂 Detected NEW project structure (Play Store ready)")
    else:
        print("\n📂 Setting up new project...")
        create_new_structure()

    # Install backend dependencies
    print("\n📦 Installing backend dependencies...")
    req_file = 'backend/requirements.txt'
    if os.path.exists(req_file):
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', req_file
        ])
        print("  ✓ Backend dependencies installed")
    else:
        print("  ⚠ requirements.txt not found in backend/")

    # Email configuration info
    print("\n📧 Email Configuration")
    print("─" * 40)
    print("  For email verification, set these environment variables:")
    print("  ")
    print("  For LOCAL development:")
    print("    set MAIL_USERNAME=your-email@gmail.com")
    print("    set MAIL_PASSWORD=your-gmail-app-password")
    print("  ")
    print("  For PRODUCTION (Render.com):")
    print("    Set them in the Render dashboard → Environment")
    print("  ")
    print("  To get a Gmail App Password:")
    print("    1. Google Account → Security → 2-Step Verification → ON")
    print("    2. Google Account → Security → App Passwords → Generate")
    print("  ")
    print("  Note: If not configured, verification code prints to terminal.")

    # Generate icons if needed
    icons_dir = os.path.join('frontend', 'icons')
    if not os.path.exists(icons_dir) or len(os.listdir(icons_dir)) == 0:
        print("\n🎨 Generating app icons...")
        if os.path.exists('generate_icons.py'):
            subprocess.check_call([sys.executable, 'generate_icons.py'])
        else:
            print("  ⚠ generate_icons.py not found — create icons manually")
            os.makedirs(icons_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("  ✅ Setup Complete!")
    print("  ")
    print("  To run LOCALLY (development):")
    print("    cd backend")
    print("    python app.py")
    print("    Open http://localhost:5000")
    print("  ")
    print("  To deploy to CLOUD (production):")
    print("    1. Push to GitHub")
    print("    2. Connect to Render.com")
    print("    3. See README.md for full instructions")
    print("  ")
    print("  To build DESKTOP .exe:")
    print("    python build_exe.py")
    print("=" * 60)


def setup_old_structure():
    """Setup for the original flat structure"""
    print("\n📦 Installing dependencies...")
    if os.path.exists('requirements.txt'):
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
    os.makedirs('static/images', exist_ok=True)
    print("  ✓ Dependencies installed")
    print("\n  To run: python app.py")
    print("  Open http://localhost:5000")


def restructure_project():
    """Migrate from old flat structure to new backend/frontend structure"""
    print("\n🔄 Restructuring project for Play Store deployment...")
    print("   (Your original files will be backed up)\n")

    # Create backup
    backup_dir = 'backup_old_structure'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"  Created backup directory: {backup_dir}/")

    # Create new directories
    dirs_to_create = [
        'backend',
        'frontend',
        'frontend/css',
        'frontend/js',
        'frontend/pages',
        'frontend/icons',
        'desktop',
    ]

    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)

    print("  ✓ Created new directory structure")

    # Move backend files
    backend_files = {
        'app.py': 'backend/app.py',
        'config.py': 'backend/config.py',
        'models.py': 'backend/models.py',
        'auth.py': 'backend/auth.py',
        'requirements.txt': 'backend/requirements.txt',
    }

    for src, dst in backend_files.items():
        if os.path.exists(src):
            # Backup
            shutil.copy2(src, os.path.join(backup_dir, src))
            # Move
            shutil.copy2(src, dst)
            print(f"  Copied {src} → {dst}")

    # Move frontend files
    if os.path.exists('static/css/style.css'):
        shutil.copy2('static/css/style.css', 'frontend/css/style.css')
        print("  Copied static/css/style.css → frontend/css/style.css")

    if os.path.exists('static/js/app.js'):
        shutil.copy2('static/js/app.js', 'frontend/js/app.js')
        print("  Copied static/js/app.js → frontend/js/app.js")

    # Move icons if they exist
    old_icons = 'static/icons'
    if os.path.exists(old_icons):
        for f in os.listdir(old_icons):
            src_path = os.path.join(old_icons, f)
            dst_path = os.path.join('frontend/icons', f)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
        print("  Copied static/icons/ → frontend/icons/")

    # Move HTML templates
    if os.path.exists('templates'):
        for f in os.listdir('templates'):
            if f.endswith('.html'):
                src_path = os.path.join('templates', f)
                dst_path = os.path.join('frontend/pages', f)
                shutil.copy2(src_path, dst_path)
        print("  Copied templates/*.html → frontend/pages/")

    # Move desktop-only files
    desktop_files = ['build_exe.py', 'app_bundled.py', 'launcher.py']
    for f in desktop_files:
        if os.path.exists(f):
            shutil.copy2(f, os.path.join(backup_dir, f))
            # Keep build_exe.py in root too for convenience
            if f == 'build_exe.py':
                shutil.copy2(f, os.path.join('desktop', f))
            print(f"  Backed up {f}")

    # Backup old directories
    for d in ['templates', 'static']:
        if os.path.exists(d):
            backup_path = os.path.join(backup_dir, d)
            if not os.path.exists(backup_path):
                shutil.copytree(d, backup_path)
            print(f"  Backed up {d}/ → {backup_dir}/{d}/")

    print(f"\n  ✓ Restructuring complete!")
    print(f"  ✓ Originals backed up to: {backup_dir}/")
    print(f"  ")
    print(f"  ⚠ IMPORTANT: You still need to:")
    print(f"    1. Update backend/app.py with production version")
    print(f"    2. Update backend/config.py with dev/prod/test configs")
    print(f"    3. Update backend/requirements.txt (add gunicorn, flask-cors)")
    print(f"    4. Create frontend/manifest.json")
    print(f"    5. Create frontend/js/sw.js")
    print(f"    6. Add PWA meta tags to all HTML pages")
    print(f"    7. Create backend/gunicorn_config.py, Procfile, runtime.txt")


def create_new_structure():
    """Create the new structure from scratch"""
    dirs_to_create = [
        'backend',
        'frontend',
        'frontend/css',
        'frontend/js',
        'frontend/pages',
        'frontend/icons',
    ]

    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)

    print("  ✓ Created project directories")


if __name__ == '__main__':
    setup()
