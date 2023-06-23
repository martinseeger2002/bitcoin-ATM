import picamera
from pyzbar import pyzbar
from PIL import Image

def read_qr_code():
    # Initialize the Pi camera
    with picamera.PiCamera() as camera:
        # Capture a frame
        camera.start_preview()
        camera.capture('qr_code.jpg')
        camera.stop_preview()

    # Open the captured image
    image = Image.open('qr_code.jpg')

    # Scan the QR code from the image
    codes = pyzbar.decode(image)

    # Extract and print the cryptocurrency address from the QR code
    if codes:
        qr_data = codes[0].data.decode('utf-8')
        if qr_data.startswith('D'):
            dogecoin_address = qr_data
            print(f"Dogecoin Address: {dogecoin_address}")
        elif qr_data.startswith(('1', '3', 'bc1')):
            bitcoin_address = qr_data
            print(f"Bitcoin Address: {bitcoin_address}")
        elif qr_data.startswith(('l', 'm')):
            litecoin_address = qr_data
            print(f"Litecoin Address: {litecoin_address}")
        else:
            print("QR code does not contain a supported cryptocurrency address.")
    else:
        print("No QR code found.")

    # Save QR code result to a txt file
    with open('qr_code_result.txt', 'w') as file:
        file.write(qr_data)

read_qr_code()
