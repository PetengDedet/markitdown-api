"""Main Flask application for markitdown API."""
import os
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session as flask_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from markitdown import MarkItDown
from models import init_db, get_session, init_default_user, init_default_config, User, Conversion, AppConfig
from ocr_utils import convert_pdf_with_ocr_fallback, extract_text_from_image
from llm_utils import process_document, initialize_llm, get_model_info, generate_title
from analysis_utils import (
    extract_keywords, 
    predict_categories, 
    predict_severity, 
    predict_title_simple,
    extract_text_statistics
)
import threading
import queue
import logging
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
engine = init_db()
db_session = get_session(engine)
init_default_user(db_session)
init_default_config(db_session)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize MarkItDown
md = MarkItDown()


class TimeoutError(Exception):
    """Custom timeout exception."""
    pass


def run_with_timeout(func, args=(), kwargs=None, timeout_duration=300):
    """
    Run a function with a timeout using threading.
    
    Args:
        func: Function to run
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        timeout_duration: Timeout in seconds
        
    Returns:
        Result of the function
        
    Raises:
        TimeoutError: If function execution exceeds timeout
    """
    if kwargs is None:
        kwargs = {}
    
    result_queue = queue.Queue()
    exception_queue = queue.Queue()
    
    def worker():
        try:
            result = func(*args, **kwargs)
            result_queue.put(result)
        except Exception as e:
            exception_queue.put(e)
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout_duration)
    
    if thread.is_alive():
        # Thread is still running, timeout occurred
        raise TimeoutError(f"Processing timeout exceeded ({timeout_duration} seconds)")
    
    # Check if there was an exception
    if not exception_queue.empty():
        raise exception_queue.get()
    
    # Get the result
    if not result_queue.empty():
        return result_queue.get()
    
    raise Exception("Function did not return a result")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return db_session.query(User).get(int(user_id))


def allowed_file(filename):
    """Check if file extension is allowed based on config."""
    config = db_session.query(AppConfig).filter_by(key='allowed_extensions').first()
    if config:
        allowed_extensions = [ext.strip() for ext in config.value.split(',')]
        return any(filename.lower().endswith(ext) for ext in allowed_extensions)
    return True


