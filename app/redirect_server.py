import flask

app = flask.Flask('redirect_server')

code = ''
access_token = ''

@app.route('/', methods=['GET'])
def draw_gui():
    url_prefix = flask.request.base_url
    
    return flask.render_template(
        template_name_or_list='redirect_gui.html',
        code=code,
        access_token=access_token,
        fav32=f'{url_prefix}/static/img/favicon-32x32.png',
        fav16=f'{url_prefix}/static/img/favicon-16x16.png'
    )

@app.route('/authorizer/code', methods=['POST'])
def redirect_code_handler():
    global code
    args =  flask.request.args.to_dict()
    print(args)
    code = args['code']
    return ""

@app.route('/authorizer/token', methods=['POST'])
def redirect_token_handler():
    global access_token
    args = flask.request.get_json()
    print(args)
    access_token = args['access_token']
    return ""

if __name__ == "__main__":
    app.run(debug=False, host="192.168.0.13", port=8000)
