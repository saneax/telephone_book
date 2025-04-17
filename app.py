from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash, check_password_hash
from tinydb import TinyDB, Query

app = Flask(__name__)
Talisman(app)  # Enforce HTTPS

auth = HTTPBasicAuth()

# In-memory user data (for the sake of simplicity; can be extended for production)
users = {
    "admin": generate_password_hash("password123")
}

# Initialize TinyDB for flat-file storage
db = TinyDB('telephone_directory.json')

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# Route to get all contacts
@app.route('/contacts', methods=['GET'])
@auth.login_required
def get_contacts():
    contacts = db.all()
    return jsonify(contacts), 200

# Route to get a specific contact by ID
@app.route('/contacts/<int:contact_id>', methods=['GET'])
@auth.login_required
def get_contact(contact_id):
    Contact = Query()
    contact = db.get(Contact.id == contact_id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    return jsonify(contact), 200

# Route to add a new contact
@app.route('/contacts', methods=['POST'])
@auth.login_required
def add_contact():
    data = request.json
    if not data.get('name') or not data.get('phone'):
        return jsonify({'error': 'Name and phone are required'}), 400
    
    # Generate a new contact ID
    contact_id = len(db) + 1
    new_contact = {
        'id': contact_id,
        'name': data['name'],
        'phone': data['phone']
    }
    db.insert(new_contact)
    return jsonify(new_contact), 201

# Route to update an existing contact
@app.route('/contacts/<int:contact_id>', methods=['PUT'])
@auth.login_required
def update_contact(contact_id):
    data = request.json
    Contact = Query()
    contact = db.get(Contact.id == contact_id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    # Update contact details
    updated_contact = {
        'id': contact_id,
        'name': data.get('name', contact['name']),
        'phone': data.get('phone', contact['phone'])
    }
    db.update(updated_contact, Contact.id == contact_id)
    return jsonify(updated_contact), 200

# Route to delete a contact
@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
@auth.login_required
def delete_contact(contact_id):
    Contact = Query()
    contact = db.get(Contact.id == contact_id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    db.remove(Contact.id == contact_id)
    return jsonify({'message': 'Contact deleted'}), 200

# Route to search contacts by name or phone
@app.route('/contacts/search', methods=['GET'])
@auth.login_required
def search_contact():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    results = [
        contact for contact in db.all()
        if query in contact['name'].lower() or query in contact['phone']
    ]
    return jsonify(results), 200

if __name__ == '__main__':
    app.run(ssl_context='adhoc', debug=True)  # Auto-generated SSL certificate for development