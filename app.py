from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'melon_super_secret_key' # 用于加密会话状态，你可以随便改

# 这里设置你的账号和密码
USERNAME = 'admin'
PASSWORD = '123'

# 访问根目录（登录页）
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # 获取表单提交的账号密码
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('calculator')) # 密码正确，跳转到计算器
        else:
            error = '账号或密码错误，请重试！'
    return render_template('login.html', error=error)

# 访问计算器页面
@app.route('/calculator')
def calculator():
    # 检查是否已经登录
    if not session.get('logged_in'):
        return redirect(url_for('login')) # 没登录就踢回登录页
    # 登录成功，渲染你的计算器网页
    return render_template('index.html')

if __name__ == '__main__':
    # 启动服务，监听 5000 端口
    app.run(host='0.0.0.0', port=5000)
