import argparse
from steps_module import generate_code, debug_code, test_code
from gpt_4_32k_model import GPT4_32k

def continuous_mode():
    for _ in range(20):
        code = generate_code(GPT4_32k)
        debugged_code = debug_code(code)
        test_code(debugged_code)

def main():
    parser = argparse.ArgumentParser(description='GPT Engineer Continuous Mode')
    parser.add_argument('continuous', type=str, help='Enable continuous mode')
    args = parser.parse_args()

    if args.continuous:
        continuous_mode()

if __name__ == "__main__":
    main()
