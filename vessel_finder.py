import asyncio
import websockets
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

async def connect_ais_stream(mmsi_filter=None, bounding_box=None):

    subscribe_message = {
        "APIKey": "1b7af1885ca28ca99cc1a166c9a6aa5983dee696",
        "FilterMessageTypes": ["PositionReport"]
    }

    if mmsi_filter:
        subscribe_message["FiltersShipMMSI"] = mmsi_filter

    if bounding_box:
        subscribe_message["BoundingBoxes"] = [bounding_box]

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        # Assuming multiple messages can be received for bounding box query
        positions = []
        try:
            async for message_json in asyncio.wait_for(websocket, timeout=60):
                message = json.loads(message_json)
                if message["MessageType"] == "PositionReport":
                    ais_message = message['Message']['PositionReport']
                    positions.append((ais_message['Latitude'], ais_message['Longitude']))
        except asyncio.TimeoutError:
            pass

        return positions

def main():
    st.title("Vessel Location Tracker")

    mode = st.radio("Choose a query mode", ["By MMSI", "By Bounding Box"])

    if mode == "By MMSI":
        mmsi_filter = st.text_input("Enter Vessel MMSI:", "")
        if st.button("Track Boat"):
            positions = asyncio.run(connect_ais_stream([mmsi_filter]))
            data = {'LATITUDE': [pos[0] for pos in positions], 'LONGITUDE': [pos[1] for pos in positions]}
            st.map(pd.DataFrame(data))
    
    elif mode == "By Bounding Box":
        min_lat = st.number_input("Enter Minimum Latitude:", value=-90.0, max_value=90.0)
        max_lat = st.number_input("Enter Maximum Latitude:", value=90.0, max_value=90.0)
        min_lon = st.number_input("Enter Minimum Longitude:", value=-180.0, max_value=180.0)
        max_lon = st.number_input("Enter Maximum Longitude:", value=180.0, max_value=180.0)

        if st.button("Fetch Vessels"):
            positions = asyncio.run(connect_ais_stream(bounding_box=[[min_lat, min_lon], [max_lat, max_lon]]))
            data = {'LATITUDE': [pos[0] for pos in positions], 'LONGITUDE': [pos[1] for pos in positions]}
            st.map(pd.DataFrame(data))

if __name__ == "__main__":
    main()
