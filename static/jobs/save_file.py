import time


f = open("demofile3", "w")
f.write("Woops! I have deleted the content!")
f.close()

time.sleep(5)