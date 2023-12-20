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
  # print('check string: ', string)
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

def calculate_sigma(array_x, array_y, array_yaw):
  """计算 x y yaw 列表数据的均值，方差，总体标志差，样本标准差

  Args:
      array_x (list): x 数据列表
      array_y (list): y 数据列表
      array_yaw (list): yaw 数据列表

  Returns:
      (float): x y yaw 数据消息
  """  
  mean_x = np.mean(array_x)
  mean_y = np.mean(array_y)
  mean_yaw = np.mean(array_yaw)
  print('mean x: %f, mean y: %f, mean yaw: %f.' %(mean_x, mean_y, mean_yaw))
  var_x = np.var(array_x)
  var_y = np.var(array_y)
  var_yaw = np.var(array_yaw)
  print('var x: %f, var y: %f, var yaw: %f.' %(var_x, var_y, var_yaw))
  total_std_x = np.std(array_x)
  total_std_y = np.std(array_y)
  total_std_yaw = np.std(array_yaw)
  print('total std x: %f, total std y: %f, total std yaw: %f.' %(total_std_x, total_std_y, total_std_yaw))
  sample_std_x = np.std(array_x, ddof=1)
  sample_std_y = np.std(array_y, ddof=1)
  sample_std_yaw = np.std(array_yaw, ddof=1)
  print('sample std x: %f, sample std y: %f, sample std yaw: %f.' %(sample_std_x, sample_std_y, sample_std_yaw))
  
  return sample_std_x, sample_std_y, sample_std_yaw
  # msg_x = 'sstd x:' + format(sample_std_x, ".3f")
  # msg_y = 'sstd y:' + format(sample_std_y, ".3f")
  # msg_yaw = 'sstd yaw:' + format(sample_std_yaw, ".3f")
  # return msg_x, msg_y, msg_yaw


if __name__ == '__main__':
  """估计回充参数的计算，需要确保充电桩的朝向和 odom 接近
     一般做法是将清洁车手动对位充电桩，然后直线后退一段距离后重置 odom
     这样感知到的充电桩坐标 [x] 表示纵向感知， [y] 表示横向感知， [yaw] 表示航向角感知
     多次测试后需要重置 odom 消除 odom 漂移累计的误差，提高估计的可靠性
  """  
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
  edock_x = [] # 感知的充电桩 odom 坐标 [x, y, yaw]
  edock_y = []
  edock_yaw = []
  first_sstd_x = [] # 第一次 approach dock 感知的样本标准差
  first_sstd_y = []
  first_sstd_yaw = []
  second_sstd_x = [] # 第二次 approach dock 感知的样本标准差
  second_sstd_y = []
  second_sstd_yaw = []
  fmsg = "" # approach dock 标志差信息
  smsg = ""
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
      if len(edock_x) > 0:
        print(' first auto dock start ')
        sstd = calculate_sigma(edock_x, edock_y, edock_yaw)
        fmsg = 'first sstd x:'+format(sstd[0], ".3f")+'---'+'sstd y:' + format(sstd[1], ".3f")+'---'+'sstd yaw:' + format(sstd[2], ".3f")
        print('first title: ', smsg)
        first_sstd_x.append(sstd[0])
        first_sstd_y.append(sstd[1])
        first_sstd_yaw.append(sstd[2])
        edock_x.clear()
        edock_y.clear()
        edock_yaw.clear()
      print(' ++++++++++ auto dock start ++++++++++ ')

    if approach_start == True and start == True:
      find_expected_index = line.find(expected_dock_marker)
      find_filtered_index = line.find(filtered_dock_marker)
      is_end = line.find(end_marker)
      if find_expected_index >= 0:
        xyt = get_pose(line, find_expected_index)
        edock_x.append(float(xyt[0]))
        edock_y.append(float(xyt[1]))
        edock_yaw.append(float(xyt[2]))
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
        # print('filter dock pose:[', filtered_dock_num, '][', xyt[0], xyt[1], xyt[2], ']')
        plot_point_with_direction(ax, float(xyt[0]), float(xyt[1]), float(xyt[2]), 0.4, str(filtered_dock_num), 'yellow')
      if is_end >= 0:
        approach_start = False
        exported_dock_num = 0
        filtered_dock_num = 0
        approach_dock_num = 0
        auto_dock_num += 1
        print(' ---------- auto dock end ---------- ')
        # print('final expected dock pose:[final][', final_exported_dock[0], final_exported_dock[1], final_exported_dock[2], ']')
        plot_point_with_direction(ax, float(final_exported_dock[0]), float(final_exported_dock[1]), float(final_exported_dock[2]), 0.4, 'final', 'blue')
        # print('final filtered dock pose:[final][', final_filtered_dock[0], final_filtered_dock[1], final_filtered_dock[2], ']')
        plot_point_with_direction(ax, float(final_filtered_dock[0]), float(final_filtered_dock[1]), float(final_filtered_dock[2]), 0.4, 'final', 'green')

        print(' second auto dock start ')
        sstd = calculate_sigma(edock_x, edock_y, edock_yaw)
        second_sstd_x.append(sstd[0])
        second_sstd_y.append(sstd[1])
        second_sstd_yaw.append(sstd[2])
        smsg = 'second sstd x:'+format(sstd[0], ".3f")+'---'+'sstd y:' + format(sstd[1], ".3f")+'---'+'sstd yaw:' + format(sstd[2], ".3f")
        print('second title: ', smsg)
        plt.title(fmsg+'\n'+smsg)
        plt.autoscale(enable=True, axis='both', tight=None)
        time = get_time(line)
        print('final time:', save_path+time)
        plt.savefig(save_path+time, dpi=300)
        # plt.show()
        plt.cla() # 清除子图
        print(' -+-+-+-+-+ auto dock end +-+-+-+-+- ')

  print('\033[31m ********** auto dock summary ********** \033[0m')
  print('\033[31m first approach dock sstd [%f, %f, %f] \033[0m' %(np.mean(first_sstd_x), np.mean(first_sstd_y), np.mean(first_sstd_yaw)))
  print('\033[31m second approach dock sstd [%f, %f, %f] \033[0m' %(np.mean(second_sstd_x), np.mean(second_sstd_y), np.mean(second_sstd_yaw)))
