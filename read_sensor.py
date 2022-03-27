import board
import time, signal
import adafruit_scd4x

import sqlite3
from sqlite3 import Error

class Killer(object):
    dead = False
    def __init__(self):
        super().__init__()
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, *args):
        self.dead = True

def connect_db(db_file):
    connection = None
    connection = sqlite3.connect(db_file)
    return connection

def initialize_sensor():
    i2c = board.I2C()
    scd = adafruit_scd4x.SCD4X(i2c)
    scd.start_periodic_measurement()
    return scd

if __name__ == "__main__":
    
    db  = connect_db("/home/pi/CO2monitor/sensor_data.db")
    dbc = db.cursor() 

    create = '''CREATE TABLE IF NOT EXISTS data(
                dt INTEGER, 
                co2 REAL, 
                t REAL, 
                rh REAL);'''
    dbc.execute(create)
    
    scd = initialize_sensor()

    killer = Killer()
    while not killer.dead:
        if scd.data_ready:

            data = (scd.CO2, 32 + 9*scd.temperature/5, scd.relative_humidity)
            insert = """
                INSERT INTO data 
                VALUES (strftime('%s', 'now'),
                        ?, ?, ?)"""
            dbc.execute(insert, data)
            db.commit()
        time.sleep(60)

    dbc.close()
    db.close()
