from flask import Flask, render_template, session, request, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = 'secret'

# Initialize game board
spaces = ["Enter"] + ["Space " + str(i) for i in range(2, 20)] + ["Finish"]

# Randomly integrate ghosts
def initialize_game():
    evil_ghosts = random.sample(range(1, 19), 3)
    friendly_ghosts = random.sample([x for x in range(1, 19) if x not in evil_ghosts], 3)
    return evil_ghosts, friendly_ghosts

evil_ghosts, friendly_ghosts = initialize_game()

@app.route('/')
def index():
    session['player1_pos'] = 0
    session['player2_pos'] = 0
    session['turn'] = 1
    return render_template('game.html', spaces=spaces, evil_ghosts=evil_ghosts, friendly_ghosts=friendly_ghosts)

@app.route('/roll', methods=['POST'])
def roll():
    dice_roll = random.randint(1, 6)
    if session['turn'] == 1:
        session['player1_pos'] = min(session['player1_pos'] + dice_roll, 19)
        pos = session['player1_pos']
        if pos in friendly_ghosts:
            session['player1_pos'] = min(session['player1_pos'] + random.randint(1, 6), 19)
        elif pos in evil_ghosts:
            session['player1_pos'] = max(session['player1_pos'] - random.randint(1, 6), 0)
        if pos == 19:
            session['winner'] = "Player 1 wins!"
            return redirect(url_for('end_game'))
        session['turn'] = 2
    else:
        session['player2_pos'] = min(session['player2_pos'] + dice_roll, 19)
        pos = session['player2_pos']
        if pos in friendly_ghosts:
            session['player2_pos'] = min(session['player2_pos'] + random.randint(1, 6), 19)
        elif pos in evil_ghosts:
            session['player2_pos'] = max(session['player2_pos'] - random.randint(1, 6), 0)
        if pos == 19:
            session['winner'] = "Player 2 wins!"
            return redirect(url_for('end_game'))
        session['turn'] = 1
    return redirect(url_for('index'))

@app.route('/end')
def end_game():
    winner = session.get('winner', '')
    return render_template('end.html', winner=winner)

if __name__ == '__main__':
    app.run(debug=True)

