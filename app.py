from flask import Flask, render_template, request

app = Flask(__name__)

# In-memory counter for new users, just as an example
current_id = 1000

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['GET', 'POST'])
def start():
    global current_id
    new_id = None

    if request.method == 'POST':
        if 'get_id' in request.form:
            # Generate a new ID and display it
            current_id += 1
            new_id = current_id
        elif 'begin_route' in request.form:
            entered_id = request.form.get('user_id')
            # In a real scenario, load user's preferences and redirect.
            # For now, just show a confirmation message.
            return f"Route started with ID: {entered_id}"

    return render_template('start.html', new_id=new_id)

if __name__ == '__main__':
    app.run(debug=True)
