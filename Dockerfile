FROM python:3.12-alpine

RUN mkdir -p /home/worker/spider
WORKDIR /home/worker/spider

COPY requirements.txt /home/worker/spider/
COPY spider/*.py /home/worker/spider/

ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install -r requirements.txt

#CMD exec fastapi dev main.py
CMD ["fastapi", "run", "main.py"]
 