import os
import sys
from datetime import datetime
from pathlib import Path

from netmiko import ConnectHandler
from auditoria import extraer_hostname, obtener_interfaces_up, generar_reporte


def obtener_datos_dispositivo():
    requeridas = ["NET_DEVICE_HOST", "NET_DEVICE_USER", "NET_DEVICE_PASSWORD"]
    faltantes = [dato for dato in requeridas if not os.getenv(dato)]
    if faltantes:
        raise ValueError("Faltan variables de entorno: " + ", ".join(faltantes))
    return {
        "device_type": os.getenv("NET_DEVICE_TYPE", "cisco_xe"),
        "host": os.environ["NET_DEVICE_HOST"],
        "username": os.environ["NET_DEVICE_USER"],
        "password": os.environ["NET_DEVICE_PASSWORD"],
        "port": int(os.getenv("NET_DEVICE_PORT", "22")),
        "conn_timeout": 30,
        "auth_timeout": 30,
        "banner_timeout": 30,
    }


def consultar(conexion, comando, timeout):
    salida = conexion.send_command(comando, read_timeout=timeout)
    errores = ("invalid input", "authorization failed", "incomplete command",
               "ambiguous command", "permission denied", "access denied")
    if not salida.strip() or any(e in linea.lower() for linea in salida.splitlines()
                                 if linea.lstrip().startswith("%") for e in errores):
        raise RuntimeError(f"Consulta vacia o rechazada: {comando}")
    return salida


def main():
    dispositivo = obtener_datos_dispositivo()
    carpeta = Path(__file__).resolve().parent / "respaldos"
    carpeta.mkdir(mode=0o700, exist_ok=True)
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("Sistema de auditoria de redes - Irvin Misael Mejia Hernandez")
    print("Conectando al dispositivo de laboratorio...")
    with ConnectHandler(**dispositivo) as conexion:
        print("Conexion SSH establecida.")
        configuracion = consultar(conexion, "show running-config", 90)
        interfaces = consultar(conexion, "show ip interface brief", 60)
        version = consultar(conexion, "show version", 60)
    hostname = extraer_hostname(configuracion)
    if hostname == "NO_DEFINIDO":
        raise RuntimeError("No se pudo validar el hostname de la configuracion obtenida.")
    if not any("interface" in l.lower() and "protocol" in l.lower() for l in interfaces.splitlines()):
        raise RuntimeError("La salida de interfaces no tiene la cabecera esperada.")
    interfaces_activas = obtener_interfaces_up(interfaces)
    archivo_respaldo = carpeta / f"respaldo_{marca_tiempo}.txt"
    archivo_reporte = carpeta / f"reporte_{marca_tiempo}.txt"
    reporte = generar_reporte(hostname, interfaces_activas)
    reporte += "\n\nRESUMEN DE VERSION\n" + version[:1000]
    # Restringe permisos de los archivos nuevos a su propietario.
    anterior = os.umask(0o077)
    try:
        archivo_respaldo.write_text(configuracion, encoding="utf-8")
        archivo_reporte.write_text(reporte, encoding="utf-8")
    finally:
        os.umask(anterior)
    print("\nAuditoria finalizada.")
    print(f"Hostname detectado: {hostname}")
    print(f"Interfaces up/up: {len(interfaces_activas)}")
    print(f"Respaldo guardado en: {archivo_respaldo.relative_to(carpeta.parent)}")
    print(f"Reporte guardado en: {archivo_reporte.relative_to(carpeta.parent)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
