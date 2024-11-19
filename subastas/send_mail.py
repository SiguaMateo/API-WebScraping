try:
    from email.mime.text import MIMEText
    from dotenv import load_dotenv
    import smtplib
    import os
    from subastas import data_base
except Exception as e:
    print(f"Ocurrio un error al importar las librerias en subastas mail, {e}")

load_dotenv()

EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Función para enviar correos en caso de error
def send_error_email(error_message):
    try:
        server = smtplib.SMTP_SSL('mail.starflowers.com.ec', 465)
        server.login("pasante.sistemas@starflowers.com.ec", EMAIL_PASSWORD)
        
        # Crear el mensaje con el asunto y el cuerpo
        subject = "API WebScraping"
        body = f"Mensaje: {error_message}"
        
        # Crear el objeto MIMEText para el correo
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = "pasante.sistemas@starflowers.com.ec"
        msg['To'] = "sistemas@starflowers.com.ec"
        
        # Enviar el correo
        #server.sendmail("pasante.sistemas@starflowers.com.ec", "sistemas@starflowers.com.ec", msg.as_string())
        
        data_base.log_to_db(2, "INFO", "correo enviado", endpoint='exitoso', status_code=200)
        server.quit()
    except Exception as e:
        data_base.log_to_db(2, "ERROR", f"Ocurrio un error al enviar el correo, {e}", endpoint='fallido', status_code=500)