from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import random
from scrape import scrape_data, get_team_urls, league_urls, get_transfer_history,scrape_data_countries, countries_url,get_team_urls_with_names
from dataclasses import dataclass
from typing import List, Dict
from itertools import combinations
from collections import Counter
import pandas as pd
import numpy as np
import time



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session management
# Global variable to store player data
all_player_data = []

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/fifa_wordle')
def fifa_wordle():
    return render_template('index.html')

@app.route('/guess_transfer_leagues')
def guess_transfer_leagues():
    return render_template('select_transfer_leagues.html')

@app.route('/update_score', methods=['POST'])
def update_score():
    score = request.form.get('score')
    session['score'] = int(score)
    return '', 204

@app.route('/reset_score', methods=['POST'])
def reset_score():
    session['score'] = 0
    return '', 204

@app.route('/select_transfer_leagues')
def select_transfer_leagues():
    return render_template('select_transfer_leagues.html')

@app.route('/select_leagues_club_guess')
def select_leagues_club_guess():
    return render_template('select_guess_club.html')


@app.route('/play_build_11_league', methods=['GET'])
def play_build_11_league():
    # Clear all relevant session data to start fresh
    session.pop('used_positions', None)
    session.pop('used_prompts', None)
    session.pop('total_submissions', None)
    session.pop('current_prompt_type', None)
    session.pop('current_prompt_value', None)
    session.pop('formation', None)
    session.pop('prompt_pool', None)
    session.pop('game_complete', None)
    session.pop('all_player_data', None)  # Clear the players so that they can be re-scraped

    return render_template('select_league_for_build_11.html')



@dataclass
class Formation:
    name: str
    url: str
    positions: Dict[str, Dict[str, int]]  # key is position, value is a dictionary with roles and count

formations = {
    "3-1-4-2": Formation(
        name="3-1-4-2",
        url="static/formations/formation-3-1-4-2.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Left Midfield": {"Left Midfield": 1, "Left-Back": 1, "Central Midfield": 1},
            "Right Midfield": {"Right Midfield": 1, "Right-Back": 1, "Central Midfield": 1},
            "Centre-Back": {"Centre-Back": 3, "Sweeper": 3},
            "Defensive Midfield": {"Defensive Midfield": 1},
            "Central Midfield": {"Central Midfield": 2},
            "Centre-Forward": {"Centre-Forward": 2, "Second Striker": 2},
        }
    ),
    "3-4-3 Diamond": Formation(
        name="3-4-3 Diamond",
        url="static/formations/formation-3-4-3-diamond.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 3, "Sweeper": 3},
            "Defensive Midfield": {"Defensive Midfield": 1},
            "Attacking Midfield": {"Attacking Midfield": 1},
            "Left Midfield": {"Left Midfield": 1, "Left-Back": 1, "Central Midfield": 1},
            "Right Midfield": {"Right Midfield": 1, "Right-Back": 1, "Central Midfield": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
            "Left Winger": {"Left Winger": 1},
            "Right Winger": {"Right Winger": 1},
        }
    ),
    "3-4-3 Flat": Formation(
        name="3-4-3 Flat",
        url="static/formations/formation-3-4-3-flat.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 3, "Sweeper": 3},
            "Central Midfield": {"Central Midfield": 2},
            "Left Midfield": {"Left Midfield": 1, "Left-Back": 1, "Central Midfield": 1},
            "Right Midfield": {"Right Midfield": 1, "Right-Back": 1, "Central Midfield": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
            "Left Winger": {"Left Winger": 1},
            "Right Winger": {"Right Winger": 1},
        }
    ),
    "3-5-1-1": Formation(
        name="3-5-1-1",
        url="static/formations/formation-3-5-1-1.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 3, "Sweeper": 3},
            "Defensive Midfield": {"Defensive Midfield": 2},
            "Central Midfield": {"Central Midfield": 1},
            "Attacking Midfield": {"Attacking Midfield": 1, "Second Striker": 1},
            "Centre-Forward": {"Centre-Forward": 1},
            "Left Midfield": {"Left Midfield": 1, "Left-Back": 1, "Central Midfield": 1},
            "Right Midfield": {"Right Midfield": 1, "Right-Back": 1, "Central Midfield": 1},
        }
    ),
    "4-1-2-1-2 Narrow": Formation(
        name="4-1-2-1-2 Narrow",
        url="static/formations/formation-4-1-2-1-2-narrow.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Defensive Midfield": {"Defensive Midfield": 1},
            "Central Midfield": {"Central Midfield": 2},
            "Attacking Midfield": {"Attacking Midfield": 1},
            "Centre-Forward": {"Centre-Forward": 2, "Second Striker": 2},
        }
    ),
    "4-1-2-1-2 Wide": Formation(
        name="4-1-2-1-2 Wide",
        url="static/formations/formation-4-1-2-1-2-wide.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Defensive Midfield": {"Defensive Midfield": 1},
            "Right Midfield": {"Central Midfield": 1, "Right Midfield": 1},
            "Left Midfield": {"Central Midfield": 1, "Left Midfield": 1},
            "Attacking Midfield": {"Attacking Midfield": 1},
            "Centre-Forward": {"Centre-Forward": 2, "Second Striker": 2},
        }
    ),
    "4-2-3-1 Narrow": Formation(
        name="4-2-3-1 Narrow",
        url="static/formations/formation-4-2-3-1-narrow.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Defensive Midfield": {"Defensive Midfield": 2},
            "Left Winger": {"Left Winger": 1, "Attacking Midfield": 1},
            "Right Winger": {"Right Winger": 1, "Attacking Midfield": 1},
            "Attacking Midfield": {"Attacking Midfield": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
        }
    ),
    "4-2-3-1 Wide": Formation(
        name="4-2-3-1 Wide",
        url="static/formations/formation-4-2-3-1-wide.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Defensive Midfield": {"Defensive Midfield": 2},
            "Left Midfield": {"Central Midfield": 1, "Left Midfield": 1},
            "Right Midfield": {"Central Midfield": 1, "Right Midfield": 1},
            "Attacking Midfield": {"Attacking Midfield": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
        }
    ),
    "4-2-4": Formation(
        name="4-2-4",
        url="static/formations/formation-4-2-4.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Central Midfield": {"Central Midfield": 2},
            "Left Winger": {"Left Winger": 1},
            "Right Winger": {"Right Winger": 1},
            "Centre-Forward": {"Centre-Forward": 2, "Second Striker": 2},
        }
    ),
    "4-3-3 Attack": Formation(
        name="4-3-3 Attack",
        url="static/formations/formation-4-3-3-attack.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Central Midfield": {"Central Midfield": 2},
            "Attacking Midfield": {"Attacking Midfield": 1},
            "Left Winger": {"Left Winger": 1},
            "Right Winger": {"Right Winger": 1},
            "Centre-Forward": {"Centre-Forward": 1,"Second Striker": 1},
        }
    ),
    "4-3-3 Defend": Formation(
        name="4-3-3 Defend",
        url="static/formations/formation-4-3-3-defend.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Defensive Midfield": {"Defensive Midfield": 2},
            "Central Midfield": {"Central Midfield": 1},
            "Left Winger": {"Left Winger": 1},
            "Right Winger": {"Right Winger": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
        }
    ),
    "4-3-3 Flat": Formation(
        name="4-3-3 Flat",
        url="static/formations/formation-4-3-3-flat.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Central Midfield": {"Central Midfield": 3},
            "Left Winger": {"Left Winger": 1},
            "Right Winger": {"Right Winger": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
        }
    ),
    "4-3-3 Holding": Formation(
        name="4-3-3 Holding",
        url="static/formations/formation-4-3-3-holding.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Defensive Midfield": {"Defensive Midfield": 1},
            "Central Midfield": {"Central Midfield": 2},
            "Left Winger": {"Left Winger": 1},
            "Right Winger": {"Right Winger": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
        }
    ),
    "4-4-1-1 Attack": Formation(
        name="4-4-1-1 Attack",
        url="static/formations/formation-4-4-1-1-attack.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Right-Back": {"Right-Back": 1},
            "Left-Back": {"Left-Back": 1},
            "Central Midfield": {"Central Midfield": 2},
            "Left Midfield": {"Left Midfield": 1, "Central Midfield": 1, "Left Winger": 1},
            "Right Midfield": {"Right Midfield": 1, "Central Midfield": 1, 'Right Winger': 1},
            "Attacking Midfield": {"Attacking Midfield": 1, "Second Striker": 1},
            "Centre-Forward": {"Centre-Forward": 1},
        }
    ),
    "4-5-1 Flat": Formation(
        name="4-5-1 Flat",
        url="static/formations/formation-4-5-1-flat.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 2},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Central Midfield": {"Central Midfield": 3},
            "Left Midfield": {"Left Midfield": 1, "Central Midfield": 1},
            "Right Midfield": {"Right Midfield": 1, "Central Midfield": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
        }
    ),
    "5-2-3": Formation(
        name="5-2-3",
        url="static/formations/formation-5-2-3.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 3},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Central Midfield": {"Central Midfield": 2},
            "Left Winger": {"Left Winger": 1},
            "Right Winger": {"Right Winger": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
        }
    ),
    "5-4-1 Diamond": Formation(
        name="5-4-1 Diamond",
        url="static/formations/formation-5-4-1-diamond.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 3},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Defensive Midfield": {"Defensive Midfield": 1},
            "Attacking Midfield": {"Attacking Midfield": 1},
            "Left Midfield": {"Central Midfield": 1,"Left Midfield": 1},
            "Right Midfield": {"Central Midfield": 1, "Right Midfield": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
        }
    ),
    "5-4-1 Flat": Formation(
        name="5-4-1 Flat",
        url="static/formations/formation-5-4-1-flat.jpg",
        positions={
            "Goalkeeper": {"Goalkeeper": 1},
            "Centre-Back": {"Centre-Back": 3},
            "Left-Back": {"Left-Back": 1},
            "Right-Back": {"Right-Back": 1},
            "Central Midfield": {"Central Midfield": 2},
            "Left Midfield": {"Left Midfield": 1, "Central Midfield": 1},
            "Right Midfield": {"Right Midfield": 1, "Central Midfield": 1},
            "Centre-Forward": {"Centre-Forward": 1, "Second Striker": 1},
        }
    ),
}

