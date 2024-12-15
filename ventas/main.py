try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup
    from dotenv import load_dotenv
    import pandas as pd
    import re
    import os
    import time
    from datetime import timedelta, datetime
    import data_base
    # import ventas.send_mail as send_email
    print("Librerias Importadas")
except Exception as e:
    print("Error al importar las librerias en ventas, ", e)

load_dotenv()

def login():
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            global driver
            # Inicializar el navegador
            chrome_options = Options()
            chrome_options.binary_location = "/usr/bin/google-chrome"
            # chrome_options.add_argument("--headless") # visualizar el navegador
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(data_base.get_url_login())
            print(f"URL obtenida: {data_base.get_url_login()}")

            # Iniciar sesión
            username = driver.find_element(By.ID, 'username')
            username.send_keys(os.getenv("USER_FreshPortal"))
            password = driver.find_element(By.ID, 'password')
            password.send_keys(os.getenv("PASSWORD_FreshPortal"))

            message = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.fps-button'))).click()
            print(message)
            break
        
        except Exception as e:
            retries += 1
            print("Ocurrio un error al iniciar sesion, ", e)
            time.sleep(3)
            if retries == max_retries:
                # data_base.log_to_db(1, "ERROR", f"Ocurrio un error al iniciar sesion, {e}", endpoint='fallido', status_code=500)
                # send_email.send_error_email(f"Ocurrio un error al inciar sesion, {e}")
                raise
        finally:
            if retries == max_retries:
                driver.quit()

def clean_value(value):
    """
    Limpia y convierte un valor numérico con formato europeo a formato estándar.
    """
    try:
        # Eliminar separadores de miles y convertir a formato de punto decimal
        value = value.replace('.', '').replace(',', '.')
        return float(value)
    except Exception as e:
        print(f"Error al limpiar valor: '{value}', {e}")
        return None

def scrape_table(url):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            driver.get(url)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "management_total_table"))
            )

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            table = soup.find(id='management_total_table')

            if not table:
                print("No se encontró la tabla en la página.")
                raise ValueError("Tabla no encontrada.")

            rows = []
            max_columns = 0

            # Procesar las filas de la tabla
            for j, row in enumerate(table.find_all('tr')):
                cells = row.find_all(['td', 'th'])
                cell_values = [cell.get_text(strip=True).replace("€", "").replace("%", "") for cell in cells]

                if j == 0:  # Primera fila son los encabezados
                    headers = cell_values
                    max_columns = len(headers)
                else:
                    max_columns = max(max_columns, len(cell_values))
                    rows.append(cell_values)

            # Ajustar encabezados y filas al mismo tamaño
            headers += [None] * (max_columns - len(headers))
            rows = [row + [None] * (max_columns - len(row)) for row in rows]

            # Crear el DataFrame
            df = pd.DataFrame(rows, columns=headers)

            # Limpiar los valores numéricos en las columnas relevantes
            for col in df.columns:
                if col and any(keyword in col.lower() for keyword in ["weight", "total", "purchase", "sale", "price", "cost", "margin"]):
                    df[col] = df[col].apply(clean_value)

            # Guardar los datos en CSV
            csv_filename = "ventas.csv"
            file_exists = os.path.isfile(csv_filename)
            df.to_csv(csv_filename, mode='a', index=False, header=not file_exists)
            print(f"Datos guardados como '{csv_filename}'")

            return df

        except Exception as e:
            retries += 1
            time.sleep(1)
            print(f"Error al extraer datos: {e}")
            if retries == max_retries:
                raise
        finally:
            if retries == max_retries:
                driver.quit()

    
def generate_monthly_urls(start_date, end_date):
    """
    Genera un rango de URLs mes por mes entre las fechas dadas.
    """
    urls = []
    current_date = start_date

    while current_date < end_date:
        # Definir la primera quincena (día 1 al 15)
        if current_date.day <= 15:
            biweekly_end_date = current_date.replace(day=15)
        else:
            # Definir la segunda quincena (día 16 al fin del mes)
            next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            biweekly_end_date = next_month - timedelta(days=1)

        # Limitar la fecha final al rango máximo permitido
        if biweekly_end_date > end_date:
            biweekly_end_date = end_date

        # Asegurar que las fechas tengan el formato correcto
        formatted_start = current_date.strftime('%Y-%m-%d')
        formatted_end = biweekly_end_date.strftime('%Y-%m-%d')
        
        # Crear la URL con los parámetros de rango de fechas
        url = f"https://fp042301.freshportal.nl/management/total/index/group/WEEK%28INV_PrintedDate%29%2CINV_PrintedDate%2CCUG_Name%2CCOALESCE%28INV_Number%3B+INV_CollectiveInvoiceNumber%29%2Cpref_cus.CUS_Name%2Ccustomer_country.COU_Name%2CPRD_Name%2CCLD_Name%2CCSI_Description%2Cactual_stock_entry.STE_Weight%2CCSI_QuantityPerPack%2Cpref_cus.CUS_Code%2CPGD_Name%2CCGD_Name%2CYEAR%28INV_PrintedDate%29%2CMONTH%28INV_PrintedDate%29%2CDAY%28INV_PrintedDate%29%2CHOUR%28INV_PrintedDate%29%2Ccustomer_stock_item_fust.FUS_Code%2C%2C/start_date/{formatted_start}/end_date/{formatted_end}/printed/0/chart_data/CSI_Quantity/limit/1000/extra_filters/%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C/"
        urls.append(url)

        # Avanzar al día 16 o al primer día del próximo mes según la quincena
        if current_date.day <= 15:
            current_date = current_date.replace(day=16)
        else:
            current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    return urls

def scrape_monthly_data():
    """
    Realiza el scraping de datos para todas las fechas especificadas.
    """
    start_date = datetime.strptime("2023-11-27", '%Y-%m-%d')  # Cambia la fecha según necesites
    end_date = datetime.today()

    # Generar las URLs mensuales
    monthly_urls = generate_monthly_urls(start_date, end_date)

    # Iniciar sesión una vez
    login()

    for url in monthly_urls:
        print(f"Scraping datos de URL: {url}")
        try:
            # Extraer datos de la tabla
            temp_df = scrape_table(url)

            # Combinar los datos en un DataFrame único
            combined_df = pd.concat([combined_df, temp_df], ignore_index=True)

        except Exception as e:
            print(f"Error al procesar la URL: {e}")

# Llamar a la función principal
scrape_monthly_data()