#! /usr/bin/python3
# code: UTF-8

import os
import sys
import argparse
import time
import subprocess

if __name__ == '__main__':
  """_summary_
  需要用户自己 source 环境变量
  """
  filename = ""
  max = 1

  if len(sys.argv) < 3:
    print("input arg@filename and arg@loop count plz.")
    exit(0)
  else: 
    filename = sys.argv[1]
    max = int(sys.argv[2])

  count=0
  output = "slp auto generate table in file:" + filename + "in loop count:" + str(max) + "\n"
  print(output)
  while count < max:
    loop_log = "start generate table, loop [" + str(count) + "]"
    print(loop_log)
    output = output + "-+-+-+-+-+ " + loop_log + " +-+-+-+-+-" + "\n"
    cmd = "roslaunch state_lattice_planner simulation_lattice_planner_stage.launch type:=table table:=" + filename + ".csv"
    log = subprocess.check_output(cmd, shell=True) # 捕获输出
    # log = os.system(cmd)
    output = output + log
    output = output + "\n"
    count += 1
  print("finish gen table.")
  count = count + "finish task."
  output = output + "\n" + "\n" + "\n"
  
  print("save log ...")
  now = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
  savepath = "home/yijiahe/slp_auto_table_gen_log_" + now
  os.makedirs(os.path.dirname(savepath), exist_ok=True)
  with open(savepath, "w") as f:
      f.write(output)
  
  print("finish task")
