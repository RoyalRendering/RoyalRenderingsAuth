from flask import Flask, redirect, request, jsonify
import requests

app = Flask(__name__)

# Configuration
CLIENT_ID = "QsFCmQAx_o1wLtiCXrYWlEFlWl6ZLHqXxsCBhoqVcz1Pp2Jubhh5-2DsnpjR_wWX"
CLIENT_SECRET = "ahKXz1L_zMVqIdUk6huaNH4tjM3fBiLfmDz0a5_EVJYtkv_IDhI0A4DGxtvYv9Ph"
REDIRECT_URI = "https://royalrenderingsauth.onrender.com/oauth/callback"
TOKEN_URL = "https://www.patreon.com/api/oauth2/token"
MEMBERSHIP_URL = "https://www.patreon.com/api/oauth2/v2/identity?include=memberships"

# Root route
@app.route('/')
def home():
    return "Welcome to the Patreon OAuth Backend!"

# Login route
@app.route('/login')
def login():
    patreon_auth_url = (
        f"https://www.patreon.com/oauth2/authorize?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=identity%20identity.memberships"
    )
    return redirect(patreon_auth_url)

# OAuth callback route
@app.route('/oauth/callback')
def oauth_callback():
    # Get the authorization code from the query parameters
    code = request.args.get("code")
    if not code:
        return "Error: No authorization code provided.", 400

    # Exchange the code for an access token
    token_response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
        },
    )

    if token_response.status_code != 200:
        return f"Error: Failed to retrieve access token. Response: {token_response.text}", 400

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return f"Error: Access token not found. Response: {token_data}", 400

    # Use the access token to get the user's membership info
    headers = {"Authorization": f"Bearer {access_token}"}
    membership_response = requests.get(MEMBERSHIP_URL, headers=headers)

    if membership_response.status_code != 200:
        return f"Error: Failed to validate membership. Response: {membership_response.text}", 400

    membership_data = membership_response.json()

    # Extract relevant membership info
    user_id = membership_data["data"]["id"]
    memberships = membership_data.get("included", [])

    active_memberships = []
    for membership in memberships:
        membership_id = membership["id"]
        membership_type = membership["type"]
        active_memberships.append({"id": membership_id, "type": membership_type})

    # Return a cleaner response
    return jsonify({
        "message": "Login successful!",
        "user_id": user_id,
        "active_memberships": active_memberships,
    })

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
