import configparser
import logging
import os
import sys

from renogybt import (
    BatteryClient,
    Utils,
)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("energy_monitor")
logger.setLevel(logging.DEBUG)

config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.ini'
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file)
config = configparser.ConfigParser(inline_comment_prefixes=('#'))
config.read(config_path)

enable_polling = config['data'].getboolean('enable_polling')

# the callback func when you receive data
def on_data_received(client, data):
    filtered_data = Utils.filter_fields(data, config['data']['fields'])
    logger.debug(f"{client.ble_manager.device.name} => {filtered_data}")

    if not enable_polling:
        logger.info("Stopping client (polling disabled)")
        client.stop()

# error callback
def on_error(client, error):
    logger.error(f"on_error: {error}")

def main():
    client = BatteryClient(config, on_data_received, on_error)

    client.start()

if __name__ == "__main__":
    main()
