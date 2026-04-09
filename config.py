# Configuraciones del servicio STP

# URL del WebService
STP_WEBSERVICE_URL = "https://demo.stpmex.com:7024/speiws/rest/ordenPago/registra"

# Datos fijos de la Empresa y Ordenante
STP_EMPRESA = "EMPRESAPRUEBA"
STP_INSTITUCION_OPERANTE = "90646"  # Generalmente igual a cuenta ordenante prefijo
STP_INSTITUCION_CONTRAPARTE = "90646"

# Cuenta y datos del Ordenante por defecto
STP_CUENTA_ORDENANTE = "646180123412345678"
STP_NOMBRE_ORDENANTE = "Nombre Ordenante"
STP_RFC_CURP_ORDENANTE = "ND"
STP_TIPO_CUENTA_ORDENANTE = "40"

# Otros valores por defecto
STP_TIPO_CUENTA_BENEFICIARIO = "40"
STP_TIPO_PAGO = "1"
STP_CUENTA_PARTICIPANTE_INDIRECTO = "646180123412345678"

# Parámetros adicionales para el SP
STP_CONCEPTO_PAGO = "VALIDACION PAGO"
STP_MONTO = "0.0" # Valor por defecto

# Configuración de Base de Datos
DB_SERVER = "appserver.europiel.com.mx"
DB_DATABASE = "rm_europiel_requerimientos"
DB_USER = "rm_europiel_master"
DB_PASSWORD = "Pa88word1"
DB_DRIVER = "{ODBC Driver 17 for SQL Server}" # Driver estándar para SQL Server en Windows
