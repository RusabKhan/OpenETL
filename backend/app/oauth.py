import os
import sys

from fastapi import HTTPException, Query, Depends, APIRouter
from fastapi.responses import RedirectResponse
import datetime

sys.path.append(os.environ['OPENETL_HOME'])
from utils.main_api_class import OAuth2Client
from utils.database_utils import DatabaseUtils


router = APIRouter(prefix="/auth", tags=["auth"])

# Endpoint: Start OAuth2 Flow (Dynamic Client Initialization)
@router.get("/oauth-login/")
def start_oauth_flow(
    client_id: str = Query(...),
    client_secret: str = Query(...),
    auth_url: str = Query(...),
    token_url: str = Query(...),
    redirect_uri: str = Query(...),
    scope: list[str] = Query(...),
    connection_id: str = Query(...),
):
    """
    Create an OAuth2 client dynamically and redirect the user to the provider's OAuth2 authorization page.
    """
    oauth_client = OAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        auth_url=auth_url,
        token_url=token_url,
        redirect_uri=redirect_uri,
        scope=scope,
    )
    authorization_url = oauth_client.get_authorization_url() + f"&connection_id={connection_id}"
    return RedirectResponse(url=authorization_url)


# Endpoint: OAuth2 Callback
@router.get("/callback/")
def oauth_callback(
    code: str = Query(...),
    client_id: str = Query(...),
    client_secret: str = Query(...),
    token_url: str = Query(...),
    redirect_uri: str = Query(...),
    scope: list[str] = Query(...),
    connection_id: str = Query(...),
):
    """
    Handle the OAuth2 callback dynamically, exchange the authorization code for tokens,
    and save them in the database.
    """
    try:
        # Create a dynamic OAuth2 client
        oauth_client = OAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            auth_url="",  # Not needed for token exchange
            token_url=token_url,
            redirect_uri=redirect_uri,
            scope=scope,
        )

        # Exchange the authorization code for tokens
        tokens = oauth_client.get_access_token(authorization_code=code)

        # Extract token data
        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in", 3600)  # Default to 1 hour if not provided
        expiry_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

        # Save tokens to the database
        if DatabaseUtils(engine=os.getenv('OPENETL_DOCUMENT_ENGINE'),
                      hostname=os.getenv('OPENETL_DOCUMENT_HOST'),
                      port=os.getenv('OPENETL_DOCUMENT_PORT'),
                      username=os.getenv('OPENETL_DOCUMENT_USER'),
                      password=os.getenv('OPENETL_DOCUMENT_PASS'),
                      database=os.getenv('OPENETL_DOCUMENT_DB')).save_oauth_token(access_token, refresh_token,
                                                                                  expiry_time, scope, connection_id):
            return {"message": "OAuth tokens saved successfully."}
        else:
            return {"message": "Failed to save OAuth tokens."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error during OAuth2 callback: {str(e)}")
