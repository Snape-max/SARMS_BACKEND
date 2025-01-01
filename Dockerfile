FROM python:3.9-slim

WORKDIR /app
COPY . .
# install the requirements
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "wsgi:appx"]

