import os
import sys
from dotenv import load_dotenv
light_path = os.path.abspath("/home/ubuntu/repos/471-project/backend/scripts/test/test_light.py")
sys.path.insert(0, light_path)
from test import test_light

load_dotenv()
LIFX_TOKEN = os.getenv("TOKEN")
LIFX_ID = os.getenv("ID")
def main():
  light1 = test_light.Light()
  test_light.cycle(light1)

if __name__ == "__main__":
  main()
