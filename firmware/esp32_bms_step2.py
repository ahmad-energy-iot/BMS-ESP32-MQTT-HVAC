from machine import Pin
from dht import DHT11
from umqtt.simple import MQTTClient
import network
import time

# Copy your existing connection settings here. Do not share passwords.
SSID = ""
PASSWORD = ""
MQTT_BROKER = "192.168.178.38"
MQTT_USER = "bms_user"
MQTT_PASSWORD = ""

MQTT_TOPIC = b"bms/room1/temperature"
HUMIDITY_TOPIC = b"bms/room1/humidity"
FAN_TOPIC = b"bms/room1/fan/command"
VALVE_TOPIC = b"bms/room1/valve/command"
READ_INTERVAL_MS = 2000
COMMAND_TIMEOUT_MS = 10000
RETRY_INTERVAL = 5
WIFI_TIMEOUT_MS = 20000

# Fan relay: IN2 -> GPIO23, active LOW.
relay = Pin(23, Pin.OUT, value=1)
# GPIO26 -> resistor -> LED long leg; short leg -> GND.
valve_led = Pin(26, Pin.OUT, value=0)
sensor = DHT11(Pin(4))
wlan = network.WLAN(network.WLAN.IF_STA)
wlan.active(True)
client = None
last_command_ms = None
last_valve_command_ms = None
reading_number = 0


def fan_off():
    global last_command_ms
    relay.value(1)
    last_command_ms = None


def valve_off():
    global last_valve_command_ms
    valve_led.value(0)
    last_valve_command_ms = None


def on_message(topic, message):
    global last_command_ms, last_valve_command_ms
    if topic == FAN_TOPIC:
        if message not in (b"ON", b"OFF"):
            fan_off()
            print("Invalid fan command: fan OFF")
            return
        last_command_ms = time.ticks_ms()
        desired = 0 if message == b"ON" else 1
        changed = relay.value() != desired
        relay.value(desired)
        if changed:
            print("Fan command received:", message.decode())
    elif topic == VALVE_TOPIC:
        if message not in (b"ON", b"OFF"):
            valve_off()
            print("Invalid valve command: LED OFF")
            return
        last_valve_command_ms = time.ticks_ms()
        desired = 1 if message == b"ON" else 0
        changed = valve_led.value() != desired
        valve_led.value(desired)
        if changed:
            print("Valve command received:", message.decode())


def close_mqtt():
    global client
    fan_off()
    valve_off()
    if client is not None:
        try:
            client.sock.close()
        except Exception:
            pass
    client = None


def retry_pause():
    fan_off()
    valve_off()
    for _ in range(RETRY_INTERVAL * 10):
        time.sleep_ms(100)


def connect_wifi():
    if wlan.isconnected():
        return True
    print("Connecting to WiFi...")
    try:
        wlan.active(True)
        wlan.disconnect()
        wlan.connect(SSID, PASSWORD)
        start = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), start) >= WIFI_TIMEOUT_MS:
                wlan.disconnect()
                print("WiFi connection timed out")
                return False
            time.sleep_ms(100)
        print("WiFi connected | ESP32 IP:", wlan.ifconfig()[0])
        return True
    except OSError as error:
        print("WiFi ERROR:", error)
        return False


def connect_mqtt():
    global client
    close_mqtt()
    try:
        client = MQTTClient(
            client_id=b"bms-step2-esp32",
            server=MQTT_BROKER,
            port=1883,
            user=MQTT_USER.encode(),
            password=MQTT_PASSWORD.encode(),
            keepalive=30
        )
        client.set_callback(on_message)
        client.connect()
        client.subscribe(FAN_TOPIC)
        client.subscribe(VALVE_TOPIC)
        print("MQTT connected | subscribed:", FAN_TOPIC.decode())
        print("Subscribed:", VALVE_TOPIC.decode())
        return True
    except Exception as error:
        print("MQTT connection ERROR:", repr(error))
        close_mqtt()
        return False


try:
    if not SSID or not PASSWORD or not MQTT_BROKER or not MQTT_PASSWORD:
        raise ValueError("Fill your existing WiFi and MQTT settings first")
    last_read_ms = time.ticks_ms()
    while True:
        if not wlan.isconnected():
            close_mqtt()
            if not connect_wifi():
                retry_pause()
                continue
        if client is None:
            if not connect_mqtt():
                retry_pause()
                continue
        try:
            if (last_command_ms is not None and
                    time.ticks_diff(time.ticks_ms(), last_command_ms)
                    >= COMMAND_TIMEOUT_MS):
                fan_off()
                print("Fan OFF: command timeout")
            if (last_valve_command_ms is not None and
                    time.ticks_diff(time.ticks_ms(), last_valve_command_ms)
                    >= COMMAND_TIMEOUT_MS):
                valve_off()
                print("Valve LED OFF: command timeout")
            client.check_msg()
            now = time.ticks_ms()
            if time.ticks_diff(now, last_read_ms) >= READ_INTERVAL_MS:
                last_read_ms = now
                reading_number += 1
                try:
                    sensor.measure()
                    temperature = sensor.temperature()
                    humidity = sensor.humidity()
                except OSError as error:
                    print("Reading", reading_number, "| SENSOR ERROR:", error)
                    client.ping()
                else:
                    client.publish(MQTT_TOPIC, str(temperature).encode(), retain=False)
                    client.publish(HUMIDITY_TOPIC, str(humidity).encode(), retain=False)
                    print(
                        "Reading", reading_number,
                        "| Temperature published:", temperature, "C",
                        "| Humidity published:", humidity, "%"
                    )
        except Exception as error:
            print("MQTT communication ERROR:", repr(error))
            close_mqtt()
            retry_pause()
            continue
        time.sleep_ms(100)
except KeyboardInterrupt:
    print("Program stopped manually")
finally:
    close_mqtt()
    print("Fan OFF | Valve LED OFF | MQTT connection closed")
