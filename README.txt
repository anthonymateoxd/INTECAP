SIGVE INTECAP - PostgreSQL V1
=============================

Estructura:

sigve_postgresql_v1/
├── docker-compose.yml
├── .env
└── database/
    └── init/
        └── 001_schema_v1.sql

Levantar PostgreSQL:

    docker compose up -d

Ver estado:

    docker compose ps

Ver logs:

    docker compose logs -f postgres

Entrar con psql dentro del contenedor:

    docker compose exec postgres psql -U sigve_user -d sigve

Detener:

    docker compose down

IMPORTANTE SOBRE EL SCRIPT DE INICIALIZACIÓN
---------------------------------------------

PostgreSQL ejecuta los archivos de /docker-entrypoint-initdb.d SOLO
cuando el volumen de datos se crea por primera vez.

Si modificas 001_schema_v1.sql después de haber levantado la base y
quieres reconstruir TODO desde cero:

    docker compose down -v
    docker compose up -d

ADVERTENCIA:
`docker compose down -v` elimina la base de datos local y todos sus datos.

Pendientes documentados en la V1:
- Confirmar capacidad de tanque por vehículo.
- Confirmar interpretación exacta de "E" en saldo de tanque.
- Confirmar cilindraje vs C.C.
- Confirmar periodicidad de mantenimiento: km, tiempo o ambos.
- Confirmar estados adicionales de comisión, si existen.
