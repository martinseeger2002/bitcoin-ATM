from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def check_dogecoin():
    rpc_username = 'dogecoinatm'
    rpc_password = 'veracity31'

    try:
        rpc_connection = AuthServiceProxy(f'http://{rpc_username}:{rpc_password}@localhost:22555')
        print("Connection successful")
        info = rpc_connection.getinfo()
        print("Retrieved Dogecoin Core information")
        if 'version' in info:
            return f"Dogecoin Core version: {info['version']} (running)"
        else:
            print("Version information not available")
    except (ConnectionRefusedError, JSONRPCException) as e:
        print(f"Connection error: {e}")

    return "Dogecoin Core is not running"

if __name__ == "__main__":
    dogecoin_status = check_dogecoin()
    print(dogecoin_status)
