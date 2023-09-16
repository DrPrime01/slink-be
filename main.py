from core.models import init_db
from core import app
from core import routes
from flask_cors import CORS

CORS(app)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
