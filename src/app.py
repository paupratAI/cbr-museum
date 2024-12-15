from flask import Flask, render_template, request, jsonify
from interface import Llama, Interface 

app = Flask(__name__)

llama_model = Llama(model_name='llama3.2')
iface = Interface()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['GET', 'POST'])
def start():
    new_id = None

    if request.method == 'POST':
        if 'get_id' in request.form:
            # Use the Interface to get the next available ID from the DB
            new_id = iface.get_id()
            return render_template('start.html', new_id=new_id)
        elif 'begin_route' in request.form:
            entered_id = request.form.get('user_id')
            # Go to questions page (no answers needed yet)
            return render_template('questions.html')

    return render_template('start.html', new_id=new_id)

@app.route('/process_answers', methods=['POST'])
def process_answers():
    answers = request.json.get('answers', [])
    result = llama_model.run_llm(answers)
    return jsonify(status='ok', result=result)

if __name__ == '__main__':
    app.run(debug=True)