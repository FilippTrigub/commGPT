FROM 3.10.11-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY .. .

EXPOSE 8080
EXPOSE 8090

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["python", "commGPT\ChatWithTGChat.py"]

HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost:8090/ || exit 1