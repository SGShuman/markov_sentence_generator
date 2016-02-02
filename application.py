from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import cPickle as pickle
from _code.markov_dict import MarkovDict
from _code.markov_chain import MarkovChain

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/recommend", methods=['POST'])
def recommend():
    user_input = str(request.form['seed'])
    sent = mc.run(user_input, 2, 3)

    return render_template('index.html', recommend=True, sent=sent)

if __name__ == '__main__':

    with open('data/neighbours.pkl') as f:
        neighbor_dict = pickle.load(f)

    md = MarkovDict('data/obama_corpus.txt', 4, gtype='syntax_pos')
    mc = MarkovChain(md.api, neighbor_dict)

    app.run(host='0.0.0.0', port=8080, debug=True)
