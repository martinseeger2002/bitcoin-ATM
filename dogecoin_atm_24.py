import picamera
from PIL import Image
from pyzbar import pyzbar
import tkinter as tk
import RPi.GPIO as GPIO
import time
import requests
from threading import Thread
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from tkinter import messagebox


# Disable GPIO warnings
GPIO.setwarnings(False)

# Set GPIO mode and pin numbers
GPIO.setmode(GPIO.BCM)
pulse_pin = 17
trigger_pin = 27

# Initialize pulse counter
pulse_count = 0
counting = False
stop_flag = False  # Flag to signal stopping the counting thread

# Define callback function for pulse detection with debounce
def count_pulses(channel):
    global pulse_count
    pulse_count += 1

# Set up GPIO pins for input and output
GPIO.setup(pulse_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(trigger_pin, GPIO.OUT)

# Turn on trigger pin initially
GPIO.output(trigger_pin, GPIO.LOW)  # Set the trigger pin to a low state initially

# Add event detection on rising edge with debounce time
debounce_time = 0.05  # Adjust this value as needed
GPIO.add_event_detect(pulse_pin, GPIO.RISING, callback=count_pulses, bouncetime=int(debounce_time * 1000))

# Function to stop the pulse counter
def stop_counter():
    global counting, stop_flag
    counting = False
    stop_flag = True
    GPIO.output(trigger_pin, GPIO.LOW)  # Disable the trigger pin

def calculate_doge_to_send():
    fee_rate = 0.15  # Adjust the fee rate as needed
    price = get_dogecoin_price()
    
    if price is not None:
        doge_to_send = pulse_count / price - (pulse_count / price * fee_rate)
        rounded_doge_to_send = round(doge_to_send, 8)
        return rounded_doge_to_send
    else:
        return 0

def send_doge_transaction(passphrase):
    rpc_port = 22255
    local_host = '192.168.1.132'
    rpc_user = 'dogecoinatm'
    rpc_password = 'veracity31'

    try:
        rpc_connection = AuthServiceProxy(f'http://{rpc_user}:{rpc_password}@{local_host}:{rpc_port}')
        unlocked = rpc_connection.walletpassphrase(passphrase, 10)  # Unlock the wallet for 10 seconds
        if unlocked:
            doge_to_send = calculate_doge_to_send()
            address = read_qr_code()
            
            if address:
                try:
                    txid = rpc_connection.sendtoaddress(address, doge_to_send)
                    pulse_count = 0  # Reset pulse count
                    final_count = 0  # Reset the final count
                    update_balance()  # Update Dogecoin balance
                    messagebox.showinfo("Transaction Successful", f"Transaction sent successfully.\nTXID: {txid}")
                except JSONRPCException as e:
                    messagebox.showerror("Transaction Failed", str(e))
            else:
                messagebox.showerror("Transaction Failed", "No QR code found.")
        else:
            messagebox.showerror("Wallet Unlock Failed", "Failed to unlock the wallet.")
    except (ConnectionRefusedError, JSONRPCException) as e:
        messagebox.showerror("Connection Error", str(e))

# Function to get Dogecoin price
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

# Function to get Dogecoin balance
def get_dogecoin_balance():
    rpc_port = 22255
    local_host = '192.168.1.132'
    rpc_user = 'dogecoinatm'
    rpc_password = 'veracity31'

    try:
        rpc_connection = AuthServiceProxy(f'http://{rpc_user}:{rpc_password}@{local_host}:{rpc_port}')
        balance = rpc_connection.getbalance()
        return balance
    except (ConnectionRefusedError, JSONRPCException) as e:
        print(f"Connection error: {e}")

    return 0

# Function to read QR code
def read_qr_code():
    qr_data = None  # Initialize qr_data variable
    
    # Initialize the Pi camera
    with picamera.PiCamera() as camera:
        # Capture a frame
        camera.start_preview()
        time.sleep(4)
        camera.capture('qr_code.jpg')
        camera.stop_preview()

    # Open the captured image
    image = Image.open('qr_code.jpg')

    # Scan the QR code from the image
    codes = pyzbar.decode(image)

    # Extract and return the QR code data
    if codes:
        qr_data = codes[0].data.decode('utf-8')
    
    return qr_data

# GUI script
class PulseCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.title("Pulse Counter")
        self.root.geometry("600x1020")

        self.running_count = 0
        self.final_count = 0
        self.counting_thread = None
        
        self.running_count_label = tk.Label(self.root, text="Counting Dollars: 0", font=("Arial", 16))
        self.running_count_label.pack(pady=20)
        
        self.final_count_label = tk.Label(self.root, text="Total Dollars Inserted: 0", font=("Arial", 16))
        self.final_count_label.pack(pady=20)
        
        self.doge_price_label = tk.Label(self.root, text="Doge Price: -", font=("Arial", 16))
        self.doge_price_label.pack(pady=20)
        
        self.doge_balance_label = tk.Label(self.root, text="Available Doge Balance: -", font=("Arial", 16))
        self.doge_balance_label.pack(pady=20)
        
        
        self.warning_label = tk.Label(self.root, text="Warning:\nDo not insert more cash than the Available Doge Balance.\n\nCheck to ensure the Dogecoin address is correct.\n\nThere is a 15% charge for purchasing Doge.",font=("Arial", 16), fg="red")
        self.warning_label.pack(pady=20)
        
        
        
        self.qr_code_label = tk.Label(self.root, text="Dogecoin Address:", font=("Arial", 16))
        self.qr_code_label.pack(pady=20)
        
        self.doge_to_send_label = tk.Label(self.root, text="Doge to Send: 0", font=("Arial", 16))
        self.doge_to_send_label.pack(pady=20)
        
        self.scan_button = tk.Button(self.root, text="Scan Address", font=("Arial", 20), command=self.scan_address)
        self.scan_button.pack(pady=20)
        
        insert_button = tk.Button(self.root, text="Insert Cash", font=("Arial", 20), command=self.start_count)
        insert_button.pack(pady=20)
        
        finish_button = tk.Button(self.root, text="Finished Inserting Cash", font=("Arial", 20), command=self.stop_count)
        finish_button.pack(pady=20)
        
        send_button = tk.Button(self.root, text="Send Doge", font=("Arial", 20), command=lambda: self.send_doge("doge from the wind and do good everyday"))
        send_button.pack(pady=20)
        
        
        self.update_doge_price()  # Update Doge price immediately
        self.update_doge_balance()  # Update Doge balance immediately
        self.schedule_doge_price_update()  # Schedule periodic Doge price updates
    
    def scan_address(self):
        qr_data = read_qr_code()
        
        if qr_data:
            self.qr_code_label.config(text=f"Doge Address: {qr_data}")
        else:
            self.qr_code_label.config(text="No QR code found.")
    
    def start_count(self):
        global counting, stop_flag
        
        if not counting:
            counting = True
            stop_flag = False
            GPIO.output(trigger_pin, GPIO.HIGH)  # Enable the trigger pin
            self.counting_thread = Thread(target=self.update_count)
            self.counting_thread.start()
    
    def update_count(self):
        global pulse_count, counting, stop_flag
        
        while counting and not stop_flag:
            current_count = pulse_count
            self.root.after(100, self.update_running_count, current_count)
            time.sleep(0.1)  # Adjust the delay as needed
        
        self.final_count = pulse_count
        self.root.after(100, self.update_final_count, self.final_count)
        self.update_doge_to_send()
    
    def update_running_count(self, current_count):
        self.running_count_label.config(text=f"Counting Dollars: {current_count}")
    
    def update_final_count(self, final_count):
        self.final_count_label.config(text=f"Total Dollars Inserted: {final_count}")
    
    def stop_count(self):
        global counting, stop_flag
        
        if counting:
            counting = False
            stop_flag = True
            GPIO.output(trigger_pin, GPIO.LOW)  # Disable the trigger pin
    
    def send_doge(self, passphrase):
        rpc_port = 22255
        local_host = '192.168.1.132'
        rpc_user = 'dogecoinatm'
        rpc_password = 'veracity31'
        
        try:
            rpc_connection = AuthServiceProxy(f'http://{rpc_user}:{rpc_password}@{local_host}:{rpc_port}')
            
            # Unlock the wallet using the provided passphrase
            rpc_connection.walletpassphrase(passphrase, 30)
            
            # Send the transaction
            doge_to_send = calculate_doge_to_send()
            address = self.qr_code_label.cget("text").split(": ")[1]
            txid = rpc_connection.sendtoaddress(address, doge_to_send)
            
            # Display success message and update balances
            self.reset_count()
            self.update_doge_balance()
            self.doge_to_send_label.config(text=f"Doge to Send: 0")
            messagebox.showinfo("Success", f"Transaction successful! Transaction ID: {txid}")
        except (ConnectionRefusedError, JSONRPCException) as e:
            # Display error message
            messagebox.showerror("Error", str(e))
        finally:
            # Lock the wallet after sending the transaction
            rpc_connection.walletlock()
    
    def update_doge_price(self):
        price = get_dogecoin_price()
        if price is not None:
            self.doge_price_label.config(text=f"Doge Price: {price} USD")
        else:
            self.doge_price_label.config(text="Doge Price: -")
        self.root.after(1200000, self.update_doge_price)  # Update every 20 minutes (1200000 milliseconds)
    
    def update_doge_balance(self):
        price = get_dogecoin_price()
        balance = float(get_dogecoin_balance())
        balance = round(balance * price, 2)
        self.doge_balance_label.config(text=f"Available Doge Balance: {balance} USD")
    
    def update_doge_to_send(self):
        doge_to_send = calculate_doge_to_send()
        self.doge_to_send_label.config(text=f"Doge to Send: {doge_to_send}")
    
    def reset_count(self):
        global pulse_count
        pulse_count = 0
    
    def schedule_doge_price_update(self):
        self.update_doge_price()
    
    def run(self):
        self.root.mainloop()

# Create the GUI window
root = tk.Tk()

# Create the PulseCounterGUI object and run it
gui = PulseCounterGUI(root)
gui.run()
