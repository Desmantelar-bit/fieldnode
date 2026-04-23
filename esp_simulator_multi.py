#!/usr/bin/env python
"""
Simulador ESP Multi-Máquinas - Envia dados dinâmicos para 3 colheitadeiras
Simula cenários realistas com variações de temperatura, vibração e RPM

Para rodar:
    python esp_simulator_multi.py
"""
import json
import uuid
import time
import random
import threading
from datetime import datetime
import paho.mqtt.client as mqtt

# Configuração
BROKER_HOST = 'localhost'
BROKER_PORT = 1883
TOPICO_BASE = 'fieldnode'
INTERVALO_ENVIO = 2  # segundos entre leituras

# Máquinas cadastradas no banco
MAQUINAS = [
    {
        'id': 'NH-C10000-01',
        'modelo': 'New Holland C10000',
        'operario': 'Ana Furlaneto',
        'cenario': 'normal'  # normal, aquecendo, critico
    },
    {
        'id': 'CASE-TC5000-02', 
        'modelo': 'Case IH TC5000',
        'operario': 'Letícia Terrete',
        'cenario': 'aquecendo'
    },
    {
        'id': 'CASE-TC5000-03',
        'modelo': 'Case IH TC5000', 
        'operario': 'João Matheus',
        'cenario': 'normal'
    }
]

class SimuladorMaquina:
    def __init__(self, maquina_info):
        self.info = maquina_info
        self.contador = 0
        self.temp_base = 75
        self.vib_base = 0.5
        self.rpm_base = 1800
        self.tendencia_temp = 0
        
    def gerar_leitura(self):
        """Gera leitura dinâmica baseada no cenário da máquina"""
        self.contador += 1
        
        # Cenários dinâmicos
        if self.info['cenario'] == 'normal':
            temp_var = random.gauss(0, 3)
            vib_var = random.gauss(0, 0.05)
            rpm_var = random.gauss(0, 30)
            
        elif self.info['cenario'] == 'aquecendo':
            # Temperatura subindo gradualmente
            self.tendencia_temp += random.uniform(0.1, 0.3)
            temp_var = self.tendencia_temp + random.gauss(0, 2)
            vib_var = random.gauss(0, 0.08)  # Mais vibração
            rpm_var = random.gauss(0, 50)
            
        else:  # crítico
            # Oscilações mais extremas
            temp_var = random.gauss(15, 5)
            vib_var = random.gauss(0.2, 0.1)
            rpm_var = random.gauss(0, 100)
        
        # Calcula valores finais
        temperatura = round(max(50, min(120, self.temp_base + temp_var)), 1)
        vibracao = round(max(0, min(1, self.vib_base + vib_var)), 2)
        rpm = int(max(1000, min(2500, self.rpm_base + rpm_var)))
        
        # Muda cenário ocasionalmente
        if self.contador % 20 == 0:
            self._mudar_cenario()
            
        return {
            'id': str(uuid.uuid4()),
            'maquina_id': self.info['id'],
            'temperatura': temperatura,
            'vibracao': vibracao,
            'rpm': rpm,
            'timestamp': datetime.now().isoformat()
        }
    
    def _mudar_cenario(self):
        """Muda cenário ocasionalmente para simular condições reais"""
        cenarios = ['normal', 'aquecendo', 'normal', 'normal']  # Normal mais provável
        novo_cenario = random.choice(cenarios)
        
        if novo_cenario != self.info['cenario']:
            self.info['cenario'] = novo_cenario
            if novo_cenario == 'normal':
                self.tendencia_temp = 0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[OK] Simulador conectado ao broker {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"[ERRO] Falha na conexão. Código: {rc}")

def simular_maquina(maquina_info, client):
    """Thread para simular uma máquina específica"""
    simulador = SimuladorMaquina(maquina_info)
    
    while True:
        try:
            leitura = simulador.gerar_leitura()
            topico = f"{TOPICO_BASE}/{maquina_info['id']}/leitura"
            payload = json.dumps(leitura)
            
            result = client.publish(topico, payload)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            status = "CRITICO" if leitura['temperatura'] > 90 else "ATENCAO" if leitura['temperatura'] > 85 else "OK"
            
            if result.rc == 0:
                print(f"[{timestamp}] [{status}] {maquina_info['id']} ({maquina_info['cenario']}) | "
                      f"Temp: {leitura['temperatura']}°C | Vib: {leitura['vibracao']} | RPM: {leitura['rpm']}")
            else:
                print(f"[{timestamp}] [ERRO] {maquina_info['id']} - Erro: {result.rc}")
                
            time.sleep(INTERVALO_ENVIO + random.uniform(-0.5, 0.5))  # Pequena variação no timing
            
        except Exception as e:
            print(f"[ERRO] Erro na máquina {maquina_info['id']}: {e}")
            time.sleep(5)

def iniciar_simulador():
    """Inicia simulador multi-máquinas"""
    client = mqtt.Client(client_id="esp-simulator-multi")
    client.on_connect = on_connect
    
    try:
        print(f"[INFO] Conectando ao broker MQTT em {BROKER_HOST}:{BROKER_PORT}...")
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_start()
        
        print(f"[INFO] Iniciando simulação de {len(MAQUINAS)} máquinas")
        print(f"[INFO] Tópicos: {TOPICO_BASE}/[MAQUINA_ID]/leitura")
        print(f"[INFO] Intervalo base: {INTERVALO_ENVIO}s (com variação)")
        print("-" * 80)
        
        # Exibe info das máquinas
        for maq in MAQUINAS:
            print(f"[MAQUINA] {maq['id']} - {maq['modelo']} - Op: {maq['operario']} - Cenário: {maq['cenario']}")
        print("-" * 80)
        
        # Inicia thread para cada máquina
        threads = []
        for maquina in MAQUINAS:
            thread = threading.Thread(target=simular_maquina, args=(maquina, client))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Aguarda interrupção
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n" + "-" * 80)
        print("[INFO] Simulador interrompido pelo usuário")
    except ConnectionRefusedError:
        print("[ERRO] Não foi possível conectar ao broker MQTT")
        print("       Certifique-se de que o broker está rodando em localhost:1883")
    except Exception as e:
        print(f"[ERRO] {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[INFO] Simulador finalizado")

if __name__ == '__main__':
    iniciar_simulador()