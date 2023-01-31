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

Deploy and run:
```
docker build -t wfaker.my_set .
# Remove intermediate build image to save disk space
docker rmi $(docker images -q -f dangling=true)
docker run --rm wfaker.my_set
```

Cleanup:
```
docker rmi wfaker.my_set
docker system prune -f
```
> and remember about base Python container (python:3.9-slim)
