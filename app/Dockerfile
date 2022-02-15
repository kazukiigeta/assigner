FROM python:3.9-slim

ARG USER_NAME=streamlit
ARG GROUP_NAME=streamlit

WORKDIR /app

RUN groupadd "${GROUP_NAME}" && useradd -m -g "${GROUP_NAME}" -s /bin/sh "${USER_NAME}" && chown -R "${USER_NAME}":"${GROUP_NAME}" /app && chown -R "${USER_NAME}":"${GROUP_NAME}" /home/streamlit

COPY requirements.txt .
COPY *py /app/

RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8501

USER streamlit

CMD ["streamlit", "run", "app.py"]
