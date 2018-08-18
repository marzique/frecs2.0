from flask import Flask, render_template

app = Flask(__name__)

news = [
	{'Author': 'Denys Tarnavskyi',
	 'Title': 'Title Post1',
	 'Date': '18, Aug, 2018',
	 'Content': 'Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.' \
				' Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna ' \
				'aliquam erat volutpat. '},

	{'Author': 'Ihor Beh',
	 'Title': 'Title Post2',
	 'Date': '15, Aug, 2018',
	 'Content': 'Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis.'
	}
]

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
