# Markov Syntax Parsed Sentence Generator
### Create real seeming sentences from a text file with ease

Ever wanted to sound like your favorite celebrity, politician, or just nonsensically quote a movie?  Well you can now generate contextually appropriate sentences from any corpus!

## How it works
Markov Sentence Generator uses Markov chains and syntax parsing to choose contextually appropriate words and form them into sentences.  Based on a seed that you put into the generator, the model can generate a sentence from a document or set of documents.

### Detailed Explanation
The module is composed of three classes: SyntaxTree, MarkovDict and MarkovChain.  SyntaxTree creates the syntax parsing, MarkovDict creates the contextual dictionaries that MarkovChain puts all that together to form sentences.

SyntaxTree is untunable but does contain additional more info than in used here for future work.

(SyntaxChain runs an even more naive model, it takes sentence grammar structures and fills in words that fit those grammar structure ignoring other context.  It can get pretty silly.)

MarkovDict can be tuned using the chain_len parameter.  Chain length is the number of words in your context.  The longer the chain length, the more context you force.  Longer chain lengths are more deterministic (more similar to the original text).

MarkovChain then offers you a choice, a naive version of the chain will not take into account syntax parsing and only give context based on word presence.  A syntax version will take syntax into account.

MarkovChain has two tuning parameters that are put into the run method. Key Gram Size determines how much of the contextual phrase to pull from.  This is a bit complex.  If you set MarkovDict.chain_len to a small number, then context will be small and many possible phrases will follow the seed.  Key Gram Size determines how much of the initial context to put in the phrase.  Value Gram Size determines how much of following context to put into the phrase.

Run code.markov_chain to get a sense of how it works.

```python
python _code.markov_chain.py
```

Finally the TrueCaser class looks at a corpus and then truecases sentences.
