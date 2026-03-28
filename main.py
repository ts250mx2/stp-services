from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from stp_client import STPClient
import uvicorn
import config

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
    Responde con la estructura obligatoria {"mensaje": "recibido"}.
    """
    print(f"Notificación de Webhook recibida: ID {request.id}, Rastreo: {request.claveRastreo}, Estado: {request.estado}")
    return {"mensaje": "recibido"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
