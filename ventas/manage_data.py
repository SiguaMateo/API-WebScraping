try:
    import csv
    from ventas import data_base
    from datetime import datetime, timedelta
    import ventas.send_mail as send_email
except Exception as e:
    print("Ocurrio un error al importar las librerias, ", e)

def save():
    # Validacion de registros anteriores
    delete_old_records()
                    
    # Leer y procesar el archivo CSV
    try:
        with open("ventas.csv", mode="r", encoding='utf-8') as file:
            reader = csv.reader(file)
            #next(reader)  # Salta los encabezados
            print("Ingresa al bloque de inserción de datos desde el csv")
            
            numeric_columns = [0, 10, 14, 15 , 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]  # Ajusta según tu CSV

            for row in reader:
                print("Ingreso al bucle")
                print("Longitud de la fila:", len(row))

                # Omitir la última fila si es vacía o no contiene datos válidos
                if row[11] == '' or row[11] is None:
                    print(f"Omitiendo la fila sin fecha: {row}")
                    continue  # Omite la fila si no contiene fecha válida

                # Limpia y convierte columnas numéricas
                try:
                    for col in numeric_columns:
                        if isinstance(row[col], str):
                            row[col] = row[col].replace(',', '.')  # Reemplaza comas por puntos
                        row[col] = float(row[col])  # Convierte a número
                except ValueError as ve:
                    print(f"Error al convertir a numérico en la columna {col}: {row[col]} - {ve}")
                    continue

                 # Limpia y convierte la columna 'Weight'
                try:
                    row[9] = int(row[9].replace('.0', ''))
                except ValueError:
                    print(f"Valor no válido en la columna Weight: {row[9]}")
                    continue  # Omite filas con datos inválidos en la columna "Weight"

                # Convertir el valor de fecha a un formato que SQL Server pueda reconocer
                try:
                    fecha_str = row[1]  # Asegúrate de que este índice es el correcto
                    # Verificar si la fecha tiene el formato 'YYYY-MM-DD'
                    if isinstance(fecha_str, str) and fecha_str.count('-') == 2:
                        try:
                            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                            row[11] = fecha_obj  # Reemplaza el valor en la fila con la fecha convertida
                        except ValueError:
                            print(f"Fecha no válida en la fila: {row}")
                            continue  # Si la fecha no se puede convertir, omitir la fila
                    else:
                        print(f"Fecha no válida en la fila: {row}")
                        continue  # Si el formato de la fecha no es válido, omitir la fila

                    print("Insertando", row)

                    # if validar_duplicados_ventas(row):
                    #     print("Registro duplicado en ventas, no se inserta:", row)
                    #     return
                    
                    # Insertar los datos en la base de datos
                    
                    data_base.cursor.execute(data_base.insert_query, row)
                    print("Datos insertados exitosamente.")

                except Exception as e:
                    print("Error al procesar la fecha o al insertar fila:", e, "Fila:", row)

                data_base.conn.commit()
            print("Datos insertados desde el CSV exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo CSV: {e}")
        data_base.log_to_db(1, "ERROR", f"Ocurrio un error al guardar la informacion en la base de datos, {e}", endpoint='fallido', status_code=500)
        send_email(f"Ocurrió un error al guardar la informacion en la base de datos: {e}")

def delete_old_records():
    try:
        # Obtener la fecha límite (hoy - 44 días)
        fecha_limite = (datetime.now() - timedelta(days=15)).date()

        # Eliminación para la tabla de ventas
        ventas_query = """
        DELETE FROM rptFresh_Portal_Ventas_Dev
        WHERE inv_date >= ?
        """
        # Aquí solo necesitas pasar un parámetro en lugar de dos
        data_base.cursor.execute(ventas_query, (fecha_limite,))
        print(f"Registros eliminados en Ventas hasta la fecha: {fecha_limite}")

        # Confirmar cambios
        data_base.conn.commit()
        print("Eliminación completada exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error durante la eliminación de registros: {e}")
        data_base.log_to_db(1, "ERROR", f"Ocurrio un error al eliminar los registros de 45 días, {e}", endpoint='fallido', status_code=500)
        send_email.send_error_email(f"Ocurrio un error al eliminar los registros de 45 días, {e}")
        print(f"Ocurrió un error durante la eliminación de registros: {e}")