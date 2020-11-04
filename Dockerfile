FROM python:3.7-alpine
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
COPY start.sh start.sh
RUN chmod 777 start.sh
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD './start.sh'