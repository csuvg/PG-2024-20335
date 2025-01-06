import requests
import time
import json

# Genera un email aleatorio
def generate_random_email():
    import random
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)) + "@example.com"

# Crear un solo usuario para la prueba
def create_single_user(base_url):
    email = generate_random_email()
    password = "12345"
    quetzalito = "quetzalito_prueba"

    data = {
        "email": email,
        "password": password,
        "quetzalito": quetzalito
    }

    try:
        response = requests.post(f"{base_url}/signup", json=data)
        if response.status_code == 200:
            response_data = response.json()
            user_id = response_data.get("id_user")
            if user_id:
                print(f"Usuario de prueba creado con éxito. ID: {user_id}")
                return {"email": email, "password": password, "id_user": user_id}
            else:
                print(f"Error: No se recibió un ID para el usuario de prueba.")
        else:
            print(f"Error al crear usuario de prueba: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error en la solicitud al crear usuario de prueba: {str(e)}")
        return None

# Función para iniciar sesión y obtener el token o el id_user
def login_user(base_url, email, password):
    login_data = {
        "email": email,
        "password": password
    }

    try:
        print(f"Solicitud de login: {login_data}")
        response = requests.post(f"{base_url}/login", json=login_data)
        if response.status_code == 200:
            return response.json().get("id_user")
        else:
            print(f"Error al iniciar sesión: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error en la solicitud de inicio de sesión: {str(e)}")
        return None

# Función para enviar un video y obtener su ID
def send_video(base_url, user_id, video_path):
    with open(video_path, 'rb') as video_file:
        files = {'video': video_file}
        data = {"id_user": user_id}

        try:
            print(f"Solicitud de envío de video: {data}, archivos: {video_path}")
            response = requests.post(f"{base_url}/send_video", files=files, data=data)
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get("id_video")
            else:
                print(f"Error al enviar video: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error en la solicitud de envío de video: {str(e)}")
            return None

# Función genérica para enviar solicitudes, soportando form-data
def send_request(request_info, preview_image=None):
    url = request_info["url"]
    method = request_info["method"]
    body = request_info["body"]

    try:
        if preview_image:
            # Si se proporciona una imagen de preview, enviar como form-data
            with open(preview_image, 'rb') as image_file:
                files = {'prev_video': image_file}
                data = body  # Asumimos que el cuerpo también debe ser enviado como form-data
                print(f"Solicitud con archivo: {data}, archivo preview: {preview_image}")
                response = requests.post(url, files=files, data=data)
        else:
            # Enviar datos como JSON o form-data según corresponda
            if method == "POST":
                if request_info.get("form_data", False):
                    # Enviar como form-data
                    print(f"Solicitud enviada (form-data): {body}")
                    response = requests.post(url, data=body)
                else:
                    # Enviar como JSON
                    print(f"Solicitud enviada (JSON): {body}")
                    response = requests.post(url, json=body)
            elif method == "GET":
                response = requests.get(url, params=body)
            elif method == "DELETE":
                response = requests.delete(url, params=body)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")

        # Medir tiempo de respuesta y estado
        return {
            "url": url,
            "status": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "response_text": response.text
        }

    except Exception as e:
        return {
            "url": url,
            "status": "Error",
            "response_time": None,
            "error": str(e)
        }

