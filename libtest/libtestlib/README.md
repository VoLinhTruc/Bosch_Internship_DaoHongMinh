# anchor-keyexchange

- reads `anchor_id`, `channel`, and `interface` from a JSON file
- derives UDS IDs from the anchor id:
  - `unlock_txid = 0x700 + anchor_id`
  - `unlock_rxid = 0x720 + anchor_id`
- uses a hardcoded factory private key blob
- generates a random 96-byte SecOC key at the start of the process
- writes that SecOC key to a text file after a successful exchange

## Expected JSON format

```json
{
  "anchor_id": 8,
  "channel": 0,
  "interface": "vector"
}
```

## Install

```bash
pip install .
```

## Example

```python
from anchor_keyexchange import AnchorKeyExchangeClient

client = AnchorKeyExchangeClient.from_json("anchor_config.json", verbose=True)
success, secoc_path = client.run_keyexchange()
print(success)
print(secoc_path)
```
