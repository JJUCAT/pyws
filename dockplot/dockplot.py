#! /usr/bin/python3
# code: UTF-8
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import math

def plot_point_with_direction(ax, x, y, theta, size, label, color):
  """绘制带标签的箭头

  Args:
      ax (plt.gca): 坐标系
      x (double): 箭头的 x 坐标
      y (double): 箭头的 y 坐标
      theta (double): 箭头的角度
      size (double): 箭头的大小
      label (str): 标签
      color (str): 颜色
  """
  ax.quiver(x, y, size*np.cos(theta), size*np.sin(theta), angles='xy', scale_units='xy', scale=70, color=color)
  ax.text(x, y, label, fontsize=8, color='black', ha='center', va='center')


def read_lines(file):
  """将文件 file 按行为单位全部读取，占用较多内存

  Args:
      file (str): 文件路径

  Returns:
      (list): 文件行
  """  
  f = open(file, 'r')
  lines = f.readlines()
  return lines


def get_pose(context, start_index = 0):
  """在 context 的 start_index 位姿开始搜索 [x, y, theta] 三个浮点数

  Args:
      context (str): 要检查的字符串
      start_index (int): 要检查的起始下标，默认下标为 0

  Returns:
      (list): 三个浮点数
  """  
  string = context[start_index:]
  print('check string: ', string)
  pattern = r"\d+\.\d+"
  # match = re.search(pattern, string) # 匹配到第一个规则就返回了
  match = re.findall(pattern, string) # 匹配全部才返回
  if match:
    return match
  else:
    return None


def get_time(context):
  """获取 context 的年月日时间

  Args:
      context (stc): 要检查的字符串

  Returns:
      (str): 年月日时间字符串
  """  
  pattern = r"\d+\/\d+\/\d+\s\d+\:\d+\:\d+"
  match = re.findall(pattern, context)
  time_string = match[0].replace(' ', '-').replace('/', '-')
  return time_string


if __name__ == '__main__':
  file_path = '/home/yijiahe/sz-no12-log/log/navit_auto_dock.log'
  save_path = '/home/yijiahe/sz-no12-log/log/'
  filelines = read_lines(file_path)
  print('file:', file_path, 'lines num is', len(filelines)) # 逗号隔开会自动加空格

  ax = plt.gca()


  auto_dock_num = 0
  start_time_marker = '2023/12/15 16:34:15:317' # 日志起始时间
  end_time_marker = '2023/12/15 17:43:47' # 日志结束时间
  start_marker = 'ApproachDock: Goal received'
  end_marker = 'FinalDock: Goal Reached'
  expected_dock_marker = 'expected dock pose'
  filtered_dock_marker = 'after filter dock'
  start = False # 找到日志起始时间的标志
  approach_start = False
  exported_dock_num = 0
  filtered_dock_num = 0
  approach_dock_num = 0
  for line in filelines:
    is_end = line.find(end_time_marker)
    if is_end >= 0:
      print(line)
      print(' ========== end check ========== ')        
      break

    is_start = line.find(start_time_marker)
    if is_start >= 0:
      if start == False:
        print(line)
        print(' ========== start check ========== ')        
        start = True

    find_index = line.find(start_marker) # 返回找到 marker 的下标，找不到返回 -1
    if find_index >= 0:
      approach_start = True
      approach_dock_num += 1
      print(' ++++++++++ auto dock start ++++++++++ ')

    if approach_start == True and start == True:
      find_expected_index = line.find(expected_dock_marker)
      find_filtered_index = line.find(filtered_dock_marker)
      is_end = line.find(end_marker)
      if find_expected_index >= 0:
        xyt = get_pose(line, find_expected_index)
        final_exported_dock = xyt
        exported_dock_num += 1
        print('expected dock pose:[', exported_dock_num, '][', xyt[0], xyt[1], xyt[2], ']')
        color = 'red'
        if approach_dock_num == 2:
          color = 'blue'
        plot_point_with_direction(ax, float(xyt[0]), float(xyt[1]), float(xyt[2]), 0.4, str(exported_dock_num), color)
      if find_filtered_index >= 0:
        xyt = get_pose(line, find_filtered_index)
        final_filtered_dock = xyt
        filtered_dock_num += 1
        print('expected dock pose:[', filtered_dock_num, '][', xyt[0], xyt[1], xyt[2], ']')
        plot_point_with_direction(ax, float(xyt[0]), float(xyt[1]), float(xyt[2]), 0.4, str(filtered_dock_num), 'yellow')
      if is_end >= 0:
        approach_start = False
        exported_dock_num = 0
        filtered_dock_num = 0
        approach_dock_num = 0
        auto_dock_num += 1
        print(' ---------- auto dock end ---------- ')
        print('final expected dock pose:[final][', final_exported_dock[0], final_exported_dock[1], final_exported_dock[2], ']')
        plot_point_with_direction(ax, float(final_exported_dock[0]), float(final_exported_dock[1]), float(final_exported_dock[2]), 0.4, 'final', 'blue')
        print('final filtered dock pose:[final][', final_filtered_dock[0], final_filtered_dock[1], final_filtered_dock[2], ']')
        plot_point_with_direction(ax, float(final_filtered_dock[0]), float(final_filtered_dock[1]), float(final_filtered_dock[2]), 0.4, 'final', 'green')
        plt.autoscale(enable=True, axis='both', tight=None)
        time = get_time(line)
        print('final time:', save_path+time)
        plt.savefig(save_path+time, dpi=300)
        # plt.show()
        plt.cla() # 清除子图

