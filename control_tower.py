"""
===========================================================================
Project : Lab 01 - Communication Between Two Towers
File    : control_tower.py
Author  : Kevin Kelly
Created : 2026-06-22
Version : 0.1.0

Description
-----------
Flask web application for creating, validating, exporting, serializing,
and transmitting observation-style configuration packets to a UDP telemetry
tower.

This is the control-tower side of the project. It loads human-editable YAML,
turns that YAML into a Python dictionary, uses the dictionary to build a web
form, validates user input, exports the final packet as JSON, serializes that
packet into bytes, and sends it over UDP to a second local server.

Workflow
--------
YAML
→ Python Dictionary
→ HTML Form
→ User Input
→ Validation
→ JSON Export
→ JSON Serialization
→ UDP Packet
→ Tower Confirmation

License
-------
MIT License
===========================================================================
"""

# ============================================================
# Standard Library Imports
# ============================================================

import json
import socket
import time
from pathlib import Path

# ============================================================
# Third-Party Imports
# ============================================================

import yaml
from flask import Flask, render_template, request

# ============================================================
# Flask Application Setup
# ============================================================

app = Flask(__name__)

# ============================================================
# Project Paths
# ============================================================

# Absolute path to the directory containing this file.
BASE_DIR = Path(__file__).parent

# YAML configuration file. This is the human-editable source of truth.
CONFIG_PATH = BASE_DIR / "config.yaml"

# Folder where transmitted packets are exported as JSON files.
EXPORT_DIR = BASE_DIR / "exports"

# Create the exports folder automatically if it does not already exist.
EXPORT_DIR.mkdir(exist_ok=True)


# ============================================================
# Configuration Loading
# ============================================================

