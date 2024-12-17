from flask import Flask, render_template, request, jsonify, redirect, url_for
from interface import Llama, Interface
import ast
import json

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
            new_id = iface.get_id()
            return render_template('start.html', new_id=new_id)
        elif 'begin_route' in request.form:
            entered_id = request.form.get('user_id')
            if entered_id:
                # Check if entered_id exists
                cursor = iface.db.cursor()
                cursor.execute("SELECT group_id FROM cases WHERE group_id = ?", (entered_id,))
                row = cursor.fetchone()

                if row:
                    # Not new, go to final_questions
                    iface.id = int(entered_id)
                    return redirect(url_for('final_questions'))
                else:
                    # New user
                    if not iface.id:
                        iface.id = iface.get_id()
                    return render_template('questions.html')
            else:
                # No ID entered -> new user
                if not iface.id:
                    iface.id = iface.get_id()
                return render_template('questions.html')

    return render_template('start.html', new_id=new_id)

@app.route('/process_answers', methods=['POST'])
def process_answers():
    answers = request.json.get('answers', [])
    result = llama_model.run_llm(answers, prompt=1)  # prompt=1 for initial questions
    results = ast.literal_eval(result) if type(result) == str else result
    results.insert(0, iface.id)
    iface.ap = results
    return jsonify(status='ok', result=results)

@app.route('/final_questions', methods=['GET'])
def final_questions():
    return render_template('final_questions.html')

@app.route('/process_final_answers', methods=['POST'])
def process_final_answers():
    final_answers = request.json.get('final_answers', [])
    # prompt=2 for final questions
    result = llama_model.run_llm(final_answers, prompt=2)
    print(result, type(result))
    fp_results = json.loads(result)
    iface.fp = fp_results
    print(fp_results)
    return jsonify(status='ok', result=fp_results)

if __name__ == '__main__':
    app.run(port=5001, debug=False)