formation_coordinates = {
    "3-1-4-2": {
        "Goalkeeper": {"x": 50, "y": 85},
        "Centre-Back 1": {"x": 70, "y": 73},
        "Centre-Back 2": {"x": 50, "y": 70},
        "Centre-Back 3": {"x": 32, "y": 73},
        "Defensive Midfield": {"x": 50, "y": 58},
        "Left Midfield": {"x": 20, "y": 47},
        "Right Midfield": {"x": 83, "y": 47},
        "Central Midfield 1": {"x": 40, "y": 54},
        "Central Midfield 2": {"x": 60, "y": 54},
        "Centre-Forward 1": {"x": 41, "y": 36},
        "Centre-Forward 2": {"x": 60, "y": 36},
    },
    "3-4-3 Diamond": {
        "Goalkeeper": {"x": 50, "y": 85},
        "Centre-Back 1": {"x": 70, "y": 73},
        "Centre-Back 2": {"x": 50, "y": 70},
        "Centre-Back 3": {"x": 32, "y": 73},
        "Defensive Midfield": {"x": 50, "y": 57},
        "Left Midfield": {"x": 22, "y": 52},
        "Right Midfield": {"x": 81, "y": 52},
        "Attacking Midfield": {"x": 50, "y": 45},
        "Centre-Forward": {"x": 50, "y": 32},
        "Left Winger": {"x": 22, "y": 37},
        "Right Winger": {"x": 81, "y": 37},
    },
    "3-4-3 Flat": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 70, "y": 73},
            "Centre-Back 2": {"x": 50, "y": 70},
            "Centre-Back 3": {"x": 32, "y": 73},
            "Central Midfield 1": {"x": 40, "y": 54},
            "Central Midfield 2": {"x": 60, "y": 54},
            "Left Midfield": {"x": 20, "y": 48},
            "Right Midfield": {"x": 83, "y": 48},
            "Centre-Forward": {"x": 50, "y": 36},
            "Left Winger": {"x": 22, "y": 35},
            "Right Winger": {"x": 81, "y": 35},
    },
    "3-5-1-1": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 70, "y": 73},
            "Centre-Back 2": {"x": 50, "y": 70},
            "Centre-Back 3": {"x": 32, "y": 73},
            "Defensive Midfield 1": {"x": 63, "y": 60},
            "Defensive Midfield 2": {"x": 37, "y": 60},
            "Central Midfield": {"x": 50, "y": 57},
            "Attacking Midfield": {"x": 50, "y": 44},
            "Centre-Forward": {"x": 50, "y": 32},
            "Left Midfield": {"x": 20, "y": 48},
            "Right Midfield": {"x": 83, "y": 48},
    },
    "4-1-2-1-2 Narrow": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 40, "y": 72},
            "Centre-Back 2": {"x": 60, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Defensive Midfield": {"x": 50, "y": 62},
            "Central Midfield 1": {"x": 40, "y": 54},
            "Central Midfield 2": {"x": 60, "y": 54},
            "Attacking Midfield": {"x": 50, "y": 45},
            "Centre-Forward 1": {"x": 41, "y": 33},
            "Centre-Forward 2": {"x": 60, "y": 33},
    },
    "4-1-2-1-2 Wide": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 40, "y": 72},
            "Centre-Back 2": {"x": 60, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Defensive Midfield": {"x": 50, "y": 62},
            "Left Midfield": {"x": 20, "y": 52},
            "Right Midfield": {"x": 83, "y": 52},
            "Attacking Midfield": {"x": 50, "y": 46},
            "Centre-Forward 1": {"x": 41, "y": 33},
            "Centre-Forward 2": {"x": 60, "y": 33},
    },
    "4-2-3-1 Narrow": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 40, "y": 72},
            "Centre-Back 2": {"x": 60, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Defensive Midfield 1": {"x": 63, "y": 59},
            "Defensive Midfield 2": {"x": 37, "y": 59},
            "Left Winger": {"x": 24, "y": 46},
            "Right Winger": {"x": 78, "y": 46},
            "Attacking Midfield": {"x": 50, "y": 46},
            "Centre-Forward": {"x": 50, "y": 33},      
    },
    "4-2-3-1 Wide":{
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 40, "y": 72},
            "Centre-Back 2": {"x": 60, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Defensive Midfield 1": {"x": 63, "y": 59},
            "Defensive Midfield 2": {"x": 37, "y": 59},
            "Left Midfield": {"x": 20, "y": 52},
            "Right Midfield": {"x": 83, "y": 52},
            "Attacking Midfield": {"x": 50, "y": 46},
            "Centre-Forward": {"x": 50, "y": 33},
    },
    "4-2-4": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 40, "y": 72},
            "Centre-Back 2": {"x": 60, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Central Midfield 1": {"x": 40, "y": 54},
            "Central Midfield 2": {"x": 60, "y": 54},
            "Left Winger": {"x": 22, "y": 38},
            "Right Winger": {"x": 81, "y": 38},
            "Centre-Forward 1": {"x": 41, "y": 36},
            "Centre-Forward 2": {"x": 60, "y": 36},
    },
    "4-3-3 Attack": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 40, "y": 72},
            "Centre-Back 2": {"x": 60, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Central Midfield 1": {"x": 40, "y": 54},
            "Central Midfield 2": {"x": 60, "y": 54},
            "Attacking Midfield": {"x": 50, "y": 46},
            "Left Winger": {"x": 22, "y": 37},
            "Right Winger": {"x": 81, "y": 37},
            "Centre-Forward": {"x": 50, "y": 33},
    },
    "4-3-3 Defend": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 40, "y": 72},
            "Centre-Back 2": {"x": 60, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Defensive Midfield 1": {"x": 63, "y": 59},
            "Defensive Midfield 2": {"x": 37, "y": 59},
            "Central Midfield": {"x": 50, "y": 53},
            "Centre-Forward": {"x": 50, "y": 36},
            "Left Winger": {"x": 22, "y": 37},
            "Right Winger": {"x": 81, "y": 37},
    },
    "4-3-3 Flat":{
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 40, "y": 72},
            "Centre-Back 2": {"x": 60, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Central Midfield 1": {"x": 35, "y": 54},
            "Central Midfield 2": {"x": 65, "y": 54},
            "Central Midfield 3": {"x": 50, "y": 56},
            "Centre-Forward": {"x": 50, "y": 36},
            "Left Winger": {"x": 22, "y": 37},
            "Right Winger": {"x": 81, "y": 37},
    },
    "4-3-3 Holding":{
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 35, "y": 72},
            "Centre-Back 2": {"x": 65, "y": 72},
            "Left-Back": {"x": 16, "y": 70},
            "Right-Back": {"x": 86, "y": 70},
            "Defensive Midfield": {"x": 50, "y": 62},
            "Central Midfield 1": {"x": 35, "y": 52},
            "Central Midfield 2": {"x": 65, "y": 53},
            "Left Winger": {"x": 22, "y": 38},
            "Right Winger": {"x": 81, "y": 40},
            "Centre-Forward": {"x": 50, "y": 35},
        },
    "4-4-1-1 Attack": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 37, "y": 72},
            "Centre-Back 2": {"x": 63, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Central Midfield 1": {"x": 37, "y": 54},
            "Central Midfield 2": {"x": 62, "y": 54},
            "Left Midfield": {"x": 20, "y": 47},
            "Right Midfield": {"x": 81, "y": 47},
            "Attacking Midfield": {"x": 50, "y": 44},
            "Centre-Forward": {"x": 50, "y": 31},
    },
    "4-5-1 Flat":{
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 37, "y": 72},
            "Centre-Back 2": {"x": 63, "y": 72},
            "Left-Back": {"x": 16, "y": 68},
            "Right-Back": {"x": 86, "y": 68},
            "Central Midfield 1": {"x": 35, "y": 54},
            "Central Midfield 2": {"x": 65, "y": 54},
            "Central Midfield 3": {"x": 50, "y": 56},
            "Left Midfield": {"x": 20, "y": 47},
            "Right Midfield": {"x": 81, "y": 47},
            "Centre-Forward": {"x": 50, "y": 36},
    },
    "5-2-3": {
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 70, "y": 73},
            "Centre-Back 2": {"x": 50, "y": 70},
            "Centre-Back 3": {"x": 32, "y": 73},
            "Left-Back": {"x": 20, "y": 66},
            "Right-Back": {"x": 83, "y": 65},
            "Central Midfield 1": {"x": 40, "y": 54},
            "Central Midfield 2": {"x": 60, "y": 54},
            "Left Winger": {"x": 22, "y": 39},
            "Right Winger": {"x": 81, "y": 39},
            "Centre-Forward": {"x": 50, "y": 36},
    },
    "5-4-1 Diamond":{
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 70, "y": 73},
            "Centre-Back 2": {"x": 50, "y": 70},
            "Centre-Back 3": {"x": 32, "y": 73},
            "Left-Back": {"x": 20, "y": 65},
            "Right-Back": {"x": 83, "y": 65},
            "Defensive Midfield": {"x": 50, "y": 58},
            "Attacking Midfield": {"x": 50, "y": 45},
            "Left Midfield": {"x": 22, "y": 49},
            "Right Midfield": {"x": 81, "y": 49},
            "Centre-Forward": {"x": 50, "y": 33}, 
        },
    "5-4-1 Flat":{
            "Goalkeeper": {"x": 50, "y": 85},
            "Centre-Back 1": {"x": 70, "y": 73},
            "Centre-Back 2": {"x": 50, "y": 70},
            "Centre-Back 3": {"x": 32, "y": 73},
            "Left-Back": {"x": 20, "y": 65},
            "Right-Back": {"x": 83, "y": 65},
            "Central Midfield 1": {"x": 40, "y": 54},
            "Central Midfield 2": {"x": 60, "y": 54},
            "Left Midfield": {"x": 20, "y": 47},
            "Right Midfield": {"x": 81, "y": 47},
            "Centre-Forward": {"x": 50, "y": 36},
    },
   
    # You can add other formations here as well...

}

