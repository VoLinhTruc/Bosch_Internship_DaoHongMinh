import can

REQ_ID = 0x123

bus = can.Bus(
    interface="vector",
    channel=0,
    bitrate=500000,
    app_name=None, 
)

# Single-frame ISO-TP request carrying UDS payload: 22 F1 93
msg = can.Message(
    arbitration_id=REQ_ID,
    is_extended_id=False,
    data=[0x03, 0x22, 0xF1, 0x93],
)

try:
    bus.send(msg, timeout=1.0)
    print(f"Sent: ID=0x{msg.arbitration_id:X}, data={[hex(b) for b in msg.data]}")
    rx = bus.recv(timeout=2.0)
    print(rx.data)
finally:
    bus.shutdown()