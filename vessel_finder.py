import asyncio
import websockets
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

async def connect_ais_stream(mmsi_filter):

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {
            "APIKey": "1b7af1885ca28ca99cc1a166c9a6aa5983dee696",
            "BoundingBoxes": [[[-90, -180], [90, 180]]],
            "FiltersShipMMSI": mmsi_filter,
            "FilterMessageTypes": ["PositionReport"]
        }

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            message = json.loads(message_json)
            message_type = message["MessageType"]

            if message_type == "PositionReport":
                ais_message = message['Message']['PositionReport']
                return ais_message['Latitude'], ais_message['Longitude']

async def main_async(mmsi_filters):
    tasks = [connect_ais_stream([mmsi_filter]) for mmsi_filter in mmsi_filters]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    latitudes = []
    longitudes = []

    for index, result in enumerate(results):
        if isinstance(result, Exception):
            st.write(f"Failed to fetch location for MMSI {mmsi_filters[index]}. Error: {result}")
        else:
            latitude, longitude = result
            latitudes.append(latitude)
            longitudes.append(longitude)
            st.write(f"MMSI: {mmsi_filters[index]} - Latitude: {round(latitude, 5)} - Longitude: {round(longitude, 5)}")
    
    if latitudes and longitudes:
        data = {'LATITUDE': latitudes, 'LONGITUDE': longitudes}
        st.map(pd.DataFrame(data))

def main():
    st.title("Vessel Location Tracker")
    mmsi_input = st.text_input("Enter Vessel MMSI (comma-separated for multiple):", "")
    mmsi_filters = [x.strip() for x in mmsi_input.split(',')] if mmsi_input else []

    if st.button("Track Boats"):
        asyncio.run(main_async(mmsi_filters))

if __name__ == "__main__":
    main()
