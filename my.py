import requests

# 1. Guarda solo el ID de tu proyecto (sin https:// ni .supabase.co)
project_id = "yczqvokerabfhuihreju" 
KEY = "TU_KEY_AQUI"
# 2. Construye la URL correctamente
url = f"https://{project_id}.supabase.co/rest/v1/"

headers = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}"
}

try:
    response = requests.get(url, headers=headers)
    
    # 3. Solo 200 (OK) indica una conexión y autenticación exitosas
    if response.status_code == 200:
        print("Conexión exitosa a la API de Supabase.")
    elif response.status_code == 401:
        print("Error de autenticación (401): Revisa tu API Key.")
    else:
        print(f"Error en la conexión. Código HTTP: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"Error al intentar conectar: {e}")