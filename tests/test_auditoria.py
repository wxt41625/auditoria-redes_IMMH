from auditoria import extraer_hostname, obtener_interfaces_up, generar_reporte


def test_extraer_hostname():
    configuracion = "version 17.9\nhostname ROUTER-ALUMNO\n!"
    assert extraer_hostname(configuracion) == "ROUTER-ALUMNO"


def test_hostname_no_definido():
    configuracion = "version 17.9\n!"
    assert extraer_hostname(configuracion) == "NO_DEFINIDO"


def test_detectar_interfaces_up():
    salida = (
        "GigabitEthernet0/0 192.0.2.1 YES manual up up\n"
        "GigabitEthernet0/1 unassigned YES unset administratively down down\n"
        "Loopback0 10.0.0.1 YES manual up up"
    )
    assert obtener_interfaces_up(salida) == ["GigabitEthernet0/0", "Loopback0"]


def test_generar_reporte():
    reporte = generar_reporte("ROUTER-ALUMNO", ["GigabitEthernet0/0"])
    assert "Hostname: ROUTER-ALUMNO" in reporte
    assert "Interfaces up/up: 1" in reporte
    assert "GigabitEthernet0/0" in reporte
    assert len(reporte.splitlines()) >= 5
