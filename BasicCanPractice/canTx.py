import can

ID = 0x123

bus = can.Bus(
    interface="vector",
    channel=0,
    bitrate=500000,
    app_name=None
)

msg = can.Message(
    arbitration_id=ID,
    data=[1, 2, 3, 4],
    is_extended_id=False,
)

try:
    bus.send(msg, timeout=1.0)
    print(f"Sent on {bus.channel_info}: ID=0x{msg.arbitration_id:X}, data={list(msg.data)}")
    rx = bus.recv(timeout=10.0)

    if rx is None:
        print("Channel 3: no response received")
    else:
        print(f"Channel 3 received: ID=0x{rx.arbitration_id:X}, data={list(rx.data)}")
    
finally:
    bus.shutdown()