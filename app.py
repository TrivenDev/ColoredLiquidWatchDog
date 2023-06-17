#!/usr/bin/env python
# flask app 函数
from importlib import import_module
import os, sys
import click
import cv2
from flask import Flask, render_template, Response, send_from_directory, request, flash, redirect, url_for
from flask_cors import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, logout_user, login_user, current_user, UserMixin
# import camera driver
from werkzeug.security import generate_password_hash, check_password_hash

import camera_opencv
import threading

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera
pydir_path = os.path.dirname(os.path.abspath(__file__))
img_savedir = pydir_path + r'/static/runs/imagesave'

isWindows = sys.platform.startswith('win')
if isWindows:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'
app = Flask(__name__)  # flask
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)

login_manager = LoginManager(app)  # 实例化登陆管理扩展类
login_manager.login_view = 'login'  # 登陆界面 是访问login（）
# 初始化相机
CORS(app, supports_credentials=True)
camera = camera_opencv.Camera()  # get camera对象


def gen(camera):
    """Video streaming generator function.
    https://blog.csdn.net/l641208111/article/details/121539596"""
    while True:
        frame = camera.get_frame()  # 获取画面

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # 返回画面


####################################################################################################################
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route('/api/img/<path:filename>')
def sendimg(filename):  # 获取图片
    return send_from_directory(dir_path + '/dist/img', filename)


@app.route('/js/<path:filename>')
def sendjs(filename):  # 获取js文件
    return send_from_directory(dir_path + '/dist/js', filename)


@app.route('/css/<path:filename>')
def sendcss(filename):  # 获取css文件
    return send_from_directory(dir_path + '/dist/css', filename)


@app.route('/api/img/icon/<path:filename>')
def sendicon(filename):  # 获取图标文件
    return send_from_directory(dir_path + '/dist/img/icon', filename)


@app.route('/fonts/<path:filename>')
def sendfonts(filename):  # 获取字体文件
    return send_from_directory(dir_path + '/dist/fonts', filename)


@app.route('/<path:filename>')
def sendgen(filename):  # 获取dist下的文件
    return send_from_directory(dir_path + '/dist', filename)


@app.route('/wspanel')
@login_required
def index():  # 获取控制台页面
    camera_opencv.m_thread.pause()  #

    return send_from_directory(dir_path + '/dist', 'index.html')


###################################################################################################################

# 消息记录页面
class User(db.Model, UserMixin):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    nickname = db.Column(db.String(20))  # 名字
    loginname = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值


class Record(db.Model):  # 表名将会是 record
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(20))  # 类型名字
    color = db.Column(db.String(15))  # 颜色
    date = db.Column(db.String(20))  # 时间日期对象
    time = db.Column(db.String(20))  # 时间日期对象


@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


@app.cli.command()
@click.option('--loginname', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=False, confirmation_prompt=True, help='The password used to login.')
def admin(loginname, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.loginname = loginname
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(loginname=loginname, nickname='Admin')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    # 全局的两个变量移动到这个函数内
    nickname = 'McEwan'
    unusual_records = [
        {'title': 'leakage', 'color': 'white', 'date': '2023-04-27', 'time': '10:31:00'},
        {'title': 'onground', 'color': 'green', 'date': '2023-04-28', 'time': '10:32:00'},
    ]
    user = User(nickname=nickname)
    db.session.add(user)
    for m in unusual_records:
        record_ele = Record(title=m['title'], color=m['color'], date=m['date'], time=m['time'])
        db.session.add(record_ele)

    db.session.commit()
    click.echo('Done.')


# 用户登录
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


@app.context_processor
def inject_user():  # 用于将变量提供给多个模板。函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('home'))  # 重定向到主页
    # 在本页面提交 新增数据的表单
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        title = request.form.get('title')  # 传入表单对应输入字段的 name 值
        color = request.form.get('color')
        date = request.form.get('date')
        time = request.form.get('time')
        # 然后验证数据
        if not title or not color or not date or not time:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('home'))  # 重定向回主页
        # 数据正确，保存表单数据到数据库
        record = Record(title=title, color=color, date=date, time=time)  # 创建Record记录
        db.session.add(record)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('home'))  # 重定向回主页

    unusual_records = Record.query.all()[::-1]  # 切片法实现列表的逆序
    camera_opencv.m_thread.pause()
    return render_template('record.html', records=unusual_records)  # 传参数，这里就是名字和列表的参数


