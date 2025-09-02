"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# L I S T   A L L   A C C O U N T S
######################################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """Returns all of the Accounts"""
    app.logger.info("Request for account list")
    accounts = []
    name = request.args.get("name")
    if name:
        accounts = Account.find_by_name(name)
    else:
        accounts = Account.all()

    results = [account.serialize() for account in accounts]
    return jsonify(results), status.HTTP_200_OK

# ... place you code here to LIST accounts ...


######################################################################
# R E A D   A N   A C C O U N T
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """
    Reads an Account
    This endpoint will read an Account based on the id specified in the path
    """
    app.logger.info("Request to read an account with id: %s", account_id)
    
    # use the Account model to find the account
    account = Account.find(account_id)
    if not account:
        # if it's not found, abort with a 404
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' was not found.")
        
    # return the serialized account and a 200 OK status code
    return account.serialize(), status.HTTP_200_OK

######################################################################
# U P D A T E   A N   E X I S T I N G   A C C O U N T
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """
    Update an Account
    This endpoint will update an Account based on the body that is posted
    """
    app.logger.info("Request to update account with id: %s", account_id)
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' was not found.")

    # Get the data from the request and update the account
    data = request.get_json()
    account.name = data.get("name", account.name)
    account.email = data.get("email", account.email)
    account.address = data.get("address", account.address)
    account.phone_number = data.get("phone_number", account.phone_number)
    
    account.update()
    
    app.logger.info("Account with ID [%s] updated.", account.id)
    return account.serialize(), status.HTTP_200_OK

######################################################################
# DELETE AN ACCOUNT
######################################################################

# ... place you code here to DELETE an account ...


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
