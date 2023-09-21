# German Translator
This is a *very* hacky server/client chrome extension I made when I decided
I wanted to learn German. It translates parts of sentences into German so that
I could pick up some German words while reading mostly English.

The translation works by first using Facebook's M2M100 model to translate
the English sentences (sped up with CTranslate2), next using SentencePiece
to align the original English words with the translated German words, and
finally randomly selecting some English words to replace with the equivalent
words/phrases in German.

This was very much a project intended for *me* and is likely to be very hard
to set up on your own. If you're interested in using this for yourself, you
can reach out to me at camacho.joseph@gmail.com and I'll try to help you get
it set up (and probably also update this repository to be easier to set up.
