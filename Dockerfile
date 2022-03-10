FROM python:3.8.8
MAINTAINER realhuhu
EXPOSE 8080
ADD doc/requriements.txt /home/
RUN pip install -r /home/requriements.txt -i https://pypi.douban.com/simple/
RUN pip install uwsgi -i https://pypi.douban.com/simple/
VOLUME ["/home"]
WORKDIR /home/backend
CMD ["uwsgi", "--ini", "uwsgi.ini"]