legend_prompts = [
    ('Brazil Legends', 'static/legends/brazil_legends.png', lambda p: p['Nationality 1'] == 'Brazil'),
    ('Argentina Legends', 'static/legends/argentina_legends.png', lambda p: p['Nationality 1'] == 'Argentina'),
    ('South America Legends (Not from Brazil or Argentina)', 'static/legends/south_america_legends.png',
     lambda p: p['Continent'] == 'South America' and p['Nationality 1'] not in ['Brazil', 'Argentina']),
    ('Germany Legends', 'static/legends/germany_legends.png', lambda p: p['Nationality 1'] == 'Germany'),
    ('Italy Legends', 'static/legends/italy_legends.png', lambda p: p['Nationality 1'] == 'Italy'),
    ('Spain Legends', 'static/legends/spain_legends.png', lambda p: p['Nationality 1'] == 'Spain'),
    ('France Legends', 'static/legends/france_legends.png', lambda p: p['Nationality 1'] == 'France'),
    ('England Legends', 'static/legends/england_legends.png', lambda p: p['Nationality 1'] == 'England'),
    ('Rest of Europe Legends (Not Germany, Italy, England, Spain, France)', 'static/legends/rest_of_europe_legends.png',
     lambda p: p['Continent'] == 'Europe' and p['Nationality 1'] not in ['Germany', 'Italy', 'Spain', 'France', 'England']),
    ('Rest of the world Legends (Not Europe or South America)', 'static/legends/rest_of_world_legends.png',
     lambda p: p['Continent'] not in ['Europe', 'South America'])
]

def get_shortened_position(position):
    # Map full positions to their abbreviations
    position_mapping = {
        'Attacking Midfield': 'AM',
        'Right Winger': 'RW',
        'Centre-Forward': 'CF',
        'Central Midfield': 'CM',
        'Centre-Back': 'CB',
        'Second Striker': 'SS',
        'Left Winger': 'LW',
        'Goalkeeper': 'GK',
        'Defensive Midfield': 'DM',
        'Left-Back': 'LB',
        'Right-Back': 'RB',
        'Right Midfield': 'RM',
        'Left Midfield': 'LM'
    }
    return position_mapping.get(position, position)  # Default to full position if not in the mapping

def format_suggestion(player):
    position_short = get_shortened_position(player['Position'])
    
    if player['League'] == 'Legends Around the World':
        decade = player.get('Decade', 'Unknown')  # Fetch the decade from the 'Decade' column
        return f"{player['Player Name']} ({position_short}/{decade})"
    
    # For non-legend players, show only position
    return f"{player['Player Name']} ({position_short})"

@app.route('/player_suggestions', methods=['POST'])
def player_suggestions():
    query = request.json.get('query', '').lower()
        
    # Filter players by the query and format the suggestion accordingly
    suggestions = [format_suggestion(player) for player in all_player_data if query in player['Player Name'].lower()]
    
    
    return jsonify(suggestions=suggestions)

