from anchor_keyexchange import AnchorKeyExchangeClient

client = AnchorKeyExchangeClient.from_json("example_config.json")
message, secoc_path = client.run_keyexchange()
print(message)
print("SecOC key file:", secoc_path)
