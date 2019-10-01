FROM swim-base.conda

LABEL maintainer="SWIM EUROCONTROL <http://www.eurocontrol.int>"

ENV PATH="/opt/conda/envs/app/bin:$PATH"

RUN mkdir -p /app
RUN touch /app/swim.env
RUN chmod 664 /app/swim.env

WORKDIR /app

COPY requirements.yml requirements.yml
RUN conda env create --name app -f requirements.yml

COPY ./swim_user_config/ ./swim_user_config/

COPY . /source/
RUN set -x \
    && pip install /source \
    && rm -rf /source

CMD ["python", "-u", "/app/swim_user_config/main.py"]
