from flask import Blueprint, jsonify, request
from app import db
from app.models import Dictionary, User

dictionary_bp = Blueprint('dictionary_bp', __name__)

@dictionary_bp.route('/add_dictionary', methods=['POST'])
def add_dictionary():
    data = request.get_json()
    id_user = data.get('id_user')
    id_word = data.get('id_word')

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "No se ha encontrado el usuario"}), 404
    
    dictionary = Dictionary.query.filter_by(id_user=id_user, id_word=id_word).first()
    if not dictionary:
        # Crear una nueva entrada en el diccionario
        new_entry = Dictionary(
            id_user=id_user,
            id_word=id_word
        )

        try:
            db.session.add(new_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error al guardar en la base de datos"}), 500

        return jsonify({"message": "Palabra agregada a favoritos"}), 200
    else:
        return jsonify({"message": "La palabra ya se encuentra en favoritos"}), 200

@dictionary_bp.route('/remove_dictionary', methods=['DELETE'])
def remove_dictionary():
    id_user = request.args.get('id_user')
    id_word = request.args.get('id_word')

    if not id_user or not id_word:
        return jsonify({"message": "id_user y id_word son requeridos"}), 400

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "No se ha encontrado el usuario"}), 404

    # Verificar que la entrada exista
    entry = Dictionary.query.filter_by(id_user=id_user, id_word=id_word).first()
    if not entry:
        return jsonify({"message": "No se ha encontrado el registro"}), 404

    # Eliminar la entrada del diccionario
    try:
        db.session.delete(entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al eliminar la entrada"}), 500

    return jsonify({"message": "Registro eliminado del diccionario"}), 200


@dictionary_bp.route('/get_dictionary', methods=['POST'])
def get_dictionary():
    data = request.get_json()
    id_user = data.get('id_user')

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "User not found"}), 404

    # Obtener todas las palabras del diccionario para el usuario
    words = Dictionary.query.filter_by(id_user=id_user).all()

    # Formatear las palabras en una lista de JSON
    word_list = [{"id_word": word.id_word} for word in words]

    return jsonify({"words": word_list}), 200
