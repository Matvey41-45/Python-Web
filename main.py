from flask import Flask, render_template, request, redirect, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (LoginManager, UserMixin, login_user, logout_user,
                         login_required, current_user)
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tom1941-1945'

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Правильное подключение к БД для Flask
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("sqlite.db")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class User(UserMixin):
    def __init__(self, id, username, password_hash, email=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    cursor = get_db().cursor()
    user = cursor.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    if user is not None:
        # Учитываем, что поле email 4-е по счету (индекс 3)
        email = user[3] if len(user) > 3 else None
        return User(user[0], user[1], user[2], email)
    return None


@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT post.id, post.title, post.content, post.author_id, user.username, COUNT([like].id) AS likes 
        FROM post 
        JOIN user ON post.author_id = user.id 
        LEFT JOIN [like] ON post.id = [like].post_id 
        GROUP BY post.id, post.title, post.content, post.author_id, user.username
    ''')
    result = cursor.fetchall()

    liked_posts = []
    if current_user.is_authenticated:
        cursor.execute(
            'SELECT post_id FROM [like] WHERE user_id = ?',
            (current_user.id,)
        )
        likes_result = cursor.fetchall()
        for l in likes_result:
            liked_posts.append(l[0])

    posts = []
    for post in reversed(result):
        posts.append({
            'id': post[0],
            'title': post[1],
            'content': post[2],
            'author_id': post[3],
            'username': post[4],
            'likes': post[5],
            'liked_posts': liked_posts
        })

    return render_template('index.html', posts=posts)


@app.route('/like/<int:post_id>')
@login_required
def like_post(post_id):
    db = get_db()
    cursor = db.cursor()
    post = cursor.execute(
        'SELECT * FROM post WHERE id = ?',
        (post_id,)
    ).fetchone()

    if post:
        like = cursor.execute(
            'SELECT * FROM [like] WHERE user_id = ? AND post_id = ?',
            (current_user.id, post_id)
        ).fetchone()

        if like:
            cursor.execute(
                'DELETE FROM [like] WHERE user_id = ? AND post_id = ?',
                (current_user.id, post_id)
            )
        else:
            cursor.execute(
                'INSERT INTO [like] (user_id, post_id) VALUES (?, ?)',
                (current_user.id, post_id)
            )
        db.commit()
        return redirect(url_for('index'))

    return 'Post not found', 404


@app.route('/add/', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO post (title, content, author_id) VALUES (?, ?, ?)',
            (title, content, current_user.id)
        )
        db.commit()
        return redirect(url_for('index'))
    return render_template('add_post.html')


@app.route('/post/<post_id>')
def post(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT post.id, post.title, post.content, post.author_id, user.username '
        'FROM post JOIN user ON post.author_id = user.id WHERE post.id = ?',
        (post_id,)
    )
    result = cursor.fetchone()
    if result is None:
        return redirect(url_for('index'))

    post_dict = {
        'id': result[0],
        'title': result[1],
        'content': result[2],
        'author_id': result[3],
        'username': result[4]
    }
    return render_template('post.html', post=post_dict)


@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    db = get_db()
    cursor = db.cursor()
    post = cursor.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    if post and post[3] == current_user.id:
        cursor.execute('DELETE FROM post WHERE id = ?', (post_id,))
        db.commit()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO user (username, password_hash, email) VALUES (?, ?, ?)',
                           (username, generate_password_hash(password), email)
                           )
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html',
                                   message='Username or Email already exists!')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        user = cursor.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user:
            email = user[3] if len(user) > 3 else None
            user_obj = User(user[0], user[1], user[2], email)
            if user_obj.check_password(password):
                login_user(user_obj)
                return redirect(url_for('index'))

        return render_template('login.html',
                               message='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()