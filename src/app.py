from flask import Flask, render_template, request, jsonify, redirect, url_for
from interface import Llama, Interface
import ast
import json
from ontology.art import artworks
from entities import AbstractSolution
import copy
from museum import run_and_plot

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
                cursor.execute("SELECT group_id FROM train_cases WHERE group_id = ?", (entered_id,))
                row = cursor.fetchone()

                if row:
                    cursor.execute("""SELECT num_people, minors, guided_visit, num_experts, past_museum_visits, preferred_year, preferred_main_theme, preferred_author_name, group_description
                                      FROM train_cases WHERE group_id = ?""", (entered_id,))
                    data_row = cursor.fetchone()
                    # Not new, go to final_questions
                    iface.id = int(entered_id)
                    iface.ap = [iface.id] + list(data_row)
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

def cut_route(time, recommendation):
    """
    Parameters:
    time: int
        The time available for the visit
    recommendation: list of artwork ids complete
    The recommendation neeeds to be adjusted. We are going to remove the artworks that exceed the time available
        """
    recommendations = recommendation[0]
    filtered_recommendations = [] 

    for id_artwork in recommendations:
        artwork = artworks[id_artwork]
        time -= artwork.default_time
        if time >= 0:  
            # Enough time to consider this artwork
            filtered_recommendations.append(id_artwork)
        else:
            # No time left
            break
    recommendation[0][:] = filtered_recommendations 
        

@app.route('/route', methods=['GET'])
def route_page():
    # We assume iface.ap and iface.fp now contain all needed info
    # iface.ap: answers from first questions
    # iface.fp: answers from final questions

    # Let's say iface.ap and iface.fp look like this:
    # iface.ap = [group_id, people, yes/no guided, ... etc from first prompt]
    # iface.fp = [days, hours, reduced_mobility_boolean]
    # You may need to combine them or build the AbstractProblem from them

    # For demonstration, let's assume ap is already built or can be built:
    # If not, you can create a method to build AbstractProblem from iface.ap and iface.fp.
    # For now, let's just call recommend with the known group_id = iface.id
    # You might need to adapt how you call recommend:
    # Let's say recommend needs: target_group_id and clean_response
    # clean_response = iface.ap or a combination of iface.ap and iface.fp, depending on how you designed it.
    """
    clean_response
    		group_id=int(clean_response[0]),
			num_people=int(clean_response[1]),
			favorite_author=clean_response[2],
			favorite_period=int(clean_response[3]),
			favorite_theme=clean_response[4],
			guided_visit=bool(int(clean_response[5])),
			minors=bool(int(clean_response[6])),
			num_experts=int(clean_response[7]),
			past_museum_visits=int(clean_response[8]),
			group_description=clean_response[9]
    """
    """
    iface.ap = [num_people, childre, guided_visit, experts, visited_museums, period, theme, author, description]
    """
    #Now we'll have to coincide the desire clean response with the iface.ap
    clean_response = [iface.ap[0], iface.ap[1], iface.ap[8], iface.ap[6], iface.ap[7], iface.ap[3], iface.ap[2], iface.ap[4], iface.ap[5], iface.ap[9]]
    iface.clean_response = clean_response

    # Suppose that you also need to incorporate the final questions (days, hours, mobility) into the route planning
    # You can append or integrate them into clean_response if needed, depending on your logic:
    # For example: clean_response.append(iface.fp[0]) # days
    # clean_response.append(iface.fp[1]) # hours
    # clean_response.append(iface.fp[2]) # mobility boolean
    # Adjust based on your system's logic

    # Now call recommend:
    recommendations = iface.recommender.recommend(target_group_id=iface.id, clean_response=clean_response)
    print(len(recommendations['cf'][0]))

    # We do a copy of recommendations to avoid modifying the original
    recommendations_c = copy.deepcopy(recommendations)
    iface.route_c = recommendations_c

    time = (iface.fp[0] * 1)*60
    iface.time = time
    
    for recommendation in recommendations.values():
        cut_route(time, recommendation)
    

    iface.route_to_plot = copy.deepcopy(recommendations)

    for recommendation in recommendations.values():
        for i, id_artwork in enumerate(recommendation[0]):
            artwork = artworks[id_artwork]
            recommendation[0][i] = artwork.artwork_name
    iface.route = recommendations

    # recommendations is a dict with keys "cf", "cbr", "hybrid"
    # Each is a list of artwork IDs

    return render_template('route.html', recommendations=recommendations)

@app.route('/select_route', methods=['POST'])
def select_route():
    data = request.get_json()
    route_type = data.get('route')
    iface.route_type = route_type
    run_and_plot(iface.route_to_plot[iface.route_type][0], bool(int(iface.fp[1])) )
    # Aquí podrías guardar la selección en la DB si quieres
    # Por ahora solo devolvemos ok
    return jsonify(status='ok')

@app.route('/feedback', methods=['GET'])
def feedback():
    return render_template('feedback.html')

@app.route('/process_feedback', methods=['POST'])
def process_feedback():
    user_feedback = request.form.get('user_feedback', '')
    user_rating = request.form.get('user_rating', '0')

    iface.user_feedback = user_feedback
    iface.user_rating = float(user_rating)

    return jsonify(status='ok')

@app.route('/goodbye', methods=['GET'])
def goodbye():
    _, ap = iface.recommender.convert_to_problems(iface.clean_response)
    abs_sol = AbstractSolution(related_to_AbstractProblem=ap)
    artworks_list = [artworks[artwork_id] for artwork_id in artworks]
    abs_sol.compute_matches(artworks=artworks_list)
    sorted_matches = sorted(abs_sol.matches, key=lambda m: m.match_type, reverse=True)
    # We redifine the variable from a list of matches to a list of match types
    sorted_matches = [m.match_type for m in sorted_matches]

    new_case = {
    'num_people': int(iface.clean_response[1]),
    'preferred_author_name': iface.clean_response[2],
    'preferred_year': int(iface.clean_response[3]),
    'preferred_main_theme': iface.clean_response[4],
    'guided_visit': int(iface.clean_response[5]),
    'minors': int(iface.clean_response[6]),
    'num_experts': int(iface.clean_response[7]),
    'past_museum_visits': int(iface.clean_response[8])
    }
    cluster_id = iface.recommender.clustering_system.classify_new_case(new_case)

    print(len(sorted_matches))
    print(len(iface.route_c[iface.route_type][0]))

    count = len(iface.route_c[iface.route_type])
    iface.recommender.store_case(clean_response=iface.clean_response, 
                                 visited_artworks_count=count,
                                 ordered_artworks=iface.route_c[iface.route_type][0],
                                 ordered_artworks_matches=sorted_matches,
                                 rating=iface.user_rating,
                                 textual_feedback=iface.user_feedback,
                                 cluster=cluster_id,
                                 time_limit=iface.time,)
    return render_template('goodbye.html')


if __name__ == '__main__':
    app.run(port=5001, debug=False)