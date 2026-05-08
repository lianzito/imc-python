from flask import Flask, render_template, request, redirect, url_for, flash
from db import execute_query, execute_one, verificar_criar_tabela

app = Flask(__name__)
app.secret_key = 'imc_secret_key_2026'

verificar_criar_tabela()

def calcular_imc(peso, altura):
    return round (peso / (altura ** 2), 2)

def classificacao(imc):
    if imc < 18.5:
     classificacao = 'Abaixo do peso'
    elif imc < 25:
     classificacao = 'Peso normal'
    elif imc < 30:
     classificacao = 'Acima do peso'
    elif imc < 45:        
     classificacao = 'Obesidade'
    else:
     classificacao = 'Erro no cálculo do IMC'

    return classificacao 

@app.route('/')
def index():

    return render_template('index.html')


@app.route('/resultados')
def resultados():

    try:
        sql = "SELECT * FROM calculos WHERE deletado_em IS NULL"

        calculos = execute_query(sql, fetch=True)

        if calculos is None:
            calculos = []

    except Exception as e:
        flash(f'Erro ao buscar dados!', 'danger')
        app.logger.error(f'Erro no SELECT: {e}')
        return redirect(url_for('resultados')) 

    return render_template('resultados.html', calculos=calculos, total=len(calculos), calcular=calcular_imc, classificacao=classificacao)


@app.route('/calcular', methods=['GET', 'POST'])
def calcular():

    if request.method == 'POST':
        nome = request.form.get('nome', 'Não foi enviado um nome!').strip()
        peso = request.form.get('peso', 'Não foi enviado um peso!').strip()
        altura = request.form.get('altura', 'Não foi enviado uma altura!').strip()

        peso = float(peso)
        altura = float(altura)

        try:
            sql = 'INSERT INTO calculos(nome, peso, altura) VALUE (%s, %s, %s);'

            execute_query(sql, (nome, peso, altura))

            flash(f'Produto [{nome}] cadastrado com sucesso!', 'success')

            return redirect(url_for('resultados'))   
        
        except Exception as e:
            flash(f'Erro ao salvar!', 'danger')
            app.logger.error(f'Erro no INSERT: {e}')
            return redirect(url_for('calcular')) 

    return render_template('formulario.html')

@app.route('/calcular/editar/<int:id>', methods=['GET', 'POST'])
def editar_imc(id):
   
    dados = execute_one('SELECT * FROM calculos WHERE id_calculo = %s', (id, ))
    # print(dados)

    if request.method == 'POST':
       try:
          nome = request.form.get('nome', 'Não foi enviado um nome!').strip()
          peso = request.form.get('peso', 'Não foi enviado um peso!').strip()
          altura = request.form.get('altura', 'Não foi enviado uma altura!').strip()

          peso = float(peso)
          altura = float(altura)

          valores = (nome, peso, altura, id)

          sql = '''
              UPDATE calculos SET
              nome = %s,
              peso = %s,
              altura = %s
              WHERE id_calculo = %s
          '''

          execute_query(sql, valores)
        
          flash(f'IMC Atualizado com sucesso!', 'warning')
          return redirect(url_for('resultados'))
       except Exception as e:
          flash(f'Erro ao atualizar: {e}', 'danger')
          return render_template('formulario.html', dados=dados)
     
    return render_template('formulario.html', dados=dados)

@app.route('/deletar/fisico/<int:id>', methods=['POST'])
def deletar_fisico(id):
    try:
       sql = "DELETE FROM calculos WHERE id_calculos= %s;"
       execute_query(sql, (id,))
       flash('Registro DELETADO PERMANENTEMENTE!', 'danger')
    except Exception as e:
       flash(f'Erro ao deletar fisicamente: {e}', 'warning')
       app.logger.error(f'Erro no DELETE: {e}')

    return redirect(url_for('resultados'))

@app.route('/deletar/logico/<int:id>', methods=['POST'])
def deletar_logico(id):
    try:
       sql = "UPDATE calculos SET deletado_em = NOW() WHERE id_calculos= %s;"
       execute_query(sql, (id,))
       flash('Registro ESCONDIDO!', 'danger')
    except Exception as e:
       flash(f'Erro ao deletar logicamente: {e}', 'warning')
       app.logger.error(f'Erro no UPDATE: {e}')

    return redirect(url_for('resultados'))      


if __name__ == '__main__':
    app.run(debug=True)
