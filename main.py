from fastapi import FastAPI, UploadFile
from deepface import DeepFace
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Middleware CORS (poner primero)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite por defecto corre aquí
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carpeta para subir imágenes
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analyze")
async def analyze_face(file: UploadFile):
    # Guardar archivo temporal
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Detectar rostro
    try:
        result = DeepFace.detectFace(file_path, detector_backend="retinaface", enforce_detection=True)
        # Por ahora devolvemos un box fijo como ejemplo
        faceBox = {"x": 50, "y": 50, "w": 200, "h": 200}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Opcional: borrar la imagen temporal
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"faceBox": faceBox}
