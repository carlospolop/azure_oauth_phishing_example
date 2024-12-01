# azure_oauth_phishing_example

This is an example of how to use Azure ENtra ID Applications OAuth to phish users with an OAuth consent screen.

## Setup

You can find more info of about how to do the setup in Azure Entra ID in https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-unauthenticated-enum-and-initial-entry/az-oauth-apps-phishing. However, here is a summary:

1. Register a new application. It can be only for the current directory if you are using an user from the attacked directory or for any directory if this is an external attack (like in the following image). Also set the redirect URI to the expected URL where you want to receive the code to the get tokens (http://localhost:8000/callback by default).
2. Then create an application secret
3. Select API permissions (e.g. Mail.Read, Notes.Read.All, Files.ReadWrite.All, User.ReadBasic.All, User.Read)
4. Execute this web page that asks for the permissions

```bash
python3 azure_oauth_phishing_example.py --client-secret <client-secret> --client-id <client-id> --scopes "email,Files.ReadWrite.All,Mail.Read,Notes.Read.All,offline_access,openid,profile,User.Read"
```

5. Send the URL to the victim (in this case http://localhost:8000)
6. Victims needs to accept the prompt
7. Use the access token to access the requested permissions
