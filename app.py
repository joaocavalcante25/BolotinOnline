from flask import Flask, render_template, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
db = SQLAlchemy(app)

class Turma(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.String(10), unique=False, nullable=False)
    alunos = db.relationship('Aluno', backref='turma', lazy=True)
    boletins = db.relationship('Boletin', backref='turma', lazy=True)
    def __repr__(self):
        return '<Turma %r>' % self.ano    
    
 
class Materia(db.Model):
    cod_materia = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    professores = db.relationship('Professor', backref='materia', lazy=True)
    notas = db.relationship('Notas', backref='materia', lazy=True)
    def __repr__(self):
        return '<Materia %r>' % self.nome
    
class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(80),  nullable=False)
    data_admissao  = db.Column(db.DateTime,  default=datetime.utcnow)
    formacao = db.Column(db.String(80), nullable=False)
    area_atuac = db.Column(db.Integer, db.ForeignKey('materia.cod_materia'), nullable=False)
    def __repr__(self):
        return '<Professor %r>' % self.nome_completo
    def to_json(self, materia):
        return {'nome_completo':self.nome_completo, 'id':self.id, 'materia':materia}   

    
class Aluno(db.Model):
    cpf =  db.Column(db.String(80), primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=False)
    data_nasci = db.Column(db.String(11), unique=False, nullable=False)
    idade = db.Column(db.Integer, unique=False, nullable=False)
    num_matricula = db.Column(db.Integer, unique=True, nullable=False, autoincrement = True)
    id_turma = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    boletins = db.relationship('Boletin', backref='aluno', lazy=True)
    nome_pai = db.Column(db.String(80),  nullable=False)
    nome_mae = db.Column(db.String(80),  nullable=False)
    def __repr__(self):
        return '<Aluno %r>' % self.nome
class Boletin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cod_turma = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    cod_aluno = db.Column(db.String(80), db.ForeignKey('aluno.cpf'), nullable=False)
    bimestre = db.Column(db.Integer, nullable=False)
    situacao = db.Column(db.Boolean, nullable=False)
    notas = db.relationship('Notas', backref='boletin', lazy=True)
    
    def __repr__(self):
        return '<Boletin %r>' % self.id
    
class Notas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_materia = db.Column(db.Integer, db.ForeignKey('materia.cod_materia'), nullable=False)
    nota_prov = db.Column(db.Integer, nullable=False) 
    nota_trab = db.Column(db.Integer, nullable=False)
    id_boletin = db.Column(db.Integer, db.ForeignKey('boletin.id'), nullable=False)
    def __repr__(self):
        return '<Notas %r>' % self.id    
 
#db.create_all()    



@app.route('/cadastro/turma')
def turmaa():
    return 'Cadastrar turmas'

@app.route('/')
@app.route('/alunos', methods=['POST', 'GET'])
def alunos():
    
    turmas = Turma.query.all()
    
    if request.method == 'GET':
        if request.args.get('turma', ''):
            turma= request.args.get('turma', '')
            t = Turma.query.filter_by(id=turma).first()
            alunos = t.alunos
            return render_template('alunos.html', turmas=turmas, turmasected=t,alunos=alunos)

    return render_template('alunos.html', turmas=turmas)

@app.route('/alunos/cadastrar', methods=['POST', 'GET'])
def alunoCadastrar():
    turmas = Turma.query.all()
    if request.method == 'POST':
        print(request.form)
        a = Aluno(cpf=request.form.get('cpf'),
              nome=request.form.get('nome'),
              data_nasci=request.form.get('data_nasc'), 
              idade=request.form.get('idade'),
              num_matricula= request.form.get('cod_matricula'),
              nome_pai=request.form.get('nome_pai'),
              nome_mae=request.form.get('nome_mae'),
              id_turma=request.form.get('turma'))
        try:
            db.session.add(a)
            db.session.commit()
            aluno = {'nome':request.form.get('nome'),'status':True}
        except:
            db.session.add(a)
            aluno = {'nome':request.form.get('nome'),'status':False}
        return render_template('alunosCadastro.html',turmas=turmas ,cadastro=aluno)    
    return render_template('alunosCadastro.html', turmas=turmas)

@app.route('/professor')
def professor():
    professores= Professor.query.all()
    professores = [ professor.to_json(Materia.query.filter_by(cod_materia=professor.area_atuac).first()) for professor in professores]
    print(professores)
    return render_template('professor.html', professores=professores)

