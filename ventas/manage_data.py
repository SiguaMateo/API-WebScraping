try:
    import csv
    from ventas import data_base
    from datetime import datetime
    # import ventas.send_mail as send_email
except Exception as e:
    print("Ocurrio un error al importar las librerias, ", e)

try:
    import csv
    import data_base
    from datetime import datetime, timedelta
except Exception as e:
    print("Ocurrio un error al importar las librerias, ", e)


def delete_old_records():
    try:
        # Obtener la fecha límite (hoy - 15 días)
        fecha_limite = '2024-11-01'

        # Eliminación para la tabla de ventas
        ventas_query = """
        DELETE FROM rptFresh_Portal_Ventas_Dev
        WHERE vent_invoice_date > ?
        """
        # Aquí solo necesitas pasar un parámetro en lugar de dos
        data_base.cursor.execute(ventas_query, (fecha_limite,))
        print(f"Registros eliminados en Ventas hasta la fecha: {fecha_limite}")

        # Confirmar cambios
        data_base.conn.commit()
        print("Eliminación completada exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error durante la eliminación de registros: {e}")
        # data_base.log_to_db(1, "ERROR", f"Ocurrio un error al eliminar los registros de 15 días, {e}", endpoint='fallido', status_code=500)
        # send_email.send_error_email(f"Ocurrio un error al eliminar los registros de 15 días, {e}")
        print(f"Ocurrió un error durante la eliminación de registros: {e}")


def save():
    #delete_old_records()
    try:
        with open("ventas.csv", mode="r", encoding='utf-8') as file:
            reader = csv.reader(file)
            print("Ingresa al bloque de inserción de datos desde el csv")
            
            numeric_columns = [0, 10, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
            negative_allowed_columns = [22, 23, 24, 25, 26, 27, 28]  # Columnas que pueden tener valores negativos

            for row in reader:
                # Limpia y convierte columnas numéricas
                for col in numeric_columns:
                    try:
                        if col == 18:  # Validación específica para la columna 'packaging'
                            if row[col] == 'No packaging':
                                row[col] = 0  # Asigna 0 si dice 'No packaging'
                            else:
                                row[col] = row[col].replace(',', '.')  # Reemplaza comas por puntos
                                row[col] = float(row[col])  # Convierte a número
                        else:
                            if isinstance(row[col], str):
                                row[col] = row[col].replace(',', '.')  # Reemplaza comas por puntos
                            # Verifica si la columna permite valores negativos
                            if col in negative_allowed_columns:
                                row[col] = float(row[col])  # Permite valores negativos
                                
                    except ValueError:
                        print(f"Error al convertir columna {col} a numérico: '{row[col]}' - Se asignará 0")
                        row[col] = 0  # Asigna 0 en caso de error

                # Limpia y convierte la columna 'Weight'
                try:
                    if isinstance(row[9], str):
                        row[9] = row[9].replace('.0', '')  # Remueve '.0' si es necesario
                    row[9] = int(row[9])  # Convierte a entero
                except ValueError:
                    print(f"Valor no válido en la columna Weight: '{row[9]}' - Se asignará 0")
                    row[9] = 0  # Asigna 0 en caso de error

                # Convertir el valor de fecha a un formato que SQL Server pueda reconocer
                try:
                    fecha_str = row[1]  # Índice de la columna de fecha
                    if isinstance(fecha_str, str) and fecha_str.count('-') == 2:
                        try:
                            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                            row[1] = fecha_obj  # Reemplaza el valor en la fila con la fecha convertida
                        except ValueError:
                            print(f"Error al convertir la fecha: '{fecha_str}' - Se ignorará esta fila")
                            continue  # Ignora la fila si la fecha es inválida
                    else:
                        print(f"Formato de fecha no válido: '{fecha_str}' - Se ignorará esta fila")
                        continue  # Ignora la fila si el formato de la fecha es incorrecto

                    # Insertar los datos en la base de datos
                    try:
                        data_base.cursor.execute(data_base.insert_query, row)
                    except Exception as db_error:
                        print(f"Error al insertar datos en la base de datos: {db_error}")
                        continue  # Salta esta fila

                except Exception as e:
                    print(f"Error general al procesar la fila: {row} - {e}")
                    continue

                # Confirma los cambios si la fila se inserta correctamente
                data_base.conn.commit()
            print("Datos insertados desde el CSV exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo CSV: {e}")
        data_base.log_to_db(1, "ERROR", f"Ocurrio un error al guardar la informacion en la base de datos, {e}", endpoint='fallido', status_code=500)

save()