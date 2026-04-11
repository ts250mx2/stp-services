import requests
import json

url = "http://127.0.0.1:8000/crear-orden-stp"

payload = {
    "nombreBeneficiario": "S.A. de C.V.",
    "cuentaBeneficiario": "646180209100000001",
    "rfcCurpBeneficiario": "ND",
    "referenciaNumerica":"123457",
    "id_sucursal": 1,
    "id_bloque": 1
}

print(f"Testing {url} with payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
