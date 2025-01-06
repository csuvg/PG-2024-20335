import requests
import concurrent.futures
import random
import time
import json

# Genera un email aleatorio
def generate_random_email():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)) + "@example.com"

# Crear 50 usuarios y almacenar sus credenciales en un archivo JSON
def create_users(base_url, num_users=50):
    user_data = []

    for i in range(num_users):
        email = generate_random_email()
        password = "12345"
        quetzalito = f"quetzalito{i}"

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

# Realizar todas las pruebas en secuencia para cada usuario
def run_test_sequence(base_url, user_data):
    results = []
    video_path = "prueba4-2024.mp4"  # Ruta al video para enviar

    for user in user_data:
        email = user['email']
        password = user['password']
        user_id = login_user(base_url, email, password)

        if user_id:
            # Obtener información del usuario
            get_user_info = {
                "url": f"{base_url}/get_user_info",
                "method": "POST",
                "body": {"id_user": user_id}
            }
            user_info_result = send_request(get_user_info, user_id=user_id)

            # Enviar video
            video_id = send_video(base_url, user_id, video_path)
            if video_id:
                # Obtener video usando el ID recibido
                get_video_info = {
                    "url": f"{base_url}/get_video",
                    "method": "POST",
                    "body": {"id_user": user_id, "id_video": video_id}
                }
                video_info_result = send_request(get_video_info, user_id=user_id, video_id=video_id)

                # Enviar traducción
                send_traduction_info = {
                    "url": f"{base_url}/send_traduction",
                    "method": "POST",
                    "body": {"id_user": user_id, "sentence_lensegua": "Yo ir universidad"}
                }
                traduction_result = send_request(send_traduction_info, user_id=user_id)

                # Almacenar los resultados de cada secuencia
                results.extend([user_info_result, video_info_result, traduction_result])

    return results

# Función genérica para enviar solicitudes
def send_request(request_info, user_id=None, video_id=None):
    url = request_info["url"]
    method = request_info["method"]
    body = request_info["body"]

    try:
        if method == "POST":
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

if __name__ == "__main__":
    base_url = "http://192.168.244.3:4242"

    # Paso 1: Crear usuarios y guardar en JSON
    user_data = create_users(base_url)

    # Paso 2: Ejecutar las pruebas en secuencia para cada usuario
    start_time = time.time()
    test_results = run_test_sequence(base_url, user_data)
    end_time = time.time()

    # Mostrar resultados
    print(f"Pruebas completadas en {end_time - start_time:.2f} segundos")
    for result in test_results:
        print(result)
