FROM ubuntu

RUN apt update -y 

RUN apt install python3 python3-dev -y

RUN apt install python3-pip -y

WORKDIR /app

COPY . /app


RUN pip3 install -r requirements.txt

EXPOSE 3000

ENTRYPOINT ["python3"]

CMD [ "app.py" ]