import can
from can.interfaces.vector import get_channel_configs

test_bus = can.Bus(
            interface='vector', 
            channel=0,
            receive_own_messages=False,
            fd=True,
            bitrate=500_000,
            data_bitrate=2_000_000,
            # Arbitration-rate bit timing
            sjw_abr=16,
            tseg1_abr=63,
            tseg2_abr=16,
            sam_abr=1,
            # Data-rate bit timing
            sjw_dbr=8,
            tseg1_dbr=31,
            tseg2_dbr=8,
            app_name=None,
        )

try:
    while True:
        message = test_bus.recv(timeout=1)
        if message:
            # if message.arbitration_id == 0x428 or message.arbitration_id == 0x427:
            if True:
                print(f"Received: {message}")
except KeyboardInterrupt:
    print("\nReceiving stopped")
finally:
    test_bus.shutdown()

