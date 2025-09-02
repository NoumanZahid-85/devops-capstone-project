"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...
    def test_get_account(self): 
        """It should Read a single Account"""
        # first, create a test account to read
        test_account = self._create_accounts(1)[0]
        # make a call to the server to get the account
        response = self.client.get(f"{BASE_URL}/{test_account.id}")
    
        # assert that the call was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        # assert that the data returned is the same as the data we created
        data = response.get_json()
        self.assertEqual(data["name"], test_account.name)

    def test_get_account_not_found(self):
        """It should not Read an Account that is not found"""
        # make a call with an id that doesn't exist
        response = self.client.get(f"{BASE_URL}/0")
    
        # assert that the call failed with a 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_accounts(self):
        """It should List all Accounts"""
        # Create some accounts
        self._create_accounts(5)
        # Make the GET request
        response = self.client.get(BASE_URL)
    
        # Assert the call was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        # Assert that the right number of accounts were returned
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_update_account(self):
        """It should Update an existing Account"""
        # Create an account to update
        test_account = self._create_accounts(1)[0]
        # Send a PUT request with new data
        new_data = {"name": "Something New", "email": "new@email.com"}
        response = self.client.put(f"{BASE_URL}/{test_account.id}", json=new_data)
    
        # Assert the call was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        # Assert the returned data is correct
        updated_account = response.get_json()
        self.assertEqual(updated_account["name"], "Something New")

    def test_delete_account(self):
        """It should Delete an Account"""
        # Create 5 accounts
        test_accounts = self._create_accounts(5)
        # Get the count of accounts before deletion
        account_count = self.get_account_count()
        # Get one of the accounts to delete
        account_to_delete = test_accounts[0]
    
        # Send a DELETE request
        response = self.client.delete(f"{BASE_URL}/{account_to_delete.id}")
    
        # Assert the call was successful (204 No Content)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Assert the response body is empty
        self.assertEqual(len(response.data), 0)
    
        # Make another GET request for the deleted account and assert it's not found
        response = self.client.get(f"{BASE_URL}/{account_to_delete.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
        # Assert that the number of accounts is now one less
        self.assertEqual(self.get_account_count(), account_count - 1)         
    def get_account_count(self):
        """save the current number of accounts"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        return len(data)


    def get_account_count(self):
        """sends a request to get the number of accounts"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        return len(data)




    def test_delete_account(self):
        """It should Delete an Account"""
        # Create an account to delete
        test_account = self._create_accounts(1)[0]
        
        # Check the count before deleting
        initial_count = self.get_account_count()
        
        # Send the DELETE request
        response = self.client.delete(f"{BASE_URL}/{test_account.id}")
        
        # 1. Assert that the response is correct (204 No Content, empty body)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        
        # 2. Assert that the account is truly gone by trying to get it again
        response = self.client.get(f"{BASE_URL}/{test_account.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # 3. Assert that the total number of accounts is now one less
        final_count = self.get_account_count()
        self.assertEqual(final_count, initial_count - 1)

        