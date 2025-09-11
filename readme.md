# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
venv\Scripts\activate  # En Windows
# source venv/bin/activate  # En MacOS/Linux

# Instalar dependencias
pip install "fastapi[standard]"
pip install "python-jose[cryptography]"
pip install psycopg2-binary sqlalchemy fastapi[all] passlib[bcrypt]
pip install tf-keras  # Si es necesario

# Correr el servidor de desarrollo
uvicorn main:app --reload

