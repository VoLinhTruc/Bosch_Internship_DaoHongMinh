import can
from can.interfaces.vector import get_channel_configs

def get_channel_by_name(channel_name):
    """Get channel index by name from Vector channel configs"""
    configs = get_channel_configs()
    for config in configs:
        if config.name == channel_name:
            return config.channel_index
    raise ValueError(f"Channel '{channel_name}' not found")

# Usage in your test
channel_name = 'Virtual Channel 2'
channel_index = get_channel_by_name(channel_name)
print(f"Using channel '{channel_name}' with index {channel_index}")

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

msg = can.Message()
msg.is_rx = False
msg.arbitration_id = 0x010
msg.data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
msg.dlc = 8
msg.is_extended_id = False

test_bus.send(msg)
print("Message sent")

test_bus.shutdown()