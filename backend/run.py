from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True automatically reloads the server when you save changes
    app.run(debug=True, port=5000)