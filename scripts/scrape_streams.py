import sys

from run_geant import run as run_geant
from run_i2 import run as run_i2


valid_user_inputs = ["all", "GEANT", "I2"]

user_input = None
if len(sys.argv) == 2 and sys.argv[1].strip() in valid_user_inputs:
    user_input = sys.argv[1].strip()
else:
    print("Please pass a valid parameter to specify the looking glass.")
    sys.exit(1)

outfile = open('output.txt', 'w+')

if user_input == "GEANT" or user_input == "all":
    run_geant(outfile)
if user_input == "I2" or user_input == "all":
    run_i2(outfile)

print("Success! Your results are available at ~/multicat-menu/scripts/output.txt.")
outfile.close()
