# Protótipo Web (Flask)

Pequeno protótipo de aplicação web em Flask com autenticação, edição de perfil e upload de imagem.

Principais arquivos e símbolos
- Código principal: [app.py](app.py)  
  - Modelo de usuário: [`User`](app.py)  
  - Função de salvar imagem: [`save_picture`](app.py)  
  - Formulários: [`RegistrationForm`](app.py), [`LoginForm`](app.py), [`ProfileForm`](app.py)  
  - Rotas: [`register`](app.py), [`login`](app.py), [`logout`](app.py), [`dashboard`](app.py), [`profile`](app.py)
- Templates: [templates/layout.html](templates/layout.html), [templates/register.html](templates/register.html), [templates/login.html](templates/login.html), [templates/profile.html](templates/profile.html), [templates/dashboard.html](templates/dashboard.html)
- Dependências: [requeriments.txt](requeriments.txt)
- Arquivos estáticos: pasta [static/profile_pics](static/profile_pics) (imagem padrão: `default.jpg`)

Pré-requisitos
- Python 3.8+ recomendado
- pip

Instalação (local)
1. Criar e ativar virtualenv:
   - Windows:
     python -m venv venv
     venv\Scripts\activate
   - macOS / Linux:
     python3 -m venv venv
     source venv/bin/activate
2. Instalar dependências:
   pip install -r requeriments.txt

Inicialização e execução
- O banco SQLite (`site.db`) é criado automaticamente ao executar o app.
- Executar:
  python app.py
- A aplicação roda em http://127.0.0.1:5000/ por padrão.

Uso
- Registrar: acesse a rota de registro (`/register`) implementada por [`register`](app.py) — template: [templates/register.html](templates/register.html).
- Login: `/login` (função [`login`](app.py)) — template: [templates/login.html](templates/login.html).
- Dashboard protegido: `/dashboard` ([`dashboard`](app.py)) — template: [templates/dashboard.html](templates/dashboard.html).
- Perfil e upload de imagem: `/profile` ([`profile`](app.py)) — template: [templates/profile.html](templates/profile.html). Upload de imagem processado por [`save_picture`](app.py) e salvo em `static/profile_pics/`.

Observações importantes
- A SECRET_KEY está hardcoded em [app.py](app.py). Troque por variável de ambiente em produção.
- Imagens são redimensionadas para 125x125 com Pillow via [`save_picture`](app.py). Verifique dependências nativas (libjpeg) se houver erro ao instalar Pillow.
- Senhas são armazenadas como hash com Flask-Bcrypt (ver [`RegistrationForm`](app.py) e uso em [`register`](app.py)).

Erros comuns
- Permissão negada ao salvar imagem: verifique permissões da pasta `static/profile_pics`.
- Dependências de compilação do Pillow faltando: instale libs do sistema (ex.: libjpeg-dev).

Licença
- Projeto de exemplo; sem licença específica.

---

Arquivos do workspace
- [app.py](app.py)  
- [requeriments.txt](requeriments.txt)  
- [templates/layout.html](templates/layout.html)  
- [templates/register.html](templates/register.html)  
- [templates/login.html](templates/login.html)  
- [templates/profile.html](templates/profile.html)  
- [templates/dashboard.html](templates/dashboard.html)  
- [static/profile_pics/default.jpg](static/profile_pics/default.jpg)
