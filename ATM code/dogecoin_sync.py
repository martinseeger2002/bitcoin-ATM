from bitcoinrpc.authproxy import AuthServiceProxy

def get_dogecoin_sync_percentage():
    rpc_user = 'dogecoinatm'
    rpc_password = 'veracity31'
    rpc_host = 'localhost'
    rpc_port = 22555  # Adjust this to your Dogecoin RPC port

    try:
        rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}")
        sync_info = rpc_connection.getblockchaininfo()
        sync_percentage = sync_info["verificationprogress"] * 100
        sync_percentage = round(sync_percentage, 2)  # Round to two decimal places

        return sync_percentage
    except Exception as e:
        error_message = str(e)
        if "Error: -28: Loading block index" in error_message:
            return "Loading block index"
            print ("Loading block index")
        else:
            print(f"Error: {error_message}")
            return None


