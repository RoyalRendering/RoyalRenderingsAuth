from flask import Flask, redirect, request, render_template
import requests

app = Flask(__name__)

# Configuration
CLIENT_ID = "QsFCmQAx_o1wLtiCXrYWlEFlWl6ZLHqXxsCBhoqVcz1Pp2Jubhh5-2DsnpjR_wWX"
CLIENT_SECRET = "ahKXz1L_zMVqIdUk6huaNH4tjM3fBiLfmDz0a5_EVJYtkv_IDhI0A4DGxtvYv9Ph"
REDIRECT_URI = "https://royalrenderingsauth.onrender.com/oauth/callback"
TOKEN_URL = "https://www.patreon.com/api/oauth2/token"
MEMBERSHIP_URL = "https://www.patreon.com/api/oauth2/v2/identity?include=memberships"

# Root route with a login button
@app.route('/')
def home():
    return render_template("home.html")

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
    # Get the authorization code
    code = request.args.get("code")
    if not code:
        return render_template("error.html", message="No authorization code provided.")

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
        return render_template("error.html", message="Failed to retrieve access token.")

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return render_template("error.html", message="Access token not found.")

    # Fetch user identity and memberships
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(MEMBERSHIP_URL, headers=headers)

    if user_response.status_code != 200:
        return render_template("error.html", message="Failed to validate membership.")

    user_data = user_response.json()

    # Extract user info
    user_info = user_data.get("data", {})
    user_name = user_info.get("attributes", {}).get("full_name", "Unknown User")
    user_profile_pic = user_info.get("attributes", {}).get("image_url", "")
    memberships = user_data.get("included", [])

    # Extract active memberships
    active_tiers = [
        membership.get("attributes", {}).get("currently_entitled_tier", {}).get("title", "No Tier")
        for membership in memberships
        if membership.get("attributes", {}).get("currently_entitled_tier")
    ]

    # Pass the data to the success page
    return render_template(
        "success.html",
        user_name=user_name,
        user_profile_pic=user_profile_pic,
        active_tiers=active_tiers,
    )

    if active_tiers:
        return render_template("success.html", tiers=active_tiers)
    else:
        return render_template("error.html", message="No active memberships found.")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)


