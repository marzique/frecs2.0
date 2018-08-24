'''wrapper for whole app package'''
from rpd_site import app


if __name__ == '__main__':
	app.run(debug=True)