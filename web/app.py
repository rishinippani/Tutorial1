from pymongo import MongoClient
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb+srv://rishi:123@cluster0.f1yts.mongodb.net/SentencesDatabase?retryWrites=true&w=majority")

db = client["SentencesDatabase"]
users = db["Users"]

class Register(Resource):
    def post(self):

        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        dataToInsert = {

            "username":username,
            "password":hashed_pw,
            "sentence":"",
            "tokens":6
            }

        db["Users"].insert_one(dataToInsert)

        retJson = {

            "Status Code":200,
            "Message":"Congrats! You signed up for the API"

            }

        return jsonify(retJson)


def verifyLogin(username, password):

    doc = db["Users"].find_one({"username":username})

    hashed_pw = doc["password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False



def verifyTokens(username):

    doc = db["Users"].find_one({"username":username})

    tokens = doc["tokens"]

    return tokens

class Store(Resource):
    def post(self):

        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        correct_pw = verifyLogin(username, password)

        if not correct_pw:
            retJson = {

                    "Status Code":302,
                    "Message":"Username or Password is Incorrect"
                    

                }
            return jsonify(retJson)

        num_tokens = verifyTokens(username)

        if num_tokens <= 0:
            retJson = {


                    "Status Code":301,
                    "Message":"Not enough tokens. Buy some more!"
                    
                }
            return jsonify(retJson)


        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        replacement = {

            "username":username,
            "password":password,
            "sentence":sentence,
            "tokens":num_tokens-1

            }

        db["Users"].find_one_and_replace({"username":username},replacement, upsert=True)


        retJson = {

            "Status":200,
            "Message": "Sentence saved successfully"

            }
        return jsonify(retJson)

api.add_resource(Register, '/register')
api.add_resource(Store, '/store')

if __name__=="__main__":
    app.run(host="0.0.0.0")


        
