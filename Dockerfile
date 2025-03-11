# syntax=docker/dockerfile:1

# Se proporcionan comentarios a lo largo de este archivo para ayudarte a comenzar.
# Si necesitas más ayuda, visita la guía de referencia de Dockerfile en
# https://docs.docker.com/go/dockerfile-reference/

ARG PYTHON_VERSION=3.12.0
FROM python:${PYTHON_VERSION}-slim as base
RUN apt-get update && apt-get install -y sudo

# Evita que Python escriba archivos pyc.
ENV PYTHONDONTWRITEBYTECODE=1

# Evita que Python almacene en búfer stdout y stderr para evitar situaciones
# donde la aplicación se bloquee sin emitir ningún registro debido al almacenamiento en búfer.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Crea un usuario no privilegiado bajo el cual se ejecutará la aplicación.
# Ver https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/nonexistent" --shell "/sbin/nologin" --no-create-home --UID ${UID} appuser

# Descarga las dependencias como un paso separado para aprovechar la caché de Docker.
# Aprovecha un montaje de caché en /root/.cache/pip para acelerar las compilaciones posteriores.
# Aprovecha un montaje de enlace a requirements.txt para evitar tener que copiarlos en
# esta capa.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install --upgrade pip && \
    python -m pip install gunicorn && \
    python -m pip install -r requirements.txt

# Copia el código fuente en el contenedor.
COPY . .
RUN sudo chown -R appuser /app

# Cambia al usuario no privilegiado para ejecutar la aplicación.
USER appuser

# Expone el puerto en el que la aplicación escucha.
EXPOSE 80

# Realiza las migraciones

# Ejecuta la aplicación.
ENV POSTGRES_PASSWORD = ${POSTGRES_PASSWORD}
ENV POSTGRES_USER = ${POSTGRES_USER}
ENV AWS_ACCESS_KEY_ID = ${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY = ${AWS_SECRET_ACCESS_KEY}
ENV SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=${SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}
ENV SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=${SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET}

RUN echo -e "POSTGRES_PASSWORD=\"$POSTGRES_PASSWORD\"POSTGRES_USER=\"$POSTGRES_USER\"AWS_ACCESS_KEY_ID=\"$AWS_ACCESS_KEY_ID\"AWS_SECRET_ACCESS_KEY=\"$AWS_SECRET_ACCESS_KEY\"" > /app/.env

CMD gunicorn 'MachineTrek.wsgi' --bind=0.0.0.0:80
