from flask import Flask


app = Flask(__name__)

@app.route('/')
def index():
    return 'ola mundo'

@app.route('/turma')
def turma():
    return 'cadstrar turma'