@app.route('/')
def index():
    """Home page - redirect to upload page if authenticated, else to login."""
    if current_user.is_authenticated:
        return redirect(url_for('upload_page'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('upload_page'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db_session.query(User).filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            # Validate next_page to prevent open redirect vulnerability
            # Only allow relative URLs (no scheme or netloc)
            if next_page:
                parsed = urlparse(next_page)
                # Check if it's a relative URL with no external domain
                if parsed.netloc == '' and parsed.scheme == '':
                    return redirect(next_page)
            return redirect(url_for('upload_page'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    return redirect(url_for('login'))


@app.route('/config', methods=['GET', 'POST'])
@login_required
def config_page():
    """Application configuration page."""
    if request.method == 'POST':
        # Update username and password
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        
        if new_username and new_username != current_user.username:
            # Check if username already exists
            existing = db_session.query(User).filter_by(username=new_username).first()
            if existing and existing.id != current_user.id:
                flash('Username already exists', 'error')
            else:
                current_user.username = new_username
                db_session.commit()
                flash('Username updated successfully', 'success')
        
        if new_password:
            current_user.set_password(new_password)
            db_session.commit()
            flash('Password updated successfully', 'success')
        
        # Update allowed extensions
        allowed_extensions = request.form.get('allowed_extensions')
        if allowed_extensions:
            config = db_session.query(AppConfig).filter_by(key='allowed_extensions').first()
            if config:
                config.value = allowed_extensions
                db_session.commit()
                flash('Allowed extensions updated', 'success')
        
        # Update max file size
        max_file_size = request.form.get('max_file_size')
        if max_file_size:
            config = db_session.query(AppConfig).filter_by(key='max_file_size').first()
            if config:
                config.value = max_file_size
                db_session.commit()
                flash('Max file size updated', 'success')
        
        # Update processing timeout
        processing_timeout = request.form.get('processing_timeout')
        if processing_timeout:
            config = db_session.query(AppConfig).filter_by(key='processing_timeout').first()
            if config:
                config.value = processing_timeout
                db_session.commit()
                flash('Processing timeout updated', 'success')
        
        # Update max OCR pages
        max_ocr_pages = request.form.get('max_ocr_pages')
        if max_ocr_pages:
            config = db_session.query(AppConfig).filter_by(key='max_ocr_pages').first()
            if config:
                config.value = max_ocr_pages
                db_session.commit()
                flash('Max OCR pages updated', 'success')
        
        # Update LLM enabled
        llm_enabled = request.form.get('llm_enabled')
        if llm_enabled is not None:
            config = db_session.query(AppConfig).filter_by(key='llm_enabled').first()
            if config:
                config.value = 'true' if llm_enabled == 'on' else 'false'
                db_session.commit()
                flash('LLM processing setting updated', 'success')
        
        # Update LLM task
        llm_task = request.form.get('llm_task')
        if llm_task:
            config = db_session.query(AppConfig).filter_by(key='llm_task').first()
            if config:
                config.value = llm_task
                db_session.commit()
                flash('LLM task updated', 'success')
        
        # Update LLM max tokens
        llm_max_tokens = request.form.get('llm_max_tokens')
        if llm_max_tokens:
            config = db_session.query(AppConfig).filter_by(key='llm_max_tokens').first()
            if config:
                config.value = llm_max_tokens
                db_session.commit()
                flash('LLM max tokens updated', 'success')
        
        # Update LLM temperature
        llm_temperature = request.form.get('llm_temperature')
        if llm_temperature:
            config = db_session.query(AppConfig).filter_by(key='llm_temperature').first()
            if config:
                config.value = llm_temperature
                db_session.commit()
                flash('LLM temperature updated', 'success')
    
    # Get current config
    allowed_ext_config = db_session.query(AppConfig).filter_by(key='allowed_extensions').first()
    max_size_config = db_session.query(AppConfig).filter_by(key='max_file_size').first()
    processing_timeout_config = db_session.query(AppConfig).filter_by(key='processing_timeout').first()
    max_ocr_pages_config = db_session.query(AppConfig).filter_by(key='max_ocr_pages').first()
    llm_enabled_config = db_session.query(AppConfig).filter_by(key='llm_enabled').first()
    llm_task_config = db_session.query(AppConfig).filter_by(key='llm_task').first()
    llm_max_tokens_config = db_session.query(AppConfig).filter_by(key='llm_max_tokens').first()
    llm_temperature_config = db_session.query(AppConfig).filter_by(key='llm_temperature').first()
    
    # Get LLM model info
    model_info = get_model_info()
    
    return render_template('config.html', 
                         username=current_user.username,
                         allowed_extensions=allowed_ext_config.value if allowed_ext_config else '',
                         max_file_size=max_size_config.value if max_size_config else '',
                         processing_timeout=processing_timeout_config.value if processing_timeout_config else '300',
                         max_ocr_pages=max_ocr_pages_config.value if max_ocr_pages_config else '50',
                         llm_enabled=llm_enabled_config.value if llm_enabled_config else 'false',
                         llm_task=llm_task_config.value if llm_task_config else 'summarize_and_correct',
                         llm_max_tokens=llm_max_tokens_config.value if llm_max_tokens_config else '2048',
                         llm_temperature=llm_temperature_config.value if llm_temperature_config else '0.7',
                         llm_model_info=model_info)


@app.route('/recent')
@login_required
def recent_conversions():
    """Page showing recent conversions in a table."""
    conversions = db_session.query(Conversion).order_by(Conversion.upload_time.desc()).limit(50).all()
    return render_template('recent.html', conversions=conversions)


@app.route('/upload')
@login_required
def upload_page():
    """Interactive upload page with chat-style interface."""
    return render_template('upload.html')


@app.route('/api/convert', methods=['POST'])
@login_required
def convert_document():
    """API endpoint to convert uploaded document to markdown."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Get selected features from request
    features = request.form.get('features', '')
    selected_features = set(features.split(',')) if features else set()
    
    # Available features
    FEATURE_TITLE = 'title_prediction'
    FEATURE_MARKDOWN = 'markdown_extraction'
    FEATURE_CATEGORY = 'document_categorization'
    FEATURE_KEYWORDS = 'keyword_extraction'
    FEATURE_SEVERITY = 'severity_classification'
    FEATURE_SUMMARY = 'summarization'
    FEATURE_CORRECTION = 'correction'
    
    filepath = None
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Get timeout and max OCR pages from config
        timeout_config = db_session.query(AppConfig).filter_by(key='processing_timeout').first()
        timeout_seconds = int(timeout_config.value) if timeout_config else 300
        
        max_ocr_pages_config = db_session.query(AppConfig).filter_by(key='max_ocr_pages').first()
        max_ocr_pages = int(max_ocr_pages_config.value) if max_ocr_pages_config else 50
        
        # Define the conversion function
        def do_conversion():
            # Check if file is an image
            if filepath.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                return extract_text_from_image(filepath)
            elif filepath.lower().endswith('.pdf'):
                return convert_pdf_with_ocr_fallback(filepath, md, max_pages=max_ocr_pages)
            else:
                result = md.convert(filepath)
                return result.text_content
        
        # Convert to markdown with timeout (always performed)
        try:
            markdown_content = run_with_timeout(do_conversion, timeout_duration=timeout_seconds)
        except TimeoutError:
            # Clean up the file
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Processing timeout exceeded ({timeout_seconds} seconds)'}), 408
        
        # Initialize result variables
        summary_content = None
        corrected_content = None
        predicted_title = None
        categories_data = None
        keywords_data = None
        severity_data = None
        
        # Check if LLM is enabled for title, summary, and correction
        llm_enabled_config = db_session.query(AppConfig).filter_by(key='llm_enabled').first()
        llm_enabled = llm_enabled_config and llm_enabled_config.value.lower() == 'true'
        
        # Process Title Prediction
        if FEATURE_TITLE in selected_features or not selected_features:
            try:
                if llm_enabled:
                    # Use LLM for title generation
                    predicted_title = generate_title(markdown_content, max_tokens=50, temperature=0.5)
                    if predicted_title:
                        logger.info(f"Generated title (LLM): {predicted_title}")
                
                # Fallback to simple heuristics if LLM fails or not enabled
                if not predicted_title:
                    predicted_title = predict_title_simple(markdown_content)
                    if predicted_title:
                        logger.info(f"Generated title (heuristic): {predicted_title}")
                        
            except Exception as e:
                logger.error(f"Title prediction error: {str(e)}")
                predicted_title = None
        
        # Process Categorization
        if FEATURE_CATEGORY in selected_features or not selected_features:
            try:
                categories = predict_categories(markdown_content)
                if categories:
                    categories_data = json.dumps(categories)
                    logger.info(f"Predicted {len(categories)} categories")
            except Exception as e:
                logger.error(f"Category prediction error: {str(e)}")
        
        # Process Keyword Extraction
        if FEATURE_KEYWORDS in selected_features or not selected_features:
            try:
                keywords = extract_keywords(markdown_content, max_keywords=10)
                if keywords:
                    keywords_data = json.dumps(keywords)
                    logger.info(f"Extracted {len(keywords)} keywords")
            except Exception as e:
                logger.error(f"Keyword extraction error: {str(e)}")
        
        # Process Severity Classification
        if FEATURE_SEVERITY in selected_features or not selected_features:
            try:
                severity = predict_severity(markdown_content)
                if severity:
                    severity_data = severity.get('severity', 'Normal')
                    logger.info(f"Predicted severity: {severity_data}")
            except Exception as e:
                logger.error(f"Severity prediction error: {str(e)}")
        
        # Process Summarization
        if FEATURE_SUMMARY in selected_features or not selected_features:
            if llm_enabled:
                try:
                    # Get LLM configuration
                    llm_max_tokens_config = db_session.query(AppConfig).filter_by(key='llm_max_tokens').first()
                    llm_max_tokens = int(llm_max_tokens_config.value) if llm_max_tokens_config else 2048
                    
                    llm_temperature_config = db_session.query(AppConfig).filter_by(key='llm_temperature').first()
                    llm_temperature = float(llm_temperature_config.value) if llm_temperature_config else 0.7
                    
                    logger.info(f"Processing summarization with LLM")
                    
                    # Process document with LLM for summarization
                    summary_content = process_document(
                        markdown_content,
                        task='summarize_and_correct',
                        max_tokens=llm_max_tokens,
                        temperature=llm_temperature
                    )
                    
                    if summary_content:
                        logger.info("Summarization completed successfully")
                    else:
                        logger.warning("Summarization returned no content")
                        
                except Exception as e:
                    logger.error(f"Summarization error: {str(e)}")
                    summary_content = None
        
        # Process Correction
        if FEATURE_CORRECTION in selected_features or not selected_features:
            if llm_enabled:
                try:
                    # Get LLM configuration
                    llm_max_tokens_config = db_session.query(AppConfig).filter_by(key='llm_max_tokens').first()
                    llm_max_tokens = int(llm_max_tokens_config.value) if llm_max_tokens_config else 2048
                    
                    llm_temperature_config = db_session.query(AppConfig).filter_by(key='llm_temperature').first()
                    llm_temperature = float(llm_temperature_config.value) if llm_temperature_config else 0.7
                    
                    logger.info(f"Processing correction with LLM")
                    
                    # Process document with LLM for correction only
                    corrected_content = process_document(
                        markdown_content,
                        task='correct_only',
                        max_tokens=llm_max_tokens,
                        temperature=llm_temperature
                    )
                    
                    if corrected_content:
                        logger.info("Correction completed successfully")
                    else:
                        logger.warning("Correction returned no content")
                        
                except Exception as e:
                    logger.error(f"Correction error: {str(e)}")
                    corrected_content = None
        
        # Save to database
        conversion = Conversion(
            filename=filename,
            original_path=filepath,
            markdown_content=markdown_content,
            summary_content=summary_content,
            predicted_title=predicted_title,
            file_size=file_size,
            categories=categories_data,
            keywords=keywords_data,
            severity=severity_data,
            corrected_content=corrected_content
        )
        db_session.add(conversion)
        db_session.commit()
        
        # Return response with all available data
        response_data = {
            'success': True,
            'id': conversion.id,
            'filename': conversion.filename,
            'upload_time': conversion.upload_time.isoformat(),
            'file_size': conversion.file_size
        }
        
        # Add features based on selection or defaults
        if FEATURE_MARKDOWN in selected_features or not selected_features:
            response_data['markdown_content'] = conversion.markdown_content
        
        if predicted_title:
            response_data['predicted_title'] = predicted_title
        
        if categories_data:
            response_data['categories'] = json.loads(categories_data)
        
        if keywords_data:
            response_data['keywords'] = json.loads(keywords_data)
        
        if severity_data:
            response_data['severity'] = severity_data
        
        if summary_content:
            response_data['summary_content'] = summary_content
        
        if corrected_content:
            response_data['corrected_content'] = corrected_content
        
        return jsonify(response_data)
    
    except Exception as e:
        # Clean up the file if it exists
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        # Log the error but don't expose stack trace to user
        app.logger.error(f"Conversion error: {str(e)}")
        return jsonify({'error': 'An error occurred during conversion'}), 500


@app.route('/conversion/<int:conversion_id>')
@login_required
def conversion_detail(conversion_id):
    """Page showing detailed information about a specific conversion."""
    conversion = db_session.query(Conversion).get(conversion_id)
    if not conversion:
        flash('Conversion not found', 'error')
        return redirect(url_for('recent_conversions'))
    
    # Determine file type for preview
    file_ext = os.path.splitext(conversion.filename)[1].lower()
    is_pdf = file_ext == '.pdf'
    is_image = file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
    
    return render_template('detail.html', 
                         conversion=conversion,
                         is_pdf=is_pdf,
                         is_image=is_image)


@app.route('/uploads/<path:filename>')
@login_required
def serve_upload(filename):
    """Serve uploaded files for preview."""
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/conversions')
@login_required
def get_conversions():
    """API endpoint to get list of conversions."""
    limit = request.args.get('limit', 50, type=int)
    conversions = db_session.query(Conversion).order_by(Conversion.upload_time.desc()).limit(limit).all()
    return jsonify({
        'conversions': [c.to_dict() for c in conversions]
    })


@app.route('/api/conversion/<int:conversion_id>')
@login_required
def get_conversion(conversion_id):
    """API endpoint to get a specific conversion."""
    conversion = db_session.query(Conversion).get(conversion_id)
    if not conversion:
        return jsonify({'error': 'Conversion not found'}), 404
    return jsonify(conversion.to_dict())


if __name__ == '__main__':
    # Use environment variable to control debug mode
    # Never set debug=True in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
