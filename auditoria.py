def extraer_hostname(configuracion):
    """Extrae el hostname de la configuracion."""
    for linea in configuracion.splitlines():
        partes = linea.strip().split()
        if len(partes) == 2 and partes[0].lower() == "hostname":
            return partes[1]
    return "NO_DEFINIDO"


def obtener_interfaces_up(salida_interfaces):
    """Identifica las interfaces con estado y protocolo up/up."""
    interfaces_activas = []
    for linea in salida_interfaces.splitlines():
        partes = linea.split()
        if len(partes) >= 6:
            if partes[-2].lower() == "up" and partes[-1].lower() == "up":
                interfaces_activas.append(partes[0])
    return interfaces_activas


def generar_reporte(hostname, interfaces_activas):
    lineas = [
        "REPORTE DE AUDITORIA DE RED",
        "Autor: Irvin Misael Mejia Hernandez",
        f"Hostname: {hostname}",
        f"Interfaces up/up: {len(interfaces_activas)}",
        "Detalle de interfaces:"
    ]
    if interfaces_activas:
        lineas.extend(f"- {nombre}" for nombre in interfaces_activas)
    else:
        lineas.append("- No se detectaron interfaces up/up")
    return "\n".join(lineas)


if __name__ == "__main__":
    ejemplo_config = "hostname ROUTER-LAB"
    ejemplo_interfaces = (
        "GigabitEthernet0/0 192.0.2.1 YES manual up up\n"
        "GigabitEthernet0/1 unassigned YES unset administratively down down"
    )
    nombre = extraer_hostname(ejemplo_config)
    activas = obtener_interfaces_up(ejemplo_interfaces)
    print(generar_reporte(nombre, activas))
