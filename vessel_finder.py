import asyncio
import websockets
import json
import streamlit as st
import pandas as pd

API_KEY = "c0ff27fded31c9c0ed390b7dcedae4e40daf0c62"


async def connect_ais_stream(mmsi_filter):
    url = "wss://stream.aisstream.io/v0/stream"
    subscribe_message = {
        "APIKey": API_KEY,
        "BoundingBoxes": [[[-90, -180], [90, 180]]],
        "FiltersShipMMSI": [mmsi_filter]    
    }

    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(subscribe_message))
        try:
            message_json = await asyncio.wait_for(websocket.recv(), timeout=90)  # Wait for 10 seconds
            message = json.loads(message_json)

            if message["MessageType"] == "PositionReport":
                ais_message = message['Message']['PositionReport']
                return ais_message['Latitude'], ais_message['Longitude']
        except asyncio.TimeoutError:
            st.write("Timed out waiting for data. Please try again.")


def main():
    st.title("Vessel Location Tracker")
    mmsi_filter = st.text_input("Enter Vessel MMSI:", "")

    if st.button("Track Boat"):
        try:
            latitude, longitude = asyncio.run(connect_ais_stream(mmsi_filter))

            st.write(f"Latitude: {round(latitude, 5)}")
            st.write(f"Longitude: {round(longitude, 5)}")

            data = {'LATITUDE': [latitude], 'LONGITUDE': [longitude]}
            st.map(pd.DataFrame(data))
        except TypeError:
            st.write("Failed to fetch vessel location. Please ensure the MMSI is correct.")


if __name__ == "__main__":
    main()
