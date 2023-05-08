FROM python:3.10.11-slim-buster

WORKDIR ./

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .env
COPY api api
COPY frontend frontend

EXPOSE 7100
EXPOSE 7000

ENV PYTHONPATH "${PYTHONPATH}:./"

COPY startup.sh startup.sh

CMD ["./startup.sh"]

HEALTHCHECK --interval=5m --timeout=3s CMD curl -f http://localhost:7000 || exit 1