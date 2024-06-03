from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def query():
    x=2
    return render_template('query.html', x=x)


if __name__ == '__main__':
    app.run()