@app.route('/imageshow/<int:record_id>', methods=['GET', 'POST'])
def imageshow(record_id):  # 访问该页面 会传入要修改的记录的id
    record = Record.query.get_or_404(record_id)  # 获取这个记录对象
    # 查看它的四项信息
    # 如果打开该网页收到POST请求：处理编辑表单的提交请求
    img_title = record.title
    img_color = record.color
    img_date = record.date.replace('-', '')
    img_time = record.time.replace(':', '')  # 把多余的符号删除掉
    if not img_title or not img_color or not img_date or not img_time:
        flash('Invalid input for image show.')
        return redirect(url_for('home'))  # 重定向回对应的编辑页面

    filename = "{0}{1}{2}{3}.jpg".format(img_title, img_color, img_date, img_time)
    # filedir = os.path.join(dir_path,"runs/imagesave",filename)
    fileurl = url_for('static', filename='./runs/imagesave/' + filename)
    flash('Item Checked.')
    # return redirect(url_for('home'))  # 重定向回主页

    return render_template('imageshow.html',
                           record=record,
                           image_name=filename,
                           image_url=fileurl,
                           info_result="Success!"
                           )  # 传入被编辑的电影记录


@app.route('/record/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit(record_id):  # 访问该页面 会传入要修改的记录的id
    record = Record.query.get_or_404(record_id)  # 获取这个记录对象
    if request.method == 'POST':  # 如果打开该网页收到POST请求：处理编辑表单的提交请求
        title = request.form['title']
        color = request.form['color']
        date = request.form['date']
        time = request.form['time']
        if not title or not color or not date or not time:
            flash('Invalid input.')
            return redirect(url_for('edit', record_id=record_id))  # 重定向回对应的编辑页面
        record.title = title  # 更新标题
        record.color = color
        record.date = date  # 更新日期
        record.time = time
        db.session.commit()  # 修改数据库内容后，提交数据库会话
        flash('Item updated.')
        return redirect(url_for('home'))  # 重定向回主页

    return render_template('edit.html', record=record)  # 传入被编辑的电影记录


@app.route('/record/delete/<int:record_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required  # 登录保护
def delete(record_id):
    record = Record.query.get_or_404(record_id)  # 获取记录条
    # 删照片
    try:
        record_date = record.date
        record_time = record.time
        record_date = record_date.replace('-', '')
        record_time = record_time.replace(':', '')
        os.remove(img_savedir + '/' + record.title + record.color + record_date + record_time + ".jpg")
    except:
        pass
    db.session.delete(record)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('home'))  # 重定向回主页


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # 如果当前用户已经认证
        return redirect(url_for('home'))  # 重定向到主页
    if request.method == 'POST':
        loginname = request.form['loginname']
        password = request.form['password']

        if not loginname or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if loginname == user.loginname and user.validate_password(password):
            login_user(user)  # 登入该用户
            flash('Login success.')
            return redirect(url_for('home'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')


@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('home'))  # 重定向回首页


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():  # 设置用户名字
    if request.method == 'POST':
        nickname = request.form['nickname']

        if not nickname or len(nickname) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.nickname = nickname
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('home'))

    return render_template('settings.html')


class webapp:  # 功能大类
    def __init__(self):
        self.camera = camera

    def commandInput(self, inputCommand, valueA=None):  # 用于接收和执行动作函数
        camera_opencv.commandAct(inputCommand, valueA)

    def modeselect(self, modeInput):  # 用于选择相机模式
        camera_opencv.Camera.modeSelect = modeInput  # 追踪物体？寻找颜色？巡线？
        camera_opencv.Camera.CVMode = 'no'

    def colorFindSet(self, H, S, V):  # 根据HSV，设置颜色搜寻
        camera.colorFindSet(H, S, V)

    def thread(self):  # 一开始就执行这个，这个是后台线程
        app.run(host='0.0.0.0', threaded=True)  # flaskapp

    def startthread(self):
        fps_threading = threading.Thread(target=self.thread)
        fps_threading.setDaemon(False)
        fps_threading.start()
