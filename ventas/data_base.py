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
#                 inv_week INT,
#                 inv_date DATE,
#                 cust_group NVARCHAR(75),
#                 inv_number NVARCHAR(75),
#                 customer NVARCHAR(50),
#                 country_of_client NVARCHAR(50),
#                 product NVARCHAR(50),
#                 colour NVARCHAR(50),
#                 apli_description NVARCHAR(50),
#                 weight_rgt INT, 
#                 content INT,
#                 cust_code NVARCHAR(20),
#                 product_group NVARCHAR(50),
#                 cbs_group NVARCHAR(50),
#                 year_invoice_date INT,
#                 month_billing_date INT,
#                 day_invoice_date INT,
#                 hour_invoice_date INT,
#                 total_pieces NUMERIC(10, 2),
#                 total_packages NUMERIC(10, 2),
#                 purchase NUMERIC(10, 2),
#                 sale NUMERIC(10, 2), 
#                 unit_price NUMERIC(10, 2), 
#                 average_purchase_price NUMERIC(10, 2), 
#                 comissions NUMERIC(10, 2), 
#                 cost NUMERIC(10, 2), 
#                 margin NUMERIC(10, 2),
#                 percentage NUMERIC(10, 2)
#             )
#         """)
#         conn.commit()
#         print("Tabla creada exitosamente.")

# create_table_Data()

def log_to_db(id_group, log_level, message, endpoint=None, status_code=None):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Logs_Info (id_group, log_level, message, endpoint, status_code)
            VALUES (?, ?, ?, ?, ?)
        """, id_group, log_level, message, endpoint, status_code)
        conn.commit()

def getUser():
    try:
        result = conn.execute(user_WSCVETS).fetchone()
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
        result = conn.execute(password_WSCVETS).fetchone()
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
    INSERT INTO rptFresh_Portal_Ventas_Dev VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""