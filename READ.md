# Instalación de Dependencias

Para instalar todas las dependencias necesarias del proyecto, sigue estos pasos:

1. Asegúrate de tener Python instalado en tu sistema
2. Abre una terminal en la raíz del proyecto
3. Ejecuta el siguiente comando:

```bash
pip install -r requirements.txt
python -m spacy download es_core_news_md
```

> Nota: Se recomienda usar un entorno virtual antes de instalar las dependencias

### Usando entorno virtual (opcional)
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows
```