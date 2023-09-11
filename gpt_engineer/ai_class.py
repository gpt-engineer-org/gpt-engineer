import os
import signal
from steps import Steps

class AI:
    def __init__(self):
        self.continuous_mode = False
        self.steps = Steps()

    def start_continuous_mode(self):
        self.continuous_mode = True
        while self.continuous_mode:
            try:
                # Execute the code generation, debugging, and testing
                self.steps.execute()
            except Exception as e:
                print(f"Error: {e}")
                continue

    def stop_continuous_mode(self):
        self.continuous_mode = False

    def signal_handler(self, signal, frame):
        print('Stopping continuous mode...')
        self.stop_continuous_mode()

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.start_continuous_mode()
