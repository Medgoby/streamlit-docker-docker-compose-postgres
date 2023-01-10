# frontent/Dockerfile

FROM python:3.9-slim-buster

COPY requirements.txt app/requirements.txt

#WORKDIR /streamlit-docker

WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

#RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8501

# cmd to launch app when container is run
ENTRYPOINT python3 scripts/load_docker_db.py
CMD streamlit run app.py

#CMD ["streamlit","run"]
#CMD ["app.py"]