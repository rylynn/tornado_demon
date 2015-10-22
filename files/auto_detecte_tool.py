import threading
import os
import time
import sys
import subprocess 
import random

def check_logic(arg):
  i = False
  #sys.argv = ['./testByYaml.py',arg]
  subprocess.call(["python ./testByYaml.py " + arg],shell=True)
  #os.system('python ./testByYaml.py' + " " + arg)
  error_f = open("./unexpectrecv.txt",'r+')
  error_str = error_f.readline()
  timeout_f = open("./timeout.txt",'r+')
  timeout_str = timeout_f.readline()
  if len(error_str) > 0:
    alarm(error_str)
    i = True
  if len(timeout_str) > 0:
    alarm(timeout_str)
    i = True
  if i == True:
    return False
  return True

ip_list = ["155","156","157","158"]

def check_query():
  check_logic("./usecases/querytask.yaml")

def check_report():
  check_logic("./usecases/reporttask.yaml")

def check_reward():
  check_logic("./usecases/rewardtask.yaml")

def check_score():
  check_logic("./usecases/scoregrade.yaml")

def check_old_query():
  dir = "./usecases/oldquerytask-%s.yaml" % (ip_list[random.randint(0,3)])
  print "-------==========--------------"
  print dir
  check_logic(dir)

def check_old_report():
  check_logic("./usecases/oldreporttask-%s.yaml" % (ip_list[random.randint(0,3)]))

def check_old_reward():
  check_logic("./usecases/oldrewardtask.yaml")

def check_old_reward2():
  check_logic("./usecases/oldrewardtask2.yaml")

def alarm(str = ""):
  print "alarm to your phone"
  subprocess.call(["python /home/dspeak/yyms/yymp/yymp_report_script/yymp_report_alarm.py 12577 79543 0 \"" + str+"\""],shell=True)


def cycle_check_logic():
  check_old_query()
  #check_old_report()
  #check_old_reward()
  #check_old_reward2()
  #check_query()
  #check_report()
  #check_reward()
  #check_score()

def check():
  cycle_check_logic()
  global check_timer
  check_timer = threading.Timer(300.0,check,[])
  check_timer.start()

if __name__ == "__main__":
  check_timer = threading.Timer(2.0,check,[])
  check_timer.start()

