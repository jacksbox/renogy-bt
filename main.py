import configparser
import logging
import os
import sqlite3
import sys

from renogybt import (
    BatteryClient,
    Utils,
)

# module logs a lot of debug info, set to WARNING or ERROR to reduce output
logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger("energy_monitor")
logger.setLevel(logging.DEBUG)

class EnergyMonitor:
    def __init__(
            self,
            config_file: str,
            db_path: str
        ):
        self.config = self.load_config(config_file)

        self.client = BatteryClient(
            self.config,
            self.on_data_received,
            self.on_error_received
        )
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def load_config(self, config_file: str):
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file)
        config = configparser.ConfigParser(inline_comment_prefixes=('#'))
        config.read(config_path)

        return config

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS battery_state (
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    voltage REAL,
                    current REAL,
                    remaining_charge REAL,
                    capacity REAL,
                    cell_voltage_0 REAL,
                    cell_voltage_1 REAL,
                    cell_voltage_2 REAL,
                    cell_voltage_3 REAL,
                    temperature_0 REAL,
                    temperature_1 REAL,
                    temperature_2 REAL,
                    temperature_3 REAL
                )
            ''')

    def log_data(
        self,
        voltage,
        current,
        remaining_charge,
        capacity,
        cell_voltage_0,
        cell_voltage_1,
        cell_voltage_2,
        cell_voltage_3,
        temperature_0,
        temperature_1,
        temperature_2,
        temperature_3
    ):
        with self.conn:
            self.conn.execute('''
                INSERT INTO battery_state (
                    voltage,
                    current,
                    remaining_charge,
                    capacity,
                    cell_voltage_0,
                    cell_voltage_1,
                    cell_voltage_2,
                    cell_voltage_3,
                    temperature_0,
                    temperature_1,
                    temperature_2,
                    temperature_3
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                voltage,
                current,
                remaining_charge,
                capacity,
                cell_voltage_0,
                cell_voltage_1,
                cell_voltage_2,
                cell_voltage_3,
                temperature_0,
                temperature_1,
                temperature_2,
                temperature_3
            ))

    def start(self):
        logger.info("Starting Energy Monitor")

        self.client.start()

    def stop(self):
        logger.info("Stopping Energy Monitor")
        self.client.stop()

    # the callback func when you receive data
    def on_data_received(self, client, data):
        filtered_data = Utils.filter_fields(data, self.config['data']['fields'])
        logger.debug(f"{client.ble_manager.device.name} => {filtered_data}")

        self.log_data(
            voltage=filtered_data.get('voltage'),
            current=filtered_data.get('current'),
            remaining_charge=filtered_data.get('remaining_charge'),
            capacity=filtered_data.get('capacity'),
            cell_voltage_0=filtered_data.get('cell_voltage_0'),
            cell_voltage_1=filtered_data.get('cell_voltage_1'),
            cell_voltage_2=filtered_data.get('cell_voltage_2'),
            cell_voltage_3=filtered_data.get('cell_voltage_3'),
            temperature_0=filtered_data.get('temperature_0'),
            temperature_1=filtered_data.get('temperature_1'),
            temperature_2=filtered_data.get('temperature_2'),
            temperature_3=filtered_data.get('temperature_3')
        )

        if not self.config['data'].getboolean('enable_polling'):
            self.stop()

    # error callback
    def on_error_received(self, client, error):
        logger.error(f"on_error: {error}")

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.ini'

    energy_monitor = EnergyMonitor(config_file, 'energy_data.db')

    energy_monitor.start()

if __name__ == "__main__":
    main()
