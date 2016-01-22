from flask import Flask, request, render_template
import cPickle as pickle
from _code.markov_dict import MarkovDict
from _code.markov_chain import MarkovChain


application = Flask(__name__)

with open('data/neighbours.pkl') as f:
    neighbor_dict = pickle.load(f)

priority_list = ['america', 'democracy', 'terrorism']
not_found_list = [
    'Change will not come if we wait for some other person or some other time. We are the ones we\'ve been waiting for. We are the change that we seek.',
    'If you\'re walking down the right path and you\'re willing to keep walking, eventually you\'ll make progress.',
    'The future rewards those who press on. I don\'t have time to feel sorry for myself. I don\'t have time to complain. I\'m going to press on.',
    'I don\'t oppose all wars. What I am opposed to is a dumb war. What I am opposed to is a rash war.',
    'There\'s not a liberal America and a conservative America - there\'s the United States of America.'
]

md = MarkovDict('data/obama_corpus.txt', 3)
mc = MarkovChain(md.api, priority_list, not_found_list, neighbor_dict)


# Main page
@application.route('/')
def index():
    return'''
    <form action="/results" method='POST' >
        <input type="text" name="user_input" />
        <input type="submit" />
    </form>
        '''
# Results page
@application.route('/results', methods=['POST'])
def results():
    word = str(request.form['user_input'])
    sentence = mc.run(word, 2, 1)
    return sentence

# Api page
@application.route('/api/v0/')
def get_statement():
    word = request.args['q']
    sentence = mc.run(word, 2, 1)
    return sentence

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080, debug=True)
