import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'melon_super_secret_key' # 用于加密会话

# 数据库文件路径 (保存在我们刚才设置的不丢失的数据卷里)
DB_DIR = 'data'
DB_PATH = os.path.join(DB_DIR, 'users.db')

# 初始化数据库
def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 创建用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE NOT NULL, 
                  password_hash TEXT NOT NULL)''')
    # 检查是否已有管理员，如果没有，自动创建 admin:123
    c.execute('SELECT * FROM users WHERE username="admin"')
    if not c.fetchone():
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                  ('admin', generate_password_hash('123')))
    conn.commit()
    conn.close()

# 每次启动时运行一次初始化
init_db()

# 获取数据库连接的辅助函数
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # 让返回的数据可以像字典一样按名字读取
    return conn

# --- 路由区 ---

# 1. 登录页面
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        # 校验账号和密码哈希值
        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('calculator'))
        else:
            error = '账号或密码错误，请重试！'
    return render_template('login.html', error=error)

# 2. 计算器主页面
@app.route('/calculator')
def calculator():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

# 3. 后台管理页面 (新增账号、修改密码、删除账号)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    db = get_db()
    message = ""
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # 添加新账号
        if action == 'add':
            new_user = request.form.get('new_username')
            new_pwd = request.form.get('new_password')
            try:
                db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                           (new_user, generate_password_hash(new_pwd)))
                db.commit()
                message = f"成功添加账号: {new_user}"
            except sqlite3.IntegrityError:
                message = "添加失败：该账号已存在！"
                
        # 修改密码
        elif action == 'change_pwd':
            user_id = request.form.get('user_id')
            new_pwd = request.form.get('new_password')
            db.execute('UPDATE users SET password_hash=? WHERE id=?', 
                       (generate_password_hash(new_pwd), user_id))
            db.commit()
            message = "密码修改成功！"
            
        # 删除账号
        elif action == 'delete':
            user_id = request.form.get('user_id')
            # 防止把当前登录的自己给删了
            user_to_del = db.execute('SELECT username FROM users WHERE id=?', (user_id,)).fetchone()
            if user_to_del['username'] == session['username']:
                message = "警告：你不能删除当前正在使用的账号！"
            elif user_to_del['username'] == 'admin':
                message = "警告：超级管理员 admin 不能被删除！"
            else:
                db.execute('DELETE FROM users WHERE id=?', (user_id,))
                db.commit()
                message = "账号已删除！"

    # 获取所有用户列表展示在网页上
    users = db.execute('SELECT * FROM users').fetchall()
    return render_template('admin.html', users=users, current_user=session['username'], message=message)

# 4. 退出登录
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
