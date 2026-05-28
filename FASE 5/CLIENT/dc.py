import socket
import json
import time
import dht
import machine
from misurazione import lettura_sensore
from cripto import criptazione   # FIX: importato ma non usato nel file originale

# Scelta identità
IDENTITA = input("Inserisci identità (es. DC-001): ").strip()

# Caricamento parametri cabina
# FIX: il path originale era "da.json" ma il file si trova in "Configurazione/da.json"
try:
    with open("Configurazione/da.json", "r") as f:
        da = json.load(f)
except Exception as e:
    print("ERRORE lettura Configurazione/da.json:", e)
    raise SystemExit

if IDENTITA not in da:
    print(f"ERRORE: '{IDENTITA}' non trovata in da.json")
    print("Identità disponibili:", list(da.keys()))
    raise SystemExit

parametri = da[IDENTITA]
IP     = parametri["IP"]
PORTA  = parametri["porta"]
CABINA = parametri["cabina"]
PONTE  = parametri["ponte"]

print(f"Dispositivo: {IDENTITA} | Cabina {CABINA} | Ponte {PONTE}")

# Inizializzazione sensore
sensor = dht.DHT11(machine.Pin(0))

# Connessione al gateway
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((IP, PORTA))
except Exception as e:
    print("ERRORE connessione al gateway:", e)
    raise SystemExit

print(f"Connesso al Gateway IoT ({IP}:{PORTA})")

# Invio dati
while True:

    try:
        temperatura, umidita = lettura_sensore(sensor)
        temperatura = round(temperatura, 2)
        umidita     = round(umidita, 2)

        dato = {
            "identita":    IDENTITA,
            "cabina":      CABINA,
            "ponte":       PONTE,
            "temperature": temperatura,
            "humidity":    umidita
        }

        dato_json = json.dumps(dato)

        # FIX: cifra il dato prima dell'invio usando cripto.py
        dato_cifrato = criptazione(dato_json)

        print(f"[{IDENTITA}] Dato inviato:", dato)
        s.sendall((dato_cifrato + "\n").encode("utf-8"))

        time.sleep(2)

    except KeyboardInterrupt:
        print(f"\n[{IDENTITA}] Chiusura...")
        s.close()
        break

    except Exception as e:
        print(f"[{IDENTITA}] ERRORE:", e)
        s.close()
        break