import asyncio
import websockets
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

API_KEY = "c0ff27fded31c9c0ed390b7dcedae4e40daf0c62"

async def connect_ais_stream(mmsi_filters):
    url = "wss://stream.aisstream.io/v0/stream"
    subscribe_message = {
        "APIKey": API_KEY,
        "BoundingBoxes": [[[-90, -180], [90, 180]]],
        "FiltersShipMMSI": mmsi_filters,
        "FilterMessageTypes": ["PositionReport"]
    }

    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(subscribe_message))
        
        try:
            message_json = await asyncio.wait_for(websocket.recv(), timeout=120)  # Wait for 10 seconds
            message = json.loads(message_json)
            
            if message["MessageType"] == "PositionReport":
                ais_message = message['Message']['PositionReport']
                return ais_message['Latitude'], ais_message['Longitude']
        except asyncio.TimeoutError:
            st.write("Timed out waiting for data. Please try again.")

def main():
    st.title("Vessel Location Tracker")
    mmsi_input = st.text_input("Enter Vessel MMSI (comma-separated for multiple):", "")

    mmsi_filters = [x.strip() for x in mmsi_input.split(',')] if mmsi_input else []

    if st.button("Track Boats"):
        latitudes = []
        longitudes = []

        for mmsi_filter in mmsi_filters:
            try:
                latitude, longitude = asyncio.run(connect_ais_stream([mmsi_filter]))
                latitudes.append(latitude)
                longitudes.append(longitude)
                st.write(f"MMSI: {mmsi_filter} - Latitude: {round(latitude, 5)} - Longitude: {round(longitude, 5)}")
            except TypeError:
                st.write(f"Failed to fetch location for MMSI {mmsi_filter}. Ensure it's correct.")

        if latitudes and longitudes:
            data = {'LATITUDE': latitudes, 'LONGITUDE': longitudes}
            st.map(pd.DataFrame(data))

if __name__ == "__main__":
    main()
