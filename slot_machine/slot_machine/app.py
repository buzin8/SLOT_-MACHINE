import random
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ── Game constants ──────────────────────────────────────────────────────────
MAX_LINES = 3
MAX_BET   = 100
MIN_BET   = 1
ROWS      = 3
COLS      = 3

symbol_count = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8
}

symbol_value = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2
}


# ── Game logic (your original code, unchanged) ──────────────────────────────
def check_winnings(columns, lines, bet, values):
    winnings = 0
    winning_lines = []
    for line in range(lines):
        symbol = columns[0][line]
        for column in columns:
            symbol_to_check = column[line]
            if symbol != symbol_to_check:
                break
        else:
            winnings += values[symbol] * bet
            winning_lines.append(line + 1)

    return winnings, winning_lines


def get_slot_machine_spin(rows, cols, symbols):
    all_symbols = []
    for symbol, symbol_count in symbols.items():
        for _ in range(symbol_count):
            all_symbols.append(symbol)

    columns = []
    for _ in range(cols):
        column = []
        current_symbols = all_symbols[:]
        for _ in range(rows):
            value = random.choice(current_symbols)
            current_symbols.remove(value)
            column.append(value)

        columns.append(column)

    return columns


# ── Flask routes ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Serve the HTML frontend."""
    return render_template("index.html")


@app.route("/spin", methods=["POST"])
def spin():
    """
    The browser sends:  { "lines": 1-3, "bet": 1-100, "balance": <int> }
    Flask sends back:   { "columns": [...], "winnings": <int>, "winning_lines": [...] }
    """
    data    = request.get_json()
    lines   = int(data.get("lines", 1))
    bet     = int(data.get("bet", 1))
    balance = int(data.get("balance", 0))

    # Validate inputs
    if not (1 <= lines <= MAX_LINES):
        return jsonify({"error": f"Lines must be between 1 and {MAX_LINES}"}), 400
    if not (MIN_BET <= bet <= MAX_BET):
        return jsonify({"error": f"Bet must be between ${MIN_BET} and ${MAX_BET}"}), 400

    total_bet = bet * lines
    if total_bet > balance:
        return jsonify({"error": "You do not have enough balance for this bet"}), 400

    # Run your original game logic
    columns = get_slot_machine_spin(ROWS, COLS, symbol_count)
    winnings, winning_lines = check_winnings(columns, lines, bet, symbol_value)

    return jsonify({
        "columns":       columns,        # e.g. [["A","B","C"], ["A","D","B"], ["A","C","D"]]
        "winnings":      winnings,       # e.g. 25
        "winning_lines": winning_lines   # e.g. [1]  (1-indexed)
    })


if __name__ == "__main__":
    app.run(debug=True)
