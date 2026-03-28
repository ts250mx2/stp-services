import requests
import json
import urllib3
import config

# Desactivar advertencias de solicitudes inseguras (para el parámetro -k)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class STPClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.STP_WEBSERVICE_URL
        self.headers = {
            'Content-Type': 'application/json'
        }

    def registrar_orden_pago(self, payload: dict):
        """
        Ejecuta la petición PUT al servicio de STP.
        """
        print(f"Enviando petición a {self.base_url}...")
        try:
            # verify=False equivale al parámetro -k de curl
            response = requests.put(
                self.base_url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=False
            )
            
            # Imprimir detalles de la respuesta (equivale a -v parcial)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            print(f"Error al realizar la petición: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Los datos se pueden omitir y tomar del config.py
    data = {
        "claveRastreo": "123456799",
        "monto": "20.00",
        "nombreBeneficiario": "Nombre Beneficiario",
        "cuentaBeneficiario": "646180110400000007",
        "institucionContraparte": config.STP_INSTITUCION_CONTRAPARTE,
        "empresa": config.STP_EMPRESA,
        "cuentaOrdenante": config.STP_CUENTA_ORDENANTE,
        "nombreOrdenante": config.STP_NOMBRE_ORDENANTE,
        "rfcCurpOrdenante": config.STP_RFC_CURP_ORDENANTE,
        "tipoCuentaOrdenante": config.STP_TIPO_CUENTA_ORDENANTE,
        "tipoCuentaBeneficiario": config.STP_TIPO_CUENTA_BENEFICIARIO,
        "tipoPago": config.STP_TIPO_PAGO,
        "cuentaParticipanteIndirecto": config.STP_CUENTA_PARTICIPANTE_INDIRECTO,
        "referenciaNumerica": "123456",
        "latitud": "19.370312",
        "longitud": "-99.180617",
        "firma": "VUtSTfmBf7LdnXtPgz+SiRH7yn1ZXrtexGpdcTj/oRREiQcTSo0UUam01sFMNC6HgqQovUlDIoilM/zd6cGjzsI8VmpXG/d9M0fk8OljGBcuS1rzK0RoCpmi7jRm2YkpEEKgKmwGIqQlDoJQqU1izLqNYt3NYMR6A7icuyoefEP1YqggSQ0+5pEWDoO/mSlAbCi3fDzdVrDrRr48rrBW08D3dDBSF2kMZqtYhK2OxWhgziVigZuy0kZpg0yt3j1bLFhOLKbp6ieReIHI5/B7OZPQ24aWzcxiRdN3OAfWzfN3f3DM8becDoTEbR6GnFsDCf8ohsOJ0HaV2ZhmTORG1w=="
    }
    
    client = STPClient()
    client.registrar_orden_pago(data)
