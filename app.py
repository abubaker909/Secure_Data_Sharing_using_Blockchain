from flask import Flask, render_template, request, jsonify
import hashlib
import json
from time import time
from uuid import uuid4

app = Flask(__name__)

# Initialize the blockchain
blockchain = []

def hash_block(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def proof_of_work(last_proof):
    proof = 0
    while not valid_proof(last_proof, proof):
        proof += 1
    return proof

def valid_proof(last_proof, proof):
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"  # Adjust difficulty by changing the number of leading zeros



@app.route('/mine')
def mine():
    # Proof of Work
    last_block = blockchain[-1] if blockchain else {}
    last_proof = last_block.get('proof', 0)
    proof = proof_of_work(last_proof)

    # Create a new block
    block = {
        'index': len(blockchain) + 1,
        'timestamp': time(),
        'proof': proof,
        'previous_hash': hash_block(last_block),
        'transactions': []  # You can add transactions here
    }

    # Add the block to the blockchain
    blockchain.append(block)

    # Mining reward (for simplicity, you can add more details like sender and recipient)
    block['transactions'].append({
        'sender': '0',
        'recipient': str(uuid4()),
        'amount': 1,
        'data': 'Mining Reward',
        'signature': ''
    })

    return jsonify({
        'message': 'New block mined!',
        'index': block['index'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    })
@app.route('/transaction')
def transaction():
    return render_template('transaction.html', chain=blockchain)

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    try:
        # Get transaction data from the request
        data = request.get_json()

        # Check if the required fields are present
        required_fields = ['sender', 'recipient', 'data', 'signature']
        if not all(field in data for field in required_fields):
            return 'Missing fields', 400

        # Create a new transaction
        index = len(blockchain) + 1
        timestamp = time()
        transactions = {
            'sender': data['sender'],
            'recipient': data['recipient'],
            'data': data['data'],
            'signature': data['signature']
        }

        # Add the transaction to the current block
        if blockchain:
            current_block = blockchain[-1]
            current_block['transactions'].append(transactions)

            return jsonify({'message': f'Transaction will be added to Block {index}'})

        else:
            return 'No existing blockchain. Mine a block first.', 400
    except Exception as e:
        return f'Error: {str(e)}', 400



@app.route('/chain')
def full_chain():
    return render_template('chain.html', chain=blockchain)
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
