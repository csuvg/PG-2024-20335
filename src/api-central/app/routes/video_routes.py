from flask import Blueprint, jsonify, request
import requests
from app.models import User, Video
from werkzeug.utils import secure_filename
from app import db  # Importar db para interactuar con la base de datos
from flask import send_from_directory
from app.config import Config
import os

video_bp = Blueprint('video_bp', __name__)

# Ruta para almacenar los videos
VIDEO_STORAGE_PATH = '/srv/web-apps/api-central/videos/'
IMAGES_STORAGE_PATH = '/srv/web-apps/api-central/images/'

ALLOWED_EXTENSIONS = {'mp4'}
ALLOWED_IMAGE_EXTENSIONS = {'png'}

# Acceder a las variables de config
use_openai = Config.USE_MODEL_OPENAI
use_cv = Config.USE_MODEL_CV

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@video_bp.route('/send_video', methods=['POST'])
def send_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video part'}), 400
    
    file = request.files['video']
    id_user = request.form.get('id_user')

    # Verificar que el usuario exista
    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    if not file or not allowed_file(file.filename):
        return jsonify({'message': 'No se seleccionó un archivo o no es el formato correcto'}), 400

    # Guardar el archivo con un nombre seguro
    filename = secure_filename(file.filename)
    file_path = os.path.join(VIDEO_STORAGE_PATH, filename)
    
    # Guardar el archivo en la ruta especificada
    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"message": "Error al guardar archivo"}), 500
    
    if use_cv:
        # Hacer una solicitud al servicio externo para obtener la traducción (try-except)
        try:
            video_url = f"http://192.168.244.3:4242/download_video/{filename}"
            process_video_url = f"http://10.47.92.60:8081/processVideo?VideoURL={video_url}"
            
            # Hacer la solicitud HTTP
            response = requests.get(process_video_url)

            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                # Parsear la respuesta JSON
                response_json = response.json()
                sentence_lensegua = response_json.get("text", "Texto no disponible")  # Extraer el valor de "text"
            else:
                return jsonify({
                    "message": f"Error al procesar video: {response.status_code}",
                    "sentence_lensegua": None
                }), 500

        except requests.exceptions.RequestException as e:
            return jsonify({"message": f"Error en la solicitud al procesar el video: {str(e)}"}), 500
    else:
        sentence_lensegua = "SENTENCE LENSGUA"

    if use_openai:
        # Hacer una solicitud POST a la URL de generar traducción en español
        try:
            process_sentence_url = "http://10.47.92.70:8081/api/generar"
            payload = {"texto": sentence_lensegua}
            
            # Hacer la solicitud HTTP POST
            response = requests.post(process_sentence_url, json=payload)
            
            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                traduction_esp = response.json().get("traduccion_esp", "Traducción no disponible")
            else:
                # return jsonify({
                #     "message": f"Error al obtener traducción: {response.status_code}",
                #     "sentence_lensegua": sentence_lensegua
                # }), 500
                traduction_esp = sentence_lensegua

        except requests.exceptions.RequestException as e:
            return jsonify({"message": f"Error en la solicitud al servicio de traducción: {str(e)}"}), 500
    else:
        traduction_esp = "Voy a la universidad"

    # Suponemos que la traducción en español es algo predeterminado o generado localmente
    # traduction_esp = "Traducción del video en español"

    # Crear un nuevo objeto Video y guardar la ruta en la base de datos
    new_video = Video(
        id_user=id_user,
        traduction_esp=traduction_esp,
        sentence_lensegua=sentence_lensegua,
        video=filename  # Guardar solo el nombre del archivo
    )

    try:
        db.session.add(new_video)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al guardar en la base de datos"}), 500

    return jsonify(
        {
            "id_video": new_video.id, 
            "traduction_esp": new_video.traduction_esp, 
            "sentence_lensegua": new_video.sentence_lensegua
        }
    ), 200

# Ruta: /report_video (POST)
@video_bp.route('/report_video', methods=['POST'])
def report_video():
    data = request.get_json()
    id_user = data.get('id_user')
    id_video = data.get('id_video')
    report_message = data.get('report_message')
    report_img = data.get('report_img')  # Se asume que es una URL o path al archivo de imagen

    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404
    
    # video = Video.query.filter_by(id=id_video, id_user=id_user).first()
    # if not video:
    #     return jsonify({"message": "Video no encontardo"}), 404

    # Aquí podrías implementar lógica para almacenar o manejar el reporte.
    # Por simplicidad, solo devolvemos un mensaje de éxito.
    
    return jsonify({"message": "Se ha reportado el video exitosamente"}), 200

