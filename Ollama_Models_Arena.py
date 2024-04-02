import tkinter as tk 
from tkinter import ttk
import threading
import time
import requests
import subprocess

class LLMTesterApp:

  def get_ollama_models(self):
    result = subprocess.run(['ollama', 'list'], capture_output=True)
    lines = result.stdout.decode().splitlines()  

    models = []
    for line in lines:
      parts = line.split("\t")
      model_name = parts[0]
      models.append(model_name)

    return models

  def __init__(self, master):
    self.master = master
    self.master.title("LLM Response Time Tester")

    self.models = self.get_ollama_models()
    self.setup_ui()

  def setup_ui(self):
    
    self.output_frames = []
    self.output_texts = []
    self.model_dropdowns = []
    self.timers = []

    for i in range(4):
      frame = ttk.Frame(self.master)
      frame.grid(row=1, column=i, padx=10, pady=10)

      model_var = tk.StringVar()
      dropdown = ttk.Combobox(frame, textvariable=model_var, values=self.models)
      dropdown.grid(row=0, column=0, padx=5, pady=5)
      self.model_dropdowns.append(model_var)

      output_text = tk.Text(frame, width=30, height=15)
      output_text.grid(row=1, column=0, padx=5, pady=5)
      self.output_texts.append(output_text)

      timer_label = ttk.Label(frame, text="00:00")
      timer_label.grid(row=2, column=0, padx=5, pady=5)
      self.timers.append(timer_label)

      self.output_frames.append(frame)

    input_frame = ttk.Frame(self.master)
    input_frame.grid(row=2, columnspan=4, padx=10, pady=10)

    self.input_field = ttk.Entry(input_frame, width=100)
    self.input_field.grid(row=0, column=0, padx=5, pady=5)

    send_button = ttk.Button(input_frame, text="Send", command=self.send_request)
    send_button.grid(row=0, column=1, padx=5, pady=5)

  def send_request(self):

    request_text = self.input_field.get()

    selected_models = []
    for model_var in self.model_dropdowns:
        model = model_var.get().strip()
        selected_models.append(model)

    for model in selected_models:
        print(f"Loading model: {model}")
        subprocess.run(['ollama', 'run', model])

# Start a thread for each model to load
    threads = []
    for model in selected_models:
        thread = threading.Thread(target=run_model, args=(model,))
        threads.append(thread)
        thread.start() 

    # Join threads to wait for completion  
    for thread in threads:
        thread.join()

    # Helper function
def run_model(model):
    print(f"Loading model: {model}") 
    subprocess.run(['ollama', 'run', model])



def make_request(self, model, text, index):

    url = f"http://localhost:11434/v1/completion"
    
    data = {
      "model": model,
      "prompt": text,
      "stream": False
    }
    
    start_time = time.time()
    
    try:
      response = requests.post(url, json=data)
      data = response.json()
      output = data["response"]
      
    except Exception as e:
      output = str(e)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    self.update_ui(index, output, elapsed_time)

def update_ui(self, index, output, elapsed_time):
    timer_text = time.strftime("%M:%S", time.gmtime(elapsed_time))
    self.output_texts[index].delete('1.0', tk.END)
    self.output_texts[index].insert(tk.END, output)
    self.timers[index].config(text=timer_text)

if __name__ == "__main__":
  root = tk.Tk()
  app = LLMTesterApp(root)
  root.mainloop()
