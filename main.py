from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from stp_client import STPClient
import uvicorn
import config
import pyodbc
import base64
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import json
import requests


app = FastAPI(title="STP Payment Service")
client = STPClient()

class PaymentOrder(BaseModel):
    claveRastreo: Optional[str] =""
    conceptoPago: Optional[str] = config.STP_CONCEPTO_PAGO
    conceptoPago2: Optional[str] = ""
    cuentaOrdenante: Optional[str] = config.STP_CUENTA_ORDENANTE
    cuentaBeneficiario: str = ""
    empresa: Optional[str] = config.STP_EMPRESA
    fechaOperacion: Optional[str] = ""
    folioOrigen: Optional[str] = ""
    institucionContraparte: Optional[str] = config.STP_INSTITUCION_CONTRAPARTE
    institucionOperante: Optional[str] = config.STP_INSTITUCION_OPERANTE
    monto: Optional[str] = config.STP_MONTO
    nombreBeneficiario: str = ""
    nombreOrdenante: Optional[str] = config.STP_NOMBRE_ORDENANTE
    referenciaNumerica: str = "0"
    rfcCurpBeneficiario: Optional[str] = "ND"
    rfcCurpOrdenante: Optional[str] = config.STP_RFC_CURP_ORDENANTE
    tipoCuentaBeneficiario: Optional[str] = config.STP_TIPO_CUENTA_BENEFICIARIO
    tipoCuentaOrdenante: Optional[str] = config.STP_TIPO_CUENTA_ORDENANTE
    tipoCuentaBeneficiario2: Optional[str] = ""
    nombreBeneficiario2: Optional[str] = ""
    cuentaBeneficiario2: Optional[str] = ""
    rfcCurpBeneficiario2: Optional[str] = ""
    emailBeneficiario: Optional[str] = ""
    claveCatUsuario1: Optional[str] = ""
    claveCatUsuario2: Optional[str] = ""
    clavePago: Optional[str] = ""
    referenciaCobranza: Optional[str] = ""
    tipoOperacion: Optional[str] = ""
    topologia: Optional[str] = ""
    usuario: Optional[str] = ""
    medioEntrega: Optional[str] = ""
    prioridad: Optional[str] = ""
    iva: Optional[str] = ""   
    tipoPago: Optional[str] = config.STP_TIPO_PAGO
    latitud: Optional[str] = "0.0"
    longitud: Optional[str] = "0.0"
    id_sucursal: Optional[int] = 0
    id_bloque: Optional[int] = 0
    firma: Optional[str] = ""

class WebhookRequest(BaseModel):
    id: int
    empresa: str
    claveRastreo: str
    estado: str
    causaDevolucion: Optional[str] = None
    tsLiquidacion: str

class CEPRequest(BaseModel):
    rfcCep: str
    urlCEP: str
    nombreCep: str
    empresa: str
    fechaOperacion: str
    sello: str
    claveRastreo: str
    cuentaBeneficiario: str

class CreateOrderRequest(BaseModel):
    nombreBeneficiario: str
    cuentaBeneficiario: str
    rfcCurpBeneficiario: str
    referenciaNumerica: str
    id_sucursal: int
    id_bloque: int
    institucionContraparte: Optional[str] = config.STP_INSTITUCION_CONTRAPARTE

class CreateOrderResponse(BaseModel):
    clave_rastreo: str = ""
    id_orden_stp: int = 0



class WebhookResponse(BaseModel):
    mensaje: str

@app.post("/registrar-pago")
async def registrar_pago(order: PaymentOrder):
    """
    Endpoint para registrar una orden de pago en STP.
    Recibe el JSON con los datos y la firma pre-calculada.
    """
    payload = order.model_dump()
    result = client.registrar_orden_pago(payload)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@app.post("/webhook", response_model=WebhookResponse)
async def webhook(request: WebhookRequest):
    """
    Endpoint de Webhook para recibir notificaciones de liquidación de STP.
    """
    print(f"Notificación de Liquidación recibida: ID {request.id}, Rastreo: {request.claveRastreo}, Estado: {request.estado}")
    
    print("\n--- Webhook Request JSON para Postman ---")
    print(request.model_dump_json(indent=None))
    print("------------------------------------------\n")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Parámetros para stp_actualizar_orden_webhook
        params = (
            request.claveRastreo,
            request.id,
            request.estado,
            request.causaDevolucion,
            request.tsLiquidacion
        )
        
        query = "{CALL stp_actualizar_orden_webhook (?, ?, ?, ?, ?)}"
        print(f"Ejecutando actualización Webhook: EXEC stp_actualizar_orden_webhook '{request.claveRastreo}', {request.id}, '{request.estado}'")
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        print("Base de datos actualizada correctamente vía Webhook.")
        
    except Exception as e:
        print(f"Error al actualizar la base de datos en el webhook: {e}")
        # Opcionalmente podrías lanzar una excepción si quieres que STP reintente el webhook
        # raise HTTPException(status_code=500, detail="Error interno al procesar webhook")
        
    return {"mensaje": "recibido"}

