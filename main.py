from __future__ import print_function
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Permiso: acceso a archivos creados o abiertos por este script
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Variable de entorno para el PATH donde se encuentre la carpeta que se desee hacer backup
VAULT_PATH = r"C:\Users\valen\OneDrive\Documentos\Obsidian Vault"

def authenticate():
    """Autentica al usuario y devuelve el servicio de la API de Drive"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    return service


def get_or_create_folder(service, folder_name, parent_id=None):
    """Busca una carpeta en Drive, y si no existe, la crea"""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])

    if items:
        return items[0]['id']
    else:
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        if parent_id:
            file_metadata['parents'] = [parent_id]
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder['id']


def upload_or_update_file(service, file_path, parent_id):
    """Sube un archivo o lo reemplaza si ya existe"""
    file_name = os.path.basename(file_path)
    query = f"name='{file_name}' and '{parent_id}' in parents"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    items = results.get('files', [])

    media = MediaFileUpload(file_path, resumable=True)
    if items:
        file_id = items[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"- Actualizado: {file_name}")
    else:
        file_metadata = {'name': file_name, 'parents': [parent_id]}
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"- Subido: {file_name}")


def upload_folder_recursive(service, local_folder, parent_id=None):
    """Sube una carpeta local completa a Drive"""
    folder_name = os.path.basename(local_folder.rstrip('/\\'))
    folder_id = get_or_create_folder(service, folder_name, parent_id)

    for root, dirs, files in os.walk(local_folder):
        relative_path = os.path.relpath(root, local_folder)
        current_parent_id = folder_id

        if relative_path != ".":
            parts = relative_path.split(os.sep)
            for part in parts:
                current_parent_id = get_or_create_folder(service, part, current_parent_id)

        for file in files:
            if file.endswith('.md') or file.endswith('.txt'):
                file_path = os.path.join(root, file)
                upload_or_update_file(service, file_path, current_parent_id)


if __name__ == '__main__':
    service = authenticate()

    # Ruta local a la carpeta de Obsidian Vault (o la que se desee backupear)
    vault_path = os.path.expanduser(VAULT_PATH)

    if os.path.exists(vault_path):
        print("--// Iniciando backup del Vault...")
        upload_folder_recursive(service, vault_path)
        print("✅ Backup completo!")
    else:
        print("❌ No se encontró la carpeta del Vault. Verifica la ruta.")