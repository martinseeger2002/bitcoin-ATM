import subprocess
from dogecoin_check import check_dogecoin
from dogecoin_price import get_dogecoin_price
from dogecoin_sync import get_dogecoin_sync_percentage
from qr_code_reader import read_qr_code
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


def print_results():
    with open('pulse_count.txt', 'r') as file:
        pulse_count = file.read()
    with open('qr_code_result.txt', 'r') as file:
        qr_code_result = file.read()

    dogeCoreStatus = check_dogecoin()
    price = get_dogecoin_price()
    sync_percentage = get_dogecoin_sync_percentage()

    print(f"Pulse Count: {pulse_count}")
    print(f"QR Code Result: {qr_code_result}")
    print(f"Doge status {dogeCoreStatus}")
    print(f"Doge price {price}")
    print(f"Doge sync status {sync_percentage}")


def calculate_doge_to_send():
    with open('pulse_count.txt', 'r') as file:
        pulse_count = int(file.read())
    price = get_dogecoin_price()
    fee_rate = 0.15  # Adjust the fee rate as needed

    doge_to_send = pulse_count / price - (pulse_count / price * fee_rate)
    return doge_to_send


def send_transaction(address, doge_to_send):
    rpc_username = 'dogecoinatm'
    rpc_password = 'veracity31'

    try:
        rpc_connection = AuthServiceProxy(f'http://{rpc_username}:{rpc_password}@localhost:22555')
        transaction_id = rpc_connection.sendtoaddress(address, doge_to_send)
        print(f"Transaction sent. Transaction ID: {transaction_id}")
        with open('pulse_count.txt', 'w') as file:
            file.write('')
        with open('qr_code_result.txt', 'w') as file:
            file.write('')
    except ConnectionRefusedError:
        print("Error sending transaction: [Errno 111] Connection refused")


def pulse_counter_process():
    pulse_process = subprocess.Popen(['python', 'pulse_counter.py'])
    pulse_process.communicate()
    print_results()


def qr_code_reader_process():
    read_qr_code()
    print_results()


while True:
    print("\nMenu:")
    print("1. Start Pulse Counter")
    print("2. Start QR Code Reader")
    print("3. Print Results")
    print("4. Calculate Doge to Send")
    print("5. Send Transaction")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        pulse_counter_process()
    elif choice == "2":
        qr_code_reader_process()
    elif choice == "3":
        print_results()
    elif choice == "4":
        doge_to_send = calculate_doge_to_send()
        print(f"Doge to Send: {doge_to_send}")
    elif choice == "5":
        with open('qr_code_result.txt', 'r') as file:
            address = file.read().strip()
        doge_to_send = calculate_doge_to_send()
        if address == "":
            print("No address found in qr_code_result.txt.")
        elif doge_to_send == 0:
            print("No Doge to send.")
        else:
            send_transaction(address, doge_to_send)
    elif choice == "6":
        break
    else:
        print("Invalid choice. Please try again.")
