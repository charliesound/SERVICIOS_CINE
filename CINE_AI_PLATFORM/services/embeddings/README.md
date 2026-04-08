# Local Embeddings Service

Servicio HTTP local para generar embeddings de 384 dimensiones compatibles con la colección `cine_project_context`.

## Modelo
- `BAAI/bge-small-en-v1.5`
- dimensiones esperadas: `384`

## Nota importante
Este servicio está alineado con la colección Qdrant `cine_project_context`, que espera vectores de **384 dimensiones**.  
Si en el futuro se cambia el modelo y cambia la dimensionalidad, también habrá que ajustar la colección en Qdrant.

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\services\embeddings\requirements.txt