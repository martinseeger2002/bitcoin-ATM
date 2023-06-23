import subprocess
#from dogecoind_script import start_dogecoind
from dogecoin_price import get_dogecoin_price
from dogecoin_sync import get_dogecoin_sync_percentage
from qr_code_reader import read_qr_code


def print_results():
    with open('pulse_count.txt', 'r') as file:
        pulse_count = file.read()
    with open('qr_code_result.txt', 'r') as file:
        qr_code_result = file.read()
        
    #dogeCoreStatus = start_dogecoind()
    price = get_dogecoin_price()
    sync_percentage = get_dogecoin_sync_percentage()

    print(f"Pulse Count: {pulse_count}")
    print(f"QR Code Result: {qr_code_result}")
    #print(f"Doge status {dogeCoreStatus}")
    print(f"Doge price {price}")
    print(f"Doge sync status {sync_percentage}")

def calculate_doge_to_send():
    with open('pulse_count.txt', 'r') as file:
        pulse_count = int(file.read())
    price = get_dogecoin_price()
    fee_rate = 0.15  # Adjust the fee rate as needed

    doge_to_send = pulse_count / price - (pulse_count / price * fee_rate)
    return doge_to_send

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
    print("5. Exit")

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
        break
    else:
        print("Invalid choice. Please try again.")
