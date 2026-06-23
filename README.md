# Open Telemetry Laboratory

## Lab 01 — Communication Between Two Towers

A beginner-friendly networking project that demonstrates how configuration data becomes a network packet.

This project simulates a very small telemetry system consisting of **two software towers**:

- **Control Tower** – A Flask web application where a user edits observation parameters.
- **Radio Tower** – A UDP server that receives those parameters, decodes them, and sends a confirmation back.

Although this project uses two programs running on the same computer, it demonstrates many of the same software concepts used in scientific instruments, satellite ground stations, telemetry systems, and radio astronomy pipelines.

---

# Why this project?

Modern scientific instruments rarely work by simply reading a file.

Instead, information moves through a pipeline:

```
Human Configuration
        │
        ▼
YAML Configuration File
        │
        ▼
Python Dictionary
        │
        ▼
Flask Web Interface
        │
        ▼
User Validation
        │
        ▼
JSON Packet
        │
        ▼
Serialized Bytes
        │
        ▼
UDP Network Packet
        │
        ▼
Receiving Tower
        │
        ▼
Confirmation Packet
```

This repository demonstrates each of those steps independently so they can be understood before introducing real radios, SDR hardware, or satellite communications.

---

# What you'll learn

By completing this lab you will gain hands-on experience with:

- YAML configuration files
- Python dictionaries
- Flask web applications
- HTML forms
- Input validation
- JSON
- Serialization
- UDP sockets
- Client/server networking
- Packet acknowledgements

These concepts are foundational to many areas of software engineering including:

- Scientific computing
- Telemetry systems
- Radio astronomy
- Ground stations
- Satellite operations
- Network programming
- Data engineering

---

# Repository Structure

```
.
├── control_tower.py                 # Flask Control Tower
├── radio_tower.py               # UDP Radio Tower
├── config.yaml            # Human-editable configuration
├── requirements.txt
├── exports/               # Exported JSON packets
└── templates/
    └── index.html
```

---

# Project Workflow

The complete workflow is:

```
config.yaml
        │
        ▼
Python Dictionary
        │
        ▼
HTML Form
        │
        ▼
User Input
        │
        ▼
Validation
        │
        ▼
JSON Export
        │
        ▼
JSON Serialization
        │
        ▼
UDP Packet
        │
        ▼
Receiving Tower
        │
        ▼
Confirmation Packet
```

---

# Requirements

- Python 3.11 or newer
- Git

---

# Installation

Clone the repository.

```bash
git clone https://github.com/kevinkell-y/two-towers.git
```

Enter the project directory.

```bash
cd two-towers
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the virtual environment.

### Linux / macOS / WSL

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Install the required packages.

```bash
pip install -r requirements.txt
```

---

# Running the project

Open **two terminal windows**.

## Terminal 1

Start the Radio Tower.

```bash
python radio_tower.py
```

You should see something similar to:

```
Radio Tower Online
Listening on udp://127.0.0.1:9009
```

---

## Terminal 2

Start the Flask Control Tower.

```bash
python control_tower.py
```

You should see:

```
Running on http://127.0.0.1:5000
```

Open your browser and navigate to:

```
http://127.0.0.1:5000
```

---

# Using the application

1. Modify any of the observation parameters.
2. Click **Send Packet**.
3. The application will:

- validate the input
- export a JSON packet
- serialize the packet
- transmit it over UDP
- receive a confirmation
- display the confirmation in the browser

The exported packet will also be written to the `exports/` directory.

---

# Why JSON?

This project intentionally exports packets as JSON instead of Python's `pickle` format.

JSON was chosen because it is:

- Human-readable
- Language-independent
- Easy to inspect
- Compatible with JavaScript
- Widely used by APIs and telemetry systems
- Safe to exchange between applications

Python's `pickle` format is useful for Python-only applications but is intentionally not used here because it is not portable and should not be used with untrusted data.

---

# Future Labs

This repository is the first project in the **Open Telemetry Laboratory** series.

Planned future labs include:

- Lab 02 — Packet Serialization
- Lab 03 — Telemetry Logging
- Lab 04 — Ground Station
- Lab 05 — Hydrogen Line Radio Astronomy
- Lab 06 — Open Telemetry Dashboard
- Lab 07 — Mission Control Visualization (Blender)

Each lab builds directly upon the previous one, gradually evolving from local UDP communication to real scientific telemetry pipelines.

---

# License

MIT License
