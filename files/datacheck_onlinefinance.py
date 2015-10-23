import time
import sys
import os
from scoredaohelperonline import ScoreDaoHelper
from scoredaohelperonline import UserTask
scoredao = ScoreDaoHelper()

log = open('datacheck.log','a+')
error_log = open('datacheck_error.log','a+')

def logging(str):
	log.write("%s: %s\n"% (time.ctime(),str))

def error_logging(str):
	error_log.write("%s: %s\n"% (time.ctime(),str))

oldtask2new_actiontype = {
					100:{
						1:501,
						2:501,
						3:501,
						4:502,
						5:502,
						6:502,
						7:503,
						8:503,
						9:503,
						10:503,
						11:503,
						12:503,
						13:505,
						14:505,
						15:505,
						16:505,
						17:505,
						18:505,
						19:506,
						20:506,
						21:506,
						22:506,
						23:506,
						24:506,
						25:507,
						26:507,
						27:507,
						28:507,
						29:507,
						30:507,
						31:508,
						32:508,
						33:508,
						34:508,
						35:508,
						36:508,
						37:509,
						38:509,
						39:509,
						45:509,
						41:509,
						42:509
						},
					101:{
						43:512,
						44:512,
						45:512,
						46:512,
						47:512,
						48:512,
						49:512,
						50:512,
						51:512,
						52:510,
						53:510,
						54:510,
						55:510,
						56:510,
						57:510,
						58:510,
						59:510,
						60:513,
						61:513,
						62:513
						}
		}

def isEqual(old_ut,new_ut):
	if old_ut.sequece != 0 and cmp(str(old_ut.sequece), new_ut.sequece) != 0:
		error_logging("uid:%u new_task_status:%u(taskid) old_task:%u,%u(taskid,taskpkgid),reward_sequence is not the same,old_seq:%s, new_seq:%s."%(old_ut.uid, new_ut.taskid,old_ut.taskpkgid,old_ut.taskid,old_ut.sequece,new_ut.sequece))
		return 1
	if old_ut.status == 0 and new_ut.status == 0:
		return 0
	if old_ut.status == 10 and new_ut.status == 1:
		return 0
	if old_ut.status == 20 and new_ut.status == 2:
		return 0
	error_logging("uid:%u new_ut:(%u,%u)(taskid,status) old_ut:(%u,%u,%u)(taskpkgid,taskid,status) is not the same"%(new_ut.uid,new_ut.taskid,new_ut.status,old_ut.taskpkgid,old_ut.taskid,old_ut.status))
	return -1

def checkActionStatus(action_status,old_ut):
	if action_status.already_done_cout < old_ut.current_status:
		#if action_status.action_type != 218 and action_status.action_type != 201 and action_status.action_type != 202 and action_status.action_type != 204: 
		error_logging("uid:%u action_type:%u taskid:%u already_done_cout:%u is smaller than old usertask(%u,%u,%u)"%(action_status.uid,action_status.action_type,action_status.taskid,action_status.already_done_cout,old_ut.taskpkgid,old_ut.taskid,old_ut.current_status))
		return False
	return True

def main():
	#counts = scoredao.get_usertask_counts(10100)
	counts = 7497248 
	print "total counts:%u" % counts
	logging("total counts:%u" % counts)
	i = 0
	while ( i <= counts):
		old_usertasks = []
		ret = scoredao.batch_get_old_usertasks(50020,i,500,old_usertasks)
		if ret == False:
			print "batch get usertasks error"
			error_logging("batch get usertasks error")
			break
		for old_ut in old_usertasks:
			action_status = scoredao.get_actionstatus("50020",old_ut.uid,old_ut.taskid)
			if action_status != None:
				checkActionStatus(action_status,old_ut)

			new_taskid = old_ut.taskid
			new_ut  = scoredao.get_new_usertask_by_uidtaskid("50020",old_ut.uid,new_taskid)
			#raw_input("scoredao:new_usertask:%s"%str(new_ut))
			if new_ut != None:
				ret = isEqual(old_ut,new_ut)
				if ret == 0:
					print "uid:%u taskid:%u usertask success move!" % (new_ut.uid,new_ut.taskid)
					#logging("uid:%u taskid:%u usertask success move!" % (new_ut.uid,new_ut.taskid))
					pass
				elif ret == -1:
					if old_ut.taskpkgid == 101:
						print "err: uid:%u taskid:%u usertask move error!" % (new_ut.uid,new_ut.taskid)
						error_logging("err: uid:%u taskid:%u old_taskpkg_id:%u old_taskid:%u usertask move error!" % (new_ut.uid,new_ut.taskid,old_ut.taskpkgid,old_ut.taskid))
				elif ret == 1:
					print "err: uid:%u taskid:%u usertask move error!,reward_seq is different, %s:%s." % (new_ut.uid,new_ut.taskid,new_ut.sequece,old_ut.sequece)
					logging("err: uid:%u taskid:%u usertask move error!,reward_seq is different, %s:%s." % (new_ut.uid,new_ut.taskid,new_ut.sequece,old_ut.sequece))
			else:
				if old_ut.status != 0:
					error_logging("err: main(),uid:%u don't find newtaskid:%u in new_usertask"%(old_ut.uid,new_taskid))
					print "uid:%u don't find newtaskid:%u in new_usertask"%(old_ut.uid,new_taskid)
					continue
				elif old_ut.status == 0:
					#print "info: uid:%u taskid:%u status == 0,so new_db won't insert it"%(old_ut.uid,new_taskid)
					logging("info: uid:%u taskid:%u status == 0,so new_db won't insert it"%(old_ut.uid,new_taskid))
					pass
		i+=500
		time.sleep(1.0)
		if i % 10000 == 0:
			logging("info:now is step to %u" % i)
		#raw_input("100 step check,continue?")
		#time.sleep(0.01)
	
if __name__ == "__main__":
	main()
