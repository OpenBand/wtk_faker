# Faker from W?ToolKit #

## To install WTL tool use virtual envinroment (ex. old one [venv](https://docs.python.org/3/library/venv.html)):

Deploy and run:
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

python ./wfaker.py
```

Cleanup:
```
rm -rf .venv
```

## Another way is to build Docker container:

To use inside a custom application in docker infrastructure.

Deploy and run:
```
docker build -t wfaker.application_domain .
# Remove intermediate build image to save disk space
docker rmi $(docker images -q -f dangling=true)
docker run --rm wfaker.application_domain
```

Cleanup:
```
docker rmi wfaker.application_domain
docker system prune -f
```
> and remember about base Python container (for example _python:3.9-slim_)
