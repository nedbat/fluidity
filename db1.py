import os
os.chdir("/Users/ned/art/fluidity")
exec(open("drawbot.py").read())


size(600, 600)

def start_page():
    translate(300, 300)
    scale(300, 300)
    fill(None)
    stroke(0, 0, 0, 0.3)
    strokeWidth(1/300)

sorter = None
for i in range(1000):
    if i > 0:
        newPage()
    f = Fluidity(LinearNoise(seed=55, istep=0.001, istart=0.001*i), npoints=15, nlines=50, one_order=True, sorter=sorter)
    if i == 0:
        sorter = f.sorter
    start_page()
    draw_dlists(f.dlists())

saveImage("f.mp4")
saveImage("f.gif", imageGIFLoop=True)