# Ejecutar una secuencia completa de pruebas para un solo usuario
def run_single_test(base_url):
    # Contador para pruebas exitosas
    successful_tests = 0
    total_tests = 0

    # Crear un solo usuario para la prueba
    user = create_single_user(base_url)
    
    if not user:
        print("No se pudo crear el usuario de prueba. Prueba fallida.")
        return successful_tests, total_tests
    
    email = user['email']
    password = user['password']
    # video_path = "prueba4-2024.kmp4"  # Ruta al video para enviar
    video_path = "prueba4-2024x4.mp4"  # Ruta al video para enviar
    preview_image_path = "prueba_img.png"  # Ruta a la imagen de preview para `fav_video`

    # Paso 1: Login
    print("______________")
    print("Iniciando sesión...")
    user_id = login_user(base_url, email, password)
    total_tests += 1
    if user_id:
        successful_tests += 1
    else:
        print("No se pudo iniciar sesión. Prueba fallida.")
        return successful_tests, total_tests

    # Paso 2: Obtener información del usuario
    print("______________")
    print("Obteniendo información del usuario...")
    get_user_info = {
        "url": f"{base_url}/get_user_info",
        "method": "POST",
        "body": {"id_user": user_id}
    }
    user_info_result = send_request(get_user_info)
    total_tests += 1
    if user_info_result["status"] == 200:
        successful_tests += 1
    print("Resultado de get_user_info:", user_info_result)

    # Paso 3: Enviar video
    print("______________")
    print("Enviando video...")
    video_id = send_video(base_url, user_id, video_path)
    total_tests += 1
    if video_id:
        successful_tests += 1
    else:
        print("No se pudo enviar el video. Prueba fallida.")
        return successful_tests, total_tests

    # Paso 4: Obtener el video enviado
    print("______________")
    print("Obteniendo el video enviado...")
    get_video_info = {
        "url": f"{base_url}/get_video",
        "method": "POST",
        "body": {"id_user": user_id, "id_video": video_id}
    }
    video_info_result = send_request(get_video_info)
    total_tests += 1
    if video_info_result["status"] == 200:
        successful_tests += 1
    print("Resultado de get_video:", video_info_result)

    # Paso 5: Marcar video como favorito con imagen de preview usando form-data
    print("______________")
    print("Marcando video como favorito con imagen de preview...")
    fav_video_info = {
        "url": f"{base_url}/fav_video",
        "method": "POST",
        "body": {"id_user": user_id, "id_video": video_id},
        "form_data": True  # Indicador para usar form-data
    }
    fav_video_result = send_request(fav_video_info, preview_image=preview_image_path)
    total_tests += 1
    if fav_video_result["status"] == 200:
        successful_tests += 1
    print("Resultado de fav_video:", fav_video_result)

    # Paso 6: Remover video de favoritos
    print("______________")
    print("Removiendo video de favoritos...")
    remove_fav_video_info = {
        "url": f"{base_url}/remove_fav_video",
        "method": "POST",
        "body": {"id_user": user_id, "id_video": video_id}
    }
    remove_fav_video_result = send_request(remove_fav_video_info)
    total_tests += 1
    if remove_fav_video_result["status"] == 200:
        successful_tests += 1
    print("Resultado de remove_fav_video:", remove_fav_video_result)

    # Paso 7: Enviar traducción
    print("______________")
    print("Enviando traducción...")
    send_traduction_info = {
        "url": f"{base_url}/send_traduction",
        "method": "POST",
        "body": {"id_user": user_id, "sentence_lensegua": "Yo ir universidad"}
    }
    traduction_result = send_request(send_traduction_info)
    total_tests += 1
    if traduction_result["status"] == 200:
        successful_tests += 1
    print("Resultado de send_traduction:", traduction_result)

    # Obtener el id de la traducción
    if traduction_result["status"] == 200:
        try:
            traduction_data = json.loads(traduction_result["response_text"])
            traduction_id = traduction_data.get("id_sentence")
        except json.JSONDecodeError:
            traduction_id = None
    else:
        traduction_id = None


    # Paso 8: Marcar traducción como favorita
    if traduction_id:
        print("______________")
        print("Marcando traducción como favorita...")
        fav_traduction_info = {
            "url": f"{base_url}/fav_traduction",
            "method": "POST",
            "body": {"id_user": user_id, "id_sentence": traduction_id}
        }
        fav_traduction_result = send_request(fav_traduction_info)
        total_tests += 1
        if fav_traduction_result["status"] == 200:
            successful_tests += 1
        print("Resultado de fav_traduction:", fav_traduction_result)

        # Paso 9: Remover traducción de favoritos
        print("______________")
        print("Removiendo traducción de favoritos...")
        remove_fav_traduction_info = {
            "url": f"{base_url}/remove_fav_traduction",
            "method": "POST",
            "body": {"id_user": user_id, "id_sentence": traduction_id}
        }
        remove_fav_traduction_result = send_request(remove_fav_traduction_info)
        total_tests += 1
        if remove_fav_traduction_result["status"] == 200:
            successful_tests += 1
        print("Resultado de remove_fav_traduction:", remove_fav_traduction_result)

    # Paso 10: Agregar palabra al diccionario
    print("______________")
    print("Agregando palabra al diccionario...")
    add_dictionary_info = {
        "url": f"{base_url}/add_dictionary",
        "method": "POST",
        "body": {"id_user": user_id, "id_word": "Agua"}
    }
    add_dictionary_result = send_request(add_dictionary_info)
    total_tests += 1
    if add_dictionary_result["status"] == 200:
        successful_tests += 1
    print("Resultado de add_dictionary:", add_dictionary_result)

    # Paso 11: Obtener diccionario
    print("______________")
    print("Obteniendo información del diccionario...")
    get_dictionary_info = {
        "url": f"{base_url}/get_dictionary",
        "method": "POST",
        "body": {"id_user": user_id}
    }
    get_dictionary_result = send_request(get_dictionary_info)
    total_tests += 1
    if get_dictionary_result["status"] == 200:
        successful_tests += 1
    print("Resultado de get_dictionary:", get_dictionary_result)

    # Paso 12: Remover palabra del diccionario
    print("______________")
    print("Removiendo palabra del diccionario...")
    remove_dictionary_info = {
        "url": f"{base_url}/remove_dictionary",
        "method": "DELETE",
        "body": {"id_user": user_id, "id_word": "Agua"}
    }
    remove_dictionary_result = send_request(remove_dictionary_info)
    total_tests += 1
    if remove_dictionary_result["status"] == 200:
        successful_tests += 1
    print("Resultado de remove_dictionary:", remove_dictionary_result)

    # Paso 13: Agregar streak al usuario
    print("______________")
    print("Agregando streak al usuario...")
    add_streak_info = {
        "url": f"{base_url}/add_streak",
        "method": "POST",
        "body": {"id_user": user_id}
    }
    add_streak_result = send_request(add_streak_info)
    total_tests += 1
    if add_streak_result["status"] == 200:
        successful_tests += 1
    print("Resultado de add_streak:", add_streak_result)

    return successful_tests, total_tests

if __name__ == "__main__":
    base_url = "http://192.168.244.3:4242"

    # Ejecutar prueba individual
    print("Iniciando prueba individual completa...")
    start_time = time.time()
    successful_tests, total_tests = run_single_test(base_url)
    end_time = time.time()
    
    # Mostrar resumen final
    print(f"\nPrueba completada en {end_time - start_time:.2f} segundos")
    print(f"Total de pruebas exitosas: {successful_tests} de {total_tests}")
    print(f"Porcentaje de éxito: {(successful_tests / total_tests) * 100:.2f}%")