def get_legends_prompt(player_data):
    """
    Selects a random legend prompt, filtering players based on the prompt value, and returns the image path.
    """
    # Randomly select a legend prompt and corresponding image
    prompt_name, image_path, filter_function = random.choice(legend_prompts)

    # Filter valid players based on the selected prompt
    valid_players = [p for p in player_data if p['League'] == 'Legends Around the World' and filter_function(p)]

    if valid_players:
        # Randomly select a player from the filtered list
        selected_player = random.choice(valid_players)

        # Debugging: Check if the image path and selected player are consistent
        print(f"Selected legend prompt: {prompt_name}, Image: {image_path}")

        return prompt_name, image_path, selected_player.get('nat_url', None)

    # If no valid players are found, return None to signify no valid prompt
    return None, None, None



@app.route('/start_build_11_scraping_legends', methods=['POST'])
def start_build_11_scraping_legends():
    selected_leagues = request.json['leagues']
    global all_player_data
    all_player_data = []

    if 'Legends Around the World' in selected_leagues:
        # Load player data from Excel or other sources
        legends_player_data = pd.read_excel('players.xlsx')
        legends_player_data = legends_player_data.dropna(subset=['Player URL'])  # Remove rows with empty 'Player URL'
        legends_player_data = legends_player_data.replace({np.nan: None})


        # Normalize text fields for consistent processing
        legends_player_data['Player Name'] = legends_player_data['Player Name'].str.strip()
        legends_player_data['League'] = legends_player_data['League'].str.strip()
        legends_player_data['Nationality 1'] = legends_player_data['Nationality 1'].str.strip()

        all_player_data = legends_player_data.to_dict(orient='records')  # Convert DataFrame to list of dicts


    if not all_player_data:
        return redirect(url_for('play_build_11_league'))

    # Initialize prompt pool and store it in session
    prompt_pool = list(set([player['Nationality 1'] for player in all_player_data] + 
                           [player['Club Name'] for player in all_player_data]))
    session['prompt_pool'] = prompt_pool

    # Set up formation for legends game
    formation_name, formation = random.choice(list(formations.items()))

    prompt_type, prompt_value, prompt_image, prompt_url = 'legends', *get_legends_prompt(all_player_data)

    session['formation'] = {
        'name': formation.name,
        'url': formation.url,
        'positions': formation.positions
    }
    session['used_positions'] = {position: 0 for position in session['formation']['positions']}
    session['used_prompts'] = {}
    session['current_prompt_type'] = prompt_type
    session['current_prompt_value'] = prompt_value
    session['prompt_url'] = prompt_url
    session['prompt_image'] = prompt_image  # Save the image URL to the session
    session['correct_submissions'] = []

    return redirect(url_for('build_11_league_game'))


@app.route('/start_build_11_scraping', methods=['POST'])
def start_build_11_scraping():
    selected_leagues = request.json['leagues']
    global all_player_data
    all_player_data = []

    legends_selected = 'Legends Around the World' in selected_leagues

    # Load player data from Excel for Legends if selected
    if legends_selected:
        legends_player_data = pd.read_excel('players.xlsx')
        legends_player_data = legends_player_data.dropna(subset=['Player URL'])  # Remove rows with empty 'Player URL'
        legends_player_data = legends_player_data.replace({np.nan: None})

        # Normalize text fields for consistent processing
        legends_player_data['Player Name'] = legends_player_data['Player Name'].str.strip()
        legends_player_data['League'] = legends_player_data['League'].str.strip()
        legends_player_data['Nationality 1'] = legends_player_data['Nationality 1'].str.strip()

        # Add default League_img for Legends players
        legends_player_data['League_img'] = 'static/legends/legend_icon.png'

        # Convert DataFrame to list of dicts and extend all_player_data
        all_player_data.extend(legends_player_data.to_dict(orient='records'))

    # Scrape data for regular leagues
    for league_name in selected_leagues:
        if league_name != 'Legends Around the World':  # Skip legends as we've already loaded from Excel
            matching_league = next((league for league in league_urls if league[0] == league_name), None)
            if matching_league:
                league_url = matching_league[1]
                team_urls = get_team_urls(league_url)
                for url in team_urls:
                    league_data = scrape_data(url)
                    for player in league_data:
                        player['League'] = league_name
                        player['League_img'] = convert_url_to_logo(league_url)
                    all_player_data.extend(league_data)

    if not all_player_data:
        return redirect(url_for('play_build_11_league'))

    # Initialize prompt pool and store it in session
    prompt_pool = list(set([player['Nationality 1'] for player in all_player_data] + 
                           [player['Club Name'] for player in all_player_data]))
    session['prompt_pool'] = prompt_pool

    formation_name, formation = random.choice(list(formations.items()))

    # If legends are selected, we ensure the first prompt is from legends
    if legends_selected:
        prompt_type, prompt_value, prompt_image, prompt_url = 'legends', *get_legends_prompt(all_player_data)
        
        # Assign prompt image properly and ensure session consistency
        session['prompt_image'] = prompt_image  # Store the correct image in the session
        session['current_prompt_value'] = prompt_value
        session['prompt_url'] = prompt_image  # Ensure this is the image URL for legends
    else:
        # Randomly choose whether to prompt for a nationality or a club
        if random.choice(['nationality', 'club']) == 'nationality':
            prompt_type = 'nationality'
            prompt_value = random.choice([player['Nationality 1'] for player in all_player_data])
            prompt_url = next(player['nat_url'] for player in all_player_data if player['Nationality 1'] == prompt_value)
        else:
            prompt_type = 'club'
            prompt_value = random.choice([player['Club Name'] for player in all_player_data])
            prompt_url = next(player['club_img'] for player in all_player_data if player['Club Name'] == prompt_value)

    # Fix: Ensure the prompt image is correctly aligned with the prompt value.
    if prompt_url:
        prompt_url += f"?t={int(time.time())}"  # Add a timestamp to ensure the image updates correctly

    # Set formation and prompt data in session
    session['formation'] = {
        'name': formation.name,
        'url': formation.url,
        'positions': formation.positions
    }
    session['used_positions'] = {position: 0 for position in session['formation']['positions']}
    session['used_prompts'] = {}  # To track used nationalities and clubs
    session['current_prompt_type'] = prompt_type  # Store whether it's nationality, club, or legends
    session['current_prompt_value'] = prompt_value  # Store the actual nationality or club
    session['prompt_url'] = prompt_url
    session['correct_submissions'] = []  # Initialize the list to track correct submissions

    return redirect(url_for('build_11_league_game'))


@app.route('/build_11_league_game')
def build_11_league_game():
    if not all_player_data:
        print("Redirecting back to league selection: all_player_data is empty.")
        return redirect(url_for('play_build_11_league'))

    formation_data = session.get('formation')
    if not formation_data:
        print("Redirecting back to league selection: formation data not found in session.")
        return redirect(url_for('play_build_11_league'))

    print(f"Rendering game with {session['current_prompt_type']}: {session['current_prompt_value']}")

    formation = Formation(
        name=formation_data['name'],
        url=formation_data['url'],
        positions=formation_data['positions']
    )

    current_prompt_type = session.get('current_prompt_type')
    current_prompt_value = session.get('current_prompt_value')
    prompt_url = session.get('prompt_url')
    coordinates = formation_coordinates.get(formation.name, {})
    unique_league_imgs = session.get('unique_league_imgs', [])

    return render_template(
        'build_11_game.html',
        prompt_type=current_prompt_type,
        prompt_value=current_prompt_value,
        prompt_url=prompt_url,  # Make sure this is set correctly
        formation=formation,
        coordinates=coordinates,
        players=all_player_data,  # Ensure legends player data is passed to the frontend
        formation_positions={pos: list(roles.keys()) for pos, roles in formation.positions.items()},
        unique_league_imgs=unique_league_imgs
    )


