import socket
import asyncio

event = asyncio.Queue()
port = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
port.bind(('192.168.1.235', 20514))
def receive_packet():
    return port.recv(4096)
async def monitor():
    while True:
        data = await asyncio.to_thread(receive_packet)
        if "DHCPACK" in data.decode():
            assoc = data.decode().split("DHCPACK(br-lan) ")[1]
            assoc = assoc.split()
            if len(assoc) == 3:
                asees = {
                    "IP": assoc[0],
                    "MAC": assoc[1],
                    "NAME": assoc[2]
                }
                await event.put(asees)
            else:
                asees = {
                        "IP": assoc[0],
                        "MAC": assoc[1],
                        "NAME": None
                    }
                await event.put(asees)