def load_config() -> dict:
    """
    Load the YAML configuration file.

    Reads config.yaml from disk, parses the YAML into a Python dictionary,
    validates that the required top-level 'config' section exists, and
    returns the configuration dictionary.

    YAML is useful here because it is pleasant for humans to read and edit.
    Once loaded, the YAML becomes a normal Python dictionary that the rest
    of the program can use.

    Returns
    -------
    dict
        Parsed configuration settings from the top-level 'config' section.

    Raises
    ------
    ValueError
        If the configuration file is empty or missing the required
        top-level 'config' section.
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not data or "config" not in data:
        raise ValueError("config.yaml needs a top-level config section")

    return data["config"]


# ============================================================
# Input Parsing and Validation
# ============================================================

def parse_number(raw: str) -> int | float:
    """
    Convert a raw form value into a Python number.

    HTML form fields arrive as strings, even when the user typed a number.
    This function converts those strings into either int or float values
    so they can be validated and serialized correctly.

    Parameters
    ----------
    raw : str
        Raw text value submitted from the HTML form.

    Returns
    -------
    int | float
        Numeric version of the submitted value.

    Raises
    ------
    ValueError
        If the submitted value cannot be converted into a number.
    """
    try:
        if "." in raw:
            return float(raw)

        return int(raw)

    except ValueError:
        raise ValueError("Must be a number")


def validate_form(form: dict, output_rules: dict) -> tuple[dict, dict]:
    """
    Validate user-submitted form values against YAML-defined rules.

    The YAML file defines each output field, including its allowed minimum
    and maximum values. This function checks each submitted field against
    those rules.

    Valid values are added to the cleaned dictionary. Invalid values are
    added to the errors dictionary so the web page can display helpful
    feedback to the user.

    Parameters
    ----------
    form : dict
        Submitted form values from Flask request.form.

    output_rules : dict
        Validation rules loaded from config.yaml.

    Returns
    -------
    tuple[dict, dict]
        cleaned:
            Validated numeric values ready to be placed into a packet.

        errors:
            Error messages keyed by field name.
    """
    cleaned = {}
    errors = {}

    for key, rules in output_rules.items():
        raw = form.get(key, "").strip()

        if raw == "":
            errors[key] = "Required"
            continue

        try:
            value = parse_number(raw)

        except ValueError as error:
            errors[key] = str(error)
            continue

        if value < rules["min"]:
            errors[key] = f"Minimum is {rules['min']}"
            continue

        if value > rules["max"]:
            errors[key] = f"Maximum is {rules['max']}"
            continue

        cleaned[key] = value

    return cleaned, errors


# ============================================================
# Packet Export
# ============================================================

def export_json(packet: dict) -> str:
    """
    Export a packet dictionary as a JSON file.

    JSON is used for exported packets because it is portable, human-readable,
    JavaScript-friendly, and widely used by APIs, dashboards, logs, and
    telemetry systems.

    Parameters
    ----------
    packet : dict
        Packet data to export.

    Returns
    -------
    str
        Name of the exported JSON file.
    """
    # Use a Unix timestamp so each exported packet gets a unique filename.
    filename = f"packet_{int(time.time())}.json"
    path = EXPORT_DIR / filename

    with open(path, "w", encoding="utf-8") as file:
        json.dump(packet, file, indent=2)

    return filename


# ============================================================
# UDP Networking
# ============================================================

def send_udp(
    packet: dict,
    host: str,
    port: int,
    timeout: int | float,
) -> dict:
    """
    Serialize a packet and send it to the UDP tower.

    The packet begins as a Python dictionary. Before it can be sent over a
    network socket, it must be serialized into a string and then encoded into
    bytes.

    This function performs the following conversion:

        Python dict → JSON string → UTF-8 bytes → UDP packet

    Parameters
    ----------
    packet : dict
        Packet data to transmit.

    host : str
        IP address or hostname of the UDP tower.

    port : int
        UDP port where the tower is listening.

    timeout : int | float
        Number of seconds to wait for a reply before declaring failure.

    Returns
    -------
    dict
        Decoded JSON reply from the UDP tower, or an error dictionary if the
        tower does not respond.
    """
    # UDP sockets send bytes, not dictionaries. JSON gives us a clean,
    # cross-language packet format before encoding to bytes.
    message = json.dumps(packet).encode("utf-8")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        sock.sendto(message, (host, int(port)))

        # Wait for the tower to send back a confirmation packet.
        data, _ = sock.recvfrom(4096)

        # Convert the reply from bytes → JSON string → Python dictionary.
        return json.loads(data.decode("utf-8"))

    except socket.timeout:
        return {
            "ok": False,
            "message": "Tower did not reply",
        }

    finally:
        sock.close()


# ============================================================
# Flask Routes
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Render the main control-tower page.

    GET request:
        Load defaults from config.yaml and display the form.

    POST request:
        Read submitted form values, validate them, build a packet, export
        the packet as JSON, send the packet over UDP, and display the tower's
        confirmation response.

    Returns
    -------
    str
        Rendered HTML page.
    """
    cfg = load_config()
    output_rules = cfg["outputs"]

    # Start with default values from config.yaml.
    values = {
        key: rules["default"]
        for key, rules in output_rules.items()
    }

    errors = {}
    result = None
    exported_file = None

    if request.method == "POST":
        # Flask form values arrive as strings. Validation converts them into
        # real Python numbers before packet creation.
        values = dict(request.form)
        cleaned, errors = validate_form(request.form, output_rules)

        if not errors:
            packet = {
                "type": "hydrogen_line_observation_config",
                "format": "json",
                "created_at": time.time(),
                "outputs": cleaned,
            }

            exported_file = export_json(packet)

            result = send_udp(
                packet,
                cfg["tower_host"],
                cfg["tower_port"],
                cfg["timeout_seconds"],
            )

    return render_template(
        "index.html",
        output_rules=output_rules,
        values=values,
        errors=errors,
        result=result,
        exported_file=exported_file,
    )


# ============================================================
# Development Entry Point
# ============================================================

if __name__ == "__main__":
    # debug=True is convenient while learning because Flask reloads when
    # files change and shows helpful error pages. Turn it off for production.
    app.run(debug=True, port=5000)