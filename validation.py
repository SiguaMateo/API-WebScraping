try:
    from datetime import datetime, timedelta
except Exception as e:
    print(f"Ocurrio un error al importar las librerias para la validacion {e}")

# Función para obtener fechas automáticamente de los últimos 15 días
def get_dates():
    today = datetime.today()
    end_date = today.date()
    start_date = (today - timedelta(days=15)).date()
    return start_date, end_date