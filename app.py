from flask import Flask ,jsonify ,request
from collections import defaultdict
# del modulo flask importar la clase Flask y los métodos jsonify,request
from flask_cors import CORS       # del modulo flask_cors importar CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship
app=Flask(__name__)  # crear el objeto app de la clase Flask
CORS(app) #modulo cors es para que me permita acceder desde el frontend al backend


# configuro la base de datos, con el nombre el usuario y la clave
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:1234@localhost/proyecto'
# URI de la BBDD                          driver de la BD  user:clave@URLBBDD/nombreBBDD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False #none
db= SQLAlchemy(app)   #crea el objeto db de la clase SQLAlquemy
ma=Marshmallow(app)   #crea el objeto ma de de la clase Marshmallow


# defino la tabla login
class login(db.Model):   # la clase Receta hereda de db.Model
    id_usuario=db.Column(db.Integer, primary_key=True)   #define los campos de la tabla
    usuario=db.Column(db.String(100))
    contraseña=db.Column(db.String(500))
    gusta_usuario=db.Column(db.String(500))
    # recetas = db.relationship('Receta', backref='autor', lazy=True)


    def __init__(self,usuario,contraseña,gusta_usuario):   #crea el  constructor de la clase
        self.usuario=usuario   # no hace falta el id porque lo crea sola mysql por ser auto_incremento
        self.contraseña=contraseña
        self.gusta_usuario=gusta_usuario


# defino la tabla
class Receta(db.Model):   # la clase Receta hereda de db.Model
    id=db.Column(db.Integer, primary_key=True)   #define los campos de la tabla
    nombre=db.Column(db.String(100))
    descripcion=db.Column(db.String(500))
    receta=db.Column(db.String(500))
    imagen=db.Column(db.String(400))
    gusta=db.Column(db.Integer)
#    id_usuario=db.Column(db.Integer)
#relación con la tabla Login
    id_usuario = db.Column(db.Integer, db.ForeignKey('login.id_usuario'))
    # usuario = relationship("Login", backref="recetas")

    def __init__(self,nombre,descripcion,receta,imagen,gusta,id_usuario):   #crea el  constructor de la clase
        self.nombre=nombre   # no hace falta el id porque lo crea sola mysql por ser auto_incremento
        self.descripcion=descripcion
        self.receta=receta
        self.imagen=imagen
        self.gusta=gusta
        self.id_usuario = id_usuario




    #  si hay que crear mas tablas , se hace aqui




with app.app_context():
    db.create_all()  # aqui crea todas las tablas
#  ************************************************************
#class RecetaSchema(ma.Schema):
  #  class Meta:
  #      fields=('id','nombre','descripcion','receta','imagen')




#Receta_schema=RecetaSchema()            # El objeto Receta_schema es para traer un Receta
#Recetas_schema=RecetaSchema(many=True)  # El objeto Recetas_schema es para traer multiples registros de Receta



#crea usuario nuevo
@app.route('/registrarse', methods=['POST']) # crea ruta o endpoint
def registrarse():

    #print(request.json)  # request.json contiene el json que envio el cliente
    usuar=request.json['usuario']
    contras=request.json['contraseña']
    gust_usuario=request.json['gusta_usuario']

    usuario_existente = login.query.filter_by(usuario=usuar).first()
    print(usuar)
    if usuario_existente:
        return jsonify({"mensaje": "El usuario ya existe"}), 409  # Retorna un código 409 (conflicto) indicando que el usuario ya existe


    new_Login=login(usuar,contras,gust_usuario,)
    db.session.add(new_Login)
    db.session.commit()
    return jsonify({"mensaje": "Usuario registrado"})


#cuando le dan me gusta
@app.route('/gusta',methods=['POST'])
def gusta():
    # usuar=request.json['usuario']
    data = request.get_json()
    usuario_ingresado=data.get('usuario')
    gusto = data.get('gusto')
   
    usuario_existente = login.query.filter_by(usuario=usuario_ingresado).first()
  
    if usuario_existente.gusta_usuario and ',' in usuario_existente.gusta_usuario: #tiene datos y una ,
         
        gusto_completo= usuario_existente.gusta_usuario.split(",")  #convierte a lista quitando las ,
        no_esta=True                            #VARIABLE PARA SABER SI TIENE EL NUMERO (USO COMO BANDERA)
        for numero in gusto_completo:
 
            if numero==str(gusto):
                usuario_existente.gusta_usuario = usuario_existente.gusta_usuario.replace(str(gusto)+",", '')
                db.session.commit()
                no_esta=False       #AVISO Q ENCONTRO EL NUMERO
                break           #si encuentra el numero lo borra y sale del for
        if no_esta:     #SI EL NUMERO NO ESTA
            usuario_existente.gusta_usuario += str(gusto) + ","
            db.session.commit()
        
    else:
        usuario_existente.gusta_usuario = str(gusto) + ","  #si esta vacio gusta usuario entonces iguala al numero
        print(str(gusto) + ",")
        db.session.commit()

    data_serializada=[]
    return jsonify(data_serializada)




