import json
import logging
import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import typer

from gpt_engineer import steps
from gpt_engineer.ai import AI
from gpt_engineer.db import DB, DBs
from gpt_engineer.steps import STEPS

app = typer.Typer()

class GPTApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GPT App")

        # Create a text box for prompt input
        self.prompt_textbox = tk.Text(self, height=10, width=50)
        self.prompt_textbox.pack(pady=10)

        # Create a text box for log display
        self.log_textbox = tk.Text(self, height=10, width=50, state="disabled")
        self.log_textbox.pack(pady=10)

        # Create an Options tab
        self.options_tab = OptionsTab(self)
        self.options_tab.pack(pady=10)

        # Create a Run button
        self.run_button = tk.Button(self, text="Run", command=self.run_gpt)
        self.run_button.pack(pady=10)

    def run_gpt(self):
        prompt = self.prompt_textbox.get("1.0", tk.END).strip()

        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt.")
            return

        log = self.generate_log(prompt)

        self.log_textbox.config(state="normal")
        self.log_textbox.delete("1.0", tk.END)
        self.log_textbox.insert(tk.END, log)
        self.log_textbox.config(state="disabled")

    def generate_log(self, prompt):
        logging.basicConfig(level=logging.INFO)
        ai = AI(model="gpt-4", temperature=0.1)
        dbs = DBs(
            memory=DB("memory"),
            logs=DB("logs"),
            input=DB("input"),
            workspace=DB("workspace"),
            identity=DB(Path(os.path.curdir) / "identity"),
        )

        for step in STEPS[steps.Config.DEFAULT]:
            messages = step(ai, dbs)
            dbs.logs[step.__name__] = json.dumps(messages)

        return dbs.logs.get("step_name", "")

class OptionsTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Create an API Key label and entry field
        self.api_key_label = tk.Label(self, text="OpenAI API Key:")
        self.api_key_label.pack(pady=5)
        self.api_key_entry = tk.Entry(self)
        self.api_key_entry.pack(pady=5)

        # Create a button to load prompt from a text file
        self.load_prompt_button = tk.Button(
            self,
            text="Load Prompt from File",
            command=self.load_prompt_from_file
        )
        self.load_prompt_button.pack(pady=5)

    def load_prompt_from_file(self):
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title="Select Prompt File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )

        if file_path:
            with open(file_path, "r") as file:
                prompt = file.read()
                GPTApp.prompt_textbox.delete("1.0", tk.END)
                GPTApp.prompt_textbox.insert(tk.END, prompt)

def main():
    GPTApp().mainloop()

if __name__ == "__main__":
    main()
