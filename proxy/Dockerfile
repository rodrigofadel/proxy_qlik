FROM python:3.12

WORKDIR /proxy

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /proxy/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]