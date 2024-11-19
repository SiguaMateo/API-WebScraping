try:
    from datetime import datetime
    import csv
    # import subastas.send_mail as send_email
    import data_base
    from datetime import timedelta
    print("Librerias importadas")
except Exception as e:
    print("Ocurrio un error al importar las librerias en subastas manage, ", e)

# Leer y procesar el archivo CSV
def save():
    # Validacion de registros anteriores
    # delete_old_records()      
    try:
        with open("subastas.csv", mode="r", encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Salta los encabezados
            print("Ingresa al bloque de inserción de datos desde el csv")
            
            for row in reader:
                print("Ingreso al bucle")
                print("Longitud de la fila:", len(row))

                # Verificar que la fila tenga el número esperado de columnas
                if len(row) < 12:
                    print("Fila incompleta, se omite:", row)
                    continue  # Si la fila no tiene suficientes columnas, se omite

                # Convertir el valor de fecha a un formato que SQL Server pueda reconocer
                try:
                    fecha_str = row[3]  # columna de la fecha
                    if isinstance(fecha_str, str) and fecha_str.count('-') == 2:
                        try:
                            # Convertir la fecha al formato correcto (YYYY-MM-DD)
                            fecha_obj = datetime.strptime(fecha_str, '%d-%m-%Y').date()
                            row[3] = fecha_obj  # Reemplaza el valor en la fila en lugar de agregar uno nuevo
                        except ValueError:
                            print(f"Fecha no válida en la fila: {row}")
                            continue  # Si la fecha no se puede convertir, omitir la fila
                    else:
                        print(f"Fecha no válida en la fila: {row}")
                        continue  # Si el formato de la fecha no es válido, omitir la fila                  

                    print("Insertando", row)

                    # # Verificar que todos los datos sean válidos (puedes agregar más validaciones según sea necesario)
                    # if any(cell == "" or cell is None for cell in row):
                    #     print("Fila con datos vacíos, se omite:", row)
                    #     continue  # Si hay celdas vacías, se omite la fila

                    # Asegúrate de que estás insertando la cantidad correcta de columnas
                    data_base.cursor.execute(data_base.insert_query, row)  # Limita la fila a 16 elementos
                    print("Datos insertados exitosamente.")

                except Exception as e:
                    print("Error al procesar la fecha o al insertar fila:", e, "Fila:", row)

                data_base.conn.commit()
            print("Datos insertados desde el CSV exitosamente.")
    except Exception as e:
        print("Ocurrió un error al procesar el archivo CSV:", e)
        data_base.log_to_db(2, "ERROR", f"Ocurrio un error al guardar la informacion en la base de datos,{e} ", endpoint='fallido', status_code=500)
        # send_email(f"Ocurrio un error al guardar la informacion en la base de datos,{e} ")

save()

def delete_old_records():
    try:
        # Obtener la fecha límite (hoy - 15 días)
        fecha_limite = (datetime.now() - timedelta(days=15)).date()

        # Eliminación para la tabla de ventas
        ventas_query = """
        DELETE FROM rptFresh_Portal_Subastas_Dev
        WHERE auction_date >= ?
        """
        # Aquí solo necesitas pasar un parámetro en lugar de dos
        data_base.cursor.execute(ventas_query, (fecha_limite,))
        print(f"Registros eliminados en Ventas hasta la fecha: {fecha_limite}")

        # Confirmar cambios
        data_base.conn.commit()
        print("Eliminación completada exitosamente.")
    except Exception as e:
        data_base.log_to_db(2, "ERROR", f"Ocurrio un error al eliminar los registros de 45 días, {e}", endpoint='fallido', status_code=500)
        # send_email.send_error_email(f"Ocurrio un error al eliminar los registros de 45 días, {e}")
        print(f"Ocurrió un error durante la eliminación de registros: {e}")
