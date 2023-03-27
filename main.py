from flask import Flask, redirect, url_for, render_template, request
import requests

app = Flask(__name__)

user = {}
server_url = 'http://127.0.0.1:8000/'

@app.route('/')
def index():
    return redirect(url_for('auth'))


@app.route('/auth', methods=('GET', 'POST'))
def auth():
    global user
    
    if request.method == 'POST':
        if 'log_in' in request.form:
            user = {'user_name': request.form['user_name'], 'password': request.form['password']}
            
        elif 'register' in request.form:
            user = {'user_name': request.form['user_name'], 'password': request.form['password']}
            server('register', user)
            
        else:
            print(request.form)
            
        return redirect(url_for('balance'))
    
    else:
        return render_template('auth.html', title = 'Account', user = user)


@app.route('/balance', methods=('GET', 'POST'))
def balance():
    if request.method == 'POST':
        server('reload_balance', user)
        
    bal = {}
    bal_sum = 0
    if user:
        bal = server('balance', user)
        for crypto in bal:
            if crypto == 'USDT':
                bal_sum += bal[crypto]
                continue
            bal_sum += server('price', {'first_crypto': crypto, 'second_crypto': 'USDT'})['price'] * bal[crypto]
    return render_template('balance.html', title='Balance', balance = bal, balance_sum = round(bal_sum, 3))


@app.route('/exchange', methods=('GET', 'POST'))
def exchange():
    pair = {'first_crypto': 'BTC', 'second_crypto': 'USDT'}
    if request.method == 'POST':
        if 'check_price' in request.form:
            pair['first_crypto'] = request.form['first_crypto']
            pair['second_crypto'] = request.form['second_crypto']
        else:
            pair['first_crypto'] = request.form['first_crypto']
            pair['second_crypto'] = request.form['second_crypto']
            
            value = request.form['first_crypto_value']
            
            if "buy" in request.form:
                server('buy', {**user, **pair, 'value': value})
            if "sell" in request.form:
                server('sell', {**user, **pair, 'value': value})
                
            return redirect(url_for('balance'))
            
    
    return render_template('exchange.html', title='Exchange', pair = pair, price = server('price', pair)['price'])


def server(action:str, params):
    data = requests.get(server_url + action, params=params)
    data = data.json()
    
    print(data)
    
    if data['status'] != 'ok':
        return {}
    
    data.pop('status')
    return data


if __name__ == '__main__':
    app.run(debug=True)