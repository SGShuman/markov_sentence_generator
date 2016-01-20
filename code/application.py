from flask import Flask, request, render_template
from chain_builder import get_sentence
import cPickle as pickle
from markov_dict import MarkovDict
from markov_chain import MarkovChain


application = Flask(__name__)
application.debug = True

with open('data/neighbours.pkl') as f:
    neighbor_list = pickle.load(f)

priority_list = ['america', 'democracy', 'terrorism']
not_found_list = ['not_found_list_1']

md = MarkovDict('data/obama_corpus.txt', 3)
mc = MarkovChain(md.api, priority_list, not_found_list, neighbor_list)


# Main page
@application.route('/')
def index():
    return render_template("index.html")

# predict page
@application.route('/api/v0/')
def get_statement():

    word = request.args['q']
    sentence = mc.run(word, 2, 1)
    return sentence
    
if __name__ == '__main__':
    application.run()