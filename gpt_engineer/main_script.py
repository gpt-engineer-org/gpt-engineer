import argparse
import signal
from gpt_engineer import AI

# Global flag for whether the continuous mode should keep running
keep_running = True

def signal_handler(signal, frame):
    """Handle the signal for stopping the continuous mode."""
    global keep_running
    keep_running = False

def main():
    """Main function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--continuous', action='store_true', help='Enable continuous mode')
    args = parser.parse_args()

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Create AI instance
    ai = AI()

    # Run in continuous mode
    if args.continuous:
        while keep_running:
            ai.run()

if __name__ == '__main__':
    main()
