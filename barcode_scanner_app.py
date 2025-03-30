import tkinter as tk
from tkinter import Label, Button, Frame, filedialog
import cv2
from PIL import Image, ImageTk
import threading
from queue import Queue, Empty
from pyzbar.pyzbar import decode
import webbrowser

class BarcodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barcode Scanner")
        
        # Set the window size
        self.root.geometry("800x800")

        # Create a frame to organize UI elements
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Create a label to display the camera feed or snapshots
        self.label = Label(self.main_frame)
        self.label.pack(expand=True, fill=tk.BOTH)

        # Create a frame for output display
        self.output_frame = Frame(self.main_frame, bd=2, relief=tk.SOLID)
        self.output_frame.pack(pady=20, fill=tk.BOTH)

        # Label to display scanned data
        self.data_label = Label(self.output_frame, text="", font=("Helvetica", 16), wraplength=700, justify="left", fg="blue", cursor="hand2")
        self.data_label.pack(padx=10, pady=10, anchor="w")
        self.data_label.bind("<Button-1>", self.open_url)  # Bind left mouse click to open URL

        # Button to start/stop scanning
        self.scan_button = Button(self.main_frame, text="Scan Live", command=self.toggle_scan, height=2, width=20)
        self.scan_button.pack(side="bottom", pady=10)

        # Button to upload image for scanning
        self.upload_button = Button(self.main_frame, text="Upload Image", command=self.upload_image, height=2, width=20)
        self.upload_button.pack(side="bottom", pady=10)

        # Initialize variables for camera capture
        self.cap = None          # VideoCapture object
        self.running = False     # Flag to indicate if scanning is running
        self.thread = None       # Thread for capturing frames
        self.last_frame = None   # Variable to store the last captured frame
        self.frame_queue = Queue()  # Queue to store frames for main thread display

        # Bind close event to the on_closing method
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_scan(self):
        """Toggles between starting and stopping the scanning process."""
        if not self.running:
            self.start_scan()
        else:
            self.stop_scan()

    def start_scan(self):
        """Starts the barcode scanning process with live camera feed."""
        if not self.running:
            self.cap = cv2.VideoCapture(0)  # Initialize camera (0 for default camera)
            if not self.cap.isOpened():
                print("Error: Unable to open camera.")
                return
            
            self.running = True  # Set running flag to True
            self.scan_button.config(text="Stop Live Scan", bg="red")  # Change button text and color
            self.thread = threading.Thread(target=self.video_loop)  # Start thread for video loop
            self.thread.start()  # Start the thread

    def stop_scan(self):
        """Stops the barcode scanning process."""
        if self.running:
            self.running = False  # Set running flag to False to stop the scanning
            if self.thread:
                self.thread.join()   # Wait for the thread to complete
            if self.cap.isOpened():
                self.cap.release()   # Release the camera capture
            self.show_last_frame()   # Show the last captured frame in the label
            self.data_label.config(text="")  # Clear scanned data
            self.scan_button.config(text="Scan Live", bg="SystemButtonFace")  # Reset button text and color

    def show_last_frame(self):
        """Displays the last captured frame in the label."""
        if self.last_frame is not None:
            try:
                img = Image.fromarray(self.last_frame)  # Convert last frame to Image
                imgtk = ImageTk.PhotoImage(image=img)  # Convert Image to ImageTk format
                self.label.imgtk = imgtk  # Store ImageTk object in label
                self.label.configure(image=imgtk)  # Update label with new image
            except AttributeError:
                pass

    def video_loop(self):
        """Capture frames from the camera and update the display."""
        while self.running:
            ret, frame = self.cap.read()  # Read a frame from the camera
            if ret:
                self.last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Store last captured frame
                frame = self.last_frame.copy()  # Use a copy of the frame for processing
                
                # Check if a barcode is detected
                barcodes = decode(frame)
                if barcodes:
                    barcode = barcodes[0]  # Take the first detected barcode
                    x, y, w, h = barcode.rect  # Get barcode position
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Draw green rectangle around barcode
                    barcode_data = barcode.data.decode('utf-8')  # Decode barcode data
                    cv2.putText(frame, barcode_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Add text near barcode

                    # Display scanned data
                    self.data_label.config(text=f"Scanned Data: {barcode_data}")

                    # Store the URL for opening later
                    self.scanned_url = barcode_data

                    # Stop further processing after capturing one barcode
                    self.running = False
                    break
                
                # Put frame in queue for main thread display
                self.frame_queue.put(frame)

                # Schedule the next update of the live video feed
                self.root.after(30, self.update_frame)

    def update_frame(self):
        """Updates the displayed frame in the GUI."""
        try:
            frame = self.frame_queue.get_nowait()  # Get frame from the queue
            if frame is not None:
                img = Image.fromarray(frame)  # Convert frame to Image
                imgtk = ImageTk.PhotoImage(image=img)  # Convert Image to ImageTk format
                self.label.imgtk = imgtk  # Store ImageTk object in label
                self.label.configure(image=imgtk)  # Update label with new image
        except Empty:
            pass
        
        # Schedule the next update of the live video feed
        self.root.after(30, self.update_frame)

    def upload_image(self):
        """Allows user to upload an image file and perform barcode detection."""
        file_path = filedialog.askopenfilename(title="Select an image file", filetypes=[("Image files", "*.jpg;*.png;*.bmp")])
        if file_path:
            self.process_image(file_path)

    def process_image(self, file_path):
        """Processes the uploaded image for barcode detection."""
        try:
            frame = cv2.imread(file_path)  # Read image file
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            barcodes = decode(frame)  # Decode barcodes

            if barcodes:
                barcode_data = barcodes[0].data.decode('utf-8')  # Take the first detected barcode
                self.data_label.config(text=f"Scanned Data: {barcode_data}")
                self.scanned_url = barcode_data
            else:
                self.data_label.config(text="No barcode detected.")
            
            # Display the uploaded image
            img = Image.open(file_path)
            img = img.resize((640, 480))  # Resize for display
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

        except Exception as e:
            print(f"Error processing image: {e}")

    def open_url(self, event):
        """Opens the scanned URL in a web browser."""
        if hasattr(self, 'scanned_url') and self.scanned_url:
            webbrowser.open_new(self.scanned_url)

    def on_closing(self):
        """Callback function when closing the application window."""
        self.stop_scan()  # Stop the scanner if it's running
        self.root.destroy()  # Destroy the tkinter window

if __name__ == "__main__":
    root = tk.Tk()  # Create the tkinter root window
    app = BarcodeScannerApp(root)  # Initialize the BarcodeScannerApp instance
    root.mainloop()  # Start the tkinter main event loop
