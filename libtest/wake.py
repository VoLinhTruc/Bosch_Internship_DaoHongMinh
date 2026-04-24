import isotp
import logging
import can
import time
import threading
from typing import Optional
from cryptography.hazmat.primitives.cmac import CMAC
from cryptography.hazmat.primitives.ciphers import algorithms

from bosch_signature_calculation import boschSigCal

# ============================================================================
# Configuration for Unlock (UDS over ISO-TP)
# ============================================================================
ADDRESS_MODE = isotp.AddressingMode.Normal_11bits
CAN_CHANNEL = 0
UNLOCK_RXID = 0x728
UNLOCK_TXID = 0x708
CANTP_PADDING = 0x55
REQUEST_SEED_SUBFCN = 0x61
SEND_KEY_SUBFCN = 0x62


# ============================================================================
# Configuration for Tsync (CAN channel 1)
# ============================================================================
TSYNC_ID = 0x50
TSYNC_KEY = bytes(16)  # 16 bytes of 0x00 for AES-CMAC

# ============================================================================
# Configuration for SysCtrl (CAN channel 1)
# ============================================================================
SYSCTRL_ID = 0x350
SYSCTRL_KEY = bytes(16)  # 16 bytes of 0x00 for AES-CMAC

# ============================================================================
# Configuration for CAN Network Management (CAN_NM) Message (CAN channel 1)
# ============================================================================
CAN_NM_MSG_ID = 0x14003800
CAN_NM_MSG_DATA = bytes([0x01, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

# ============================================================================
# Global flags for thread control
# ============================================================================
stop_messaging = threading.Event()


# ============================================================================
# Shared CAN Bus Setup
# ============================================================================
shared_bus = can.Bus(
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

addr = isotp.Address(ADDRESS_MODE, rxid=UNLOCK_RXID, txid=UNLOCK_TXID)
params = {'blocking_send': True, 'tx_padding': CANTP_PADDING}


def can_nm_sender():
    """Send CAN Network Management (CAN_NM) message on shared CAN bus every 100ms"""
    
    try:
        can_nm_msg = can.Message()
        can_nm_msg.is_rx = False
        can_nm_msg.arbitration_id = CAN_NM_MSG_ID
        can_nm_msg.is_extended_id = True
        can_nm_msg.is_fd = True
        can_nm_msg.data = CAN_NM_MSG_DATA
        can_nm_msg.dlc = len(CAN_NM_MSG_DATA)
        
        print("[CAN_NM] Sender thread started")
        
        while not stop_messaging.is_set():
            shared_bus.send(can_nm_msg)
            print(f"[CAN_NM] Message sent: ID=0x{CAN_NM_MSG_ID:X} (extended), Data={can_nm_msg.data.hex().upper()}")
            
            # Wait 100ms before sending next message
            time.sleep(0.1)
        
        print("[CAN_NM] Sender thread stopped")
        
    except Exception as e:
        print(f"[CAN_NM] Error in sender thread: {e}")

def main():
    print("\n" + "="*70)
    print("CIR PRECONDITION PROCEDURE")
    print("="*70)
    
    can_nm_thread = threading.Thread(target=can_nm_sender, daemon=False)
    can_nm_thread.start()
    # waiting for the Anchor awake
    time.sleep(0.1)



if __name__ == "__main__":
    main()
