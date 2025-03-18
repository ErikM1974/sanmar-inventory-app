from flask import Flask, render_template, jsonify
import zeep
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Sanmar API credentials from environment variables
USERNAME = os.getenv("SANMAR_USERNAME")
PASSWORD = os.getenv("SANMAR_PASSWORD")
CUSTOMER_NUMBER = os.getenv("SANMAR_CUSTOMER_NUMBER")

# SOAP clients for Sanmar APIs
product_wsdl = "https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl"
inventory_wsdl = "https://ws.sanmar.com:8080/promostandards/InventoryServiceBindingV2final?WSDL"
pricing_wsdl = "https://ws.sanmar.com:8080/promostandards/PricingAndConfigurationServiceBinding?WSDL"

product_client = zeep.Client(wsdl=product_wsdl)
inventory_client = zeep.Client(wsdl=inventory_wsdl)
pricing_client = zeep.Client(wsdl=pricing_wsdl)

# Warehouse mapping
WAREHOUSES = {
    "1": "Seattle, WA", "2": "Cincinnati, OH", "3": "Dallas, TX", "4": "Reno, NV",
    "5": "Robbinsville, NJ", "6": "Jacksonville, FL", "7": "Minneapolis, MN",
    "12": "Phoenix, AZ", "31": "Richmond, VA"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product/<style>')
def product_page(style):
    # Fetch product data
    product_data = get_product_data(style)
    if not product_data:
        return "Product not found", 404

    colors = product_data["colors"]
    sizes = product_data["sizes"]
    part_id_map = product_data["part_id_map"]
    images = product_data["images"]

    inventory = get_inventory(style)
    pricing = get_pricing(style)

    return render_template('product.html', style=style, colors=colors, sizes=sizes,
                           inventory_json=json.dumps(inventory), pricing_json=json.dumps(pricing),
                           part_id_map_json=json.dumps(part_id_map), warehouses=WAREHOUSES,
                           images=images)

def get_product_data(style):
    request_data = {
        "arg0": {"style": style, "color": "", "size": ""},
        "arg1": {"sanMarCustomerNumber": CUSTOMER_NUMBER, "sanMarUserName": USERNAME,
                 "sanMarUserPassword": PASSWORD}
    }
    try:
        response = product_client.service.getProductInfoByStyleColorSize(**request_data)
        if response.errorOccured:
            return None
        colors = list(set(item.catalogColor for item in response.listResponse.productBasicInfo))
        sizes = response.listResponse.productBasicInfo[0].availableSizes.split(", ")
        part_id_map = {}
        images = {}
        for item in response.listResponse.productBasicInfo:
            color = item.catalogColor
            size = item.size
            part_id = item.uniqueKey
            if color not in part_id_map:
                part_id_map[color] = {}
            part_id_map[color][size] = part_id
            if color not in images:
                images[color] = item.colorProductImage
        return {"colors": colors, "sizes": sizes, "part_id_map": part_id_map, "images": images}
    except Exception as e:
        print(f"Error fetching product data: {e}")
        return None

def get_inventory(product_id):
    request_data = {
        "wsVersion": "2.0.0", "id": USERNAME, "password": PASSWORD, "productId": product_id
    }
    try:
        response = inventory_client.service.GetInventoryLevelsRequest(**request_data)
        inventory = {}
        for part in response["Inventory"]["PartInventoryArray"]["PartInventory"]:
            part_id = part["partId"]
            total = part["quantityAvailable"]["Quantity"]["value"]
            warehouses = {
                loc["inventoryLocationId"]: loc["inventoryLocationQuantity"]["Quantity"]["value"]
                for loc in part["InventoryLocationArray"]["InventoryLocation"]
            }
            inventory[part_id] = {"total": total, "warehouses": warehouses}
        return inventory
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return {}

def get_pricing(product_id):
    request_data = {
        "wsVersion": "1.0.0", "id": USERNAME, "password": PASSWORD, "productId": product_id,
        "currency": "USD", "fobId": "1", "priceType": "Net", "localizationCountry": "US",
        "localizationLanguage": "EN", "configurationType": "Blank"
    }
    try:
        response = pricing_client.service.GetConfigurationAndPricingRequest(**request_data)
        pricing = {}
        for part in response["Configuration"]["PartArray"]["Part"]:
            part_id = part["partId"]
            price_info = part["PartPriceArray"]["PartPrice"][0]
            pricing[part_id] = {
                "original": price_info.get("price", 0),
                "sale": price_info.get("salePrice", None),
                "program": price_info.get("incentivePrice", None),
                "case_size": 72
            }
        return pricing
    except Exception as e:
        print(f"Error fetching pricing: {e}")
        return {}

if __name__ == "__main__":
    app.run(debug=True)
