# POS Django (super corto)

Vender en local con Django + MariaDB: carrito, efectivo (cambio en vivo) / tarjeta, historial con filtros. **Cualquier usuario autenticado puede vender.** Gestión de categorías/productos solo *staff*.

## Requisitos
- Python 3.11+ • Docker & docker-compose
- Linux: `sudo apt-get install -y build-essential pkg-config libmariadb-dev` (para `mysqlclient`)

## Arranque rápido (también para otra laptop)
```bash
git clone el repo
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip && pip install -r requirements.txt
cp .env.example .env
docker compose up -d
python manage.py migrate
python manage.py seed_pos
# usuario para vender
python manage.py shell -c "from django.contrib.auth import get_user_model as g; U=g(); U.objects.filter(username='cajero').exists() or U.objects.create_user('cajero','cajero@example.com','cajero123'); print('cajero/cajero123')"
# (opcional) hacerlo staff para gestionar cat/productos
python manage.py shell -c "from django.contrib.auth import get_user_model as g; u=g().objects.get(username='cajero'); u.is_staff=True; u.save(); print('cajero es staff')"
python manage.py runserver