#  trae un  registro de la tabla
@app.route('/entrar',methods=['POST'])
def entrar():
    # usuar=request.json['usuario']
    data = request.get_json()
    usuario_ingresado=data.get('usuario')
    contraseña_ingresada=data.get('contraseña')

    entra = login.query.filter_by(usuario=usuario_ingresado).first()

    
    if contraseña_ingresada==entra.contraseña:
        data_serializada = [{
                "usuario": entra.usuario,
                "contraseña": entra.contraseña
            }]
    # data_serializada.append({"usuar":entra.usuario,"contras":entra.contraseña})

    return jsonify(data_serializada)                       # retorna un JSON de todos los registros de la tabla




# @app.route('/todos',methods=['GET'])
# def todos():
#     all_todos = login.query.all()
#     conteo_elementos = {}

#     for objeto in all_todos:
#         if objeto.gusta_usuario and ',' in objeto.gusta_usuario:
#             gusto_completo = objeto.gusta_usuario.split(",")
            
#             for elemento in gusto_completo:
#                 # Verifica si el elemento ya está en el diccionario, si no está, inicialízalo en 0
#                 if elemento !="":
#                     if elemento not in conteo_elementos:
#                         conteo_elementos[elemento] = 0
                    
#                     # Incrementa en 1 la cantidad de repeticiones del elemento
                    
#                     conteo_elementos[elemento] += 1
    
        

#     return jsonify(conteo_elementos)

@app.route('/todos', methods=['GET'])
def todos():
    all_todos = login.query.all()
    conteo_elementos = defaultdict(int)

    for objeto in all_todos:
        if objeto.gusta_usuario and ',' in objeto.gusta_usuario:
            gusto_completo = objeto.gusta_usuario.split(",")
            for elemento in gusto_completo:
                if elemento:
                    conteo_elementos[int(elemento)] += 1

    # Convertir el defaultdict a una lista de diccionarios
    lista_conteo = [{'id_receta': clave, 'valor': valor} for clave, valor in conteo_elementos.items()]

    return jsonify(lista_conteo)








#nueva receta
@app.route('/postre', methods=['POST']) # crea ruta o endpoint
def postre():
    #print(request.json)  # request.json contiene el json que envio el cliente
    nombre=request.json['nombre']
    descripcion=request.json['descripcion']
    receta=request.json['receta']
    imagen=request.json['imagen']
    gusta =0
    id_usuario=2
    new_Receta=Receta(nombre,descripcion,receta,imagen,gusta,id_usuario)
    db.session.add(new_Receta)
    db.session.commit()
    return "solicitud de post recibida"


# trae todos los registros de la tabla
@app.route('/postres',methods=['GET'])
def postres():
    all_postres=Receta.query.all()         # el metodo query.all() lo hereda de db.Model
    data_serializada=[]
    for objeto in all_postres:
        data_serializada.append({"id":objeto.id,"nombre":objeto.nombre,"descripcion":objeto.descripcion,"receta":objeto.receta,"imagen":objeto.imagen,"is_usuraio":objeto.id_usuario})

    return jsonify(data_serializada)                       # retorna un JSON de todos los registros de la tabla




#modificar
@app.route('/editar/<id>' ,methods=['PUT'])
def editar(id):
    postre=Receta.query.get(id)


    nombre=request.json['nombre']
    descripcion=request.json['descripcion']
    receta=request.json['receta']
    imagen=request.json['imagen']


    postre.nombre=nombre
    postre.descripcion=descripcion
    postre.receta=receta
    postre.imagen=imagen


    db.session.commit()

    data_serializada=[{"id":postre.id,"nombre":postre.nombre,"descripcion":postre.descripcion,"receta":postre.receta,"imagen":postre.imagen}]

    return jsonify(data_serializada)



#borrar
@app.route('/borrar/<id>',methods=['DELETE'])
def delete_postre(id):
    postre=Receta.query.get(id)
    db.session.delete(postre)
    db.session.commit()

    data_serializada=[{"id":postre.id,"nombre":postre.nombre,"descripcion":postre.descripcion,"receta":postre.receta,"imagen":postre.imagen}]

    return jsonify(data_serializada)






# programa principal *******************************
if __name__=='__main__':
    app.run(debug=True, port=5000)    # ejecuta el servidor Flask en el puerto 5000


