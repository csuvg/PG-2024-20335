from flask import Blueprint, jsonify, request
import requests
from app import db
from app.models import Traduccion, User
from app.config import Config

traduction_bp = Blueprint('traduction_bp', __name__)

# Acceder a las variables de config
use_openai = Config.USE_MODEL_OPENAI

@traduction_bp.route('/send_traduction', methods=['POST'])
def send_traduction():
    data = request.get_json()
    id_user = data.get('id_user')
    sentence_lensegua = data.get('sentence_lensegua')

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404
    
    # Verificar que se ha proporcionado la frase en lensegua
    if not sentence_lensegua:
        return jsonify({"message": "Frase en lensegua es requerida"}), 400
    
    # Verificar si se usa el modelo OpenAI
    if use_openai:
        # Hacer una solicitud POST al servicio de traducción
        try:
            process_sentence_url = "http://10.47.92.70:8081/api/generar"
            payload = {"texto": sentence_lensegua}
            
            # Hacer la solicitud HTTP POST
            response = requests.post(process_sentence_url, json=payload)
            
            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                # Acceder a la clave 'respuesta' en lugar de 'traduccion_esp'
                traduction_esp = response.json().get("respuesta", "")
                if not traduction_esp:
                    return jsonify({"message": "No se pudo obtener la traducción"}), 500
            else:
                return jsonify({"message": f"Error al obtener traducción: {response.status_code}"}), 500

        except requests.exceptions.RequestException as e:
            return jsonify({"message": f"Error en la solicitud al servicio de traducción: {str(e)}"}), 500
    else:
        traduction_esp = "Voy a la universidad"

    # Crear y guardar la nueva traducción en la base de datos
    new_traduction = Traduccion(
        id_user=id_user,
        sentence_lensegua=sentence_lensegua,
        traduction_esp=traduction_esp,
        is_favorite=False
    )

    try:
        db.session.add(new_traduction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al guardar en la base de datos"}), 500

    # Responder con los datos de la traducción guardada
    return jsonify(
        {
            "id_sentence": new_traduction.id, 
            "traduction_esp": new_traduction.traduction_esp
        }
    ), 200

@traduction_bp.route('/fav_traduction', methods=['POST'])
def fav_traduction():
    data = request.get_json()
    id_user = data.get('id_user')
    id_sentence = data.get('id_sentence')

    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Verificar que la traducción exista y pertenezca al usuario
    traduction = Traduccion.query.filter_by(id=id_sentence, id_user=id_user).first()
    if not traduction:
        return jsonify({"message": "La traduccion no existe o no le pertenece al usuario"}), 404

    # Marcar la traducción como favorita
    traduction.is_favorite = True
    db.session.commit()

    return jsonify({"message": "Traduccion marcada como favorita"}), 200

@traduction_bp.route('/remove_fav_traduction', methods=['POST'])
def remove_fav_traduction():
    data = request.get_json()
    id_user = data.get('id_user')
    id_sentence = data.get('id_sentence')

    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Verificar que la traducción exista y pertenezca al usuario
    traduction = Traduccion.query.filter_by(id=id_sentence, id_user=id_user).first()
    if not traduction:
        return jsonify({"message": "La traduccion no existe o no le pertenece al usuario"}), 404

    # Marcar la traducción como favorita
    traduction.is_favorite = False
    db.session.commit()

    return jsonify({"message": "Traduccion desmarcada como favorita"}), 200

@traduction_bp.route('/remove_traduction', methods=['DELETE'])
def remove_traduction():
    id_sentence = request.args.get('id_sentence')

    # Verificar que la traducción exista
    traduction = Traduccion.query.filter_by(id=id_sentence).first()
    if not traduction:
        return jsonify({"message": "Traduccion no encontrada"}), 404

    # Eliminar la traducción
    db.session.delete(traduction)
    db.session.commit()

    return jsonify({"message": "Traduccion borrada con exito"}), 200