def validate_legends_prompt(player, prompt_value):
    # Validation logic for each legend category
    legend_prompts = {
        'Brazil Legends': lambda p: p['Nationality 1'].lower() == 'brazil',
        'Argentina Legends': lambda p: p['Nationality 1'].lower() == 'argentina',
        'South America Legends (Not from Brazil or Argentina)': lambda p: p['Continent'].lower() == 'south america' and p['Nationality 1'].lower() not in ['brazil', 'argentina'],
        'Germany Legends': lambda p: p['Nationality 1'].lower() == 'germany',
        'Italy Legends': lambda p: p['Nationality 1'].lower() == 'italy',
        'Spain Legends': lambda p: p['Nationality 1'].lower() == 'spain',
        'France Legends': lambda p: p['Nationality 1'].lower() == 'france',
        'England Legends': lambda p: p['Nationality 1'].lower() == 'england',
        'Rest of Europe Legends (Not Germany, Italy, England, Spain, France)': lambda p: p['Continent'].lower() == 'europe' and p['Nationality 1'].lower() not in ['germany', 'italy', 'spain', 'france', 'england'],
        'Rest of the world Legends (Not Europe or South America)': lambda p: p['Continent'].lower() not in ['europe', 'south america']
    }

    # Clean and simplify the prompt value to match the dictionary keys
    prompt_value = prompt_value.strip()

    # Debug: Print player data and prompt value for transparency
    print(f"Validating Player: {player['Player Name']} | Continent: {player['Continent']} | Nationality: {player['Nationality 1']} | Prompt: {prompt_value}")

    # Check if the player's league is 'Legends Around the World' and validate based on the prompt
    if player['League'].lower() == 'legends around the world':
        validation_function = legend_prompts.get(prompt_value)
        if validation_function:
            result = validation_function(player)
            # Debug: Print the result of the validation function
            print(f"Validation Result for {player['Player Name']}: {result}")
            return result
        else:
            # Debug: Indicate that the prompt was not found in the legend_prompts
            print(f"Prompt '{prompt_value}' not found in legend_prompts.")
            return False

    # Default to False if no valid prompt or failed validation
    print(f"Validation failed for {player['Player Name']} | Prompt: {prompt_value}")
    return False



@app.route('/submit_player_selection', methods=['POST'])
def submit_player_selection():
    # Define the position mapping
    position_mapping = {
        "Centre-Back 1": "Centre-Back",
        "Centre-Back 2": "Centre-Back",
        "Centre-Back 3": "Centre-Back",
        "Central Midfield 1": "Central Midfield",
        "Central Midfield 2": "Central Midfield",
        "Central Midfield 3": "Central Midfield",
        "Centre-Forward 1": "Centre-Forward",
        "Centre-Forward 2": "Centre-Forward",
        "Defensive Midfield 1": "Defensive Midfield",
        "Defensive Midfield 2": "Defensive Midfield",
    }

    data = request.json
    if not data or 'selected_player' not in data or 'position' not in data:
        return jsonify(result="error", message="Missing data"), 400

    selected_player_name = data['selected_player'].strip().lower()
    position = data['position']

    # Normalize the position using the mapping
    normalized_position = position_mapping.get(position, position)

    selected_player = next((player for player in all_player_data if player['Player Name'].strip().lower() == selected_player_name), None)

    if selected_player is None:
        return jsonify(result="error", message="Player not found."), 400

    current_prompt_type = session.get('current_prompt_type')
    current_prompt_value = session.get('current_prompt_value')
    formation = session.get('formation')
    used_positions = session.get('used_positions', Counter())
    total_submissions = session.get('total_submissions', 0)

    # Determine if the player selection is correct
    is_correct = False
    if current_prompt_type == 'legends':
        # Mark player as correct if they belong to the 'Legends Around the World' league and match the legends criteria
        is_correct = (selected_player['League'].strip().lower() == 'legends around the world' and 
                     validate_legends_prompt(selected_player, current_prompt_value) and selected_player['Position'] in formation['positions'][normalized_position])
    elif current_prompt_type == 'nationality':
        # Mark player as correct if their nationality matches and they are not from 'Legends Around the World'
        is_correct = (selected_player['Position'] in formation['positions'][normalized_position] and 
                      selected_player['Nationality 1'] == current_prompt_value and 
                      selected_player['League'].strip().lower() != 'legends around the world')
    elif current_prompt_type == 'club':
        # Mark player as correct if their club matches and they are not from 'Legends Around the World'
        is_correct = (selected_player['Position'] in formation['positions'][normalized_position] and 
                      selected_player['Club Name'] == current_prompt_value and 
                      selected_player['League'].strip().lower() != 'legends around the world')

    # Update the correct_submissions list based on whether the submission is correct
    correct_submissions = session.get('correct_submissions', [])
    correct_submissions.append(is_correct)
    session['correct_submissions'] = correct_submissions

    # Mark the position as filled regardless of correctness
    used_positions[normalized_position] += 1
    session['used_positions'] = used_positions
    total_submissions += 1
    session['total_submissions'] = total_submissions

    # Check if the game is complete (after 11 total submissions)
    if total_submissions >= 11:
        correct_positions_count = sum(1 for correct in session['correct_submissions'] if correct)
        return jsonify(
            result="game_complete",
            correct_count=correct_positions_count,
            player_name=selected_player['Player Name'],
            nationality_url=selected_player.get('nat_url', None),
            club_img=selected_player.get('club_img', None)
        )

    # Otherwise, select a new prompt for the next round
    new_prompt_type, new_prompt_value, new_prompt_url = select_new_prompt()

    session['current_prompt_type'] = new_prompt_type
    session['current_prompt_value'] = new_prompt_value

    return jsonify(
        result="correct" if is_correct else "wrong",
        player_name=selected_player['Player Name'],
        nationality_url=selected_player.get('nat_url', None),
        club_img=selected_player.get('club_img', None),
        new_prompt_value=new_prompt_value,  # Send new prompt value
        new_prompt_url=new_prompt_url  # Send new prompt image URL
    )



def get_available_positions(formation, used_positions):
    """
    Returns the list of available positions that haven't been filled by the user.
    A position is considered unavailable if the user has already submitted a player for that position.
    Handles positions with multiple instances (e.g., Central Midfield x2).
    """
    available_positions = []
    for position, roles in formation['positions'].items():
        # Safely access used_positions and set a default of 0 if the position is missing
        max_roles = len(roles)
        if used_positions.get(position, 0) < max_roles:
            available_positions.append(position)
    return available_positions



def reshuffle_prompt_pool():
    # Reset the usage of all nationalities and clubs that haven't been used twice
    for key in session['prompt_usage']:
        if session['prompt_usage'][key] < 2:
            session['prompt_usage'][key] = 0


