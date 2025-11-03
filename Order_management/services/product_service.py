import requests
from config import PRODUCT_SERVICE_URL

def check_inventory(product_id,quantity):
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")
        if response.status_code == 200:
            product = response.json()
            return product['quantity'] >= quantity
        return False
    except Exception as e:
        print("Inventory check failed:", e)
        return False