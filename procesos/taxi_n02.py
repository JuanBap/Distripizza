import zmq
import time
import random
import json


def mover_taxi(id_taxi, grid_size, velocidad, max_servicios):
    context = zmq.Context()

    # Publisher para enviar posiciones
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect(f"tcp://localhost:5555")

    # REP para recibir servicios
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind(f"tcp://*:556{id_taxi}")
    time.sleep(1)

    # Posición inicial del taxi
    x, y = random.randint(0, grid_size[0] - 1), random.randint(0, grid_size[1] - 1)
    servicios_realizados = 0

    # Poller para manejar el tiempo de espera de los servicios
    poller = zmq.Poller()
    poller.register(rep_socket, zmq.POLLIN)

    while servicios_realizados < max_servicios:
        # Enviar la posición actual en formato JSON
        taxi_posicion = {"x": x, "y": y}
        mensaje = json.dumps(taxi_posicion)
        pub_socket.send_string(f"Taxi {id_taxi} {mensaje}")
        print(f"Enviado: Taxi {id_taxi} {mensaje}")

        # Esperar un servicio (poller para manejar el tiempo de espera)
        socks = dict(poller.poll(1000))  # Esperar hasta 1 segundo para recibir un servicio

        if socks.get(rep_socket) == zmq.POLLIN:
            print("Datos disponibles para recibir en el taxi.")
            servicio = rep_socket.recv_string()
            print(f"Recibido servicio: {servicio}")
            rep_socket.send_string(f"Taxi {id_taxi} aceptando servicio")
            servicios_realizados += 1

            # Simular 30 minutos de servicio (equivalente a 15 segundos)
            print(f"Taxi {id_taxi} ocupado realizando servicio... (30 minutos simulados)")
            time.sleep(15)  # Simulación de 30 minutos
            print(f"Taxi {id_taxi} ha terminado el servicio.")
        else:
            print("No se ha recibido ningún servicio en este ciclo.")

        # Mover el taxi en la cuadrícula (movimiento bidireccional)
        x, y = mover_taxi_en_grilla(x, y, grid_size, velocidad)

        # Simular el tiempo de espera entre movimientos (5 segundos)
        time.sleep(5)

    print(f"Taxi {id_taxi} ha completado los {max_servicios} servicios.")
    pub_socket.close()
    rep_socket.close()
    context.term()


# Actualización para mover el taxi en ambas direcciones
def mover_taxi_en_grilla(x, y, grid_size, velocidad):
    movimiento = random.choice(['vertical', 'horizontal'])

    if movimiento == 'vertical':
        direccion = random.choice([-1, 1])  # Elige moverse hacia arriba (-1) o hacia abajo (1)
        x = max(0, min(x + direccion * velocidad, grid_size[0] - 1))
    else:
        direccion = random.choice([-1, 1])  # Elige moverse hacia la izquierda (-1) o hacia la derecha (1)
        y = max(0, min(y + direccion * velocidad, grid_size[1] - 1))

    return x, y


if __name__ == "__main__":
    id_taxi = 2  # Identificador del taxi
    grid_size = (10, 10)  # Tamaño de la cuadrícula NxM
    velocidad = 1  # Velocidad del taxi (en km/h)
    max_servicios = 3  # Número máximo de servicios
    mover_taxi(id_taxi, grid_size, velocidad, max_servicios)
