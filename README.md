# Markov Sentence Generator
### Create real seeming sentences from a text file with ease

Ever wanted to sound like your favorite celebrity, politician, or just nonsensically quote a movie?  Well you can now generate contextually appropriate sentences from any corpus!

## How it works
Markov Sentence Generator uses Markov chains to choose contextually appropriate words and form them into sentences.  Based on a seed that you put into the generator, the model can generate a sentence from a document or set of documents.

### Tuning
The module is composed of two classes: MarkovDict and MarkovChain.  MarkovDict creates the contextual dictionaries that MarkovChain puts together to form sentences.

MarkovDict can be tuned using the chain_len parameter.  Chain length is the number of words in your context.  The longer the chain length, the more context your force.  Larger chain lengths are more deterministic (more similar to the original text).

MarkovChain has two possible tuning parameters that are put into the run method. Key Gram Size determines how much of the contextual phrase to pull from.  This is a bit complex.  If you set MarkovDict.chain_len to a small number, then context will be small and many possible phrases will follow the seed.  Key Gram Size determines how much of the initial context to put in the phrase.  Value Gram Size determines how much of following context to put into the phrase.
