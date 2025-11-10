import secrets
import os
from PIL import Image
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_bcrypt import Bcrypt
from datetime import datetime

# --- Configuração do App ---
app = Flask(__name__)
# Define o caminho absoluto para o banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = '1323wasd' # Chave secreta para sessões e formulários
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Rota para onde usuários não logados são redirecionados
login_manager.login_message_category = 'info'

# --- Modelos do Banco de Dados (Propriedades do Usuário) ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # imagem_perfil: Vamos simplificar e usar um nome de arquivo padrão por enquanto
    imagem_perfil = db.Column(db.String(20), nullable=False, default='default.jpg')
    # password: Armazenamos apenas o hash
    password = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# --- HELPER FUNCTION ---
# Função para salvar a foto
def save_picture(form_picture):
    # Gera um nome aleatório para o arquivo
    random_hex = secrets.token_hex(8)
    # Pega a extensão do arquivo original (.jpg, .png)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    # Define o caminho completo onde a imagem será salva
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # Redimensiona a imagem para economizar espaço
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    # Salva a imagem redimensionada no caminho
    i.save(picture_path)

    return picture_fn

# --- Formulários (WTForms) ---
class RegistrationForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    descricao = TextAreaField('Descrição')
    # Adicione este campo
    picture = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Atualizar')

# --- Rotas da Aplicação ---
@app.route("/")
@app.route("/home")
def home():
    return "<h1>Página Inicial</h1><p><a href='/login'>Login</a> ou <a href='/register'>Registre-se</a></p>"

# (Adicione uma rota de registro para poder testar)
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(nome_completo=form.nome_completo.data, 
                    username=form.username.data, 
                    email=form.email.data, 
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Sua conta foi criada! Você já pode fazer login.', 'success')
        return redirect(url_for('login'))
    # (Você precisará criar o template 'register.html')
    return render_template('register.html', title='Registrar', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        else:
            flash('Login sem sucesso. Verifique o email e a senha.', 'danger')
    # (Você precisará criar o template 'login.html')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- Rotas Protegidas (Dashboard e Perfil) ---

@app.route("/dashboard")
@login_required # <-- Mágica do Flask-Login!
def dashboard():
    # (Você precisará criar o template 'dashboard.html')
    return render_template('dashboard.html', title='Dashboard')

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        # --- Lógica de upload da foto ---
        if form.picture.data:
            # (Opcional: apagar a foto antiga se não for a default)
            if current_user.imagem_perfil != 'default.jpg':
                try:
                    os.remove(os.path.join(app.root_path, 'static/profile_pics', current_user.imagem_perfil))
                except FileNotFoundError:
                    pass # Ignora se o arquivo não existir
            
            # Salva a nova foto
            picture_file = save_picture(form.picture.data)
            current_user.imagem_perfil = picture_file
        # --- Fim da lógica da foto ---
            
        current_user.nome_completo = form.nome_completo.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.descricao = form.descricao.data
        db.session.commit()
        flash('Seu perfil foi atualizado!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.nome_completo.data = current_user.nome_completo
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.descricao.data = current_user.descricao
    
    # Passa o caminho da imagem atual para o template
    image_file = url_for('static', filename='profile_pics/' + current_user.imagem_perfil)
    return render_template('profile.html', title='Perfil', form=form, image_file=image_file)

# --- Ponto de entrada ---
if __name__ == '__main__':
    # Cria o banco de dados (apenas na primeira vez)
    with app.app_context():
        db.create_all()
    app.run(debug=True)