@app.post("/webhook-cep", response_model=WebhookResponse)
async def webhook_cep(request: CEPRequest):
    """
    Endpoint de Webhook para recibir notificaciones de CEP (Comprobante Electrónico de Pago).
    """
    print(f"Notificación CEP recibida: Rastreo: {request.claveRastreo}, Beneficiario: {request.nombreCep}")

    print("\n--- Webhook CEP Request JSON para Postman ---")
    print(request.model_dump_json(indent=None))
    print("----------------------------------------------\n")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Parámetros para stp_actualizar_orden_webhook
        params = (
            request.rfcCep,
            request.urlCEP,
            request.nombreCep,
            request.empresa,
            request.fechaOperacion,
            request.sello,
            request.claveRastreo,
            request.cuentaBeneficiario
        )
        
        query = "{CALL stp_actualizar_orden_webhook_cep (?, ?, ?, ?, ?, ?, ?, ?)}"
        print(f"Ejecutando actualización Webhook: EXEC stp_actualizar_orden_webhook_cep '{request.rfcCep}', '{request.urlCEP}', '{request.nombreCep}', '{request.empresa}', '{request.fechaOperacion}', '{request.sello}', '{request.claveRastreo}', '{request.cuentaBeneficiario}'")
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        print("Base de datos actualizada correctamente vía Webhook.")
        
    except Exception as e:
        print(f"Error al actualizar la base de datos en el webhook: {e}")
        # Opcionalmente podrías lanzar una excepción si quieres que STP reintente el webhook
        # raise HTTPException(status_code=500, detail="Error interno al procesar webhook")
        
    return {"mensaje": "recibido"}

