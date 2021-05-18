#!/bin/bash
openssl genrsa -out ssl/security.key 2048
openssl req -new -key ssl/security.key -out ssl/security.csr
openssl x509 -req -days 365 -in ssl/security.csr -signkey ssl/security.key -out ssl/security.crt