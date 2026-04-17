import time
import can

CHANNEL = "239.74.74.74"
PORT = 43113

REQUEST_ID = 0x100
RESPONSE_ID = 0x101

def main():
    bus = can.Bus(
        interface="udp_multicast",
        channel=CHANNEL,
        port=PORT,
        can_filters=[
            {"can_id": RESPONSE_ID, "can_mask": 0x7FF, "extended": False}
        ],
    )

    print("Node A started")
    time.sleep(1.0)

    msg = can.Message(
        arbitration_id=REQUEST_ID,
        data=[1, 2, 3, 4],
        is_extended_id=False
    )

    bus.send(msg)
    print(f"Node A sent: ID=0x{msg.arbitration_id:X}, data={list(msg.data)}")

    print("Node A waiting for response...")
    reply = bus.recv(timeout=5.0)

    if reply is None:
        print("Node A: timeout")
    else:
        print(f"Node A received: ID=0x{reply.arbitration_id:X}, data={list(reply.data)}")

    bus.shutdown()

if __name__ == "__main__":
    main()