@app.route('/reset_game', methods=['POST'])
def reset_game():
    # Clear session data
    session.clear()  # This will clear all session data, including 'used_positions', 'used_prompts', etc.

    # Re-randomize the formation
    formation_name, formation = random.choice(list(formations.items()))
    session['formation'] = {
        'name': formation.name,
        'url': formation.url,
        'positions': formation.positions
    }
    session['used_positions'] = {position: 0 for position in session['formation']['positions']}  # Reset all positions
    session['used_prompts'] = {}
    session['total_submissions'] = 0  # Reset total submissions
    session['correct_submissions'] = []  # Reinitialize the correct submissions
    session['prompt_usage'] = {}  # Initialize prompt usage dictionary

    # Initialize the prompt pool again
    prompt_pool = list(set([player['Nationality 1'] for player in all_player_data] +
                           [player['Club Name'] for player in all_player_data]))
    session['prompt_pool'] = prompt_pool

    # Select a new prompt (nationality, club, or legends if applicable)
    if any(player['League'] == 'Legends Around the World' for player in all_player_data):
        # Handle the Legends Around the World case
        prompt_name, new_prompt_url, nat_url = get_legends_prompt(all_player_data)
        new_prompt_value = prompt_name  # Use the legend prompt name as the value
        new_prompt_type = 'legends'
        session['prompt_image'] = new_prompt_url  # Ensure legend image is stored correctly in session
    else:
        # Handle regular nationality or club prompts
        new_prompt_value = random.choice(prompt_pool)

        # Determine if the prompt is a nationality or a club
        if any(player['Nationality 1'] == new_prompt_value for player in all_player_data):
            new_prompt_type = 'nationality'
            new_prompt_url = next((player['nat_url'] for player in all_player_data if player['Nationality 1'] == new_prompt_value), None)
        else:
            new_prompt_type = 'club'
            new_prompt_url = next((player['club_img'] for player in all_player_data if player['Club Name'] == new_prompt_value), None)

    # Ensure new_prompt_url is correctly set
    if not new_prompt_url:
        new_prompt_url = "static/default_image_url.png"  # Set a fallback image in case no image is found.

    # Add a timestamp to prevent browser caching issues
    new_prompt_url += f"?t={int(time.time())}"

    # Update session with the new prompt and its corresponding image URL
    session['current_prompt_type'] = new_prompt_type
    session['current_prompt_value'] = new_prompt_value
    session['prompt_url'] = new_prompt_url  # Store the correct image URL in the session for non-legends cases

    # Return success response to the frontend with the correct prompt and image URL
    return jsonify(
        success=True,
        new_prompt_value=new_prompt_value,  # The text to be displayed for the prompt
        new_prompt_url=new_prompt_url  # The image URL for the prompt, including the timestamp to avoid caching
    )

def select_new_prompt():
    """
    Selects a new prompt depending on the leagues present in the collected data, ensuring that:
    - Each prompt is used a maximum of 2 times.
    - There are valid players available for at least one open position before showing the prompt.
    - Pools are refilled once all options are exhausted.
    """
    def valid_players_for_prompt(prompt_type, prompt_value, available_positions):
        """
        Check if there are valid players for the selected prompt (either nationality or club)
        who can fill at least one of the open positions in the formation.
        """
        if prompt_type == 'nationality':
            valid_players = [
                player for player in all_player_data
                if player['Nationality 1'] == prompt_value and player['Position'] in available_positions
            ]
        elif prompt_type == 'club':
            valid_players = [
                player for player in all_player_data
                if player['Club Name'] == prompt_value and player['Position'] in available_positions
            ]
        elif prompt_type == 'legends':
            valid_players = [
                player for player in all_player_data
                if player['League'] == 'Legends Around the World' and player['Position'] in available_positions
            ]
        return len(valid_players) > 0

    def get_available_positions(used_positions, formation):
        """
        Get the list of available positions (those that have not yet been filled).
        """
        available_positions = []
        for position, roles in formation['positions'].items():
            max_roles = len(roles)
            if used_positions.get(position, 0) < max_roles:
                available_positions.append(position)
        return available_positions

    # Get current formation and used positions from the session
    formation = session.get('formation', {})
    used_positions = session.get('used_positions', {})
    available_positions = get_available_positions(used_positions, formation)

    # Track prompt usage and filter out prompts that have already been used 2 times
    prompt_usage = session.get('prompt_usage', {})

    # Step 1: Separate leagues based on 'Legends Around the World'
    all_leagues = [player['League'] for player in all_player_data]
    unique_leagues = set(all_leagues)
    legends_present = 'Legends Around the World' in unique_leagues
    non_legends_data = [player for player in all_player_data if player['League'] != 'Legends Around the World']

    # Step 2: Handle the case when only "Legends Around the World" is present
    if legends_present and len(unique_leagues) == 1:
        # Choose only from the legends pool
        available_legends_prompts = [(prompt, img) for prompt, img, _ in legend_prompts if prompt_usage.get(prompt, 0) < 2]
        while available_legends_prompts:
            prompt_name, new_prompt_url = random.choice(available_legends_prompts)
            if valid_players_for_prompt('legends', prompt_name, available_positions):
                # If valid players exist for this prompt, return it
                prompt_usage[prompt_name] = prompt_usage.get(prompt_name, 0) + 1
                session['prompt_usage'] = prompt_usage
                return 'legends', prompt_name, new_prompt_url
            else:
                # Remove the prompt if no valid players can fill the available positions
                available_legends_prompts.remove((prompt_name, new_prompt_url))

    # Step 3: Handle the case when legends + other leagues are present
    elif legends_present and len(unique_leagues) > 1:
        # Get unique nationalities and clubs from non-legends data
        valid_nationalities = list({player['Nationality 1'] for player in non_legends_data})
        valid_clubs = list({player['Club Name'] for player in non_legends_data if player['Club Name'] != 'Retired'})

        available_prompt_types = ['legends', 'nationality', 'club']
        random.shuffle(available_prompt_types)

        while available_prompt_types:
            prompt_type = available_prompt_types.pop()

            if prompt_type == 'nationality':
                available_nationalities = [nat for nat in valid_nationalities if prompt_usage.get(nat, 0) < 2]
                while available_nationalities:
                    new_prompt_value = random.choice(available_nationalities)
                    if valid_players_for_prompt('nationality', new_prompt_value, available_positions):
                        # Valid players exist, return this prompt
                        prompt_usage[new_prompt_value] = prompt_usage.get(new_prompt_value, 0) + 1
                        session['prompt_usage'] = prompt_usage
                        new_prompt_url = next((player['nat_url'] for player in non_legends_data if player['Nationality 1'] == new_prompt_value), None)
                        return 'nationality', new_prompt_value, new_prompt_url
                    else:
                        available_nationalities.remove(new_prompt_value)

            elif prompt_type == 'club':
                available_clubs = [club for club in valid_clubs if prompt_usage.get(club, 0) < 2]
                while available_clubs:
                    new_prompt_value = random.choice(available_clubs)
                    if valid_players_for_prompt('club', new_prompt_value, available_positions):
                        # Valid players exist, return this prompt
                        prompt_usage[new_prompt_value] = prompt_usage.get(new_prompt_value, 0) + 1
                        session['prompt_usage'] = prompt_usage
                        new_prompt_url = next((player['club_img'] for player in non_legends_data if player['Club Name'] == new_prompt_value), None)
                        return 'club', new_prompt_value, new_prompt_url
                    else:
                        available_clubs.remove(new_prompt_value)

            elif prompt_type == 'legends':
                available_legends_prompts = [(prompt, img) for prompt, img, _ in legend_prompts if prompt_usage.get(prompt, 0) < 2]
                while available_legends_prompts:
                    prompt_name, new_prompt_url = random.choice(available_legends_prompts)
                    if valid_players_for_prompt('legends', prompt_name, available_positions):
                        # Valid players exist, return this prompt
                        prompt_usage[prompt_name] = prompt_usage.get(prompt_name, 0) + 1
                        session['prompt_usage'] = prompt_usage
                        return 'legends', prompt_name, new_prompt_url
                    else:
                        available_legends_prompts.remove((prompt_name, new_prompt_url))

    # Step 4: Handle the case when no legends are present
    else:
        # Get unique nationalities and clubs from non-legends data
        valid_nationalities = list({player['Nationality 1'] for player in non_legends_data})
        valid_clubs = list({player['Club Name'] for player in non_legends_data if player['Club Name'] != 'Retired'})

        available_prompt_types = ['nationality', 'club']
        random.shuffle(available_prompt_types)

        while available_prompt_types:
            prompt_type = available_prompt_types.pop()

            if prompt_type == 'nationality':
                available_nationalities = [nat for nat in valid_nationalities if prompt_usage.get(nat, 0) < 2]
                while available_nationalities:
                    new_prompt_value = random.choice(available_nationalities)
                    if valid_players_for_prompt('nationality', new_prompt_value, available_positions):
                        # Valid players exist, return this prompt
                        prompt_usage[new_prompt_value] = prompt_usage.get(new_prompt_value, 0) + 1
                        session['prompt_usage'] = prompt_usage
                        new_prompt_url = next((player['nat_url'] for player in non_legends_data if player['Nationality 1'] == new_prompt_value), None)
                        return 'nationality', new_prompt_value, new_prompt_url
                    else:
                        available_nationalities.remove(new_prompt_value)

            elif prompt_type == 'club':
                available_clubs = [club for club in valid_clubs if prompt_usage.get(club, 0) < 2]
                while available_clubs:
                    new_prompt_value = random.choice(available_clubs)
                    if valid_players_for_prompt('club', new_prompt_value, available_positions):
                        # Valid players exist, return this prompt
                        prompt_usage[new_prompt_value] = prompt_usage.get(new_prompt_value, 0) + 1
                        session['prompt_usage'] = prompt_usage
                        new_prompt_url = next((player['club_img'] for player in non_legends_data if player['Club Name'] == new_prompt_value), None)
                        return 'club', new_prompt_value, new_prompt_url
                    else:
                        available_clubs.remove(new_prompt_value)

    # Step 5: Refill the pools if all options are exhausted
    prompt_usage.clear()
    session['prompt_usage'] = prompt_usage
    return select_new_prompt()

