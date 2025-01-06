from flask import Blueprint, jsonify, request
from app.models import User, Video, Traduccion
from app import db

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/usuario', methods=['POST'])
def get_usuario_by_email():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"message": "No email provided"}), 400

    # Buscar el usuario por correo
    usuario = User.query.filter_by(mail=email).first()
    if not usuario:
        return jsonify({"message": "User not found"}), 404
    
    # Obtener todas las traudcciones favoritas
    # words = Dictionary.query.filter_by(id_user=id_user).all()
    traductions = Traduccion.query.filter_by(id_user=usuario.id).all()

    traductions_list = [
        {
            "sentence_lensegua": traduction.sentence_lensegua, 
            "traduction_esp": traduction.traduction_esp
        } for traduction in traductions]
    
    videos = Video.query.filter_by(id_user=usuario.id).all()

    videos_list = [
        {
            "id": video.id,
            "traduction_esp": video.traduction_esp,
            "sentence_lensegua": video.sentence_lensegua,
            "video": video.video
        } for video in videos
    ]

    # Preparar la respuesta en formato JSON con los datos del usuario, videos y traducciones
    usuario_info = {
        "id": usuario.id,
        "mail": usuario.mail,
        "streak": usuario.streak,
        "quetzalito": usuario.quetzalito,
        "videos": videos_list,
        "traducciones": traductions_list
    }

    return jsonify(usuario_info), 200

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email:
        return jsonify({"message": "No email provided"}), 400

    # Buscar el usuario por correo
    usuario = User.query.filter_by(mail=email).first()
    if not usuario:
        return jsonify({"message": "User not found"}), 404
    if usuario.password != password:
        return jsonify({"message": "Password incorrect"}), 404

    # Preparar la respuesta en formato JSON con los datos del usuario, videos y traducciones
    responce = {
        "id_user": usuario.id
    }

    return jsonify(responce), 200

@user_bp.route('/signup', methods=['POST'])
def singup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    quetzalito = data.get('quetzalito')
    if not email:
        return jsonify({"message": "No email provided"}), 400
    
    # Buscar el usuario por correo
    usuario = User.query.filter_by(mail=email).first()
    if usuario:
        return jsonify({"message": "User already exist"}), 404
    
    # Crear el usuario
    nuevo_usuario = User(
        mail=email,
        password=password,
        streak=0, 
        quetzalito=quetzalito
    )

    # Enviar correo de confirmación
    # send_confirmation_email(email)

    # Agregar el usuario a la sesión
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Preparar la respuesta en formato JSON con los datos del usuario, videos y traducciones
    responce = {
        "id_user": nuevo_usuario.id
    }

    return jsonify(responce), 200

@user_bp.route('/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    email = data.get('id_user')
    new_password = data.get('new_password')
   
    usuario = User.query.filter_by(mail=email).first()
    if not usuario:
        return jsonify({"message": "User not found"}), 404
    
    if not new_password:
        return jsonify({"message": "No new password provided"}), 400

    # Cambiar la contraseña
    usuario.password = new_password

    # Guardar los cambios en la base de datos
    db.session.commit()

    # Preparar la respuesta en formato JSON con los datos del usuario, videos y traducciones
    responce = {
        "id_user": usuario.id
    }

    return jsonify(responce), 200
