import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("NBA Player Shooting Percentage Animation")

year = st.selectbox("Select Year", np.arange(1996, 2025, 1))
nba_shot_data = pd.read_csv(f"nba_data/shotdetail_{year}.csv")

player_list = nba_shot_data["PLAYER_NAME"].unique()
player = st.selectbox("Select Player", player_list)
shots = st.selectbox("Select Shot Type", ["all", "2 pointers", "3 pointers"])
speed = st.select_slider("Speed of Animation", options=["very slow", "slow", "medium", "fast", "very fast"])

speed_dictionary = {
    "very slow": 50,
    "slow": 25,
    "medium": 10,
    "fast": 2.5,
    "very fast": 0.5
}


def nba_func(player, shots):
    assert shots in ["2 pointers", "3 pointers", "all"]

    player_shots = nba_shot_data[nba_shot_data["PLAYER_NAME"] == player][["SHOT_ATTEMPTED_FLAG", "SHOT_MADE_FLAG", "SHOT_TYPE"]]

    if shots == "2 pointers":
        player_shots = player_shots[player_shots["SHOT_TYPE"] == '2PT Field Goal']
    elif shots == "3 pointers":
        player_shots = player_shots[player_shots["SHOT_TYPE"] == '3PT Field Goal']
    elif shots == "all":
        player_shots = player_shots

    
    player_shots["shot_number"] = player_shots["SHOT_ATTEMPTED_FLAG"].cumsum()
    player_shots["shots_made"] = player_shots["SHOT_MADE_FLAG"].cumsum()
    player_shots["FG_PCT"] = player_shots["shots_made"] / player_shots["shot_number"]

    return player_shots

# Get the player's shooting data
try:
    df_shots = nba_func(player, shots)

    # Check if data is empty
    if df_shots.empty:
        st.error(f"No data found for {player} with {shots}.")
    else:
        # Calculate the final shooting percentage
        final_fg_pct = df_shots['FG_PCT'].iloc[-1]

        # Prepare data for animation
        data = []
        for i in range(1, len(df_shots) + 1):
            frame_data = {
                'shot_number': df_shots['shot_number'][:i],
                'FG_PCT': df_shots['FG_PCT'][:i],
                'frame': [i] * i
            }
            data.append(pd.DataFrame(frame_data))

        df_anim = pd.concat(data, ignore_index=True)

        # Create the animated line plot
        fig = px.line(
            df_anim,
            x='shot_number',
            y='FG_PCT',
            animation_frame='frame',
            animation_group='shot_number',
            range_x=[1, df_shots['shot_number'].max()],
            range_y=[0, 1],
            title=f"{player}'s Field Goal Percentage ({shots}) - 2024 Season"
        )

        # Add dashed line for final shooting percentage
        fig.add_hline(
            y=final_fg_pct,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Final FG%: {final_fg_pct:.1%}",
            annotation_position="top right",
            line_width=2
        )

        # Customize the plot
        fig.update_traces(line=dict(width=2, color='blue'))
        fig.update_layout(
            xaxis_title="Shot Number",
            yaxis_title="Field Goal Percentage",
            showlegend=False,
            yaxis_tickformat=".0%"
        )

        # Adjust animation settings
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = speed_dictionary[speed]
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 0

        # Display the plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)

except FileNotFoundError:
    st.error("Data file not found. Please check the path to shotdetail_2024.csv.")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")