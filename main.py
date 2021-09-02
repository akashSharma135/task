from todo_app import create_app

# instantiating the flask app
app = create_app()

# running the app
if __name__ == '__main__':
    app.run(debug=True)