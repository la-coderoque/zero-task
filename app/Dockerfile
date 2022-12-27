FROM python:3.11
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
RUN mkdir upload
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