@app.route('/professor/cadastrar', methods=['POST', 'GET'])
def professorCadastrar():
    materias = Materia.query.all()
    if request.method == 'POST':
        print(request.form)
        a = Professor(
                      nome_completo=request.form.get('nome_completo'), 
                      formacao= request.form.get('formacao'),
                      area_atuac=request.form.get('area_atuac'))
        try:
            db.session.add(a)
            db.session.commit()
            professor = {'nome':request.form.get('nome_completo'),'status':True}
        except:
            professor = {'nome':request.form.get('nome_completo'),'status':False}
        return render_template('professorCadastro.html',materias=materias ,cadastro=professor)    
    return render_template('professorCadastro.html', materias=materias)      

@app.route('/turma/cadastrar', methods=['POST', 'GET'])
def turmaCadastrar():
    if request.method == 'POST':
        print(request.form)
        a = Turma(ano=request.form.get('ano'))
        
        try:
            db.session.add(a)
            db.session.commit()
            turma = {'id':a.id,'status':True}
        except:
            db.session.add(a)
            turma = {'id':a.id,'status':False}
        return render_template('turmaCadastro.html', cadastro=turma)    
    
    return render_template('turmaCadastro.html')
@app.route('/materia/cadastrar', methods=['POST', 'GET'])
def materiaCadastrar():
    if request.method == 'POST':
        print(request.form)
        a = Materia(nome=request.form.get('nome'))
        try:
            db.session.add(a)
            db.session.commit()
            materia = {'nome':request.form.get('nome'),'status':True}
        except:
            materia = {'nome':request.form.get('nome'),'status':False}
        return render_template('materiaCadastro.html',cadastro=materia)    
    return render_template('materiaCadastro.html')
@app.route('/materias')
def materia():
    materias = Materia.query.all()
    return render_template('materias.html', materias=materias)
@app.route('/turmas')
def turma():
    turma = Turma.query.all()
    return render_template('turma.html', turmas=turma)
    
@app.route('/boletin/procurar', methods=['POST', 'GET'])
def boletin():
    turma = Turma.query.all()
    if request.method == 'GET' and request.args.get('cpf', ''):
        aluno = Aluno.query.filter_by(cpf=request.args.get('cpf', '')).first()
        turma= request.form.get('turma')
        t = Turma.query.filter_by(id=turma).first()
        return render_template('boletinCadastro.html', turma=t, aluno=aluno)
    if request.method == 'POST':
        turma= request.form.get('turma')
        t = Turma.query.filter_by(id=turma).first()
        alunos = t.alunos
        
        return render_template('boletins.html', turma=t, alunos=alunos)
    return render_template('boletinProcurar.html', turmas=turma)

@app.route('/boletin/cadastro', methods=['POST', 'GET'])
def selecionarTurma():
    turma = Turma.query.all()
    if request.method == 'POST':
        turma= request.form.get('turma')
        t = Turma.query.filter_by(id=turma).first()
        alunos = t.alunos
        
        return render_template('boletins.html', alunos=alunos)
    return render_template('boletinProcurar.html', turmas=turma)

@app.route('/boletin/notas', methods=['POST', 'GET'])
def boletinNotas():
    if request.method == 'GET':
        if request.args.get('cpf', ''):
            
            aluno = request.args.get('cpf', '')
            aluno = Aluno.query.filter_by(cpf=aluno).first()
            boletins = aluno.boletins 
            boletins = [{  'boletin':boletin,
                        'notas':[{
                                "nota":nota,
                                "mediaFinal":(nota.nota_prov+nota.nota_trab)/2, 
                                'situacao': 'aprovado' if (nota.nota_prov+nota.nota_trab)/2 > 6 else "reprovado",
                                'materia':Materia.query.filter_by(cod_materia = nota.id_materia).first()
                                } for nota in boletin.notas]} for boletin in boletins]
            print(boletins)
            return render_template('notas.html', aluno=aluno, boletins=boletins)
        
    return render_template('notas.html')    

@app.route('/nota', methods=['POST', 'GET'])
def nota():
    materias =  Materia.query.all()
    if request.method == 'GET':
        if request.args.get('turma', ''):
            s = request.args.get('turma', '')
            s = Turma.query.filter_by(id=s).first()
            alunos = s.alunos
            return render_template('notas.html', materias=materias,alunos =alunos, turma=s) 
    
    return render_template('notas.html', materias=materias) 


@app.route('/boletin/cadastrar', methods=['POST', 'GET'])
def cadastrarBoletin():
    materias =  Materia.query.all()
    if request.method == 'GET' and request.args.get('cpf', ''):
        aluno = Aluno.query.filter_by(cpf=request.args.get('cpf', '')).first()
        turma= request.form.get('turma')
        t = Turma.query.filter_by(id=turma).first()
        return render_template('boletinCadastro.html', turma=t, aluno=aluno, materias =materias)
    

