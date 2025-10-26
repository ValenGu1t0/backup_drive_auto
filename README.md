
### 🗂️ Backup de Obsidian a Google Drive (o cualquier carpeta con archivos que quieras)

Desarrollé un pequeño script en Python que realiza una copia de seguridad diaria de la carpeta de archivos raíz que genera Obsidian Vault (subcarpetas y archivos .md / .txt) en mi Google Drive. La idea era automatizar este proceso que realizo casi a diario y de paso probar un poco las API de Google Cloud.

El comportamiento esperado es que la carpeta se crea o sobrescribe en la raíz de Drive cada vez que corre el script. Este script fue automatizado con el task manager de Windows para realizar una copia cada dia. 


- Estructura ideal del repositorio

```
backup_drive_auto/
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
├── credentials.json   # NO subir a GitHub
└── token.json         # generado en la primera ejecución al autorizar el script en tu cuenta de drive (NO subir tampoco)
```

- Contenido recomendado para .gitignore:

```
venv/
__pycache__/
credentials.json
token.json
```

### ⚠️ Importante sobre seguridad

**No subas credentials.json ni token.json a GitHub**. Si por error subiste credenciales, bórralas del repositorio y del historial (ver sección Remover credenciales del repo abajo). Trata las credenciales como secretos: guárdalas fuera de repositorios públicos.

---

## Setup!

### 🛠️ Requisitos previos

- Python 3.9+ (o 3.8+ recomendado)
- Cuenta Google con espacio disponible (Google Drive)
- Acceso a la consola de Google Cloud (https://console.cloud.google.com)
- Git y una cuenta en GitHub (obligatorio para clonar en tu máquina, opcional para compartir)


### 🚀 Instalación y uso (Windows / Linux)


**1. Clonar el repositorio**

```
git clone https://github.com/ValenGu1t0/backup_drive_auto.git
cd backup_drive_auto
```

**2. Crear y activar entorno virtual**

- Windows: 

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

- Linux / macOS

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- requirements.txt debe contener las dependencias usadas, por ejemplo:

```
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
```

**3. Configurar credenciales de Google Cloud (paso a paso)**

Nota importante: Google muestra y permite descargar el client_secret **solo al momento de crear el secreto**. Si cerrás el dialogo sin descargar, después puede no estar disponible y tendrás que crear uno nuevo. Si ves un aviso en la consola sobre "viewing and downloading client secrets will no longer be available" o similar, seguí las indicaciones abajo.

**a) Crear proyecto en Google Cloud**

Entrá en https://console.cloud.google.com/ y logueate con tu cuenta.
En la parte superior -> Seleccionar proyecto -> Nuevo proyecto. Ponle un nombre (ej. BackupObsidian) y crealo.

**b) Habilitar Google Drive API**

Dentro del proyecto: API y servicios -> Biblioteca.
Buscá Google Drive API y hacé Habilitar.

**c) Configurar pantalla de consentimiento (OAuth)**

API y servicios -> Pantalla de consentimiento OAuth.
Tipo: Externo (si vas a usarlo solo para tu cuenta, está bien).
Completá los campos mínimos: nombre de la app, correo, y guardá.

**d) Crear credenciales (ID de cliente OAuth)**

API y servicios -> Credenciales -> Crear credenciales -> ID de cliente de OAuth.
Aplicación: Escritorio.


**IMPORTANTE: Al crear el ID verás un cuadro con el ID y el secreto y un botón “Descargar JSON”.**

Descargá ese JSON de inmediato. Ese archivo es tu credentials.json. Si no lo descargaste o nunca apareció el cuadro, volvé a la fila del credential (icono lápiz) -> Agregar secreto / Create new secret y descargalo justo después de crearlo.

Guardá el archivo descargado como credentials.json en la raíz del proyecto (backup_obsidian/credentials.json).

Si el botón de descarga no aparece por problemas del navegador, probá otro navegador (Firefox, Chrome sin extensiones) o desactivá bloqueadores de popups. Si ya cerraste la ventana sin descargar, generá un nuevo client secret como se indicó.


**4. Ejecutar por primera vez (autorización)**

Con **credentials.json ya en la carpeta del proyecto** que clonaste de github y el **entorno virtual activo**:

