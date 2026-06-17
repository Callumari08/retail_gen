FROM python:3

# install pip packages, defined in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./

RUN mkdir -p videos/

CMD [ "python", "src/main.py" ]