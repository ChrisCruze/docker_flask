#!/usr/bin/python
from flask import Flask, render_template, send_from_directory,redirect,url_for,request
import requests
import os
from flask_restful import Resource, Api,reqparse
from flask_cors import CORS
from supporting_functions import SupportingFunctions,FileFunctions
from multiprocessing import Process
import jobs
import time
import traceback
import json
server = Flask(__name__)
api = Api(server)
CORS(server)


"""
Below are the API definitions
"""
def read_file(directory):
    with open(directory,'r+') as f:
        r = str(f.read())
    if '.json' in str(directory).lower():
        return json.loads(r)
    else:
        return r

class Read(Resource):
    def get(self,file_id):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        directory = '/'#os.path.join(dir_path,'static','jobs')
        directory = os.path.join(directory,file_id)
        return read_file(directory)
api.add_resource(Read, '/read/<string:file_id>')

class Jobs(Resource):
    def get(self):
        directory = FileFunctions().static_directory_get('jobs')
        array = FileFunctions().files_from_directory(directory)
        return array
api.add_resource(Jobs, '/jobs')


class Delete(Resource):
    def get(self,file_id):
        directory = FileFunctions().static_directory_get('jobs')
        file_directory = os.path.join(directory,file_id)
        try:
            os.remove(file_directory)
            return "Successfully Deleted"
        except Exception as err:
            error_message = traceback.format_exc()
            print (error_message)
            return error_message

class Stop(Resource):
    def get(self,file_id):
        directory = FileFunctions().static_directory_get('jobs')
        file_directory = os.path.join(directory,file_id + '.pid')
        try:
            pid = open(file_directory,'r+').read()
            os.kill(pid)
            return "Successfully Stopped"
        except Exception as err:
            error_message = traceback.format_exc()
            print (error_message)
            return error_message


class Start(Resource):
    def get(self,file_id):
        directory = FileFunctions().static_directory_get('jobs')
        file_directory = os.path.join(directory,file_id + '.py')
        try:
            script = open(file_directory,'r+').read()
            f = open(file_directory, 'w+')
            f.write(script)
        except Exception as err:
            error_message = traceback.format_exc()
            print (error_message)
            return error_message

api.add_resource(Delete, '/delete/<string:file_id>')
api.add_resource(Stop, '/stop/<string:file_id>')
api.add_resource(Start, '/start/<string:file_id>')





@server.route("/")
def hello():
    return render_template("home.html")

@server.route("/job")
def script_page(name=None):
    return render_template("job.html")


@server.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        dir_path = os.path.dirname(os.path.realpath(__file__))
        directory = uploaded_file.filename #os.path.join(dir_path,'static','jobs',uploaded_file.filename)
        uploaded_file.save(directory)
    return redirect(request.url)

def run_job_listener():
    while True:
        python_files = jobs.jobs_ready_get()
        for python_file in python_files:
            p = Process(target=jobs.initiate_python_script, args=(python_file,))
            p.start()
            p.join()
        time.sleep(5)


@server.route("/run")
def test_function():
    etl_jobs = Process(target=run_job_listener)
    etl_jobs.start()
    print ("Running")
    return "Running Threaded Job"





# def run_server():
#     server.run(host='0.0.0.0', port=8080, debug=True, threaded=True)


# if __name__ == "__main__":
#     etl_jobs = Process(target=run_job_listener)
#     flask_server = Process(target=run_server)
#     etl_jobs.start()
#     flask_server.start()
