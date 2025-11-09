import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///herblify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(200), nullable=False)
    scientific_name = db.Column(db.String(200), nullable=False)
    uses = db.Column(db.Text, nullable=False)
    habitat = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'common_name': self.common_name,
            'scientific_name': self.scientific_name,
            'uses': self.uses,
            'habitat': self.habitat,
            'category': self.category
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search.html', plants=[], query='')
    
    plants = Plant.query.filter(
        or_(
            Plant.common_name.ilike(f'%{query}%'),
            Plant.scientific_name.ilike(f'%{query}%')
        )
    ).limit(50).all()
    
    return render_template('search.html', plants=plants, query=query)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    plants = Plant.query.filter(
        or_(
            Plant.common_name.ilike(f'%{query}%'),
            Plant.scientific_name.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify([plant.to_dict() for plant in plants])

@app.route('/plant/<int:plant_id>')
def plant_detail(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    return render_template('plant_detail.html', plant=plant)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
