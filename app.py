import os
import json
import logging
import sys
import zipfile
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import subprocess
import tempfile
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'a15-patcher-secret-key-2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
DATA_FILE = 'data.json'
ALLOWED_EXTENSIONS = {'jar'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_data(data):
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving data: {e}")
        return False

def process_jar_file(jar_path, name, description):
    """Process the uploaded JAR file using existing patch scripts"""
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            logging.info(f"Processing JAR file: {jar_path}")
            
            # Validate file size and type
            if os.path.getsize(jar_path) < 1000:  # Less than 1KB is likely invalid
                return {
                    'success': False,
                    'message': 'Geçersiz JAR dosyası - dosya çok küçük'
                }
            
            # Check if it's a valid ZIP/JAR file
            try:
                import zipfile
                with zipfile.ZipFile(jar_path, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    if not any(f.endswith('.dex') for f in file_list):
                        return {
                            'success': False,
                            'message': 'Bu bir Android JAR dosyası değil (DEX dosyası bulunamadı)'
                        }
            except zipfile.BadZipFile:
                return {
                    'success': False,
                    'message': 'Geçersiz JAR/ZIP dosyası'
                }
            
            # Determine jar type based on file contents
            jar_type = detect_jar_type(jar_path)
            
            # Copy JAR to processing directory
            processing_jar = os.path.join(temp_dir, f"{jar_type}.jar")
            shutil.copy2(jar_path, processing_jar)
            
            # Extract JAR
            extract_dir = os.path.join(temp_dir, jar_type)
            os.makedirs(extract_dir, exist_ok=True)
            
            # Extract with 7z command (simulate the GitHub Actions process)
            extract_result = subprocess.run([
                '7z', 'x', processing_jar, f'-o{extract_dir}'
            ], capture_output=True, text=True)
            
            if extract_result.returncode != 0:
                # Fallback to Python zipfile
                with zipfile.ZipFile(processing_jar, 'r') as zip_file:
                    zip_file.extractall(extract_dir)
            
            # Process based on jar type
            success = apply_patches(extract_dir, jar_type, temp_dir)
            
            if success:
                # Create patched JAR
                patched_jar_path = create_patched_jar(extract_dir, jar_type, jar_path)
                
                return {
                    'success': True,
                    'message': f'{jar_type.upper()} dosyası başarıyla yamalandı: {name}',
                    'processed_file': patched_jar_path,
                    'jar_type': jar_type
                }
            else:
                return {
                    'success': False,
                    'message': f'{jar_type.upper()} dosyası yamalanırken hata oluştu'
                }
                
    except Exception as e:
        logging.error(f"Error processing JAR file: {e}")
        return {
            'success': False,
            'message': f'İşlem sırasında hata oluştu: {str(e)}'
        }

def detect_jar_type(jar_path):
    """Detect the type of JAR file (framework, services, miui-services)"""
    try:
        with zipfile.ZipFile(jar_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            
            # Check for MIUI-specific files
            if any('miui' in f.lower() or 'xiaomi' in f.lower() for f in file_list):
                return 'miui-services'
            
            # Check for services-specific files
            if any('com/android/server/' in f for f in file_list):
                return 'services'
            
            # Check for framework-specific files
            if any('android/content/pm/' in f or 'android/util/' in f for f in file_list):
                return 'framework'
            
            # Default to framework
            return 'framework'
            
    except Exception:
        return 'framework'

def apply_patches(extract_dir, jar_type, temp_dir):
    """Apply patches using existing patch scripts"""
    try:
        # Change to the temp directory to run patch scripts
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # Copy extracted files to expected directory structure
        if jar_type == 'framework':
            # Look for classes directories
            classes_dirs = [d for d in os.listdir(extract_dir) if d.startswith('classes') or d == 'classes']
            if not classes_dirs and os.path.exists(os.path.join(extract_dir, 'classes.dex')):
                # Need to decompile DEX files first
                success = decompile_dex_files(extract_dir, ['classes'])
            else:
                # Move existing classes directories
                for class_dir in classes_dirs:
                    src = os.path.join(extract_dir, class_dir)
                    dst = os.path.join(temp_dir, class_dir)
                    if os.path.exists(src):
                        shutil.move(src, dst)
                success = True
            
            if success:
                # Import and run framework patch
                sys.path.insert(0, original_cwd)
                import framework_patch
                framework_patch.modify_smali_files(['classes', 'classes2', 'classes3', 'classes4', 'classes5'])
        
        elif jar_type == 'services':
            # Similar for services
            classes_dirs = [d for d in os.listdir(extract_dir) if d.startswith('services_classes')]
            if not classes_dirs:
                success = decompile_dex_files(extract_dir, ['services_classes'])
            else:
                for class_dir in classes_dirs:
                    src = os.path.join(extract_dir, class_dir)
                    dst = os.path.join(temp_dir, class_dir)
                    if os.path.exists(src):
                        shutil.move(src, dst)
                success = True
            
            if success:
                sys.path.insert(0, original_cwd)
                import services_patch
                services_patch.modify_smali_files(['services_classes', 'services_classes2', 'services_classes3', 'services_classes4', 'services_classes5'])
        
        elif jar_type == 'miui-services':
            # Similar for MIUI services
            classes_dir = 'miui_services_classes'
            if not os.path.exists(os.path.join(extract_dir, classes_dir)):
                success = decompile_dex_files(extract_dir, [classes_dir])
            else:
                src = os.path.join(extract_dir, classes_dir)
                dst = os.path.join(temp_dir, classes_dir)
                if os.path.exists(src):
                    shutil.move(src, dst)
                success = True
            
            if success:
                sys.path.insert(0, original_cwd)
                # Import the MIUI service patch with correct name
                import importlib.util
                spec = importlib.util.spec_from_file_location("miui_service_patch", os.path.join(original_cwd, "miui-service_Patch.py"))
                miui_service_patch = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(miui_service_patch)
                miui_service_patch.modify_smali_files([classes_dir])
        
        os.chdir(original_cwd)
        return True
        
    except Exception as e:
        logging.error(f"Error applying patches: {e}")
        os.chdir(original_cwd)
        return False

def decompile_dex_files(extract_dir, target_dirs):
    """Decompile DEX files using baksmali"""
    try:
        baksmali_path = os.path.join(os.getcwd(), 'tools', 'baksmali.jar')
        if not os.path.exists(baksmali_path):
            logging.error("baksmali.jar not found in tools directory")
            return False
        
        # Find DEX files
        dex_files = [f for f in os.listdir(extract_dir) if f.endswith('.dex')]
        
        for i, dex_file in enumerate(dex_files):
            dex_path = os.path.join(extract_dir, dex_file)
            if i == 0:
                output_dir = target_dirs[0] if target_dirs else 'classes'
            else:
                output_dir = f"{target_dirs[0]}{i+1}" if target_dirs else f'classes{i+1}'
            
            output_path = os.path.join(extract_dir, '..', output_dir)
            
            # Run baksmali
            result = subprocess.run([
                'java', '-jar', baksmali_path, 'd', '-a', '35', dex_path, '-o', output_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.error(f"Failed to decompile {dex_file}: {result.stderr}")
                return False
        
        return True
        
    except Exception as e:
        logging.error(f"Error decompiling DEX files: {e}")
        return False

def create_patched_jar(extract_dir, jar_type, original_jar_path):
    """Create patched JAR file"""
    try:
        # Get the original filename and create a patched version
        original_filename = os.path.basename(original_jar_path)
        name_without_ext = os.path.splitext(original_filename)[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        patched_filename = f"{name_without_ext}_patched_{timestamp}.jar"
        patched_path = os.path.join(app.config['UPLOAD_FOLDER'], patched_filename)
        
        # Create ZIP file with patched content
        with zipfile.ZipFile(patched_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, extract_dir)
                    zip_file.write(file_path, arc_name)
        
        return patched_path
        
    except Exception as e:
        logging.error(f"Error creating patched JAR: {e}")
        return None

@app.route('/')
def index():
    """Main upload page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Validate request
        if 'jar_file' not in request.files:
            flash('Dosya seçilmedi', 'error')
            return redirect(request.url)
        
        file = request.files['jar_file']
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate inputs
        if file.filename == '':
            flash('Dosya seçilmedi', 'error')
            return redirect(request.url)
        
        if not name:
            flash('İsim alanı gereklidir', 'error')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Sadece .jar dosyaları kabul edilir', 'error')
            return redirect(request.url)
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        
        # Process the file
        result = process_jar_file(filepath, name, description)
        
        # Save metadata
        data = load_data()
        entry = {
            'id': len(data) + 1,
            'name': name,
            'description': description,
            'filename': filename,
            'filepath': filepath,
            'upload_time': datetime.now().isoformat(),
            'processed': result['success'],
            'message': result['message']
        }
        data.append(entry)
        save_data(data)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
            
        return render_template('result.html', 
                             entry=entry, 
                             success=result['success'])
        
    except Exception as e:
        logging.error(f"Upload error: {e}")
        flash(f'Yükleme sırasında hata oluştu: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/history')
def history():
    """Show upload history"""
    data = load_data()
    return render_template('history.html', entries=data)

@app.route('/api/status')
def api_status():
    """API endpoint for status check"""
    return jsonify({
        'status': 'running',
        'uploads_count': len(load_data()),
        'version': '1.0.0'
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed files"""
    try:
        from flask import send_from_directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Download error: {e}")
        flash('Dosya indirilemedi', 'error')
        return redirect(url_for('history'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)