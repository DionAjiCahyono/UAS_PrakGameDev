from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from direct.task import Task
import random
from past.builtins import xrange
loadPrcFileData('', 'window-title Grid\'Game')

base = ShowBase()

gridSize = 30 # mengatur ukuran grid.. semakin besar nilai maka grid akan semakin banyak

loopRunning = False
tombolacak = None
tombolmulai = None
tomboledit = None
editMode = False
grid = []
liveGrid = []

class Cell:
    def __init__(self, alive):
        self.model = loader.loadModel('gfx/block') #memanggil model pada folder GFX
        self.model.reparentTo(render)
        self.alive = alive
        self.model.setTag('cell', '1')

    def draw(self):
        if self.alive:
            self.model.unstash()
            self.model.setColorScale(13,12,21,31) # mengatur warna pada grid
        else:
            if editMode:
                self.model.unstash()
                self.model.setColorScale(0.2,0.54,0.3,1) # mengatur background Grid saat di edit
            else:
                self.model.stash()

def initialize():
    global tombolacak #membuat variabel tombolacak
    global tombolmulai #membuat variabel tombolmulai
    global tomboledit #membuat variabel tombol untuk edit
    global liveGrid #membuat variabel live grid

    # Camera setup
    base.disableMouse()
    base.camera.setPos(gridSize/2, gridSize/2, gridSize*2.5)#mengatur posisi jarak pergerakan pada grid
    base.camera.setP(270)#mengatur camera

    # DirectGui pada game 
    tombolacak = DirectButton(text = ("Acak", "Acak", "Acak", "Acak"), scale = 0.05, command = step, pos = (-0.33, 20, 0.75))
    tombolmulai = DirectButton(text = ("jalankan", "jalankan", "jalankan", "jalankan"), scale = 0.05, command = toggleRun, pos = (0, 0, 0.75))
    tomboledit = DirectButton(text = ("Edit", "Edit", "Edit", "Edit"), scale = 0.05, command = toggleEdit, pos = (0.33, 20, 0.75))

    # Buat array 2D, sehingga sel dapat dilihat dengan menggunakan [x][y]. Juga buat grid awal
    for x in xrange(0, gridSize):
        row = []
        for y in xrange (0, gridSize):
            cell = Cell(random.choice([True, False]))
            row.append(cell)
            cell.model.setPos(x, y, 0)
        grid.append(row)
    draw()

def draw():
    for row in grid:
        for cell in row:
            cell.draw()

def getCellAlive(cellX, cellY):
    try:
        liveGrid[cellX][cellY]
    except:
        if cellX >= gridSize:
            cellX = 0
        elif cellX < 0:
            cellX = gridSize - 1

        if cellY >= gridSize:
            cellY = 0
        elif cellY < 0:
            cellY = gridSize - 1

    return liveGrid[cellX][cellY]

def step():#function mengacak  grid
    global liveGrid
    liveGrid = []

    for x in xrange(0, gridSize):
        liveGrid.append([])

    for x in grid:
        for y in x:
            liveGrid[grid.index(x)].append(y.alive)

    for x in grid:
        for y in x:
            neighbors = [getCellAlive(grid.index(x)-1, x.index(y)), getCellAlive(grid.index(x)-1, x.index(y)-1), getCellAlive(grid.index(x)-1, x.index(y)+1), getCellAlive(grid.index(x)+1, x.index(y)),
                         getCellAlive(grid.index(x)+1, x.index(y)-1), getCellAlive(grid.index(x)+1, x.index(y)+1), getCellAlive(grid.index(x), x.index(y)-1), getCellAlive(grid.index(x), x.index(y)+1)]
            if y.alive:
                if neighbors.count(True) < 2 or neighbors.count(True) > 3:
                    y.alive = False
            elif neighbors.count(True) == 3:
                y.alive = True
    draw()

def toggleRun(): #function menjalankan pada grid
    global loopRunning
    if loopRunning:
        loopRunning = False
        tombolmulai["text"] = ("jalankan", "jalankan", "jalankan", "jalankan")
        taskMgr.remove("jalankan Loop")
    else:
        loopRunning = True
        tombolmulai["text"] = ("Stop", "Stop", "Stop", "Stop")
        taskMgr.add(runLoop, "jalankan Loop")

def runLoop(task):#function proses loop pada grid
    step()
    return task.cont

def toggleEdit():#function edit grid
    global editMode
    if loopRunning:
        toggleRun()
    if editMode:
        editMode = False
        tomboledit["text"] = ("Edit", "Edit", "Edit", "Edit")
        tombolacak["text"] = ("Acak", "Acak", "Acak", "Acak")
        tombolacak["command"] = step
        tombolmulai.show()
    else:
        editMode = True
        tomboledit["text"] = ("Kembali", "Kembali", "Kembali", "Kembali")
        tombolacak["text"] = ("Bersihkan", "Bersihkan", "Bersihkan", "Bersihkan")
        tombolacak["command"] = clearGrid
        tombolmulai.hide()
    draw()

traverser = CollisionTraverser()
handler = CollisionHandlerQueue()

pickerNode = CollisionNode('mouseRay')
pickerNP = camera.attachNewNode(pickerNode)
pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
pickerRay = CollisionRay()
pickerNode.addSolid(pickerRay)
traverser.addCollider(pickerNP, handler)

def handlePick():
    if not editMode:
        return

    if base.mouseWatcherNode.hasMouse():
        mpos = base.mouseWatcherNode.getMouse()
        pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())

        traverser.traverse(render)
        if handler.getNumEntries() > 0:
            handler.sortEntries()
            pickedObj = handler.getEntry(0).getIntoNodePath()
            pickedObj = pickedObj.findNetTag('cell')
            if not pickedObj.isEmpty():
                cell = grid[int(pickedObj.getX())][int(pickedObj.getY())]
                cell.alive = not cell.alive
                cell.draw()

def clearGrid(): #function menghapus grid
    for row in grid:
        for cell in row:
            cell.alive = False
    draw()

base.accept('mouse1', handlePick)

initialize()
base.run()
