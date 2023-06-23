import requests

def get_dogecoin_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=dogecoin&vs_currencies=usd'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'dogecoin' in data:
            price = data['dogecoin']['usd']
            return price
        else:
            return None
    else:
        return None
