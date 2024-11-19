try:
    import pyodbc
    import os
    from dotenv import load_dotenv
    import subastas.send_mail as send_email
    print("Librerias importadas")
except Exception as e:
    print("Ocurrio un error al importar las librerias")

# Cargar variables de entorno desde el archivo .env
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
    print("Conexion realizada con exito")
except Exception as e:
    print("Ocurrio un error al instanciar los datos o conectarme con la base de datos en subastas: ", e)
    send_email(f"Ocurrio un error en la conexión con la base de datos en subastas, {e}")

# def create_table_Data():
#     with conn.cursor() as cursor:
#         # Verificar si la tabla existe y eliminarla si es así
#         cursor.execute("""
#             IF EXISTS (SELECT * FROM sysobjects WHERE name='rptFresh_Portal_Subastas_Dev' AND xtype='U')
#             BEGIN
#                 DROP TABLE rptFresh_Portal_Subastas_Dev
#             END
#         """)
#         conn.commit()

#         # Crear una nueva tabla con los tipos de datos ajustados
#         cursor.execute("""
#             CREATE TABLE rptFresh_Portal_Subastas_Dev (
#                 id INT PRIMARY KEY IDENTITY(1,1),
#                 sub_name NVARCHAR(50),
#                 sub_lot_number NVARCHAR(20),
#                 sub_auction_date DATE,
#                 sub_date DATE,
#                 sub_description NVARCHAR(75),
#                 sub_weight INT,
#                 sub_colour_treated NVARCHAR(20),
#                 sub_packaging_code INT,
#                 sub_quantity INT,
#                 sub_content INT,
#                 sub_total FLOAT,
#                 sub_price FLOAT,
#                 sub_total_price FLOAT,
#                 sub_average_lot_price FLOAT,
#                 sub_code NVARCHAR(20),
#                 sub_buyer NVARCHAR(50),
#                 sub_trading_instrument NVARCHAR(25),
#                 sub_sales_channel NVARCHAR(25)
#             )
#         """)
#         conn.commit()
#         print("Tabla creada exitosamente.")

# create_table_Data()

# def create_table_Logs():
#     with conn.cursor() as cursor:
#         # Verificar si la tabla existe y eliminarla si es así
#         cursor.execute("""
#             IF EXISTS (SELECT * FROM sysobjects WHERE name='Logs_Info' AND xtype='U')
#             BEGIN
#                 DROP TABLE Logs_Info
#             END
#         """)
#         conn.commit()

#         # Crear una nueva tabla
#         cursor.execute("""
#             CREATE TABLE Logs_Info (
#             id INT PRIMARY KEY IDENTITY(1,1),
#             id_group INT NOT NULL,
#             log_time DATETIME DEFAULT GETDATE(),
#             log_level VARCHAR(20),
#             message TEXT,
#             endpoint VARCHAR(255),
#             status_code INT
#             )
#         """)
#         conn.commit()

# create_table_Logs()

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
      INSERT INTO rptFresh_Portal_Subastas_Dev VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""