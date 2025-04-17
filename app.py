from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import sqlite3
import bcrypt
from werkzeug.utils import secure_filename

# استيراد الوحدات المساعدة
from utils.arabic_text_extractor import ArabicTextExtractor
from utils.law_search_engine import LawSearchEngine

app = Flask(__name__)
app.secret_key = 'hamad_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'doc', 'docx'}

# التأكد من وجود مجلد التحميلات
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# إنشاء قاعدة البيانات إذا لم تكن موجودة
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # إنشاء جدول المستخدمين
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # إنشاء جدول القضايا
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        user_id INTEGER,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # إنشاء جدول المستندات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_id) REFERENCES cases (id)
    )
    ''')
    
    # إنشاء جدول القوانين
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS laws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        country TEXT NOT NULL,
        category TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# تهيئة قاعدة البيانات
init_db()

# التحقق من امتدادات الملفات المسموح بها
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة!', 'danger')
        
        conn.close()
    
    return render_template('login.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح!', 'success')
    return redirect(url_for('index'))

# التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # تشفير كلمة المرور
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
                          (username, hashed_password, email, 'user'))
            conn.commit()
            flash('تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل!', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html')

# لوحة التحكم
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM cases WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],))
    cases = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', cases=cases)

# إنشاء قضية جديدة
@app.route('/case/new', methods=['GET', 'POST'])
def new_case():
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO cases (title, description, user_id, status) VALUES (?, ?, ?, ?)',
                      (title, description, session['user_id'], 'جديدة'))
        
        case_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash('تم إنشاء القضية بنجاح!', 'success')
        return redirect(url_for('view_case', case_id=case_id))
    
    return render_template('new_case.html')

# عرض تفاصيل القضية
@app.route('/case/<int:case_id>')
def view_case(case_id):
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM cases WHERE id = ? AND user_id = ?', (case_id, session['user_id']))
    case = cursor.fetchone()
    
    if not case:
        flash('القضية غير موجودة أو ليس لديك صلاحية للوصول إليها!', 'danger')
        return redirect(url_for('dashboard'))
    
    cursor.execute('SELECT * FROM documents WHERE case_id = ? ORDER BY uploaded_at DESC', (case_id,))
    documents = cursor.fetchall()
    
    conn.close()
    
    return render_template('view_case.html', case=case, documents=documents)

# تحميل مستند
@app.route('/document/upload/<int:case_id>', methods=['GET', 'POST'])
def upload_document(case_id):
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM cases WHERE id = ? AND user_id = ?', (case_id, session['user_id']))
    case = cursor.fetchone()
    
    if not case:
        flash('القضية غير موجودة أو ليس لديك صلاحية للوصول إليها!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        if 'document' not in request.files:
            flash('لم يتم اختيار ملف!', 'danger')
            return redirect(request.url)
        
        file = request.files['document']
        
        if file.filename == '':
            flash('لم يتم اختيار ملف!', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            cursor.execute('INSERT INTO documents (case_id, filename, filepath) VALUES (?, ?, ?)',
                          (case_id, filename, filepath))
            conn.commit()
            
            flash('تم تحميل المستند بنجاح!', 'success')
            return redirect(url_for('view_case', case_id=case_id))
        else:
            flash('نوع الملف غير مسموح به!', 'danger')
    
    conn.close()
    
    return render_template('upload_document.html', case=case)

# استخراج النص من مستند
@app.route('/document/extract/<int:document_id>')
def extract_document(document_id):
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT d.*, c.user_id FROM documents d
    JOIN cases c ON d.case_id = c.id
    WHERE d.id = ? AND c.user_id = ?
    ''', (document_id, session['user_id']))
    
    document = cursor.fetchone()
    
    if not document:
        flash('المستند غير موجود أو ليس لديك صلاحية للوصول إليه!', 'danger')
        return redirect(url_for('dashboard'))
    
    conn.close()
    
    # استخراج النص من المستند
    filepath = document['filepath']
    filename = document['filename']
    
    extracted_text = ""
    
    if filename.lower().endswith('.pdf'):
        # استخراج النص من ملف PDF
        extractor = ArabicTextExtractor()
        extracted_text = extractor.extract_from_pdf(filepath)
        
        # تصحيح اتجاه النص العربي
        extracted_text = extractor.fix_pdf_text_direction(extracted_text)
    else:
        # قراءة النص من ملفات أخرى
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                extracted_text = file.read()
        except Exception as e:
            extracted_text = f"حدث خطأ أثناء قراءة الملف: {str(e)}"
    
    return render_template('view_document.html', document=document, extracted_text=extracted_text)

# البحث في القوانين
@app.route('/search_laws', methods=['GET', 'POST'])
def search_laws():
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'danger')
        return redirect(url_for('login'))
    
    results = []
    
    if request.method == 'POST':
        query = request.form['query']
        country = request.form.get('country', None)
        
        search_engine = LawSearchEngine()
        results = search_engine.search(query, country)
    
    return render_template('search_laws.html', results=results)

# تحديث قاعدة بيانات القوانين
def update_laws():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # إضافة بعض القوانين للاختبار
    laws = [
        {
            'title': 'قانون الشركات السعودي',
            'content': 'المادة الأولى: يقصد بالألفاظ والعبارات الآتية - أينما وردت في هذا النظام - المعاني المبينة أمام كل منها، ما لم يقتض السياق خلاف ذلك. المادة الثانية: تسري أحكام هذا النظام على الشركات التي تؤسس في المملكة، وكذلك الشركات التي تؤسس في الخارج وتتخذ من المملكة مركزاً لممارسة نشاطها.',
            'country': 'السعودية',
            'category': 'قانون تجاري'
        },
        {
            'title': 'قانون المعاملات المدنية الإماراتي',
            'content': 'المادة (1): تسري النصوص التشريعية على جميع المسائل التي تتناولها هذه النصوص في لفظها أو في فحواها. المادة (2): لا مساغ للاجتهاد في مورد النص.',
            'country': 'الإمارات',
            'category': 'قانون مدني'
        },
        {
            'title': 'قانون العقوبات القطري',
            'content': 'المادة 1: تسري أحكام الشريعة الإسلامية في شأن الجرائم الآتية إذا كان المتهم أو المجني عليه مسلماً: 1- الجرائم المنصوص عليها في قانون القصاص والدية. 2- جرائم الحدود المتعلقة بالسرقة والحرابة والزنا وشرب الخمر والردة.',
            'country': 'قطر',
            'category': 'قانون جنائي'
        }
    ]
    
    for law in laws:
        cursor.execute('INSERT OR REPLACE INTO laws (title, content, country, category) VALUES (?, ?, ?, ?)',
                      (law['title'], law['content'], law['country'], law['category']))
    
    conn.commit()
    conn.close()
    
    # تحديث فهرس البحث
    search_engine = LawSearchEngine()
    search_engine.update_index()

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
