from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "<h1> Trần Quốc Khánh </h1>"

@app.route('/user/<name>')
def hello_user(name):
    return f"<h2>Chào bạn, {name}</h2>"

@app.route("/blog/<int:blog_id>")
def blog(blog_id):
    return f"<h2>Blog số {blog_id}"

if __name__ == '__main__':
    app.run(debug=True)