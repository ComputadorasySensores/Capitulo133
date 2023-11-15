from machine import Pin, UART
import utime, time

import st7789
import tft_config
import vga1_16x16 as font

from micropyGPS import MicropyGPS        # https://github.com/inmcm/micropyGPS

tft = tft_config.config(1)
tft.init()

modulo_gps = UART(1, baudrate=9600, tx=17, rx=18)

Zona_Horaria = -3
gps = MicropyGPS(Zona_Horaria)

tft.jpg(f'gps-tracker-imagen.jpg', 0, 0, st7789.FAST)

ultimo_valor = 0
intervalo_valores = 30

def convertir(secciones):
    if (secciones[0] == 0): # secciones[0] contiene los grados
        return None
    # secciones[1] contiene los minutos    
    data = secciones[0]+(secciones[1]/60.0)
    # secciones[2] contiene 'E', 'W', 'N', 'S'
    if (secciones[2] == 'S'):
        data = -data
    if (secciones[2] == 'W'):
        data = -data

    data = '{0:.6f}'.format(data) # 6 digitos decimales
    return str(data)

try:
    while True:
        largo = modulo_gps.any()
        if largo > 0:
            b = modulo_gps.read(largo)
            for x in b:
                msg = gps.update(chr(x))
        
        latitud = convertir(gps.latitude)
        longitud = convertir(gps.longitude)
        
        if (latitud == None or longitud == None):
            tft.text(font,'Satelites: ?   ', 50, 0)
            tft.text(font,'Lat: ?        ', 0, 40)
            tft.text(font,'Lon: ?        ', 0, 80)
            tft.text(font,'Horario: ?       ', 0, 120)
            continue
        
        t = gps.timestamp
        #t[0] => horas : t[1] => minutos : t[2] => segundos
        horario = '{:02d}:{:02d}:{:02}'.format(t[0], t[1], t[2])
        
        tft.text(font,'Satelites: ' + str(gps.satellites_in_use), 50, 0)
        tft.text(font,'Lat:'+ latitud, 0, 40)
        tft.text(font,'Lon:'+ longitud, 0, 80)
        tft.text(font,'Horario:'+ horario, 0, 120)
        
        if (time.time() - ultimo_valor) > intervalo_valores:
            archivo = open("datos_gps.csv", "a")
            archivo.write(latitud + ",")
            archivo.write(longitud + ",")
            archivo.write(horario + "\n")
            archivo.close()
            ultimo_valor = time.time()
finally:
        tft.deinit()
