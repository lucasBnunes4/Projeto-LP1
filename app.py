from flask import Flask, render_template, request
from sympy import Matrix, lcm
import re
from chempy import balance_stoichiometry

app = Flask(__name__, static_url_path='/static', template_folder='templates')

def validar_equacao(equacao):
    # Adicione lógica de validação aqui, dependendo do formato esperado
    return True  # Retorna True se a equação for válida, False caso contrário

@app.route('/')
@app.route('/index.html')
def tabela_periodica():
    return render_template('/index.html')

@app.route('/Balanceamento', methods=['GET', 'POST'])
def balanceamento():
    equation = ""
    solution = None

    if request.method == 'POST':
        equation = request.form['equation']

        try:
            if not validar_equacao(equation):
                raise ValueError("Equação química inválida!")

            elementList = []
            elementMatrix = []

            # Divida a equação em reagentes e produtos apenas se ela contiver o sinal de igualdade
            if "->" in equation:
                reagentes = equation.split("->")[0].replace(' ', '').split("+")
                produtos = equation.split("->")[1].replace(' ', '').split("+")

                def addToMatrix(elemento, índice, contagem, lado):
                    nonlocal elementMatrix  # Adicione essa linha para referenciar a variável global
                    if índice == len(elementMatrix):
                        elementMatrix.append([])
                        for x in elementList:
                            elementMatrix[índice].append(0)
                    if elemento not in elementList:
                        elementList.append(elemento)
                        for i in range(len(elementMatrix)):
                            elementMatrix[i].append(0)
                    column = elementList.index(elemento)
                    elementMatrix[índice][column] += contagem * lado

                def findElements(segmento, índice, multiplicador, lado):
                    nonlocal elementMatrix  # Adicione essa linha para referenciar a variável global
                    elementosAndNumbers = re.findall(r'([A-Z][a-z]*)(\d*)', segmento)
                    for elemento, contagem in elementosAndNumbers:
                        contagem = int(contagem) if contagem else 1
                        addToMatrix(elemento, índice, contagem * multiplicador, lado)

                for i in range(len(reagentes)):
                    findElements(reagentes[i], i, 1, 1)
                for i in range(len(produtos)):
                    findElements(produtos[i], i + len(reagentes), -1, -1)

                elementMatrix = Matrix(elementMatrix)
                elementMatrix = elementMatrix.transpose()
                solucao = elementMatrix.nullspace()[0]
                multiplo = lcm([val.q for val in solucao])
                solucao = multiplo * solucao
                coEffi = solucao.tolist()
                saida = ""
                for i in range(len(reagentes)):
                    saida += str(coEffi[i][0]) + reagentes[i]
                    if i < len(reagentes) - 1:
                        saida += " + "
                saida += " -> "
                for i in range(len(produtos)):
                    saida += str(coEffi[i + len(reagentes)][0]) + produtos[i]
                    if i < len(produtos) - 1:
                        saida += " + "

                solution = saida
            else:
                raise ValueError("A equação não contém o sinal de implicabilidade '->'.")

        except ValueError as ve:
            solution = f"Erro ao validar a equação: {str(ve)}"
        except Exception as e:
            solution = f"Erro ao balancear a equação: {str(e)}"
            

    return render_template('Balanceamento.html', equation=equation, solution=solution)

@app.route('/contatos')
def contatos():
    return render_template('contatos.html')

if __name__ == '__main__':
    app.run(debug=True)
