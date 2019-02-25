from flask import Flask 
from flask import g
from flask import render_template 

from flask import request
from flask import Response

app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'hello world!'

def main() : 
	app.debug = True
	app.run(host = '0.0.0.0' , port = 5000)

if __name__ == '__main__' :
	main()

