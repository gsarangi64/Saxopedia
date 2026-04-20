#!usr/bin/env python3
from flask import Flask, render_template
from services import load_repertoire, fetch_composer
app = Flask(__name__)

@app.route("/")
def index():
    data = load_repertoire()
    return render_template("index.html", data=data)

@app.route("/repertoire")
def repertoire():
    data = load_repertoire()
    return render_template("repertoire.html", repertoire=data)

@app.route("/composer/<name>")
def composer(name):
    composer = fetch_composer(name)
    return render_template("composer.html", composer=composer)

if __name__ == '__main__':
    app.run(debug=True)