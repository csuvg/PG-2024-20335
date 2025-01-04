import requests
import concurrent.futures
import random
import time
import json
import os

# Genera un email aleatorio
def generate_random_email():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)) + "@example.com"

def create_users(base_url, num_users, create_if_not_exist=True):
    user_data = []

    # Verificar si ya existe el archivo JSON con los usuarios creados
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r") as file:
            user_data = json.load(file)
        
        if len(user_data) >= num_users:
            print(f"Se encontraron {len(user_data)} usuarios existentes. No se crearán usuarios nuevos.")
            return user_data

    # Si no hay suficientes usuarios, crear más
    if create_if_not_exist:
        for i in range(num_users - len(user_data)):
            email = generate_random_email()
            password = "12345"
            quetzalito = f"quetzalito{i + len(user_data)}"

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
                        user_data.append({"email": email, "password": password, "id_user": user_id})
                        print(f"Usuario creado con éxito. ID: {user_id}")
                    else:
                        print(f"Error: No se recibió un ID para el usuario con email {email}")
                else:
                    print(f"Error al crear usuario: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"Error en la solicitud: {str(e)}")

        # Guardar los datos de los usuarios en un archivo JSON
        with open("user_data.json", "w") as file:
            json.dump(user_data, file)

        print(f"Se han creado {len(user_data)} usuarios.")

    return user_data

# Función para iniciar sesión y obtener el token o el id_user
def login_user(base_url, email, password):
    login_data = {
        "email": email,
        "password": password
    }

    try:
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

# Función para ejecutar la secuencia completa de pruebas para un usuario
def user_test_sequence(base_url, user):
    results = []
    # video_path = "prueba4-2024.mp4"  # Ruta al video para enviar
    video_path = "prueba4-2024x4.mp4"  # Ruta al video para enviar

    email = user['email']
    password = user['password']
    user_id = login_user(base_url, email, password)

    if user_id:
        print("______________")
        # Obtener información del usuario
        get_user_info = {
            "url": f"{base_url}/get_user_info",
            "method": "POST",
            "body": {"id_user": user_id}
        }
        user_info_result = send_request(get_user_info)
        results.append(user_info_result)

        print("______________")
        add_streak_info = {
            "url": f"{base_url}/add_streak",
            "method": "POST",
            "body": {"id_user": user_id}
        }
        add_streak_result = send_request(add_streak_info)
        results.append(add_streak_result)

        # Enviar video
        video_id = send_video(base_url, user_id, video_path)
        if video_id:
            print("______________")
            # Obtener video usando el ID recibido
            get_video_info = {
                "url": f"{base_url}/get_video",
                "method": "POST",
                "body": {"id_user": user_id, "id_video": video_id}
            }
            video_info_result = send_request(get_video_info)
            results.append(video_info_result)

            # Marcar video como favorito con imagen de preview usando form-data
            print("______________")
            print("Marcando video como favorito con imagen de preview...")
            fav_video_info = {
                "url": f"{base_url}/fav_video",
                "method": "POST",
                "body": {"id_user": user_id, "id_video": video_id},
                "form_data": True  # Indicador para usar form-data
            }
            fav_video_result = send_request(fav_video_info, preview_image="prueba_img.png")  # Ruta a la imagen de preview
            results.append(fav_video_result)

            # Enviar traducción
            print("______________")
            send_traduction_info = {
                "url": f"{base_url}/send_traduction",
                "method": "POST",
                "body": {"id_user": user_id, "sentence_lensegua": "Yo ir universidad"}
            }
            traduction_result = send_request(send_traduction_info)

            # Extraer correctamente el id de la traducción desde la respuesta JSON
            if traduction_result["status"] == 200:
                try:
                    traduction_data = json.loads(traduction_result["response_text"])
                    traduction_id = traduction_data.get("id_sentence")
                except json.JSONDecodeError:
                    traduction_id = None
            else:
                traduction_id = None

            results.append(traduction_result)

            # Marcar traducción como favorita si se obtuvo correctamente el id_sentence
            if traduction_id:
                print("______________")
                print("Marcando traducción como favorita...")
                fav_traduction_info = {
                    "url": f"{base_url}/fav_traduction",
                    "method": "POST",
                    "body": {"id_user": user_id, "id_sentence": traduction_id}
                }
                fav_traduction_result = send_request(fav_traduction_info)
                results.append(fav_traduction_result)

    return results

# Función para manejar la concurrencia y simular usuarios simultáneos
def concurrent_test(base_url, user_data, num_users):
    results = []

    # Usamos un ThreadPoolExecutor para manejar la concurrencia
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [
            executor.submit(user_test_sequence, base_url, user)
            for user in user_data
        ]
        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result())

    return results

if __name__ == "__main__":
    base_url = "http://192.168.244.3:4242"

    numero_usuarios = 50

    # Paso 1: Crear usuarios y guardar en JSON si no existen suficientes
    user_data = create_users(base_url, numero_usuarios, create_if_not_exist=True)

    # Mostrar hora de inicio de la prueba
    start_time = time.time()

    # Paso 2: Ejecutar pruebas concurrentes simulando usuarios simultáneos
    test_results = concurrent_test(base_url, user_data, num_users=numero_usuarios)
 
    # Mostrar hora de fin de la prueba
    end_time = time.time()
    print("Numero de usuarios:", numero_usuarios)
    print("Inicio de la prueba:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)))
    print("Fin de la prueba:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)))

    # Mostrar resultados
    print(f"Pruebas completadas en {end_time - start_time:.2f} segundos")
    # Descomenta la siguiente línea si deseas imprimir cada resultado
    # for result in test_results:
    #     print(result)