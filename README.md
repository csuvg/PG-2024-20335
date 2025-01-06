# Proyecto de Graduación

Este repositorio contiene el código para el proyecto de graduación.

## 1. Descripción
**API Central** es un proyecto diseñado para centralizar y gestionar servicios API de manera eficiente. Este sistema permite a los usuarios interactuar con diferentes APIs desde un solo punto de acceso, mejorando la organización, seguridad y escalabilidad. Es ideal para proyectos que requieren integraciones con múltiples servicios externos.

---

## 2. Instrucciones de Instalación

### **Requisitos Previos**
Antes de instalar el proyecto, asegúrese de tener los siguientes elementos:
- **Python 3.8+**
- **Pip**
- **Virtualenv**
- **PostgreSQL** o cualquier base de datos compatible
- **Git**

### **Pasos de Instalación**
1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/JoseGon20335/api-central.git
   cd api-central
   ```

2. **Crear un entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate
   ```

3. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**:
   Cree una base de datos y configure las credenciales en el archivo `.env` (ver sección de Variables de Entorno).

5. **Migrar la base de datos**:
   ```bash
   flask db upgrade
   ```

### **Variables de Entorno**
Cree un archivo `.env` en la raíz del proyecto con el siguiente formato:
```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost/db_name
SECRET_KEY=your_secret_key
```

### **Ejecución de la Aplicación**
Para iniciar la aplicación, ejecute:
```bash
flask run
```
La aplicación estará disponible en: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### **Ejecución de Tests**
Ejecute los tests con el siguiente comando:
```bash
pytest
```

---

## 3. Demo
Una demostración visual del proyecto está disponible en la carpeta `/demo/` como un archivo de video.

Para visualizar la demo:
1. Navegue a la carpeta `demo/`.
2. Reproduzca el archivo `demo.mp4` con cualquier reproductor de video compatible.

---

## 4. Informe Final
El informe final del proyecto de graduación está disponible en la carpeta `/docs/` en formato PDF. 

Para acceder al informe:
- Navegue a la carpeta `docs/`.
- Abra el archivo `Informe_Final.pdf`.

---

## 5. Checklist de Verificación Final
Antes de entregar el proyecto, asegúrese de cumplir con los siguientes puntos:

### **1. Estructura de Carpetas**
- [ ] La carpeta `/demo` existe y contiene el archivo `Demo.mp4`.
- [ ] La carpeta `/docs` existe y contiene el archivo `Informe.pdf`.
- [ ] La carpeta `/src` existe y contiene:
  - [ ] Todos los archivos del código fuente del proyecto.

### **2. Archivo README.md**
- [ ] El archivo `README.md` está presente en la raíz del repositorio.
- [ ] Está escrito en formato Markdown (.md).
- [ ] Contiene una breve descripción del proyecto.
- [ ] Proporciona instrucciones claras de instalación y ejecución.
- [ ] Incluye una referencia al video demo en la carpeta `/demo/`.
- [ ] Proporciona un enlace o referencia clara al informe final en la carpeta `/docs/`.

### **3. Revisión de Recursos**
- [ ] El archivo `Demo.mp4` está presente y es reproducible.
- [ ] El archivo `Informe.pdf` está presente y es accesible.

Cualquier proyecto que no cumpla con estos requisitos deberá ser corregido antes de la entrega final.

