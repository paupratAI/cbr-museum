from flask import Flask, render_template, request, jsonify
from src.llama import Llama

app = Flask(__name__)

# In-memory counter for new users, just as an example
current_id = 1000

# Instantiate the Llama class
llama_model = Llama(model_name='llama3.2')

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
            # Go to questions page (no answers needed yet)
            return render_template('questions.html')

    # If it's a GET request or no action triggered
    return render_template('start.html', new_id=new_id)

@app.route('/process_answers', methods=['POST'])
def process_answers():
    # answers expected as JSON
    answers = request.json.get('answers', [])
    # Use the Llama model to run the LLM with the given answers
    result = llama_model.run_llm(answers)
    return jsonify(status='ok', result=result)

if __name__ == '__main__':
    app.run(debug=True)
