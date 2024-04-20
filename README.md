This python project is designed to return instagram stories compatible images according to sales links sent to it

Current implementations cover:

* /ama         - Amazon
* /nat         - Natura
* /ml          - Mercado Livre
* /mag         - Magazine Luiza
* /mag ofertas - Magazine Luiza

To run it:
```
docker run -d --rm --env-file sample.env marcelocollyer/sales-scrapper-py
```