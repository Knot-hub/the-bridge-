import secrets

def generate_flutterwave_link(lead_id: int, amount: float):
    # This is a mock implementation of the Flutterwave Standard Payment Link API
    # In a real scenario, you would call https://api.flutterwave.com/v3/payments
    
    # Simulate a unique transaction reference
    tx_ref = f"BL-L{lead_id}-{secrets.token_hex(4)}"
    
    # Mock link
    # In reality, the API returns a 'link' property in the data object
    mock_link = f"https/checkout.flutterwave.com/pay/the-bridge-{tx_ref}?amount={amount}&currency=USD"
    
    return {
        "status": "success",
        "link": mock_link,
        "tx_ref": tx_ref
    }

def verify_webhook_signature(signature: str, secret_hash: str):
    # Verify the 'verif-hash' header sent by Flutterwave
    # flutterwave_secret_hash should be stored in env variables
    return signature == secret_hash
