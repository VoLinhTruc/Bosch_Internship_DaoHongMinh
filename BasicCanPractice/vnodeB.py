import can

CHANNEL = "239.74.74.74"   
PORT = 43113

REQUEST_ID = 0x100
RESPONSE_ID = 0x101


def main():
    bus = can.Bus(
        interface="udp_multicast",
        channel=CHANNEL,
        port=PORT
    )

    print("Node B started")
    print("Node B waiting for request...")

    while True:
        msg = bus.recv(timeout=10.0)

        if msg is None:
            print("Node B: no message received, still waiting...")
            continue

        print(f"Node B received: ID=0x{msg.arbitration_id:X}, data={list(msg.data)}")

        if msg.arbitration_id == REQUEST_ID:
            response = can.Message(
                arbitration_id=RESPONSE_ID,
                data=[9, 8, 7, 6],
                is_extended_id=False
            )

            try:
                bus.send(response)
                print(f"Node B sent: ID=0x{response.arbitration_id:X}, data={list(response.data)}")
            except can.CanError as e:
                print(f"Node B send failed: {e}")

            break

    bus.shutdown()


if __name__ == "__main__":
    main()