import threading
import os
from datetime import datetime 

def add_two(nums):
  print(nums[0]+nums[1])
  print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
  print("ID of process running task 1: {}".format(os.getpid()))

def sub_two(nums):
  print(nums[0]-nums[1])

  print("Task 2 assigned to thread: {}".format(threading.current_thread().name))
  print("ID of process running task 2: {}".format(os.getpid()))

def main():
  d1 = datetime.strptime("2025-02-08 00:23:00", "%Y-%d-%m %H:%M:%S")
  d2 = datetime.strptime("2025-02-08 10:23:00", "%Y-%d-%m %H:%M:%S")
  if d1 > d2:
    print("hi")
  else:
    print("bye")

if __name__ == "__main__":
  main()
