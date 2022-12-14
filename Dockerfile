FROM python:3.9

ADD /requirements.txt project/requirements.txt
ADD /api_parser.py project/api_parser.py
ADD /main.py project/main.py
ADD /.env project/.env
ADD /db/client.py project/db/client.py
ADD /db/interaction.py project/db/interaction.py
ADD /metrics/metrics.py project/metrics/metrics.py
ADD /src/creds.json project/src/creds.json

RUN pip3 install -r /project/requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/project"
WORKDIR /project

EXPOSE 8001

CMD ["python", "main.py"]