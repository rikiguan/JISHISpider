FROM python:3.8.5

ADD . /opt/jishi

WORKDIR /opt/jishi

ENV TZ=Asia/Shanghai

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone



RUN apt-get update && apt-get install -y \
    fontconfig \
    && apt-get clean


COPY ./fonts /usr/share/fonts/truetype/custom/

RUN fc-cache -fv

VOLUME ["/opt/jishi/data", "/opt/jishi/log"]

RUN pip install -r requirements.txt

EXPOSE 3000

ENTRYPOINT ["python", "Spider.py"]