@app.route('/start_club_guess_scraping', methods=['POST'])
def start_club_guess_scraping():
    data = request.json
    selected_leagues = data['leagues']
    
    all_teams = []  # List to store all team names and URLs

    # Scrape team data for each selected league
    for league_name, league_url in league_urls:
        if league_name in selected_leagues:
            teams = get_team_urls_with_names(league_url)
            all_teams.extend(teams)

    # Store the teams in session
    session['all_teams'] = all_teams

    # Redirect to the guessing game
    return jsonify(success=True)

@app.route('/guess_the_club')
def guess_the_club():
    if 'all_teams' not in session or not session['all_teams']:
        return redirect(url_for('select_leagues_club_guess'))

    all_teams = session['all_teams']
    random_team = random.choice(all_teams)

    # Scrape player data for the random team
    players = scrape_data(random_team['url'])

    # Filter top 5 players by market value
    top_players = sorted(
        [player for player in players if player['Market Value']],
        key=lambda x: x['Market Value'], reverse=True
    )[:5]

    # If less than 5 players, select another team
    if len(top_players) < 5:
        return redirect(url_for('guess_the_club'))

    # Save the correct club name in the session
    session['correct_club'] = random_team['name']

    # Prepare data for rendering
    club_names_list = [team['name'] for team in all_teams]
    
    return render_template('guess_the_club.html', players=top_players, club_names_list=club_names_list)

@app.route('/check_guess_the_club', methods=['POST'])
def check_guess_the_club():
    data = request.json
    user_answer = data['answer']
    correct_club = session.get('correct_club')

    if user_answer.lower() == correct_club.lower():
        return jsonify({'correct': True, 'club': correct_club})
    else:
        return jsonify({'correct': False, 'club': correct_club})

@app.route('/start_transfer_scraping', methods=['POST'])
def start_transfer_scraping():
    data = request.json
    selected_leagues = data['leagues']

    global all_player_data
    all_player_data = []  # Reset player data

    # Define the filter parameters for Legends
    valid_skill_levels = range(1, 8)  # Skill levels 1 to 7 inclusive
    valid_decades = [1970, 1980, 1990, 2000, 2010]  # Valid decades

    # Check if Legends is selected and load from Excel
    legends_selected = 'Legends' in selected_leagues
    if legends_selected:
        legends_player_data = pd.read_excel('players.xlsx')  # Assuming the file is players.xlsx

        # Apply filters for skill level and decade
        legends_player_data = legends_player_data.dropna(subset=['Player URL'])  # Drop rows with empty 'Player URL'
        legends_player_data = legends_player_data.replace({np.nan: None})  # Replace NaN with None

        # Convert skill level and decade to numeric (just in case they are stored as strings)
        legends_player_data['Skill Level'] = pd.to_numeric(legends_player_data['Skill Level'], errors='coerce')
        legends_player_data['Decade'] = pd.to_numeric(legends_player_data['Decade'], errors='coerce')

        # Filter the players based on skill level and decade
        legends_player_data = legends_player_data[
            (legends_player_data['Skill Level'].isin(valid_skill_levels)) &
            (legends_player_data['Decade'].isin(valid_decades))
        ]


        # Add the filtered data to all_player_data
        all_player_data.extend(legends_player_data.to_dict(orient='records'))


    for league_name, league_url in league_urls:
        if league_name in selected_leagues:
            # Skip legends since it's handled above
            if league_name == 'Legends':
                continue

            # Continue scraping data for regular leagues
            team_urls = get_team_urls(league_url)
            for url in team_urls:
                league_data = scrape_data(url)
                print(f"Scraped {len(league_data)} players from {league_name}.")  # Debugging

                for player in league_data:
                    player['League'] = league_name
                all_player_data.extend(league_data)

    # Log final player count
    print(f"Total players loaded: {len(all_player_data)}")  # Debugging

    # Redirect to the transfer guessing game
    return jsonify(success=True)


@app.route('/guess_the_country')
def guess_the_country():
    # Select a random country
    country_tuple = random.choice(countries_url)
    country_name, country_url = country_tuple

    # Scrape player data for the country
    players = scrape_data_countries(country_url)


    # Filter top 5 players by market value
    top_players = sorted(
        [player for player in players if player['Market Value']],
        key=lambda x: x['Market Value'], reverse=True
    )[:5]


    # If less than 5 players, select another country
    if len(top_players) < 5:
        return redirect(url_for('guess_the_country'))

    # Save the correct answer in the session
    session['correct_country'] = country_name

    # Prepare data for rendering
    countries_list = [country[0] for country in countries_url]
    
    return render_template('guess_the_country.html', players=top_players, countries_list=countries_list)

@app.route('/check_guess_the_country', methods=['POST'])
def check_guess_the_country():
    data = request.json
    user_answer = data['answer']
    correct_country = session.get('correct_country')

    if user_answer.lower() == correct_country.lower():
        return jsonify({'correct': True, 'country': correct_country})
    else:
        return jsonify({'correct': False, 'country': correct_country})
    
@app.route('/guess_transfer')
def guess_transfer():
    if not all_player_data:
        return redirect(url_for('guess_transfer_leagues'))

    # Initialize score in session if it doesn't exist
    if 'score' not in session:
        session['score'] = 0
    if 'current_player_index' not in session:
        session['current_player_index'] = 0

    random_player = None
    valid_transfers = []

    # Loop to find a player with valid transfers
    while not valid_transfers:
        # Pick a random player
        random_player = random.choice(all_player_data)

        # Fetch transfer history using the function from scrape.py
        transfer_history = get_transfer_history(random_player['Player URL'])

        if transfer_history is None:
            continue  # If transfer history is not available, pick another player

        # Filter out future transfers
        valid_transfers = [transfer for transfer in transfer_history if transfer['futureTransfer'] == 0]

    # Log the data to ensure it's valid
    print(f"Random Player: {random_player}")
    print(f"Transfer History: {valid_transfers}")
    
    # Get the nationality image URL and player name
    nationality_url = random_player.get('nat_url', '')
    nationality_text = random_player.get('Nationality 1', 'Unknown')
    player_name = random_player.get('Player Name', 'Unknown')


    # Pass data to the template
    return render_template('guess_transfer.html', 
                           nationality_text=nationality_text,
                           nationality_url=nationality_url,
                           transfers=valid_transfers,
                           random_player=player_name,
                           all_player_data=all_player_data or [],
                           score=session['score'])

