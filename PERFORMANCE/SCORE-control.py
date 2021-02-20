# The Indifefrence of the Cosmic Love
# for flauto d'amore (or flute, or alto flute or piccolo), multi-channel audio, electronics and cosmic rays
# by Marco Buongiorno Nardelli for Ginevra Petrucci (2020)

# _PERFORMANCE SCORE CONTROL_

import os, time
import multiprocessing as mp

processes = ('SCORE.py', 'SCORE_START.py', 'SCORE_PEDAL.py')

def run_process(process):                                                             
  os.system('sudo /Users/marco/anaconda38/bin/python {}'.format(process))

def iterate(n): 
  print('iteration # ',n)
  pool = mp.Pool(processes=3)
  pool.map(run_process, processes)
  n += 1
  return(iterate,n)

if __name__ == '__main__':
  n = 0 
  while True:
    try:
      _,n = iterate(n)
      time.sleep(30)
    except KeyboardInterrupt:
      break

# Clean up
os.system("kill $(ps aux | grep SCORE | grep -v grep | awk '{print $2}')")

