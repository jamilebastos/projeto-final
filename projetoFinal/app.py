from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "1234567"


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'SuaNovaSenha'  
app.config['MYSQL_DB'] = 'empresa_wayne'

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['Email']
        senha = request.form['Senha']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nome, senha, cargo FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()

        if usuario and usuario[2] == senha:
            session['usuario_id'] = usuario[0]
            session['usuario_nome'] = usuario[1]
            session['cargo'] = usuario[3]
            flash(f'Bem-vindo de volta, {usuario[1]}!')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro='Email ou senha incorretos!')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM itens")
    total_itens = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cargo = 'funcionario'")
    funcionarios = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cargo = 'gerente'")
    gerentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cargo = 'administrador'")
    admins = cursor.fetchone()[0]
    cursor.close()

    return render_template('dashboard.html',
                           usuario=session['usuario_nome'],
                           cargo=session['cargo'],
                           total_itens=total_itens,
                           total_usuarios=total_usuarios,
                           funcionarios=funcionarios,
                           gerentes=gerentes,
                           admins=admins)


@app.route('/itens')
def listar_itens():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM itens")
    itens = cursor.fetchall()
    cursor.close()

    return render_template('itens.html', itens=itens, cargo=session['cargo'])


@app.route('/adicionar_item', methods=['POST'])
def adicionar_item():
    if 'usuario_id' not in session or session['cargo'] != 'administrador':
        flash('Apenas administradores podem adicionar itens!')
        return redirect(url_for('listar_itens'))

    nome = request.form['nome']
    quantidade = request.form['quantidade']
    descricao = request.form['descricao']

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO itens (nome, quantidade, descricao) VALUES (%s, %s, %s)", (nome, quantidade, descricao))
    mysql.connection.commit()
    cursor.close()
    flash('Item adicionado com sucesso!')
    return redirect(url_for('listar_itens'))


@app.route('/remover_item/<int:item_id>')
def remover_item(item_id):
    if 'usuario_id' not in session or session['cargo'] != 'administrador':
        flash('Apenas administradores podem remover itens!')
        return redirect(url_for('listar_itens'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM itens WHERE id = %s", (item_id,))
    mysql.connection.commit()
    cursor.close()

    flash('Item removido com sucesso!')
    return redirect(url_for('listar_itens'))


@app.route('/criar_usuario', methods=['GET', 'POST'])
def criar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])
        cargo = request.form['cargo']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha, cargo) VALUES (%s, %s, %s, %s)",
                       (nome, email, senha, cargo))
        mysql.connection.commit()
        cursor.close()

        flash('Usuário criado com sucesso!')
        return redirect(url_for('login'))

    return render_template('criar_usuario.html')


if __name__ == '__main__':
    app.run(debug=True)