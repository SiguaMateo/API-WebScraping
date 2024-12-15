try:
    import pyodbc
    import os
    from dotenv import load_dotenv
    import ventas.send_mail as send_mail
    print("Librerias importadas")
except Exception as e:
    print("Ocurrio un error al importar las librerias, ventas")

load_dotenv()

# Configuración de datos para la conexión con la base de datos SQL Server
try:
    conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={os.getenv("DATABASE_SERVER")};'
        f'DATABASE={os.getenv("DATABASE_NAME")};'
        f'UID={os.getenv("DATABASE_USER")};'
        f'PWD={os.getenv("DATABASE_PASSWORD")}'
    )
    cursor = conn.cursor()
except Exception as e:
    print("Ocurrio un error al instanciar los datos o conectarme con la base de datos en ventas: ", e)
    send_mail(f"Ocurrio un error en la conexión con la base de datos en ventas, {e}")

# def create_table_Data():
#     with conn.cursor() as cursor:
#         # Verificar si la tabla existe y eliminarla si es así
#         cursor.execute("""
#             IF EXISTS (SELECT * FROM sysobjects WHERE name='rptFresh_Portal_Ventas_Dev' AND xtype='U')
#             BEGIN
#                 DROP TABLE rptFresh_Portal_Ventas_Dev
#             END
#         """)
#         conn.commit()

#        # Crear una nueva tabla con los tipos de datos ajustados
#         cursor.execute("""
#             CREATE TABLE rptFresh_Portal_Ventas_Dev (
#                 id INT PRIMARY KEY IDENTITY(1,1),
#                 vent_invoice_week INT,
#                 vent_invoice_date DATE,
#                 vent_customer_group NVARCHAR(75),
#                 vent_invoice_number NVARCHAR(75),
#                 vent_customer NVARCHAR(50),
#                 vent_country_of_client NVARCHAR(50),
#                 vent_product NVARCHAR(50),
#                 vent_colour NVARCHAR(50),
#                 vent_description_allocation NVARCHAR(100),
#                 vent_weight INT, 
#                 vent_content INT,
#                 vent_customer_code NVARCHAR(20),
#                 vent_product_group NVARCHAR(50),
#                 vent_cbs_group NVARCHAR(50),
#                 vent_year_invoice_date INT,
#                 vent_month_billing_date INT,
#                 vent_day_invoice_date INT,
#                 vent_hour_invoice_date INT,
#                 vent_packaging INT,
#                 vent_total_pieces NUMERIC(10),
#                 vent_total_packages NUMERIC(10),
#                 vent_purchase NUMERIC(10, 2),
#                 vent_sale NUMERIC(10, 2), 
#                 vent_unit_price NUMERIC(10, 2), 
#                 vent_average_purchase_price NUMERIC(10, 2), 
#                 vent_comissions NUMERIC(10, 2), 
#                 vent_cost NUMERIC(10, 2), 
#                 vent_margin NUMERIC(10, 2),
#                 vent_percentage NUMERIC(10, 2)
#             )
#         """)
#         conn.commit()
#         print("Tabla creada exitosamente.")

# create_table_Data()

def drop_table_Data():
    with conn.cursor() as cursor:
        # Verificar si la tabla existe y eliminarla si es así
        cursor.execute("""
            IF EXISTS (SELECT * FROM sysobjects WHERE name='rptFresh_Portal_Ventas_Test' AND xtype='U')
            BEGIN
                DROP TABLE rptFresh_Portal_Ventas_Test
            END
        """)
        conn.commit()

drop_table_Data()

def log_to_db(id_group, log_level, message, endpoint=None, status_code=None):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Logs_Info (id_group, log_level, message, endpoint, status_code)
            VALUES (?, ?, ?, ?, ?)
        """, id_group, log_level, message, endpoint, status_code)
        conn.commit()

def get_url_login():
    try:
        result = cursor.execute(url_login_query).fetchone()
        if result:
            url = result[0]
            return str(url)
        else:
            print("No se pudo obtener la url login")
            return None
    except Exception as e:
        print(f"Error al obtener la url login, {e}")

def getUser():
    try:
        result = cursor.execute(user_WSCVETS).fetchone()
        if result:
            user = result[0]
            return str(user)
        else:
            print("No se obtuvo ningún resultado para el usuario")
            return None
    except Exception as e:
        print(f'Ocurrio un error al obtener el usuario: {e}')
        return None

def getPass():
    try:
        result = cursor.execute(password_WSCVETS).fetchone()
        if result:
            password = result[0]
            return str(password)
        else:
            print("No se obtuvo ningún resultado para la contraseña")
            return None
    except Exception as e:
        print(f'Ocurrio un error al obtener la contraseña: {e}')
        return None
    
user_WSCVETS = """SELECT prm_valor 
                    FROM dbo.Parametros_Sistema
                    WHERE id_grupo = 1 AND prm_descripcion LIKE 'user_name'"""

password_WSCVETS = """SELECT prm_valor 
                        FROM dbo.Parametros_Sistema
                        WHERE id_grupo = 1 AND prm_descripcion LIKE 'password';"""

# sql Querys
insert_query = """
    INSERT INTO rptFresh_Portal_Ventas_Dev VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

url_login_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'url'"""