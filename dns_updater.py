import os
from flask import Flask, request, render_template_string, redirect, url_for, session
from dotenv import load_dotenv
from cloudflare import Cloudflare

# Load environment variables from .env file
load_dotenv()

# Ensure the environment variables are set externally before running the script
if not os.environ.get("CLOUDFLARE_EMAIL") or not os.environ.get("CLOUDFLARE_API_KEY"):
    raise EnvironmentError("Please set the CLOUDFLARE_EMAIL and CLOUDFLARE_API_KEY environment variables.")

# Setup Cloudflare client
client = Cloudflare(
    api_email=os.environ.get("CLOUDFLARE_EMAIL"),
    api_key=os.environ.get("CLOUDFLARE_API_KEY"), 
)

# Get zone_id and name filter from environment variables
zone_id = os.environ.get("CLOUDFLARE_ZONE_ID")
name_filter = os.environ.get("CLOUDFLARE_NAME_FILTER")

# Create a Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

def get_visitor_ip():
    """Get the visitor's IP address from the X-Forwarded-For header or remote_addr."""
    return request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

def get_dns_ip():
    """Fetch the current IP address from the DNS record."""
    page = client.dns.records.list(
        zone_id=zone_id,
        name={"contains": name_filter}
    )
    record = page.result[0]
    return record

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == os.environ.get("ADMIN_USERNAME") and password == os.environ.get("ADMIN_PASSWORD"):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid credentials", 401
    return render_template_string('''
        <form method="post">
            <p><input type=text name=username placeholder="Username">
            <p><input type=password name=password placeholder="Password">
            <p><input type=submit value=Login>
        </form>
    ''')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Define the index route
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    visitor_ip = get_visitor_ip()
    record = get_dns_ip()
    current_ip = record.content
    dns_name = record.name

    return render_template_string('''
        <h1>Update DNS Record</h1>
        <p>Updating: {{ dns_name }}</p>
        <p>Current DNS IP: {{ current_ip }}</p>
        <p>Your IP: {{ visitor_ip }}</p>
        <form action="/update" method="post">
            <button type="submit">Update DNS Record with My IP</button>
        </form>
        <a href="/logout">Logout</a>
    ''', dns_name=dns_name, current_ip=current_ip, visitor_ip=visitor_ip)

# Define the update route
@app.route('/update', methods=['POST'])
def update_dns():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    visitor_ip = get_visitor_ip()
    record = get_dns_ip()
    record_id = record.id
    record_content = record.content

    # Update the DNS record
    client.dns.records.edit(
        dns_record_id=record_id,
        zone_id=zone_id,
        content=visitor_ip
    )
    return render_template_string('''
        <h1>DNS Record Updated</h1>
        <p>DNS record {{ record_name }} updated with IP: {{ visitor_ip }}</p>
        <p>Previous IP: {{ record_content }}</p>
        <a href="/">Back to Index</a>
    ''', record_name=record.name, visitor_ip=visitor_ip, record_content=record_content)

if __name__ == '__main__':
    app.run(host='0.0.0.0')