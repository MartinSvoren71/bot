

from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "super_secret_key"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]

        if password == "correct_password":
            session["logged_in"] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=1)
            return redirect(url_for("index"))
        else:
            flash("Bad key provided")
            return redirect(url_for("bad_key"))

    return render_template("login.html")

@app.route("/bad_key")
def bad_key():
    return render_template("badkey.html")

@app.route("/index")
def index():
    if "logged_in" in session:
        return render_template("indexSplit.html")
    else:
        flash("Please log in first")
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
    
    
@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    theme = request.form['theme']
    key = request.form['key']
    if question.strip().lower() == 'exit':
        return redirect(url_for('indexSplit'))
    elif key == 'xxx007':
        response = ask_ai(question, theme)
        return render_template('indexSplit.html', question=question, theme=theme, response=response, key=key)
    else:
        return redirect(url_for('wrong_key'))

t = Thread(target=initialize_ai)
t.start()
app.run(host='0.0.0.0', port='5000')
