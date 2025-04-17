from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import random

app = Flask(__name__)
app.secret_key = "ghostly-secret"

BOARD_SIZE = 20

def init_game():
    positions = list(range(1, BOARD_SIZE - 1))  # exclude enter (0) and finish (19)

    evil_ghosts = random.sample(positions, 3)
    remaining = list(set(positions) - set(evil_ghosts))
    friendly_ghosts = random.sample(remaining, 3)

    session['board'] = {
        'evil_ghosts': evil_ghosts,
        'friendly_ghosts': friendly_ghosts
    }
    session['players'] = {
        'red': 0,
        'blue': 0
    }
    session['turn'] = 'red'
    session['winner'] = None

import random

def roll_dice():
    return random.randint(1, 6)

def move_player(player, roll):
    new_position = player['position'] + roll
    if new_position >= len(board):
        new_position = len(board) - 1  # Ensure player doesn't exceed board length

    space = board[new_position]
    if space == 'friendly_ghost':
        bonus_roll = roll_dice()
        new_position += bonus_roll
        if new_position >= len(board):
            new_position = len(board) - 1
    elif space == 'evil_ghost':
        penalty_roll = roll_dice()
        new_position -= penalty_roll
        if new_position < 0:
            new_position = 0

    player['position'] = new_position
    return new_position


@app.route('/')
def index():
    if 'board' not in session:
        init_game()
    return render_template('index.html',
                           board=session['board'],
                           players=session['players'],
                           turn=session['turn'],
                           winner=session['winner'])

@app.route('/roll', methods=['POST'])
def roll():
    if session.get('winner'):
        return jsonify({'error': 'Game already over.'}), 400

    current_player = session['turn']
    other_player = 'blue' if current_player == 'red' else 'red'
    roll_value = random.randint(1, 6)
    pos = session['players'][current_player]
    board = session['board']

    new_pos = pos + roll_value
    if new_pos >= BOARD_SIZE - 1:
        session['players'][current_player] = BOARD_SIZE - 1
        session['winner'] = current_player
        return jsonify({
            'roll': roll_value,
            'new_position': BOARD_SIZE - 1,
            'effect': 'finish',
            'winner': current_player
        })

    effect = None
    if new_pos in board['friendly_ghosts']:
        effect = 'friendly'
        roll_bonus = random.randint(1, 6)
        new_pos = min(BOARD_SIZE - 1, new_pos + roll_bonus)
    elif new_pos in board['evil_ghosts']:
        effect = 'evil'
        roll_penalty = random.randint(1, 6)
        new_pos = max(0, new_pos - roll_penalty)

    session['players'][current_player] = new_pos

    if new_pos == BOARD_SIZE - 1:
        session['winner'] = current_player
        return jsonify({
            'roll': roll_value,
            'new_position': new_pos,
            'effect': effect,
            'winner': current_player
        })

    session['turn'] = other_player

    return jsonify({
        'roll': roll_value,
        'new_position': new_pos,
        'effect': effect,
        'next_turn': other_player
    })

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

