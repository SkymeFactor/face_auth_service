FROM tensorflow/tensorflow

COPY . /id_service

WORKDIR /id_service

RUN apt update && apt install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6

RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT bash -c "/usr/bin/python3 app/app.py"
