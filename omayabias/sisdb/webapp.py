import bottle

app = bottle.app()

@bottle.route('/hello')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(app=app, host='localhost', port=8080, debug=True)
