from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from stp_client import STPClient
import uvicorn
import config
import pyodbc

app = FastAPI(title="STP Payment Service")
client = STPClient()

class PaymentOrder(BaseModel):
    claveRastreo: str
    monto: str
    nombreBeneficiario: str
    cuentaBeneficiario: str
    firma: str
    # Campos opcionales con valores por defecto del config.py
    conceptoPago: Optional[str] = "Pago SPEI"
    cuentaOrdenante: Optional[str] = config.STP_CUENTA_ORDENANTE
    nombreOrdenante: Optional[str] = config.STP_NOMBRE_ORDENANTE
    cuentaParticipanteIndirecto: Optional[str] = config.STP_CUENTA_PARTICIPANTE_INDIRECTO
    empresa: Optional[str] = config.STP_EMPRESA
    institucionContraparte: Optional[str] = config.STP_INSTITUCION_CONTRAPARTE
    institucionOperante: Optional[str] = config.STP_INSTITUCION_OPERANTE
    referenciaNumerica: Optional[str] = "123456"
    rfcCurpBeneficiario: Optional[str] = "ND"
    rfcCurpOrdenante: Optional[str] = config.STP_RFC_CURP_ORDENANTE
    tipoCuentaBeneficiario: Optional[str] = config.STP_TIPO_CUENTA_BENEFICIARIO
    tipoCuentaOrdenante: Optional[str] = config.STP_TIPO_CUENTA_ORDENANTE
    tipoPago: Optional[str] = config.STP_TIPO_PAGO
    latitud: Optional[str] = "0.0"
    longitud: Optional[str] = "0.0"

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
    nombre_beneficiario: str
    cuenta_beneficiario: str
    rfc_curp_beneficiario: str
    id_sucursal: int
    id_bloque: int

class CreateOrderResponse(BaseModel):
    clave_rastreo: str

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
    return {"mensaje": "recibido"}

@app.post("/webhook-cep", response_model=WebhookResponse)
async def webhook_cep(request: CEPRequest):
    """
    Endpoint de Webhook para recibir notificaciones de CEP (Comprobante Electrónico de Pago).
    """
    print(f"Notificación CEP recibida: Rastreo: {request.claveRastreo}, Beneficiario: {request.nombreCep}")
    return {"mensaje": "recibido"}

def get_db_connection():
    conn_str = (
        f"DRIVER={config.DB_DRIVER};"
        f"SERVER={config.DB_SERVER};"
        f"DATABASE={config.DB_DATABASE};"
        f"UID={config.DB_USER};"
        f"PWD={config.DB_PASSWORD}"
    )
    return pyodbc.connect(conn_str)

@app.post("/crear-orden-stp", response_model=CreateOrderResponse)
async def crear_orden_stp(request: CreateOrderRequest):
    """
    Endpoint para crear una orden de pago ejecutando un Store Procedure en SQL Server.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Parámetros para stp_crear_orden
        params = (
            request.nombre_beneficiario,
            request.cuenta_beneficiario,
            config.STP_TIPO_CUENTA_BENEFICIARIO,
            request.rfc_curp_beneficiario,
            config.STP_INSTITUCION_CONTRAPARTE,
            config.STP_NOMBRE_ORDENANTE,
            config.STP_CUENTA_ORDENANTE,
            config.STP_TIPO_CUENTA_ORDENANTE,
            config.STP_RFC_CURP_ORDENANTE,
            config.STP_INSTITUCION_OPERANTE,
            config.STP_EMPRESA,
            config.STP_CONCEPTO_PAGO,
            config.STP_MONTO,
            config.STP_TIPO_PAGO,
            1,
            1
        )
        
        # Ejecución del SP
        query = "{CALL stp_crear_orden (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}"
        cursor.execute(query, params)
        
        # Se asume que el SP retorna un resultado con la clave_rastreo
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="El SP no retornó resultados")
            
        clave_rastreo = str(row[0])
        conn.commit()
        conn.close()
        
        return {"clave_rastreo": clave_rastreo}
        
    except Exception as e:
        print(f"Error en crear_orden_stp: {e}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
