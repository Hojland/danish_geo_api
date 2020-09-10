FROM python:3

COPY requirements.txt requirements.txt

COPY data/ /app/data/

RUN pip install -r requirements.txt

RUN pip install jupyterlab

WORKDIR /app/src/

CMD ["sh", "-c", "jupyter lab --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token=dist"]