`python main.py`

Se abrirá una ventana para que autorices la app con tu cuenta Google. Al autorizarse se generará `token.json` (almacena el token de acceso/refresh). Ese archivo ya está en .gitignore.


**5. Ajustar la ruta del Vault**

En `main.py`, apenas comienza el archivo, hay una variable que apunta a la ruta de la carpeta a ser backupeada:

`VAULT_PATH = r"C:\Users\tuUsuario\Documentos\Obsidian Vault"`

Modificala si tu Vault está en otra ruta (Windows: C:\Users\TuUsuario\Documents\Obsidian Vault, Linux: /home/tuusuario/Documents/Obsidian Vault, etc.).

---

## Ejecutando..

### 🔁 Comportamiento del script

- Crea en la raíz de tu Google Drive una carpeta con el nombre “Obsidian Vault” (si no existe). 
- Recorre recursivamente subcarpetas y sube archivos .md y .txt.
- Si un archivo ya existe en la misma carpeta de Drive, lo sobrescribe (actualiza) — no duplica.
- Muestra en consola los archivos subidos/actualizados.

---

### ⏰ Automatizar ejecución diaria

Si deseas automatizar esta tarea como yo, debes ingresar a:

- Windows (Task Scheduler)

Abrir Task Scheduler (Programador de tareas).
Crear tarea básica: Programación diaria -> acción: Iniciar un programa.
Programa: python (ruta completa del ejecutable dentro de venv\Scripts\python.exe).
Argumentos: C:\ruta\a\backup_obsidian\main.py
Configurar usuario y “Run whether user is logged on or not” si querés que corra en background.

- Linux (cron)

Editar cron con crontab -e y añadir por ejemplo para ejecutar cada día a las 02:00:

0 2 * * * /home/tuusuario/backup_obsidian/venv/bin/python /home/tuusuario/backup_obsidian/main.py >> /home/tuusuario/backup_obsidian/backup.log 2>&1

---

### 🧰 Problemas comunes

- No se descargó credentials.json al crear el OAuth client:

-> Probá crear un nuevo secret (editar credencial -> crear nuevo secreto) y descargarlo inmediatamente.

-> Probar otro navegador y desactivar bloqueadores de popup.

- `credentials.json` o `token.json` apareció en GitHub por error:

-> Remover el archivo del repo:

```
git rm --cached credentials.json
git commit -m "Remover credentials del repo"
git push
```

- Para eliminar del historial (si querés limpiar commits anteriores), usar herramientas como git filter-repo o BFG Repo-Cleaner (buscar guía detallada antes de ejecutar).

- Permisos insuficientes: revisá el scope usado en main.py (por defecto https://www.googleapis.com/auth/drive.file) y que el usuario haya autorizado ese scope.

- Popup de autorización no se abre: el script flow.run_local_server() abre un navegador. Si usás servidor remoto o WSL sin GUI, usá flow.run_console() y pegá manualmente el URL/token que te da Google.

---

### 🧾 Notas sobre permisos y alcance (SCOPES)

El script usa por defecto:

`SCOPES = ['https://www.googleapis.com/auth/drive.file']`

`drive.file` solo permite al script acceder y crear/editar archivos que la app crea o con los que el usuario la autoriza explícitamente. Es más seguro que pedir acceso completo a todo Drive.

Si necesitás otro alcance (por ejemplo para listar todo Drive), deberás ajustar SCOPES y re-autenticar.

---

### ✅ Verificación rápida (después de correr)

Ejecutá `python main.py`.

Mirá la consola: verás mensajes `- Subido:` o `- Actualizado:`.

Abrí tu Google Drive y verificá que exista la carpeta Obsidian Vault con las subcarpetas y .md subidos.



### ❓ Preguntas frecuentes (rápidas)

- ¿Puedo usar otra carpeta que no esté en Documents? Sí: cambia vault_path en main.py.

- ¿Puedo incluir otros tipos de archivo? Sí: modificar la condición if file.endswith(...) en main.py.

- ¿Puedo restaurar fácilmente desde Drive? Sí: descargá los archivos desde la carpeta Obsidian Vault en Drive.