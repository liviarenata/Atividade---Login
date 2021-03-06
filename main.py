from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask('app')
app.config['SECRET_KEY'] = 'ABC1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Todos(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100))
  complete = db.Column(db.Boolean)
  category = db.Column(db.String(50))
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())
  email = db.Column(db.String())
  password = db.Column(db.String())
  role = db.Column(db.String())

# Index
@app.route('/')
def index():
  
  #verificando se o usuário está logado
  if 'user.id' not in session:
    return redirect('/login')
  
  todos = Todos.query.all()
  return render_template(
    'index.html',
    todos=todos
  )


# Create
@app.route('/create', methods=['POST'])
def create():
  title = request.form.get('title')
  cat = request.form.get('category')
  new_todo = Todos(
    title=title,
    category=cat,
    complete=False
  )
  db.session.add(new_todo)
  db.session.commit()
  return redirect('/')


# Delete
@app.route('/delete/<int:id>')
def delete(id):
  todo = Todos.query.filter_by(id=id).first()
  db.session.delete(todo)
  db.session.commit()
  return redirect('/')


# Complete
@app.route('/complete/<int:id>')
def complete(id):
  todo = Todos.query.filter_by(id=id).first()
  todo.complete = True
  db.session.commit()
  return redirect('/')


# Update
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
  title = request.form.get('title')

  todo = Todos.query.filter_by(id=id).first()
  todo.title = title
  db.session.commit()
  
  return redirect('/')


# Login
@app.route('/login')
def login():
  return render_template('login.html')


# Register
@app.route('/register')
def register():
  return render_template('register.html')


# SignUp
@app.route('/signup', methods=['POST'])
def signup():
  name_input = request.form.get('name')
  email_input = request.form.get('email')
  password_input = request.form.get('password')

  #Verificar se existe email no db
  user = Users.query.filter_by(email=email_input).first()
  if user:
    return redirect('/register')

  new_user = Users(
    name=name_input,
    email=email_input,
    password=generate_password_hash(password_input)
  )
  db.session.add(new_user)
  db.session.commit()
  return redirect('/')


# SignIn
@app.route('/signin', methods=['POST'])
def signin():
  email_input = request.form.get('email')
  password_input = request.form.get('password')

  user = Users.query.filter_by(email=email_input).first()

  #verificando se existe um usuário com o e-mail
  if not user:
    return redirect('/login')
    
  #verificando se a senha não está correta
  if not check_password_hash(user.password, password_input):
    return redirect('/login')

  #guardar usuário na sessão
  session['user_id'] = user.id
  return redirect('/')


# Logout
@app.route('/logout')
def logout():
  session.pop('user.id', None)
  return redirect('/login')
if __name__ == '__main__':
  db.create_all()
  app.run(host='0.0.0.0', port=8080)