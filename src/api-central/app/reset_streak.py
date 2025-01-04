from app import create_app, db
from app.models import User
from datetime import datetime, timedelta

# Crear la aplicación Flask y contexto
app = create_app()
app.app_context().push()

def reset_streaks():
    # Obtener todos los usuarios
    users = User.query.all()
    for usuario in users:
        if usuario.last_streak_update:
            # Calcular la diferencia de tiempo desde la última actualización
            delta = datetime.utcnow() - usuario.last_streak_update
            if delta > timedelta(days=1):
                # Ha pasado más de un día, reiniciar el streak
                usuario.streak = 0
                usuario.last_streak_update = datetime.utcnow()
                db.session.commit()
                print(f"Streak reset for user {usuario.mail}")

if __name__ == "__main__":
    reset_streaks()
