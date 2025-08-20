FROM public.ecr.aws/docker/library/python:3.10.6-alpine3.15
ADD ./application /application
WORKDIR /application
RUN set -e; \
	apk add --no-cache --virtual .build-deps \
		gcc \
		libc-dev \
		linux-headers \
	; \
   pip install --upgrade pip; \
	pip install -r requirements.txt; \
	apk del .build-deps;
EXPOSE 8000
CMD uwsgi --http :8000  --manage-script-name --mount /myapplication=flask_app:app --enable-threads --processes 5

