FROM python:3.9
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
