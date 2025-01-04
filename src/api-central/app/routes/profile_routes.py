from flask import Blueprint, jsonify, request, url_for
from app import db
from app.models import User, Video, Traduccion
from datetime import datetime, timedelta

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/get_user_info', methods=['POST'])
def get_user_info():
    data = request.get_json()
    id_user = data.get('id_user')

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "User not found"}), 404

    # Obtener videos y traducciones favoritas del usuario
    videos_fav = Video.query.filter_by(id_user=id_user, is_favorite=True).all()
    traducciones_fav = Traduccion.query.filter_by(id_user=id_user, is_favorite=True).all()

    # Preparar la lista de videos con enlaces
    video_fav_with_link = []
    for video in videos_fav:
        video_fav_with_link.append({
            "id_video": video.id,
            "sentence_lensegua": video.sentence_lensegua,
            "traduction_esp": video.traduction_esp,
            "link_video": url_for('video_bp.download_video', filename=video.video.split('/')[-1], _external=True),
            "prev_image": url_for('video_bp.download_image', filename=video.prev_image.split('/')[-1], _external=True)
        })

    # Preparar la respuesta con la información del usuario
    user_info = {
        "mail": usuario.mail,
        "streak": usuario.streak,
        "quetzalito": usuario.quetzalito,
        "videos_fav": video_fav_with_link,  # Usar la lista con enlaces
        "traductions_fav": [
            {
                "traduction": trad.traduction_esp, 
                "sentence_lensegua": trad.sentence_lensegua, 
                "id_traduction": trad.id
            } 
            for trad in traducciones_fav
        ]
    }

    return jsonify(user_info), 200

@profile_bp.route('/get_video', methods=['POST'])
def get_video():
    data = request.get_json()
    id_user = data.get('id_user')
    id_video = data.get('id_video')

    # Verificar que el usuario y el video existan
    video = Video.query.filter_by(id=id_video, id_user=id_user).first()
    if not video:
        return jsonify({"message": "Video not found or does not belong to the user"}), 404

    # Crear la URL que apunta a la ruta para descargar el video
    download_url = url_for('video_bp.download_video', filename=video.video.split('/')[-1], _external=True)

    return jsonify({"video": download_url}), 200

@profile_bp.route('/get_images', methods=['POST'])
def get_images():
    data = request.get_json()
    id_user = data.get('id_user')
    id_video = data.get('id_video')

    # Verificar que el usuario y el video existan
    video = Video.query.filter_by(id=id_video, id_user=id_user).first()
    if not video:
        return jsonify({"message": "Video not found or does not belong to the user"}), 404

    # Crear la URL que apunta a la ruta para descargar el video
    download_url = url_for('video_bp.download_image', filename=video.prev_image.split('/')[-1], _external=True)

    return jsonify({"image": download_url}), 200

@profile_bp.route('/get_image', methods=['POST'])
def get_image():
    data = request.get_json()
    id_user = data.get('id_user')
    id_video = data.get('id_video')

    # Verificar que el usuario y el video existan
    video = Video.query.filter_by(id=id_video, id_user=id_user).first()
    if not video:
        return jsonify({"message": "Video not found or does not belong to the user"}), 404

    # Crear la URL que apunta a la ruta para descargar la imagen
    download_url = url_for('video_bp.download_image', filename=video.prev_image.split('/')[-1], _external=True)

    return jsonify({"image": download_url}), 200

@profile_bp.route('/delete_user', methods=['DELETE'])
def delete_user():
    id_user = request.args.get('id_user')

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "User not found"}), 404

    # Eliminar el usuario y todas las entidades relacionadas
    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200

@profile_bp.route('/add_streak', methods=['POST'])
def add_streak():
    data = request.get_json()
    id_user = data.get('id_user')

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "User not found"}), 404

    # Incrementar el streak del usuario
    usuario.streak += 1
    usuario.last_streak_update = datetime.utcnow() 
    db.session.commit()

    return jsonify({"message": "Streak incremented", "streak": usuario.streak}), 200

@profile_bp.route('/remove_streak', methods=['POST'])
def remove_streak():
    data = request.get_json()
    id_user = data.get('id_user')

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "User not found"}), 404

    # Incrementar el streak del usuario
    usuario.streak = 0
    db.session.commit()

    return jsonify({"message": "Streak deleted", "streak": usuario.streak}), 200

@profile_bp.route('/check_streak', methods=['POST'])
def check_streak():
    data = request.get_json()
    id_user = data.get('id_user')

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "User not found"}), 404

    # Calcular la diferencia de tiempo desde la última actualización
    if usuario.last_streak_update:
        delta = datetime.utcnow() - usuario.last_streak_update
        if delta > timedelta(days=1):
            # Ha pasado más de un día, reiniciar el streak
            usuario.streak = 0
            usuario.last_streak_update = datetime.utcnow()
            db.session.commit()
            return jsonify({"message": "Streak reset due to inactivity", "streak": usuario.streak}), 200
        else:
            return jsonify({"message": "Streak is up to date", "streak": usuario.streak}), 200
    else:
        # Si no hay registro previo, considera inicializarlo
        usuario.last_streak_update = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Initialized streak update timestamp", "streak": usuario.streak}), 200
