# Cafetería POS

Proyecto de ejemplo con Django 5 y Prisma Client Python.

## Requisitos

- Python 3.11
- MySQL o MariaDB

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configura tus variables de entorno:

```bash
cp .env.example .env
# edita .env con tu DATABASE_URL
```

Genera el cliente de Prisma y aplica migraciones:

```bash
prisma generate
prisma migrate deploy
```

Ejecuta el servidor de desarrollo:

```bash
python manage.py runserver
```

## Estructura

- `core/` configuración de Django
- `pos/` aplicación del punto de venta
- `prisma/schema.prisma` modelos de base de datos
