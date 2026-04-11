# Configuraciones del servicio STP

# URL del WebService
STP_WEBSERVICE_URL = "https://demo.stpmex.com:7024/speiws/rest/ordenPago/registra"

# Datos fijos de la Empresa y Ordenante
STP_EMPRESA = "EUROPIEL"
STP_INSTITUCION_OPERANTE = "90646"  # Generalmente igual a cuenta ordenante prefijo
STP_INSTITUCION_CONTRAPARTE = "90646"

# Cuenta y datos del Ordenante por defecto
STP_CUENTA_ORDENANTE = "646180688500000002"
STP_NOMBRE_ORDENANTE = "S.A. de C.V."
STP_RFC_CURP_ORDENANTE = "ND"
STP_TIPO_CUENTA_ORDENANTE = "40"

# Otros valores por defecto
STP_TIPO_CUENTA_BENEFICIARIO = "40"
STP_TIPO_PAGO = "1"

# Parámetros adicionales para el SP
STP_CONCEPTO_PAGO = "Prueba REST"
STP_MONTO = "0.01" # Valor por defecto

# Configuración de Base de Datos
DB_SERVER = "appserver.europiel.com.mx"
DB_DATABASE = "rm_europiel_requerimientos"
DB_USER = "rm_europiel_master"
DB_PASSWORD = "Pa88word1"
DB_DRIVER = "{ODBC Driver 17 for SQL Server}" # Driver estándar para SQL Server en Windows

# Configuración de Certificado STP
STP_CERT_PATH = r"c:\Fuentes\europielprod.pem"
STP_CERT_PASSWORD = "Europiel2025*"