@app.route('/get_leagues', methods=['POST'])
def get_leagues():
    data = request.json
    continent = data['continent']
    
    continent_leagues = {
           "European": ["England Premier League", "Spain La Liga", "Italy Serie A", "Germany Bundesliga", "France Ligue 1", "Portugal Liga Portugal", "Netherlands Eredivise", "Turkey Super Lig", "Russia Premier Liga", "Belgium Jupiler Pro League", "Greece Super League 1", "Austria Bundesliga", "Ukraine Premier Liga", "Switzerland Super League", "Denmark Superliga", "Czech Republic Chance Liga", "Scotland Premiership", "Serbia Super liga Srbije", "Poland Ekstraklasa", "Croatia SuperSport HNL", "Sweden Allsvenskan", "Norway Eliteserien", "Romania SuperLiga", "Bulgaria efbet Liga", "Hungary NB I.", "Cyprus Protahlima Cyta", "Israel Ligat ha'Al", "Slovakia Nike Liga", "Azerbaijan Premyer Liqa", "Khazakstan Premier Liga", "Bosnia-Herzegovina Premijer Liga BiH", "Belarus Vysheyshaya Liga", "Slovenia Prva Liga", "Lithuania A Lyga", "Finland Veikkausliiga", "Latvia Virsliga", "Armenia Bardzraguyn khumb", "Albania Kategoria Superiore", "North Macedonia Prva liga", "Georgia Erovnuli Liga", "Kosovo Superliga e Kosovës", "Malta Premier League Opening Round", "Moldova Super Liga", "Ireland Premier Division", "Iceland Besta deild", "Northern Ireland Premiership", "Estonia Premium Liiga", "Montenegro Meridianbet 1. CFL", "Luxembourg BGL Ligue", "Andorra Primera Divisió", "Faroe Islands Betri-deildin", "Wales Cymru Premier", "Gibraltar Gibraltar Football League", "Sanmarino Camp. Sammarinese", "Malta Gozo League"],
            "SouthAmerica": ["Brazil Série A", "Argentina Liga Profesional", "Colombia Liga Dimayor I", "Chile Primera División", "Ecuador Serie A Primera Etapa", "Uruguay Primera División Apertura", "Peru Liga 1 Apertura", "Paraguay Primera División Apertura", "Bolivia División Profesional Apertura", "Venezuela Liga FUTVE Apertura"],
            "NorthCentralAmerica": ["United States MLS", "Mexico Liga MX Apertura", "Costa Rica Primera División Apertura", "Honduras Liga Nacional Apertura", "Guatemala Liga Guate Apertura", "El Salvador Primera División Apertura", "Canada CanPL", "Panama Liga Panameña Apertura", "Nicaragua Liga Primera Apertura", "Dominican Republic Liga Dominicana de Fútbol", "Jamaica Jamaica Premier League"],
            "Africa": ["South Africa Betway Premiership", "Egypt Premier League", "Morocco Botola Pro Inwi", "Argelia Ligue Professionnelle 1", "Tunisia Ligue I Pro", "Ghana Premier League", "Angola Girabola", "Mozambique Moçambola", "Uganda Premier League", "Nigeria NPFL", "Ethiopia Premier League"],
            "Asia": ["Saudi Arabia Saudi Pro League", "United Araba Emirates UAE Pro League", "Qatar Stars League", "Japan J1 League", "Korea, South K League 1", "China Super League", "Iran Persian Gulf Pro League", "Uzbekistan Superliga", "Thailand Thai League", "Indonesia Liga 1", "India Indian Super League", "Malaysia Super League", "Vietnam V.League 1", "Oman Oman Pro League", "Lebanon Leb. Premier League", "Hongkong Hong Kong Premier League", "Singapore Premier League", "Bangladesh Bangladesh PL", "Cambodia C. Premier League", "Philippines PFL", "Tajikistan Vysshaya Liga", "Chinese Taipei Football Premier League", "Myanmar National League", "Laos Lao League 1"],
            "Oceania": ["Australia A-League Men", "New Zeland National League - North", "New Zeland National League Championship", "New Zeland National League - Central", "Fiji Fiji Premier League", "New Zeland National League - South"]
    }
    
    return jsonify(continent_leagues.get(continent, []))

def convert_url_to_logo(url):
    # Split the URL by '/' and extract the identifier after 'wettbewerb'
    parts = url.split('/')
    # Find the position of 'wettbewerb' and get the next part (the identifier)
    if 'wettbewerb' in parts:
        index = parts.index('wettbewerb') + 1
        identifier = parts[index].lower()  # Make it lowercase to match the logo format

        # Construct the new URL with the identifier
        logo_url = f"https://tmssl.akamaized.net//images/logo/header/{identifier}.png"
        return logo_url
    else:
        logo_url = "static/legends/legend_icon.png"
        return logo_url
    
@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    data = request.json
    selected_leagues = data['leagues']
    
    global all_player_data
    all_player_data = []  # Reset player data
    
    # Scrape player data for each selected league
    for league_name, league_url in league_urls:  # Unpack the tuple directly
        if league_name in selected_leagues:
            team_urls = get_team_urls(league_url)
            for url in team_urls:
                league_data = scrape_data(url)
                for player in league_data:
                    player['League'] = league_name  # Add league name to player data
                    player['League_img'] = convert_url_to_logo(league_url)  # Optional if needed
                all_player_data.extend(league_data)
    
    # Filter out players where 'Market Value' is empty
    all_player_data = [player for player in all_player_data if player.get('Market Value')]

    # If no players left after filtering, handle the case
    if not all_player_data:
        return "No players found with valid Market Value.", 400
    
    # Choose a random player
    random_player = random.choice(all_player_data)
    
    # Redirect to the guessing game page, passing the data
    return render_template('guessing_game.html', all_player_data=all_player_data, random_player=random_player)



@app.route('/guessing_game')
def guessing_game():
    if not all_player_data:
        return redirect(url_for('index'))
    random_player = random.choice(all_player_data)
    return render_template('guessing_game.html', all_player_data=all_player_data, random_player=random_player)

@app.route('/check_player', methods=['POST'])
def check_player():
    data = request.json
    selected_player_name = data['selected_player']
    random_player = data['random_player']
    
    global all_player_data
    selected_player = next((player for player in all_player_data if player['Player Name'] == selected_player_name), None)

    if not selected_player:
        return jsonify({'error': 'Player not found'}), 404
    
    comparison_result = {}
    for key in selected_player.keys():
        if selected_player[key] == random_player[key]:
            comparison_result[key] = {'value': selected_player[key], 'status': 'match'}
        elif isinstance(selected_player[key], (int, float)) and isinstance(random_player[key], (int, float)):
            comparison_result[key] = {
                'value': selected_player[key],
                'status': 'higher' if selected_player[key] > random_player[key] else 'lower'
            }
        elif isinstance(selected_player[key], str) and selected_player[key].isdigit() and random_player[key].isdigit():
            comparison_result[key] = {
                'value': selected_player[key],
                'status': 'higher' if int(selected_player[key]) > int(random_player[key]) else 'lower'
            }
        else:
            comparison_result[key] = {'value': selected_player[key], 'status': 'mismatch'}
    
    return jsonify(comparison_result)

if __name__ == '__main__':
    app.run(debug=True)