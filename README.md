

<h2 align="center">Outlier Identifier</h2>


## Overview

Use this repository to identify outliers in the stock exchange data:

<table>
<tr>
  <th>Language</th>
  <td>Python</td>
</tr>
<tr>
  <th>API</th>
  <td>FastAPI</td>
</tr>
</table>

## Preconditions:

- Python 3

## Clone the project

```
git clone https://github.com/nitinsaivishnu/outlier-identifier.git
```

### Install dependencies

```
pip install -r requirements.txt
```

### Run server

```
uvicorn app:app --host 0.0.0.0 --reload
```

## Run with docker
```
docker build -t <image_name> .
```


### Run server

```
docker run -it -p 8000:8000 <image_name>
```


## API documentation (provided by Swagger UI)

```
http://localhost:8000/docs
```

## Docker Instructions


## Assumptions

1. Stock Exchanges assumed to be Enum (LSE,NASDAQ,NYSE)
2. Data is available inside data folder in the repo
3. Output folder is created with the name results and outlier csvs are stored inside it.

## Questions


## License

This template repository is [MIT licensed](LICENSE).