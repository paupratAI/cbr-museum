from flask import Flask, render_template, request

app = Flask(__name__)

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
            # Generate a new ID and display it in start.html
            current_id += 1
            new_id = current_id
            return render_template('start.html', new_id=new_id)
        elif 'begin_route' in request.form:
            entered_id = request.form.get('user_id')
            # Instead of printing a message, go to questions.html
            # You can store entered_id in session or database if needed
            return render_template('questions.html')

    # If it's a GET request or no action triggered
    return render_template('start.html', new_id=new_id)

if __name__ == '__main__':
    app.run(debug=True)
