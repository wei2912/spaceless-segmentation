import time
import sys

# update() : Displays or updates a console progress bar
## Accepts two values: the number of jobs finished
## and the total number of jobs.
def update(finished, total):
    progress = finished*100/total

    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 100:
        progress = 100
        status = "Done...\r\n"
    block = int(round(barLength*progress/100))
    text = "\rPercent: [%s] %d%% %d/%d %s" % ("#"*block + "-"*(barLength - block), round(progress), finished, total, status)
    sys.stdout.write(text)
    sys.stdout.flush()