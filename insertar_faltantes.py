from db_manager import guardar_registro

guardar_registro(
    ip="192.168.14.141",
    nombre="Brother MFC-7065DN",
    sector="Oficina Planta alta (San lorenzo)",
    fecha="2026-09-23",      # Año-Mes-Día del mes anterior
    contador=12345,          # El dato que tienes
    diferencia=None          # Se calculará automáticamente después
)