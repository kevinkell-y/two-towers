"""
===========================================================================
Project : Lab 01 - Communication Between Two Towers
File    : radio_tower.py
Author  : Kevin Kelly
Created : 2026-06-22
Version : 0.1.0

Description
-----------
UDP telemetry tower for receiving, decoding, validating, and acknowledging
incoming JSON packets.

This program represents the "receiving tower" in the Two Towers project.
It listens continuously for UDP packets, converts incoming bytes into
Python dictionaries, prints the received packet to the console, and
responds with a confirmation packet indicating whether the transmission
was successful.

In future projects, this program will evolve into a telemetry ground
station capable of receiving SDR, radio astronomy, and satellite data.

Workflow
--------
Receive UDP Bytes
→ Decode UTF-8
→ Parse JSON
→ Python Dictionary
→ Validate Packet
→ Build Reply Packet
→ Serialize JSON
→ Encode UTF-8
→ Send UDP Confirmation

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

# ============================================================
# Network Configuration
# ============================================================

# The tower listens only on the local computer (localhost).
# Future versions may listen on a LAN or public network.
HOST = "127.0.0.1"

# UDP port where incoming telemetry packets will be received.
PORT = 9009


# ============================================================
# Main UDP Tower
# ============================================================

def main() -> None:
    """
    Start the UDP telemetry tower.

    This function creates a UDP socket, binds it to the configured host
    and port, and then waits forever for incoming packets.

    Every received packet follows this workflow:

        UDP bytes
        → UTF-8 string
        → JSON
        → Python dictionary

    If decoding succeeds, a confirmation packet is created and sent back
    to the sender.

    If decoding fails, an error packet is returned instead.

    Returns
    -------
    None
    """

    # Create a UDP socket.
    #
    # AF_INET
    #     IPv4 Internet addressing.
    #
    # SOCK_DGRAM
    #     UDP datagram socket (connectionless communication).
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind this socket to the configured network address so it begins
    # listening for incoming UDP packets.
    sock.bind((HOST, PORT))

    print("=" * 60)
    print("Radio Tower Online")
    print(f"Listening on udp://{HOST}:{PORT}")
    print("=" * 60)

    # Run forever until the program is stopped.
    while True:

        # Wait for an incoming UDP packet.
        #
        # recvfrom() returns:
        #
        # data
        #     Raw packet bytes.
        #
        # address
        #     IP address and port number of the sender.
        data, address = sock.recvfrom(4096)

        print("\nIncoming transmission...")
        print(f"Sender: {address}")

        try:

            # Incoming UDP packets are bytes.
            #
            # Step 1:
            # Convert bytes into a UTF-8 string.
            #
            # Step 2:
            # Parse the JSON string into a Python dictionary.
            packet = json.loads(data.decode("utf-8"))

            print("Packet successfully decoded.")
            print(packet)

            # Build a confirmation packet.
            #
            # Notice that we are constructing another Python dictionary.
            # This dictionary will later be serialized into JSON and sent
            # back across the network.
            reply = {
                "ok": True,
                "message": "Message went through!",
                "packet_type": packet.get("type"),
            }

        except json.JSONDecodeError as error:

            # If the incoming packet cannot be decoded as JSON,
            # return a failure response instead.
            reply = {
                "ok": False,
                "message": str(error),
            }

        # Convert the reply dictionary into:
        #
        # Python dictionary
        # → JSON string
        # → UTF-8 bytes
        #
        # before sending it over UDP.
        sock.sendto(
            json.dumps(reply).encode("utf-8"),
            address,
        )

        print("Confirmation sent.")


# ============================================================
# Development Entry Point
# ============================================================

if __name__ == "__main__":
    main()