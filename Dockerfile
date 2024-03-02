FROM python:3.10-slim

RUN python -m pip --no-cache-dir install pdm
RUN pdm config python.use_venv false

COPY pyproject.toml pdm.lock /project/

WORKDIR /project
RUN pdm install

COPY src/recruit_tracker_api /project/recruit_tracker_api

WORKDIR /project

EXPOSE 3000

# ENTRYPOINT ["sleep", "600"]
ENTRYPOINT ["pdm", "run", "--", "python", "-m", "uvicorn", "recruit_tracker_api.app:app", "--host", "0.0.0.0", "--port", "3000"]
CMD []
