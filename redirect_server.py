import flask

app = flask.Flask('redirect_server')

@app.route('/authorizer/code', methods=['POST'])
def redirect_code_handler():
    print(flask.request.args.to_dict())
    return ""

@app.route('/authorizer/token', methods=['POST'])
def redirect_token_handler():
    print(flask.request.get_json())
    return ""

if __name__ == "__main__":
    app.run(debug=False, host="192.168.0.13", port=8000)
