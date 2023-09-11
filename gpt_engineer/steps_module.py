import os
import sys
from gpt_4_32k_model import GPTModel
from code_generation import CodeGeneration
from debugging import Debugging
from testing import Testing

class ContinuousOperation:
    def __init__(self):
        self.model = GPTModel()
        self.code_gen = CodeGeneration()
        self.debug = Debugging()
        self.test = Testing()

    def run(self):
        iteration = 0
        while True:
            try:
                iteration += 1
                print(f"Starting iteration {iteration}")
                code = self.code_gen.generate(self.model)
                debugged_code = self.debug.debug(code)
                test_result = self.test.run(debugged_code)
                if test_result.passed:
                    print("Test passed. Continuing with next iteration.")
                else:
                    print("Test failed. Fixing errors and trying again.")
                    self.code_gen.learn_from_errors(test_result.errors)
            except KeyboardInterrupt:
                print("User interrupted. Stopping continuous operation.")
                sys.exit(0)
