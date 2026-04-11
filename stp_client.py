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

    
    client = STPClient()
    client.registrar_orden_pago(data)
