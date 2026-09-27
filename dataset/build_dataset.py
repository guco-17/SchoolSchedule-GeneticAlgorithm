# -*- coding: utf-8 -*-
import csv
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Datos fuente: los 48 grupos del plan 828 (Ingenieria en Sistemas
# Computacionales), extraidos de la Planta Docente 2023-2024(2). Se
# incrustan aqui mismo para que el script no dependa de ningun archivo
# externo.
# ---------------------------------------------------------------------------

GRUPOS = [
    {"clave_materia": '828104', "materia": 'FÍSICA I', "bloque": 1, "grupo": '1DSAA', "expediente": '95484', "maestro": 'RODRIGUEZ FLORES MARIA FERNANDA', "horas": 5, "horarios": [{"dia": 'Jueves', "inicio": '10:00', "fin": '11:40', "aula": 'AULA 7'}, {"dia": 'Viernes', "inicio": '09:10', "fin": '11:40', "aula": 'AULA 25'}]},
    {"clave_materia": '828147', "materia": 'ADMINISTRACIÓN DE LAS ORGANIZACIONES', "bloque": 2, "grupo": '2DSA', "expediente": '15112', "maestro": 'ALFÉREZ RODRÍGUEZ EVARISTO', "horas": 3, "horarios": [{"dia": 'Lunes', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 3'}, {"dia": 'Jueves', "inicio": '07:30', "fin": '08:20', "aula": 'AULA 10'}]},
    {"clave_materia": '828147', "materia": 'ADMINISTRACIÓN DE LAS ORGANIZACIONES', "bloque": 2, "grupo": '2DSAA', "expediente": '15661', "maestro": 'LUNA RENTERÍA JOSÉ LUIS', "horas": 3, "horarios": [{"dia": 'Jueves', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 8'}]},
    {"clave_materia": '828103', "materia": 'CÁLCULO DIFERENCIAL', "bloque": 2, "grupo": '2DSAA', "expediente": '15443', "maestro": 'CORTÉS RAYGOZA CRISTINA ELIZABETH', "horas": 5, "horarios": [{"dia": 'Jueves', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 9'}, {"dia": 'Viernes', "inicio": '10:50', "fin": '12:30', "aula": 'AULA 9'}]},
    {"clave_materia": '828103', "materia": 'CÁLCULO DIFERENCIAL', "bloque": 2, "grupo": '2DSA', "expediente": '36384', "maestro": 'SALAS RAMOS BRENDA MARGARITA', "horas": 5, "horarios": [{"dia": 'Miércoles', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 10'}, {"dia": 'Jueves', "inicio": '10:00', "fin": '11:40', "aula": 'AULA 10'}]},
    {"clave_materia": '828402', "materia": 'COMUNICACIÓN EFECTIVA', "bloque": 2, "grupo": '2DSAA', "expediente": '37227', "maestro": 'HERRERA HERNANDEZ ALEJANDRO', "horas": 3, "horarios": [{"dia": 'Martes', "inicio": '07:30', "fin": '10:00', "aula": 'AULA 9'}]},
    {"clave_materia": '828402', "materia": 'COMUNICACIÓN EFECTIVA', "bloque": 2, "grupo": '2DSA', "expediente": '15661', "maestro": 'LUNA RENTERÍA JOSÉ LUIS', "horas": 3, "horarios": [{"dia": 'Martes', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 23'}]},
    {"clave_materia": '828109', "materia": 'FÍSICA II', "bloque": 2, "grupo": '2DSA', "expediente": '97761', "maestro": 'RAMIREZ GOMEZ PAMELA ESTEFANY', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 10'}, {"dia": 'Jueves', "inicio": '10:00', "fin": '11:40', "aula": 'AULA 10'}]},
    {"clave_materia": '828109', "materia": 'FÍSICA II', "bloque": 2, "grupo": '2DSAA', "expediente": '36384', "maestro": 'SALAS RAMOS BRENDA MARGARITA', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 9'}, {"dia": 'Martes', "inicio": '10:50', "fin": '12:30', "aula": 'AULA 3'}]},
    {"clave_materia": '828106', "materia": 'CÁLCULO INTEGRAL', "bloque": 3, "grupo": '3DSA', "expediente": '94725', "maestro": 'FLORES GONZALEZ LEONARDO', "horas": 5, "horarios": [{"dia": 'Jueves', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 15'}, {"dia": 'Viernes', "inicio": '10:00', "fin": '11:40', "aula": 'AULA 15'}]},
    {"clave_materia": '828106', "materia": 'CÁLCULO INTEGRAL', "bloque": 3, "grupo": '3DSAA', "expediente": '14662', "maestro": 'HERNÁNDEZ OVALLE RAUL MIGUEL', "horas": 5, "horarios": [{"dia": 'Martes', "inicio": '10:50', "fin": '12:30', "aula": 'AULA 17'}, {"dia": 'Miércoles', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 17'}]},
    {"clave_materia": '828152', "materia": 'CONTABILIDAD FINANCIERA', "bloque": 3, "grupo": '3DSA', "expediente": '97214', "maestro": 'FARIAS VALDES LUIS', "horas": 3, "horarios": [{"dia": 'Jueves', "inicio": '07:30', "fin": '10:00', "aula": 'AULA 13'}]},
    {"clave_materia": '828152', "materia": 'CONTABILIDAD FINANCIERA', "bloque": 3, "grupo": '3DSAA', "expediente": '98421', "maestro": 'JIMENEZ SOLIS LESLIE BETHSAYRA', "horas": 3, "horarios": [{"dia": 'Martes', "inicio": '10:00', "fin": '10:50', "aula": 'AULA 3'}, {"dia": 'Miércoles', "inicio": '10:00', "fin": '11:40', "aula": 'AULA 17'}]},
    {"clave_materia": '828228', "materia": 'ESTRUCTURA DE DATOS', "bloque": 3, "grupo": '3DSAA', "expediente": '14213', "maestro": 'ADAME LEYVA DAVID ERNESTO', "horas": 5, "horarios": [{"dia": 'Jueves', "inicio": '09:10', "fin": '10:50', "aula": 'AULA CISCO'}, {"dia": 'Viernes', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 34 LAB C.C'}]},
    {"clave_materia": '828228', "materia": 'ESTRUCTURA DE DATOS', "bloque": 3, "grupo": '3DSA', "expediente": '6407', "maestro": 'NEVAREZ ACEVES JESÚS ANTONIO', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 34 C.C'}, {"dia": 'Miércoles', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 34 C.C'}, {"dia": 'Viernes', "inicio": '07:30', "fin": '08:20', "aula": 'AULA 34 C.C'}]},
    {"clave_materia": '828149', "materia": 'ÉTICA', "bloque": 3, "grupo": '3DSAA', "expediente": '94021', "maestro": 'DELGADO OROZCO OCTAVIO', "horas": 3, "horarios": [{"dia": 'Viernes', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 5'}]},
    {"clave_materia": '828149', "materia": 'ÉTICA', "bloque": 3, "grupo": '3DSA', "expediente": '91646', "maestro": 'MTANOUS VILLARREAL ALMA BELICA', "horas": 3, "horarios": [{"dia": 'Martes', "inicio": '10:50', "fin": '12:30', "aula": 'AULA 14'}]},
    {"clave_materia": '828412', "materia": 'ALGORITMOS DE ORDENAMIENTO Y BÚSQUEDA', "bloque": 4, "grupo": '4DSA', "expediente": '6407', "maestro": 'NEVAREZ ACEVES JESÚS ANTONIO', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 34 LAB C.C'}, {"dia": 'Miércoles', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 34 LAB C.C'}, {"dia": 'Jueves', "inicio": '08:20', "fin": '09:10', "aula": 'AULA 34 LAB C.C'}]},
    {"clave_materia": '828412', "materia": 'ALGORITMOS DE ORDENAMIENTO Y BÚSQUEDA', "bloque": 4, "grupo": '4NSB', "expediente": '95379', "maestro": 'CHIO BENAVIDES SANTIAGO', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '19:00', "fin": '21:30', "aula": 'AULA 29 CISCO I'}, {"dia": 'Jueves', "inicio": '18:10', "fin": '19:50', "aula": 'AULA 29 CISCO I'}]},
    {"clave_materia": '828273', "materia": 'BASE DE DATOS I', "bloque": 4, "grupo": '4DSA', "expediente": '11485', "maestro": 'MESTA AGUILAR OSCAR FORTUNATO', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 31 LAB CB'}, {"dia": 'Jueves', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 31 LAB CB'}, {"dia": 'Viernes', "inicio": '07:30', "fin": '08:20', "aula": 'AULA 31 LAB CB'}]},
    {"clave_materia": '828273', "materia": 'BASE DE DATOS I', "bloque": 4, "grupo": '4NSB', "expediente": '14240', "maestro": 'CASTILLA ESPINOZA ROSA MARÍA', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 29 CISCO I'}, {"dia": 'Jueves', "inicio": '18:10', "fin": '19:50', "aula": 'AULA 29 CISCO I'}]},
    {"clave_materia": '828110', "materia": 'CÁLCULO MULTIVARIABLE', "bloque": 4, "grupo": '4NSB', "expediente": '94230', "maestro": 'GARCIA ESPARZA LAURA MONICA MONSERRAT', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 14'}, {"dia": 'Jueves', "inicio": '16:30', "fin": '18:10', "aula": 'AULA 14'}]},
    {"clave_materia": '828110', "materia": 'CÁLCULO MULTIVARIABLE', "bloque": 4, "grupo": '4DSA', "expediente": '14662', "maestro": 'HERNÁNDEZ OVALLE RAUL MIGUEL', "horas": 5, "horarios": [{"dia": 'Martes', "inicio": '07:30', "fin": '10:00', "aula": 'AULA 23'}, {"dia": 'Miércoles', "inicio": '08:20', "fin": '10:00', "aula": 'AULA 23'}]},
    {"clave_materia": '828108', "materia": 'ESTADÍSTICA', "bloque": 4, "grupo": '4DSA', "expediente": '13607', "maestro": 'MENDOZA ZAMORA MIGUEL ÁNGEL', "horas": 3, "horarios": [{"dia": 'Martes', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 31 LAB CB'}]},
    {"clave_materia": '828108', "materia": 'ESTADÍSTICA', "bloque": 4, "grupo": '4NSB', "expediente": '15453', "maestro": 'ORTÍZ LEOS GABRIELA DEL CARMEN', "horas": 3, "horarios": [{"dia": 'Lunes', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 20'}]},
    {"clave_materia": '828115', "materia": 'ELECTRICIDAD Y MAGNETISMO', "bloque": 4, "grupo": '4NSB', "expediente": '91693', "maestro": 'LIMONES MAGALLANES JORGE', "horas": 5, "horarios": [{"dia": 'Martes', "inicio": '08:20', "fin": '10:00', "aula": 'AULA 23'}, {"dia": 'Jueves', "inicio": '07:30', "fin": '10:00', "aula": 'AULA 23'}]},
    {"clave_materia": '828115', "materia": 'ELECTRICIDAD Y MAGNETISMO', "bloque": 4, "grupo": '4DSA', "expediente": '93157', "maestro": 'PÉREZ GOMEZ GAONA OCTAVIO', "horas": 5, "horarios": [{"dia": 'Martes', "inicio": '10:00', "fin": '11:40', "aula": 'AULA 13'}, {"dia": 'Viernes', "inicio": '09:10', "fin": '10:50', "aula": 'AULA 8'}]},
    {"clave_materia": '828102', "materia": 'ÁLGEBRA LINEAL', "bloque": 5, "grupo": '5NSB', "expediente": '95086', "maestro": 'CERDA DURAN ISAAC ESAU', "horas": 3, "horarios": [{"dia": 'Lunes', "inicio": '16:30', "fin": '19:00', "aula": 'AULA LAB CB 31'}]},
    {"clave_materia": '828102', "materia": 'ÁLGEBRA LINEAL', "bloque": 5, "grupo": '5DSA', "expediente": '36384', "maestro": 'SALAS RAMOS BRENDA MARGARITA', "horas": 3, "horarios": [{"dia": 'Jueves', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 31 LAB CB'}]},
    {"clave_materia": '828277', "materia": 'BASE DE DATOS II', "bloque": 5, "grupo": '5NSB', "expediente": '14240', "maestro": 'CASTILLA ESPINOZA ROSA MARÍA', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 29 CISCO I'}, {"dia": 'Jueves', "inicio": '16:30', "fin": '18:10', "aula": 'AULA 29 CISCO I'}]},
    {"clave_materia": '828277', "materia": 'BASE DE DATOS II', "bloque": 5, "grupo": '5DSA', "expediente": '16104', "maestro": 'FLORES ZARAGOZA URBANO DE JESÚS', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '07:30', "fin": '10:00', "aula": 'AULA 30 CISCO II'}, {"dia": 'Jueves', "inicio": '09:10', "fin": '10:50', "aula": 'AULA 30 CISCO II'}]},
    {"clave_materia": '828111', "materia": 'ECUACIONES DIFERENCIALES', "bloque": 5, "grupo": '5DSA', "expediente": '93157', "maestro": 'PÉREZ GOMEZ GAONA OCTAVIO', "horas": 5, "horarios": [{"dia": 'Martes', "inicio": '10:50', "fin": '12:30', "aula": 'AULA 13'}, {"dia": 'Miércoles', "inicio": '10:00', "fin": '12:30', "aula": 'AULA 13'}]},
    {"clave_materia": '828111', "materia": 'ECUACIONES DIFERENCIALES', "bloque": 5, "grupo": '5NSB', "expediente": '97751', "maestro": 'SANCHEZ CONTRERAS PAOLA ALEJANDRINA', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '19:00', "fin": '21:30', "aula": 'AULA 17'}]},
    {"clave_materia": '828139', "materia": 'EVALUACIÓN DE PROYECTOS', "bloque": 5, "grupo": '5DSA', "expediente": '96418', "maestro": 'CISNEROS TORRES JUAN CARLOS', "horas": 4, "horarios": [{"dia": 'Lunes', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 30 CISCO II'}, {"dia": 'Martes', "inicio": '07:30', "fin": '09:10', "aula": 'AULA 30 CISCO II'}]},
    {"clave_materia": '828139', "materia": 'EVALUACIÓN DE PROYECTOS', "bloque": 5, "grupo": '5NSB', "expediente": '12926', "maestro": 'ARELLANO TAMÉZ JOSÉ FELIX', "horas": 4, "horarios": [{"dia": 'Jueves', "inicio": '16:30', "fin": '18:10', "aula": 'AULA 18'}, {"dia": 'Viernes', "inicio": '16:30', "fin": '18:10', "aula": 'AULA 18'}]},
    {"clave_materia": '828504', "materia": 'INGENIERÍA DE SOFTWARE', "bloque": 5, "grupo": '5DSA', "expediente": '95996', "maestro": 'SOTO MENDOZA VALERIA', "horas": 3, "horarios": [{"dia": 'Lunes', "inicio": '09:10', "fin": '11:40', "aula": 'AULA 33 LAB INF'}]},
    {"clave_materia": '828504', "materia": 'INGENIERÍA DE SOFTWARE', "bloque": 5, "grupo": '5NSB', "expediente": '14213', "maestro": 'ADAME LEYVA DAVID ERNESTO', "horas": 3, "horarios": [{"dia": 'Martes', "inicio": '19:00', "fin": '21:30', "aula": 'AULA 22'}]},
    {"clave_materia": '828605', "materia": 'ANÁLISIS Y MODELACIÓN DE SISTEMAS', "bloque": 6, "grupo": '6NSB', "expediente": '94880', "maestro": 'RIOS WILLARS ERNESTO', "horas": 3, "horarios": [{"dia": 'Lunes', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 14'}]},
    {"clave_materia": '828707', "materia": 'CALIDAD Y PRUEBAS DE SOFTWARE', "bloque": 7, "grupo": '7NSB', "expediente": '97942', "maestro": 'TREJO GARCIA CARLOS NASSIF', "horas": 5, "horarios": [{"dia": 'Jueves', "inicio": '19:50', "fin": '21:30', "aula": 'AULA 15'}, {"dia": 'Viernes', "inicio": '19:00', "fin": '21:30', "aula": 'AULA CC 34'}]},
    {"clave_materia": '828151', "materia": 'DESARROLLO SUSTENTABLE', "bloque": 7, "grupo": '7NSB', "expediente": '93174', "maestro": 'RODRIGUEZ SANCHEZ ARUMI', "horas": 3, "horarios": [{"dia": 'Miércoles', "inicio": '19:00', "fin": '21:30', "aula": 'AULA 15'}]},
    {"clave_materia": '828708', "materia": 'DISEÑO Y ARQUITECTURA DE SOFTWARE', "bloque": 7, "grupo": '7NSB', "expediente": '92298', "maestro": 'PÉREZ TINOCO DAVID', "horas": 4, "horarios": [{"dia": 'Martes', "inicio": '19:00', "fin": '20:40', "aula": 'AULA 7'}, {"dia": 'Miércoles', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 29 CISCO I'}]},
    {"clave_materia": '828709', "materia": 'GRAFICACIÓN Y REALIDAD VIRTUAL', "bloque": 7, "grupo": '7NSB', "expediente": '17367', "maestro": 'FLORES HERMOSILLO BERNARDO DAVID', "horas": 5, "horarios": [{"dia": 'Martes', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 6'}]},
    {"clave_materia": '828811', "materia": 'ADMINISTRACIÓN DE PROYECTOS DE SOFTWARE', "bloque": 8, "grupo": '8NSB', "expediente": '94880', "maestro": 'RIOS WILLARS ERNESTO', "horas": 3, "horarios": [{"dia": 'Jueves', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 15'}]},
    {"clave_materia": '828812', "materia": 'ADMINISTRACIÓN DE SERVIDORES', "bloque": 8, "grupo": '8NSB', "expediente": '91198', "maestro": 'RAMOS GONZÁLEZ FRANCISCO HORACIO', "horas": 3, "horarios": [{"dia": 'Lunes', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 23'}]},
    {"clave_materia": '828813', "materia": 'DESARROLLO DE APLICACIONES DE CÓMPUTO MÓVIL', "bloque": 8, "grupo": '8NSB', "expediente": '17367', "maestro": 'FLORES HERMOSILLO BERNARDO DAVID', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '16:30', "fin": '19:00', "aula": 'AULA 30 CISCO'}, {"dia": 'Miércoles', "inicio": '16:30', "fin": '18:10', "aula": 'AULA 18'}]},
    {"clave_materia": '828814', "materia": 'DESARROLLO DE APLICACIONES WEB', "bloque": 9, "grupo": '9NSB', "expediente": '92298', "maestro": 'PÉREZ TINOCO DAVID', "horas": 5, "horarios": [{"dia": 'Martes', "inicio": '19:00', "fin": '20:40', "aula": 'AULA 34 LAB C.C'}, {"dia": 'Jueves', "inicio": '18:10', "fin": '20:40', "aula": 'AULA 34 LAB C.C'}]},
    {"clave_materia": '828916', "materia": 'DESARROLLO DE PROYECTOS DE SOFTWARE', "bloque": 9, "grupo": '9NSB', "expediente": '7842', "maestro": 'GARCÍA RIVERA VICTOR MANUEL', "horas": 5, "horarios": [{"dia": 'Lunes', "inicio": '19:00', "fin": '21:30', "aula": 'AULA 33 LAB INF'}, {"dia": 'Jueves', "inicio": '19:00', "fin": '20:40', "aula": 'AULA 18'}]},
    {"clave_materia": '828917', "materia": 'DISEÑO DE COMPILADORES', "bloque": 9, "grupo": '9NSB', "expediente": '15115', "maestro": 'LIÑAN GARCIA ERNESTO', "horas": 3, "horarios": [{"dia": 'Martes', "inicio": '19:00', "fin": '21:30', "aula": 'AULA 17'}]},
]


# ---------------------------------------------------------------------------
# Normalizacion de nombres de aula: el PDF original tiene inconsistencias de
# captura (p.ej. "AULA 30 CISCO" vs "AULA 30 CISCO II", "AULA CC 34" vs
# "AULA 34 LAB C.C") que hay que unificar antes de tratarlas como el mismo
# recurso fisico.
# ---------------------------------------------------------------------------
NORMALIZAR_AULA = {
    "AULA 30 CISCO": "AULA 30 CISCO II",
    "AULA CC 34": "AULA 34 LAB C.C",
    "AULA CISCO": "AULA 29 CISCO I",
    "AULA LAB CB 31": "AULA 31 LAB CB",
    "AULA 34 C.C": "AULA 34 LAB C.C",
}


def normalizar(aula):
    aula = aula.strip()
    return NORMALIZAR_AULA.get(aula, aula)


def tipo_de_aula(aula):
    a = aula.upper()
    if "CISCO" in a:
        return "laboratorio_redes_cisco"
    if "LAB" in a or "C.C" in a:
        return "laboratorio_computo"
    return "aula_regular"


CAPACIDAD_POR_TIPO = {
    "aula_regular": 35,
    "laboratorio_computo": 32,
    "laboratorio_redes_cisco": 35,
}

EQUIPAMIENTO_POR_TIPO = {
    "aula_regular": "pantalla;pizarron_blanco;bancas_individuales",
    "laboratorio_computo": "computadoras_escritorio;pantalla;pizarron_blanco",
    "laboratorio_redes_cisco": "computadoras_escritorio;pantalla;pizarron_blanco",
}

# Palabras clave -> tipo de aula requerido por la clase, y software tipico.
# (Mismo criterio, inferido, que en la version anterior del dataset.)
REQUISITOS_POR_MATERIA = {
    "PROGRAMACION": ("laboratorio_computo", "IDE, compilador/interprete segun lenguaje del curso"),
    "PROGRAMACIÓN": ("laboratorio_computo", "IDE, compilador/interprete segun lenguaje del curso"),
    "BASE DE DATOS": ("laboratorio_redes_cisco", "MySQL/PostgreSQL, MySQL Workbench"),
    "ESTRUCTURA DE DATOS": ("laboratorio_computo", "IDE, compilador"),
    "LOGICA DIGITAL": ("laboratorio_computo", "Simulador de circuitos (Logisim)"),
    "LÓGICA DIGITAL": ("laboratorio_computo", "Simulador de circuitos (Logisim)"),
    "REDES": ("laboratorio_redes_cisco", "Cisco Packet Tracer / equipo real"),
    "SERVIDORES": ("laboratorio_redes_cisco", "Sistema operativo de servidor, maquinas virtuales"),
    "APLICACIONES": ("laboratorio_computo", "IDE / entorno de desarrollo especifico"),
    "PROYECTOS DE SOFTWARE": ("laboratorio_computo", "IDE, control de versiones (Git)"),
    "COMPILADORES": ("aula_regular", "IDE, herramientas ANTLR/Flex-Bison"),
    "GRAFICACION": ("laboratorio_computo", "Motor grafico (Unity/Unreal)"),
    "GRAFICACIÓN": ("laboratorio_computo", "Motor grafico (Unity/Unreal)"),
    "SOFTWARE": ("aula_regular", "Herramienta de modelado UML"),
}
REQUISITO_DEFAULT = ("aula_regular", "Ninguno especifico")


def requisitos_de(materia):
    m = materia.upper()
    for clave, val in REQUISITOS_POR_MATERIA.items():
        if clave in m:
            return val
    return REQUISITO_DEFAULT


def inferir_turno(grupo):
    """2a letra del codigo de grupo: D=Diurno, N=Nocturno (convencion real
    de la propia facultad, visible en todo el documento de oferta)."""
    letras = [c for c in grupo if c.isalpha()]
    if not letras:
        return "Desconocido"
    return {"D": "Diurno", "N": "Nocturno"}.get(letras[0].upper(), "Desconocido")


def escribir_csv(nombre, encabezado, filas):
    ruta = os.path.join(OUT_DIR, nombre)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(encabezado)
        w.writerows(filas)
    print(f"  -> {ruta}  ({len(filas)} filas)")


def main():
    grupos = GRUPOS

    # --- 1. AULAS (dominio R): solo el recurso fisico, sin horario ---
    aulas_vistas = {}
    for g in grupos:
        for h in g["horarios"]:
            aula = normalizar(h["aula"])
            if aula not in aulas_vistas:
                tipo = tipo_de_aula(aula)
                aulas_vistas[aula] = tipo

    print("Generando aulas.csv ...")
    filas_aulas = []
    for aula, tipo in sorted(aulas_vistas.items()):
        filas_aulas.append((
            aula, tipo, CAPACIDAD_POR_TIPO[tipo], EQUIPAMIENTO_POR_TIPO[tipo]
        ))
    escribir_csv(
        "aulas.csv",
        ["aula_id", "tipo", "capacidad_estimada", "equipamiento"],
        filas_aulas,
    )

    # --- 2. HORARIOS (dominio H): bloques dia+hora que realmente existen ---
    print("Generando horarios.csv ...")
    horarios_vistos = set()
    for g in grupos:
        for h in g["horarios"]:
            horarios_vistos.add((h["dia"], h["inicio"], h["fin"]))

    orden_dias = ["Lunes", "Martes", "Miercoles", "Miércoles", "Jueves", "Viernes", "Sabado"]
    horarios_ordenados = sorted(
        horarios_vistos,
        key=lambda x: (orden_dias.index(x[0]) if x[0] in orden_dias else 99, x[1]),
    )
    filas_horarios = []
    for i, (dia, inicio, fin) in enumerate(horarios_ordenados, start=1):
        filas_horarios.append((f"H{i:03d}", dia, inicio, fin))
    escribir_csv("horarios.csv", ["horario_id", "dia", "hora_inicio", "hora_fin"], filas_horarios)

    # --- 3. CLASES (dominio C): SIN aula ni horario fijos ---
    print("Generando clases.csv ...")
    filas_clases = []
    for idx, g in enumerate(grupos, start=1):
        tipo_req, software_req = requisitos_de(g["materia"])
        turno = inferir_turno(g["grupo"])
        num_sesiones = len(g["horarios"])
        filas_clases.append((
            idx, g["grupo"], turno, g["materia"], g["maestro"],
            g["horas"], num_sesiones, tipo_req,
            EQUIPAMIENTO_POR_TIPO[tipo_req], software_req,
        ))
    escribir_csv(
        "clases.csv",
        ["clase_id", "grupo", "turno_inferido", "materia", "profesor",
         "horas_semana", "num_sesiones_requeridas", "tipo_aula_requerido",
         "equipamiento_requerido", "software_requerido"],
        filas_clases,
    )

    # --- 4. LINEA BASE (solo para comparar, nunca como entrada del AG) ---
    print("Generando asignacion_actual.csv (linea base, NO usar como input del AG) ...")
    filas_base = []
    for idx, g in enumerate(grupos, start=1):
        for h in g["horarios"]:
            filas_base.append((
                idx, g["grupo"], g["materia"], h["dia"], h["inicio"], h["fin"],
                normalizar(h["aula"]),
            ))
    escribir_csv(
        "asignacion_actual.csv",
        ["clase_id", "grupo", "materia", "dia", "hora_inicio", "hora_fin", "aula"],
        filas_base,
    )

    print(f"\nResumen: {len(filas_aulas)} aulas | {len(filas_horarios)} bloques horarios "
          f"| {len(filas_clases)} clases a programar (sin R,H) | "
          f"{len(filas_base)} sesiones de la asignacion actual (linea base).")


if __name__ == "__main__":
    main()