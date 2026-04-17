import can

ID = 0x123

def main():
    
    bus = can.Bus(
        interface="vector",
        channel=1,
        bitrate=500000,
        app_name=None
    )

    while True:
        rx = bus.recv(timeout=10.0)

        if rx is None:
            print("Channel 4: no message received, still waiting...")
            continue

        print(f"channel 4 received: ID=0x{rx.arbitration_id:X}, data={list(rx.data)}")

        response = can.Message(
            arbitration_id=ID,
            data=[9, 8, 7, 6],
            is_extended_id=False
        )

        try:
            bus.send(response)
            print(f"channel 4 sent: ID=0x{response.arbitration_id:X}, data={list(response.data)}")
        except can.CanError as e:
            print(f"channel 4 send failed: {e}")

        break

    bus.shutdown()


if __name__ == "__main__":
    main()