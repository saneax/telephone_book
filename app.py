from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database (a dictionary to store contacts)
telephone_directory = {}

# Route to get all contacts
@app.route('/contacts', methods=['GET'])
def get_contacts():
    return jsonify(telephone_directory), 200

# Route to get a specific contact by ID
@app.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    contact = telephone_directory.get(contact_id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    return jsonify(contact), 200

# Route to add a new contact
@app.route('/contacts', methods=['POST'])
def add_contact():
    data = request.json
    if not data.get('name') or not data.get('phone'):
        return jsonify({'error': 'Name and phone are required'}), 400
    
    # Generate a new contact ID
    contact_id = len(telephone_directory) + 1
    telephone_directory[contact_id] = {
        'id': contact_id,
        'name': data['name'],
        'phone': data['phone']
    }
    return jsonify(telephone_directory[contact_id]), 201

# Route to update an existing contact
@app.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data = request.json
    contact = telephone_directory.get(contact_id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    # Update contact details
    contact['name'] = data.get('name', contact['name'])
    contact['phone'] = data.get('phone', contact['phone'])
    return jsonify(contact), 200

# Route to delete a contact
@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    contact = telephone_directory.pop(contact_id, None)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    return jsonify({'message': 'Contact deleted'}), 200

# Route to search contacts by name or phone
@app.route('/contacts/search', methods=['GET'])
def search_contact():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    results = [
        contact for contact in telephone_directory.values()
        if query in contact['name'].lower() or query in contact['phone']
    ]
    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True)