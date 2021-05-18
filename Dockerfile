FROM tensorflow/tensorflow

COPY . /id_service

WORKDIR /id_service

RUN apt update && apt install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 libssl-dev

RUN python3 -m pip install -r requirements.txt

RUN UWSGI_PROFILE_OVERRIDE=ssl=true pip install uwsgi -I --no-cache-dir

EXPOSE 5000

ENTRYPOINT bash -c "celery -A utils.celery_tasks --workdir=./app worker --loglevel=info --logfile=/id_service/celery.log & \
                    uwsgi --vacuum --lazy-apps --workers 4 --threads 2 --https :5000,ssl/security.crt,ssl/security.key --chdir app -w wsgi:app"
