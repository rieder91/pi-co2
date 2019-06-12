# Raspberry Pi CO2 and Temperature Sensor with Prometheus Exporter

## Flags

 * ``-v`` -- set log level to DEBUG (default=INFO)

## Running

You need Python 3.

```
# enable i2c using raspi-config
apt install -y python3-dev python3-venv i2c-tools
pip3 install --upgrade pip
pip3 install --upgrade setuptools

# clone the repo

virtualenv --no-site-packages --distribute .env
source .env/bin/activate
pip install -r requirements.txt
python main.py
```

The default port for the Promtheus HTTP server is 8000.

