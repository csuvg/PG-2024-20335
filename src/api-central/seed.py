from app import create_app, db
from app.models import User, Video, Traduccion

app = create_app()

with app.app_context():

    # Elimina todos los datos de las tablas especificadas
    db.session.query(Video).delete()
    db.session.query(Traduccion).delete()
    db.session.query(User).delete()
    db.session.commit()

    # Crear el usuario
    nuevo_usuario = User(
        mail='user-dummy@se-chapinas.com',
        password='123',
        streak=5,  # Ejemplo: podrías ajustar el valor de streak
        quetzalito='MiQuetzalito'
    )

    # Agregar el usuario a la sesión
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Crear videos asociados al usuario
    video_paths = [
        '/srv/web-apps/api-central/videos/prueba1-2024.mp4',
        '/srv/web-apps/api-central/videos/prueba2-2024.mp4',
        '/srv/web-apps/api-central/videos/prueba3-2024.mp4'
    ]

    images_path = [
        '/srv/web-apps/api-central/images/prueba1-2024.png',
        '/srv/web-apps/api-central/images/prueba2-2024.png',
        '/srv/web-apps/api-central/images/prueba3-2024.png'
    ]

    videos = [
        Video(id_user=nuevo_usuario.id, traduction_esp='video1', sentence_lensegua='sentence1', video=video_paths[0], prev_image=images_path[0]),
        Video(id_user=nuevo_usuario.id, traduction_esp='video2', sentence_lensegua='sentence2', video=video_paths[1], prev_image=images_path[1]),
        Video(id_user=nuevo_usuario.id, traduction_esp='video3', sentence_lensegua='sentence3', video=video_paths[2], prev_image=images_path[2])
    ]

    # Agregar los videos a la sesión
    db.session.add_all(videos)
    db.session.commit()

    # Crear traducciones asociadas al usuario
    traducciones = [
        Traduccion(id_user=nuevo_usuario.id, sentence_lensegua='hola1', traduction_esp='holaesp1'),
        Traduccion(id_user=nuevo_usuario.id, sentence_lensegua='hola2', traduction_esp='holaesp2'),
        Traduccion(id_user=nuevo_usuario.id, sentence_lensegua='hola3', traduction_esp='holaesp3')
    ]

    # Agregar las traducciones a la sesión
    db.session.add_all(traducciones)
    db.session.commit()

    # Crear el usuario
    nuevo_usuario = User(
        mail='tiendas@gmail.com',
        password='Ti3ndas@2001',
        streak=1,  # Ejemplo: podrías ajustar el valor de streak
        quetzalito='MiQuetzalito'
    )

    # Agregar el usuario a la sesión
    db.session.add(nuevo_usuario)
    db.session.commit()

    print("Usuario, videos y traducciones creados exitosamente.")
