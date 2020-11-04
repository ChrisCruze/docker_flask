from multiprocessing import Process
from supporting_functions import log_creator,FileFunctions
import os
import ntpath
import logging
import time
import traceback
import runpy

def job_file_directory_create(file_name):
	directory = FileFunctions().static_directory_get('jobs')
	directory = os.path.join(directory,file_name)
	return directory


def initiate_python_script(directory):
	file_name = ntpath.basename(directory).replace('.py','')

	pid = str(os.getpid())
	pidfile = os.path.join(FileFunctions().static_directory_get('jobs'),file_name + '.pid')
	if not os.path.isfile(pidfile):
		f = open(pidfile, 'w+')
		f.write(pid)
		f.close()

	format="[%(levelname)s] %(asctime)s: %(message)s"
	logging.basicConfig(
	    filename=os.path.join(FileFunctions().static_directory_get('jobs'),file_name + '.Log'),
	    format=format,
	    level=logging.DEBUG,
	    filemode='w',
	    datefmt="%H:%M:%S")
	logging.info('start')



	current_working_directory = os.getcwd()
	os.chdir(FileFunctions().static_directory_get('jobs'))
	try:
		script_directory = os.path.join(FileFunctions().static_directory_get('jobs'),file_name + '.py')
		print (script_directory)
		runpy.run_path(script_directory,run_name='__main__')
		logging.info('done')
	except Exception as err:
		error_message = traceback.format_exc()
		logging.error(error_message)
		with open(file_name+'.TXT', 'w+') as outfile:
			outfile.write(error_message)
	os.chdir(current_working_directory)
	

	os.unlink(pidfile)

def jobs_files_get():
	directory = FileFunctions().static_directory_get('jobs')
	array = FileFunctions().files_from_directory(directory)
	return array

def determine_if_script_after_log_file(log_files,python_dict):
	log_files_associated = [D for D in log_files if D['file_name'] == python_dict['file_name']]
	if len(log_files_associated) > 0:
		log_dict = log_files_associated[0]
		return python_dict['modified'] > log_dict['modified']
	else:
		return True

def jobs_ready_get():
	array = jobs_files_get()
	pid_files = [D['file_name'] for D in array if D['extension'] == '.pid']
	log_files = [D for D in array if D['extension'] == '.Log']
	python_files = [D for D in array if D['extension'] == '.py' and D['file_name'] not in pid_files]
	python_files_after_modified = [D['directory'] for D in python_files if determine_if_script_after_log_file(log_files,D)]
	return python_files_after_modified



# while True:
# 	python_files = jobs_ready_get()
# 	for python_file in python_files:
# 		p = Process(target=initiate_python_script, args=(python_file,))
# 		p.start()
# 		p.join()
# 	time.sleep(5)


