FROM public.ecr.aws/docker/library/python:3.10.6-alpine3.15
RUN set -e; \
   pip install --upgrade pip; \
   pip install pymysql==1.1.0; \
   mkdir /application
WORKDIR /application
ADD db_filler.py ./db_filler.py
CMD python3 db_filler.py

