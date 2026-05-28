# SaludGestion MVP

Aplicacion web monolito en Python/Flask para gestionar pacientes, citas, historiales medicos, medicos, consultorios y autenticacion por roles.

## Stack

- Flask + Jinja2
- SQLAlchemy + Flask-Migrate
- PostgreSQL
- JWT para endpoints protegidos
- MVC por modulos

## Configuracion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` con tu cadena de PostgreSQL.

## Base de datos

```powershell
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

## Datos iniciales

```powershell
.\.venv\Scripts\python.exe seed.py
```

Usuarios de prueba:

- Recepcionista: `recepcion` / `Recepcion123`
- Medicos: `lperez`, `mgomez`, `cvargas` / `Medico123`

## Ejecutar

```powershell
flask run
```

Abre `http://127.0.0.1:5000`.

## Docker

Construir imagen:

```powershell
docker build -t saludgestion .
```

Ejecutar contenedor:

```powershell
docker run --rm -p 8000:8000 --env-file .env saludgestion
```

Antes de usar una base nueva, ejecuta las migraciones apuntando al mismo `DATABASE_URL`:

```powershell
docker run --rm --env-file .env saludgestion flask db upgrade
```

## Usuario inicial

Puedes crear el primer usuario desde `/register` seleccionando rol `recepcionista`. Para crear medicos y consultorios, entra a `/resources`.

## Endpoints principales

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET|POST /api/patients`
- `PUT /api/patients/<id>`
- `GET|POST /api/appointments`
- `POST /api/appointments/<id>/cancel`
- `GET /api/doctors/<id>/availability?date=YYYY-MM-DD`
- `POST /api/records`
- `GET /api/patients/<id>/records`
- `GET|POST /api/doctors`
- `GET|POST /api/rooms`

## Roles

- `recepcionista`: gestiona pacientes, citas, disponibilidad y recursos.
- `medico`: consulta agenda y registra historiales medicos.

## Formato de respuesta API

Todos los endpoints JSON responden:

```json
{
  "success": true,
  "data": {},
  "timestamp": "2026-05-28T12:00:00Z"
}
```
