# Pythonイメージの取得
FROM python:3.7.9-slim-buster
# ワーキングディレクトリの指定
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
# モジュールを揃える
COPY . .
# 起動環境設定
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]