def get_db_connection():
    conn_str = (
        f"DRIVER={config.DB_DRIVER};"
        f"SERVER={config.DB_SERVER};"
        f"DATABASE={config.DB_DATABASE};"
        f"UID={config.DB_USER};"
        f"PWD={config.DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

@app.post("/crear-orden-stp", response_model=CreateOrderResponse)
async def crear_orden_stp(request_in: CreateOrderRequest):
    """
    Endpoint para crear una orden de pago ejecutando un Store Procedure en SQL Server.
    """
    try:
        conn = get_db_connection()
        print(f"Conexion: {conn}")
        cursor = conn.cursor()
        print(f"Cursor: {cursor}")
        
        # Inicializar PaymentOrder con datos fijos/config y los recibidos
        order_data = PaymentOrder()
        order_data.nombreBeneficiario = request_in.nombreBeneficiario
        order_data.cuentaBeneficiario = request_in.cuentaBeneficiario
        order_data.rfcCurpBeneficiario = request_in.rfcCurpBeneficiario
        order_data.id_sucursal = request_in.id_sucursal
        order_data.id_bloque = request_in.id_bloque
        order_data.referenciaNumerica = request_in.referenciaNumerica
        order_data.institucionContraparte = request_in.institucionContraparte

        print(f"order_data: {order_data}")
        # Parámetros para stp_crear_orden
        params = (
            order_data.nombreBeneficiario,
            order_data.cuentaBeneficiario,
            order_data.tipoCuentaBeneficiario,
            order_data.rfcCurpBeneficiario,
            order_data.institucionContraparte,
            order_data.nombreOrdenante,
            order_data.cuentaOrdenante,
            order_data.tipoCuentaOrdenante,
            order_data.rfcCurpOrdenante,
            order_data.institucionOperante,
            order_data.empresa,
            order_data.conceptoPago,
            order_data.monto,
            order_data.tipoPago,
            order_data.id_sucursal,
            order_data.id_bloque
        )
        
        # Ejecución del SP
        query = "SET NOCOUNT ON; {CALL stp_crear_orden (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}"
        sql_debug = f"EXEC stp_crear_orden {', '.join([f'{repr(p)}' for p in params])}"
        print(f"SQL Debug: {sql_debug}")
        cursor.execute(query, params)
        
        # Se asume que el SP retorna un resultado con la clave_rastreo
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="El SP no retornó resultados")
            
        order_data.claveRastreo = str(row[0])
        conn.commit()
        conn.close()
        
        # Generar cadena original
        fields = [
            order_data.institucionContraparte, order_data.empresa, order_data.fechaOperacion,
            order_data.folioOrigen, order_data.claveRastreo, order_data.institucionOperante,
            order_data.monto, order_data.tipoPago, order_data.tipoCuentaOrdenante,
            order_data.nombreOrdenante, order_data.cuentaOrdenante, order_data.rfcCurpOrdenante,
            order_data.tipoCuentaBeneficiario, order_data.nombreBeneficiario, order_data.cuentaBeneficiario,
            order_data.rfcCurpBeneficiario, order_data.emailBeneficiario, order_data.tipoCuentaBeneficiario2,
            order_data.nombreBeneficiario2, order_data.cuentaBeneficiario2, order_data.rfcCurpBeneficiario2,
            order_data.conceptoPago, order_data.conceptoPago2, order_data.claveCatUsuario1,
            order_data.claveCatUsuario2, order_data.clavePago, order_data.referenciaCobranza,
            order_data.referenciaNumerica, order_data.tipoOperacion, order_data.topologia,
            order_data.usuario, order_data.medioEntrega, order_data.prioridad, order_data.iva
        ]
        cadena_original = "||" + "|".join(str(f) if f is not None else "" for f in fields) + "||"
        print(f"Cadena Original STP: {cadena_original}")
        
        # Generar firma
        try:
            if os.path.exists(config.STP_CERT_PATH):
                with open(config.STP_CERT_PATH, "rb") as key_file:
                    private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=config.STP_CERT_PASSWORD.encode() if config.STP_CERT_PASSWORD else None
                    )
                
                signature = private_key.sign(
                    cadena_original.encode('utf-8'),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                order_data.firma = base64.b64encode(signature).decode('utf-8')
            else:
                print(f"Advertencia: No se encontró el certificado en {config.STP_CERT_PATH}")
        except Exception as sign_error:
            print(f"Error al generar la firma: {sign_error}")
        
        print(f"Firma STP Final: {order_data.firma}")
        
        # Consumir el servicio de registro de STP
        endpoint_registro = config.STP_WEBSERVICE_URL #"https://demo.stpmex.com:7024/speiws/rest/ordenPago/registra"
        
        # Filtrar campos vacíos o nulos
        payload_data = {k: v for k, v in order_data.model_dump().items() if v is not None and v != ""}
        payload_json = json.dumps(payload_data, indent=None)
        
        print("\n--- Request JSON para Postman ---")
        print(payload_json)
        print("---------------------------------\n")
        
        try:
            print(f"Consumiendo servicio en PUT: {endpoint_registro}")
            # Se usa verify=False por ser ambiente de demo/desarrollo
            response = requests.put(
                endpoint_registro,
                headers={"Content-Type": "application/json"},
                data=payload_json,
                verify=False
            )
            print(f"Respuesta STP - Status Code: {response.status_code}")
            print(f"Respuesta STP - Body: {response.text}")
            
            response_json = response.json()
            if "resultado" in response_json and "id" in response_json["resultado"]:
                id_stp = response_json["resultado"]["id"]
                res = CreateOrderResponse()
                res.clave_rastreo = str(order_data.claveRastreo or "")
                res.id_orden_stp = id_stp

                # Actualizar la orden en la base de datos
                try:
                    conn_update = get_db_connection()
                    cursor_update = conn_update.cursor()
                    
                    query_update = "{CALL stp_actualizar_orden (?, ?)}"
                    params_update = (res.clave_rastreo, res.id_orden_stp)
                    
                    print(f"Ejecutando actualización: EXEC stp_actualizar_orden '{res.clave_rastreo}', {res.id_orden_stp}")
                    cursor_update.execute(query_update, params_update)
                    conn_update.commit()
                    conn_update.close()
                    print("Orden actualizada exitosamente en la base de datos.")
                except Exception as db_update_error:
                    print(f"Error al actualizar la orden en la BD: {db_update_error}")
                    # No lanzamos excepción aquí para no invalidar el retorno exitoso de STP, 
                    # pero lo registramos en consola. Dependiendo del requerimiento, se podría cambiar.

                return res
            else:
                raise HTTPException(status_code=500, detail="Respuesta inesperada de STP SERVICE")
            
        except Exception as api_error:
            print(f"Error al consumir el servicio STP: {api_error}")
            raise HTTPException(status_code=500, detail=f"Error al consumir el servicio STP: {str(api_error)}")
        
        #eturn {"clave_rastreo": request.claveRastreo}
        
    except Exception as e:
        print(f"Error en crear_orden_stp: {e}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