# Ruta: /fav_video (POST)
@video_bp.route('/fav_video', methods=['POST'])
def fav_video():
    id_user = request.form.get('id_user')
    id_video = request.form.get('id_video')
    prev_video = request.files.get('prev_video')

    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404
    
    video = Video.query.filter_by(id=id_video, id_user=id_user).first()
    if not video:
        return jsonify({"message": "Video no encontrado"}), 404

    if not prev_video or not allowed_image(prev_video.filename):
        return jsonify({"message": "No se ha proporcionado imagen de preview o el formato no es válido"}), 400
    
    # Asegurarse de que el nombre del archivo es seguro para usarlo en el sistema de archivos
    filename = secure_filename(prev_video.filename)

    # Definir la ruta para guardar la imagen
    save_path = os.path.join(IMAGES_STORAGE_PATH, filename)

    # Guardar la imagen en la ruta especificada
    try:
        prev_video.save(save_path)
    except Exception as e:
        return jsonify({"message": "Error al guardar la imagen"}), 500

    # Marcar el video como favorito
    video.is_favorite = True
    # Guardar la ruta de la imagen si es necesario
    video.prev_image = filename  # Asumiendo que tienes este campo en tu modelo
    db.session.commit()

    return jsonify({"message": "Video marcado como favorito"}), 200

@video_bp.route('/remove_fav_video', methods=['POST'])
def remove_fav_video():
    data = request.get_json()
    id_user = data.get('id_user')
    id_video = data.get('id_video')

    usuario = User.query.filter_by(id=id_user).first()
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404

    video = Video.query.filter_by(id=id_video, id_user=id_user).first()
    if not video:
        return jsonify({"message": "No se ha dado video id"}), 404

    # Eliminar la imagen previa existente si hay una
    if video.prev_image:
        try:
            os.remove(os.path.join(IMAGES_STORAGE_PATH, video.prev_image))
            video.prev_image = None
        except Exception as e:
            return jsonify({"message": f"Failed to delete existing image: {str(e)}"}), 500

    # Marcar el video como no favorito
    video.is_favorite = False
    db.session.commit()

    return jsonify({"message": "Video removido de favoritos e imagen eliminada"}), 200

# Ruta: /remove_video (DELETE)
@video_bp.route('/remove_video', methods=['DELETE'])
def remove_video():
    id_video = request.args.get('id_video')

    video = Video.query.filter_by(id=id_video).first()
    if not video:
        return jsonify({"message": "Video no encontrado"}), 404

    # Intentar eliminar el archivo de video del sistema de archivos
    video_path = video.video
    try:
        os.remove(os.path.join(VIDEO_STORAGE_PATH, video_path))
    except OSError as e:
        print(f"Error al eliminar el archivo de video: {str(e)}")

    # Intentar eliminar el archivo de imagen de previsualización si existe
    if video.prev_image:
        try:
            os.remove(os.path.join(IMAGES_STORAGE_PATH, video.prev_image))
        except OSError as e:
            print(f"Error al eliminar el archivo de imagen: {str(e)}")

    # Eliminar el video de la base de datos
    db.session.delete(video)
    db.session.commit()

    return jsonify({"message": "Video eliminado exitosamente"}), 200

@video_bp.route('/download_video/<path:filename>', methods=['GET'])
def download_video(filename):
    video_directory = "/srv/web-apps/api-central/videos/"
    file_path = os.path.join(video_directory, filename)
    
    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404
    
    try:
        return send_from_directory(directory=video_directory, path=filename, as_attachment=True)
    except Exception as e:
        return jsonify({"message": f"Error downloading video: {str(e)}"}), 500

@video_bp.route('/download_image/<path:filename>', methods=['GET'])
def download_image(filename):
    image_directory = "/srv/web-apps/api-central/images/"
    file_path = os.path.join(image_directory, filename)
    
    if not os.path.exists(file_path):
        return jsonify({"message": f"File not found: {file_path}"}), 404
    
    try:
        return send_from_directory(directory=image_directory, path=filename, as_attachment=True)
    except Exception as e:
        return jsonify({"message": f"Error downloading image: {str(e)}"}), 500