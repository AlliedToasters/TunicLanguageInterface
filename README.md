# Tunic Language Interface
This project evolved out of a personal project to decode the in-game "language" in Tunic. I suspect the language is some kind of cipher, and I settled into a workflow of hand-drawing symbols and tracking them.

Since this is an aimless personal project, I got sidetracked by the idea of automating the drawing and matching of symbols to the in-game language. This project is the result of that.

## Running the Application
As a streamlit application, you can run the application by running the following command:
```bash
streamlit run app.py
```

## Known letters and words
The in-game language consists of "words" that are made up of "letters". If you look carefully at symbols, they can all be broken down into single-character symbols. To create a "word," you need to first add all its "letters" to the dictionary. Start with the "letter creator" tab to create the "letters" and then move to the "word creator" tab to create the "words" from letters you have created. You can also add entire sequences of words, e.g. "sentences," in the "sentence creator" tab.