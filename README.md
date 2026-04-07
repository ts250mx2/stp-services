# STP Payment Service

Este servicio permite registrar órdenes de pago en el ambiente de pruebas de STP.

## Requisitos

- Python 3.7+
- Dependencias listadas en `requirements.txt`

## Instalación

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Como Script Independiente

Puedes ejecutar `stp_client.py` directamente para realizar la petición con los datos de prueba:
```bash
python stp_client.py
```

### Como Servicio Web (FastAPI)

1. Inicia el servidor:
   ```bash
   python main.py
   ```
   O usando uvicorn con recarga automática:
   ```bash
   python -m uvicorn main:app --reload
   ```

2. Realiza una petición POST al endpoint `/registrar-pago`:
   ```bash
   curl -X POST http://localhost:8000/registrar-pago \
   -H "Content-Type: application/json" \
   -d '{
     "claveRastreo": "123456789",
     "conceptoPago": "Prueba REST",
     "cuentaOrdenante": "646180123412345678",
     "cuentaBeneficiario": "646180110400000007",
     "cuentaParticipanteIndirecto": "646180123412345678",
     "empresa": "EMPRESAPRUEBA",
     "institucionContraparte": "90646",
     "institucionOperante": "90646",
     "monto": "20.00",
     "nombreBeneficiario": "Nombre Beneficiario",
     "nombreOrdenante": "Nombre Ordenante",
     "referenciaNumerica": "123456",
     "rfcCurpBeneficiario": "ND",
     "rfcCurpOrdenante": "ND",
     "tipoCuentaBeneficiario": "40",
     "tipoCuentaOrdenante": "40",
     "tipoPago": "1",
     "latitud": "19.370312",
     "longitud": "-99.180617",
     "firma": "VUtSTfmBf7LdnXtPgz+SiRH7yn1ZXrtexGpdcTj/oRREiQcTSo0UUam01sFMNC6HgqQovUlDIoilM/zd6cGjzsI8VmpXG/d9M0fk8OljGBcuS1rzK0RoCpmi7jRm2YkpEEKgKmwGIqQlDoJQqU1izLqNYt3NYMR6A7icuyoefEP1YqggSQ0+5pEWDoO/mSlAbCi3fDzdVrDrRr48rrBW08D3dDBSF2kMZqtYhK2OxWhgziVigZuy0kZpg0yt3j1bLFhOLKbp6ieReIHI5/B7OZPQ24aWzcxiRdN3OAfWzfN3f3DM8becDoTEbR6GnFsDCf8ohsOJ0HaV2ZhmTORG1w=="
   }'
   ```

### Webhook de Liquidación

El servicio expone un endpoint en `/webhook` para recibir notificaciones de STP.

Para probarlo localmente:
```bash
curl -X POST http://localhost:8000/webhook \
-H "Content-Type: application/json" \
-d "{
 \"id\": 12342912,
 \"empresa\": \"string\",
 \"claveRastreo\": \"string\",
 \"estado\": \"LQ\",
 \"causaDevolucion\": \"string\",
 \"tsLiquidacion\": \"1634919027297\"
}"
```

Respuesta esperada:
```json
{"mensaje":"recibido"}
```

### Webhook de CEP (Comprobante Electrónico de Pago)

El servicio también expone un endpoint en `/webhook-cep` para recibir notificaciones de CEP.

Para probarlo localmente:
```bash
curl -X POST http://localhost:8000/webhook-cep \
-H "Content-Type: application/json" \
-d '{
    "rfcCep": "MAAN8609106DA",
    "urlCEP": "http://example.com/cep",
    "nombreCep": "NICOLAS MARIN ALVARADO",
    "empresa": "VALIDADORA",
    "fechaOperacion": "19691231",
    "sello": "aiBme48xn84xspLEQ0WE",
    "claveRastreo": "STPCRPT1661795995902IDZOLNV",
    "cuentaBeneficiario": "152580100000000307"
}'
```

Respuesta esperada:
```json
{"mensaje":"recibido"}
```
