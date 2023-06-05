import requests

def test_add_new_order():
    IP = requests.get('https://api.ipify.org').content.decode('utf8')
    print(IP)
    url = f'http://{IP}:8087/add_new_order'
    order = {'name': 'ליאור', 'phone': '0505567800', 'address': 'מגדל שורשן 2', 'shipment_date': '2023-06-01T01:35', 'paid': 'שולם',\
        'delivered': 'נמסר', 'payment_method': 'מזומן', 'quantity': 2}

    response = requests.post(url, json = order)
    assert response.status_code == 200
        