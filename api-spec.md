# ENDPOINTS

- Homepage (anonymous user): slink.com/
- Homepage (logged in user): slink.com/username
- Dashboard: slink.com/dashboard
- Settings: slink.com/settings
- Login: slink.com/login
- Signup: slink.com/signup

## Anonymous User Homepage

- Receive a POST request with url only
- If no url is entered, return an error message, "please enter url"
- If url is entered, generate a short_id, append the short_id to the host_url (request.host_url) and return them as the shortened url

## Logged in User Homepage

- Receive a POST request with url, custom_id (optional), new_custom_id
- If no url is entered, return an error message, "please enter url"
- If url is entered, shorten the link and return the shortened url
- If custom_id is entered, store the custom_id in the db as short_id
- Append the custom_id to the host_url and return them as the shortened url
- If no custom_id is provided in the POST request, generate a short_id, append the short_id to the host_url (request.host_url) and return them as the shortened url
- new_custom_id can only be provided if a custom_id already exists in the db
- if a new_custom_id is provided, rewrite the old custom_id, change the shortened_url, invalidate the old one, and return the new one.

## Dashboard

- Return a table of all shortened URLs (original_url, shortened_url, date_created, date_modified (if a custom_id is changed))

## Settings

- Serves to change password
- Receives a POST request of new password
- Writes off old password with the new password
- Returns a 200 status code with a message of "Password changed, successfully."
