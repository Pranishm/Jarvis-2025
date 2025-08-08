from flask import Flask, render_template, request
import subprocess
import threading
import os
import sys

app = Flask(__name__)

def run_python_script():
    try:
        # Path to your Python script
        script_path = r"C:\Users\nithy\Jarvis-2025\run.py"
        
        # Check if file exists
        if not os.path.exists(script_path):
            return f"Error: Script not found at {script_path}"
        
        # Get Python interpreter path
        python_path = sys.executable
        
        # Get script directory
        script_dir = os.path.dirname(script_path)
        
        # Run script in new console window
        subprocess.Popen(
            [python_path, script_path],
            cwd=script_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        return "JARVIS started in new window!"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script', methods=['POST'])
def execute_script():
    # Run script in separate thread to avoid blocking server
    thread = threading.Thread(target=run_python_script)
    thread.start()
    return "Starting JARVIS..."

if __name__ == '__main__':
    app.run(debug=True)