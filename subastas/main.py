try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from selenium.webdriver.common.keys import Keys
    from dotenv import load_dotenv
    from bs4 import BeautifulSoup
    import pandas as pd
    import re
    import time
    # import subastas.send_mail as send_email
    # from subastas import data_base
    from datetime import datetime,timedelta
    import os
except Exception as e:
    print("Ocurrió un error al importar las librerías en subastas main", e)

# Cargar variables de entorno desde el archivo .env
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
            driver.get("https://fp042301.freshportal.nl/login_v2/index/index/")

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
                # data_base.log_to_db(2, "ERROR", f"Ocurrio un error al iniciar sesión, {e}", endpoint='fallido', status_code=500)
                # send_email.send_error_email(f"Ocurrio un error al inciar sesión, {e}")
                raise
        finally:
            if retries == max_retries:
                driver.quit()

def wait_table():
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.ajax_table_table tbody"))
        )
        print("Tabla cargada correctamente")
    except Exception as e:
        print("Error al cargar la tabla:", e)
        driver.quit()

def scroll_down():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

def go_to_next_page():
    try:
        # Comprobar si el botón "Next" está presente y es clicable
        next_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='page-link next_page waves-effect' and @aria-label='Next']"))
        )

        # Verificar si el botón "Next" está habilitado
        if next_button.get_attribute('aria-hidden') == 'true':
            print("El botón 'Next' está deshabilitado.")
            return False

        # Hacer clic en el botón "Next"
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        print("Pasando a la siguiente página...")
        time.sleep(1)  # Espera para que la página cargue el nuevo contenido
        return True
    except TimeoutException:
        print("No hay más páginas o no se encontró el botón de siguiente página.")
        return False
    except Exception as e:
        print(f"Error inesperado al intentar pasar a la siguiente página: {e}")
        return False

# Función principal de scraping
def scrape_table(url):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            driver.get(url)
            wait_table()

            rows = []
            headers = []
            max_columns = 0

            page_number = 1
            while True:
                print(f"Scrapeando la página {page_number}...")
                time.sleep(5)

                # Scroll hacia abajo para cargar contenido adicional
                scroll_down()

                # Extracción de datos
                page_content = driver.page_source
                soup = BeautifulSoup(page_content, 'html.parser')

                # Verificar el contenido HTML obtenido para el tbody
                tbody_content = soup.select_one("table.ajax_table_table tbody")
                
                if tbody_content:
                    print("Contenido de tbody encontrado.")
                else:
                    print("No se encontró tbody en la página.")
                    break

                # Extraer datos de la tabla
                table_rows = tbody_content.find_all("tr") if tbody_content else []

                if not table_rows:
                    print("No se encontraron filas en la tabla.")
                    break

                for i, row in enumerate(table_rows):
                    cells = row.find_all(['td', 'th'])
                    cell_values = [cell.get_text(strip=True).replace("€", "").replace("%", "").replace(",", ".") for cell in cells]

                    if i == 0 and not headers:
                        # Almacenar encabezados y omitir la primera y la columna 15
                        headers = [cell_values[j] for j in range(len(cell_values)) if j != 0 and j != 15]
                        max_columns = len(headers)
                    else:
                        # Omitir la primera columna y la columna 14 en cada fila
                        row_data = [cell_values[j] for j in range(len(cell_values)) if j != 0 and j != 15]
                        if any(row_data):  # Solo agregar filas no vacías
                            rows.append(row_data)

                if not go_to_next_page():
                    break

                page_number += 1

            # Completar filas y columnas para un DataFrame bien formateado
            headers += [None] * (max_columns - len(headers))
            rows = [row + [None] * (max_columns - len(row)) for row in rows]
            df = pd.DataFrame(rows, columns=headers)

            # Detectar y limpiar columnas numéricas
            num_columns = [col for col in df.columns if col is not None and any(
                keyword in col.lower() for keyword in ["weight", "total", "purchase", "sale", "price", "cost", "margin"]
            )]

            for col in num_columns:
                df[col] = df[col].apply(clean_value)

            # Guardar en CSV
            # csv_filename = "subastas.csv"
            # df.to_csv(csv_filename, index=False)
            # print(f"Datos guardados como '{csv_filename}'")

            csv_filename = f"subastas.csv"
            # Verificar si el archivo ya existe
            file_exists = os.path.isfile(csv_filename)
            # Guardar en modo 'append' para no sobreescribir
            df.to_csv(csv_filename, mode='a', index=False, header=not file_exists)
            print(f"Data {i+1} guardada como '{csv_filename}'")

            # return df

            break 
            


        except Exception as e:
            retries += 1
            time.sleep(1)
            print("Ocurrio un error al obtener los datos de la tabla, ", e)
            if retries == max_retries:
                raise
            # data_base.log_to_db(2, "ERROR", f"Ocurrio un error al realizar el webscraping de subastas, {e}", endpoint='fallido', status_code=500)
            # send_email.send_error_email(f"Ocurrio un error al realizar el webscraping de subastas, {e}")
            break
        finally:
            if retries == max_retries:
                driver.quit()


