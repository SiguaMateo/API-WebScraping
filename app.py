try:
    from fastapi import FastAPI
    import subastas.main as main_file_subastas
    import ventas.main as main_file_ventas
    import ventas.manage_data as manage_data_ventas
    import subastas.manage_data as manage_data_subastas
    import validation
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    import uvicorn
except Exception as e:
    print(f"Ocurrio un error al importar las librerias, {e}")

app =  FastAPI(
    title="API para la obtención de datos a través de WebScraping de Starflowers Cia. Ltda.",
    description="Está API obtiene datos de páginas Web que almacenan datos de las ventas y subastas de la empresa Starflowers Cia. Ltda.",
    version="1.0.0"
)

@app.get("/", description="Endpoint raiz")
def default_endpoint():
    return {"message": "Inicio la API de WebScraping"}

@app.get("/get-sales", description="Endpoint para obtener las ventas")
def webscraping_sales_endpoint():
    try:
        start_date, end_date = validation.get_dates()
        url = f"https://fp042301.freshportal.nl/management/total/index/group/WEEK%28INV_PrintedDate%29%2CINV_PrintedDate%2CCUG_Name%2CCOALESCE%28INV_Number%3B+INV_CollectiveInvoiceNumber%29%2Cpref_cus.CUS_Name%2Ccustomer_country.COU_Name%2CPRD_Name%2CCLD_Name%2CCSI_Description%2Cactual_stock_entry.STE_Weight%2CCSI_QuantityPerPack%2Cpref_cus.CUS_Code%2CPGD_Name%2CCGD_Name%2CYEAR%28INV_PrintedDate%29%2CMONTH%28INV_PrintedDate%29%2CDAY%28INV_PrintedDate%29%2CHOUR%28INV_PrintedDate%29%2C%2C%2C/start_date/{start_date}/end_date/{end_date}/printed/0/chart_data/CSI_Quantity/limit/1000/extra_filters/%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C/"
        main_file_ventas.scrape_table(url)
        main_file_ventas.driver.quit()
        # manage_data_ventas.save()
        print(f"Ventas fecha: {start_date} - {end_date}")
        return {"message": "Scraping realizado con éxito de las ventas"}
    except Exception as e:
        print(f"Ocurrió un error al obtener los datos de las ventas: {e}")
        return {"Ocurrio un error al obtener los datos de las ventas ": str(e)}

@app.get("/get-auctions", description="Endpoint para obtener las subastas")
def webscraping_auctions_endpoint():
    try:
        start_date, end_date = validation.get_dates()
        url = f"https://fp042301.freshportal.nl/floriday_io_yield/index/index/?1=1&page=1&auction_date_from={start_date}&auction_date_to={end_date}#!"
        main_file_subastas.scrape_table(url)
        main_file_subastas.driver.quit()
        manage_data_subastas.save()
        print(f"Ventas fecha: {start_date} - {end_date}")
        return {"message": "Scraping realizado con éxito de las subastas"}
    except Exception as e:
        print(f"Ocurrio un error al obtener los datos de las subastas: {e}")
        return {f"Ocurrio un error al obtener los datos de las subastas: {str(e)}"}
    
# @app.get("/save-sales", description="Endpoint para almacenar las ventas en la base de datos")
# def save_sales_endpoint():
#     try:
#         manage_data_ventas.save()
#     except Exception as e:
#         print("Ocurrio un error con el endpoint que permite guardar las ventas")
    
# @app.get("/save-auctions", description="Endpoint para almacenar las subastas en la base de datos")
# def save_sales_endpoint():
#     try:
#         manage_data_subastas.save()
#     except Exception as e:
#         print("Ocurrio un error con el endpoint que permite guardar las subastas")

# Función para programar las tareas
def schedule_scraping_tasks():
    try:
        scheduler = BackgroundScheduler()

        # Programar el scraping de ventas todos los días a las 8 PM
        scheduler.add_job(
            webscraping_sales_endpoint,
            CronTrigger(hour=7, minute=00),
            id='scrape_sales',
            replace_existing=True
        )

        # Programar el scraping de subastas todos los días a las 8:05 PM
        scheduler.add_job(
            webscraping_auctions_endpoint,
            CronTrigger(hour=7, minute=00),
            id='scrape_auctions',
            replace_existing=True
        )

        # Iniciar el scheduler
        scheduler.start()
        print("Scheduler iniciado. Tareas programadas.")
    except Exception as e:
        print(f"Ocurrio un error en el evento programado")

# Inicializar el scheduler al iniciar la aplicación
@app.on_event("startup")
def startup_event():
    schedule_scraping_tasks()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)