import streamlit as st
import numpy as np
import pandas as pd
import math

st.set_page_config(page_title="Spiral Visualizer", page_icon="🌀")

st.title("🌀 Interactive Spiral Visualizer")

num_points = st.sidebar.slider("Number of points in spiral", min_value=1, max_value=10000, value=5000, step=1)
num_turns = st.sidebar.slider("Number of turns in spiral", min_value=1, max_value=100, value=10, step=1)

indices = np.arange(num_points)
theta = indices * (num_turns * 2 * math.pi / num_points)
radius = indices / num_points

x = radius * np.cos(theta)
y = radius * np.sin(theta)

df = pd.DataFrame({"X": x, "Y": y})
st.line_chart(df, x="X", y="Y")