def clean_value(value):
    try:
        value = re.sub(r'[^\d.]', '', value.replace(' ', '').replace(',', '.'))
        if value.count('.') > 1:
            parts = value.split('.')
            value = ''.join(parts[:-1]) + '.' + parts[-1]
        return float(value)
    except ValueError:
        return 0.0
    
# def generate_monthly_urls(start_date, end_date):
#     """
#     Genera un rango de URLs mes por mes entre las fechas dadas.
#     """
#     urls = []
#     current_date = start_date

#     while current_date < end_date:
#         # Definir la primera quincena (día 1 al 15)
#         if current_date.day <= 15:
#             biweekly_end_date = current_date.replace(day=15)
#         else:
#             # Definir la segunda quincena (día 16 al fin del mes)
#             next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
#             biweekly_end_date = next_month - timedelta(days=1)

#         # Limitar la fecha final al rango máximo permitido
#         if biweekly_end_date > end_date:
#             biweekly_end_date = end_date

#         # Asegurar que las fechas tengan el formato correcto
#         formatted_start = current_date.strftime('%Y-%m-%d')
#         formatted_end = biweekly_end_date.strftime('%Y-%m-%d')
        
#         # Crear la URL con los parámetros de rango de fechas
#         url = f"https://fp042301.freshportal.nl/floriday_io_yield/index/index/?1=1&page=1&auction_date_from={formatted_start}&auction_date_to={formatted_end}#!"
#         urls.append(url)

#         # Avanzar al día 16 o al primer día del próximo mes según la quincena
#         if current_date.day <= 15:
#             current_date = current_date.replace(day=16)
#         else:
#             current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)

#     return urls

# def scrape_monthly_data():
#     """
#     Realiza el scraping de datos para todas las fechas especificadas.
#     """
#     start_date = datetime.strptime("2024-11-16", '%Y-%m-%d')  # Cambia la fecha según necesites
#     end_date = datetime.today()

#     # Generar las URLs mensuales
#     monthly_urls = generate_monthly_urls(start_date, end_date)

#     # Iniciar sesión una vez
#     login()

#     # Archivo CSV único
#     csv_filename = "subastas.csv"
#     combined_df = pd.DataFrame()  # Para combinar todos los datos

#     for url in monthly_urls:
#         print(f"Scraping datos de URL: {url}")
#         try:
#             # Extraer datos de la tabla
#             temp_df = scrape_table(url)

#             # Combinar los datos en un DataFrame único
#             combined_df = pd.concat([combined_df, temp_df], ignore_index=True)

#         except Exception as e:
#             print(f"Error al procesar la URL: {e}")

#     # Guardar los datos combinados en un CSV
#     combined_df.to_csv(csv_filename, index=False)
#     print(f"Todos los datos se guardaron en '{csv_filename}'.")

# # Llamar a la función principal
# scrape_monthly_data()