from flask import Flask, flash, request, jsonify
from conn import set_connection         # fetching the connection from other file
from settings import logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'


#  srno | holder_name | account_type | balance
# ------+-------------+--------------+---------
#     3 | Naruto      | Savings      |    3000
#     1 | akshith     | savings      |    3000
#     2 | Naruto      | Savings      |    3200
#     6 | Akamaru     | Current      |    6000

@app.route("/insert", methods=["GET", "POST"])      # CREATE an account
def create_account():
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to create account")

    try:
        # accept only POST method
        if request.method == "POST":
            # Take value from the user
            holder_name = request.json["holderName"]
            account_type = request.json["accountType"]
            balance = request.json["balance"]

            # input_format = {
            #     "holderName": "Akamaru",
            #     "accountType": "Current",
            #     "balance": 6000
            # }

            # insert query
            postgres_insert_query = """ INSERT INTO bank (holder_name,
                                           account_type,balance) VALUES (%s,%s,%s)"""
            record_to_insert = (holder_name, account_type, balance,)

            # execute the query with required values
            cur.execute(postgres_insert_query, record_to_insert)

            # Log the details into logger file
            logger(__name__).info(f"{holder_name}'s account created")

            # commit to database
            conn.commit()
        return jsonify({"message": "Account created"}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence account created, closing the connection")



@app.route("/", methods=["GET"])        # READ the details
def show_list():
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to display list of accounts")

    try:
        # execute the query to fetch all values
        cur.execute("SELECT * FROM bank")
        data = cur.fetchall()
        # Log the details into logger file
        logger(__name__).info("Displayed list of all accounts")

        return jsonify({"message": data}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence accounts displayed, closing the connection")


# UPDATE (Amount Withdrawal)
@app.route("/withdraw/<int:srno>", methods=["GET", "PUT"])
def withdrawal(srno):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to deposit amount into the account")

    try:
        # fetch the balance from table
        cur.execute("SELECT balance from bank WHERE srno = %s", (srno, ))
        get_balance = cur.fetchall()
        balance = get_balance[0][0]
        print("get balance", get_balance)
        print("before", balance)

        # get the amount from the user to deduct the balance
        amount = float(request.json["withdrawAmount"])

        # input_format = {
        #     "withdrawAmount": 2000
        # }

        updated_amt = 0
        if balance > amount:            # only if balance is greater than the amount
            updated_amt = balance - amount
            print("after", updated_amt)

            # execute the query
            postgres_query = "UPDATE bank SET balance = %s WHERE srno = %s"
            cur.execute(postgres_query, (updated_amt, srno))
            conn.commit()
        else:                           # else alert message
            flash("Insufficient balance")

        flash("Withdrawal completed")
        # Log the details into logger file
        logger(__name__).info(f"Amount withdrawal from account no. {srno} completed")
        return jsonify({"message": "Withdrawal completed", "amount": updated_amt}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence withdrawal completed, closing the connection")


@app.route("/deposit/<int:srno>", methods=["GET", "PUT"])
def deposit(srno):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to deposit into the account")
    try:
        # fetch the balance from table
        cur.execute("SELECT balance from bank WHERE srno = %s", (srno, ))
        get_balance = cur.fetchall()
        balance = get_balance[0][0]
        print("get balance", get_balance)
        print("after", balance)

        # input_format = {
        #     "depositAmount": 2000
        # }


        # get the amount to be added to the balance
        amount = float(request.json["depositAmount"])

        # update the balance
        updated_balance = amount + balance

        # execute the query
        postgres_query = "UPDATE bank SET balance = %s WHERE srno = %s"
        cur.execute(postgres_query, (updated_balance, srno))
        print("after", updated_balance)
        flash("Amount Deposited")
        conn.commit()

        # Log the details into logger file
        logger(__name__).info(f"Depositing amount into account no. {srno} completed")
        return jsonify({"message": "Amount Deposited", "amount": updated_balance}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence deposit completed, closing the connection")


@app.route("/bank/link_account/<int:srno>", methods=["PUT"])
def link_accounts(srno):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to link the accounts")
    try:
        # link account name
        account_link = request.json["link_ac"]

        query = "UPDATE bank SET link_account = %s WHERE srno = %s"
        values = (account_link, srno)
        cur.execute(query, values)

        conn.commit()
        # Log the details into logger file
        logger(__name__).info(f"Linking to account no. {srno} completed")
        return jsonify({"message": "Account linked"}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence linking account completed, closing the connection")



@app.route("/bank/<int:srno>", methods=["PUT"])
def update_account_details(srno):
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to update the details ")
    try:
        # fetch the account if exists
        cur.execute("SELECT holder_name from bank where srno = %s", (srno,))
        get_account = cur.fetchone()

        # if not return error
        if not get_account:
            return jsonify({"message": "Account not found"}), 200

        # get details from the user
        data = request.get_json()
        holder_name = data.get('holderName')
        ac_type = data.get('ac_type')
        account_link = data.get('link_ac')

        if holder_name:
            cur.execute("UPDATE bank SET holder_name = %s WHERE srno = %s", (holder_name, srno))
        elif ac_type:
            cur.execute("UPDATE bank SET account_type = %s WHERE srno = %s", (ac_type, srno))
        elif account_link:
            cur.execute("UPDATE bank SET linked_account = %s WHERE srno = %s", (account_link, srno))

        conn.commit()

        # Log the details into logger file
        logger(__name__).info(f"Account updated: {data}")
        return jsonify({"message": "Account updated", "Details": data}), 200
    except Exception as error:
        # Raise an error and log into the log file
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence accounts updated, closing the connection")


@app.route("/delete/<int:srno>", methods=["DELETE"])      # DELETE account from the list
def delete_account(srno):
    # start the database connection
    cur, conn = set_connection()
    logger(__name__).warning("Starting the db connection to delete the account")
    try:
        # execute the delete query
        delete_query = "DELETE from bank WHERE srno = %s"
        cur.execute(delete_query, (srno,))
        conn.commit()
        # Log the details into logger file
        logger(__name__).info(f"Account no {srno} deleted from the table")
        return jsonify({"message": "Deleted Successfully", "holder_name_no": srno}), 200
    except Exception as error:
        logger(__name__).exception(f"Error occurred: {error}")
        return jsonify({"message": error})
    finally:
        # close the database connection
        conn.close()
        cur.close()
        logger(__name__).warning("Hence accounts displayed, closing the connection")


if __name__ == "__main__":
    app.run(debug=True, port=5000)