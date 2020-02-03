## TKPAINTER: Inspired by Microsoft Paint 
## By Shayan Panjwani
##

## Citations:

## Speech Recognitio
# n from https://pypi.org/project/SpeechRecognition/
## CMU 112 Graphics from http://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
## colorList compiled by me

import speech_recognition as sr
from cmu_112_graphics import *
from colorList import colorListLegit
from tkinter import *
from tkinter.colorchooser import *
import tkinter.scrolledtext as tkst
from tkinter import ttk
import os
import copy, math

# Used to update value of Voice response variable
def setInput(text, value):
    text.delete(1.0, "END")
    text.insert("END", value)

# Used to compile words/phrases to check for speech recognition of phrases
def listSubsetter(L):
    subsets = []
    for first in range(len(L)):
        for end in range(first, len(L)):
            subsets.append("".join(L[first:end+1]))
    return subsets

# class for Shapes to be drawn
class Shape(object):
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def __repr__(self):
        return f"{self.color.upper()} shape with radius {self.radius} at ({self.x}, {self.y})"

class Circle(Shape):
    pass

class Triangle(Shape):
    pass

class Rectangle(Shape):
    pass


class TKPAINTER(ModalApp):
    def appStarted(app):
        app.mode = Mode()
        app.loadScreen = LoadMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.loadScreen)
        app.mouseMovedDelay = 1

class LoadMode(Mode):
    def appStarted(mode):
        mode.logo = ImageTk.PhotoImage(mode.scaleImage(mode.loadImage("https://i.imgur.com/t3UH0lB.png"), 1 / 2))
        mode.bkgdImg = mode.loadImage("https://i.imgur.com/kLfDWCC.png")
        mode.bkgdImg = mode.bkgdImg.resize((mode.width, mode.height), resample=0)
        mode.bkgd = ImageTk.PhotoImage(mode.bkgdImg)
        
    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.helpMode)

    def mousePressed(mode, event):
        mode.app.setActiveMode(mode.app.helpMode)
        
    def redrawAll(mode, canvas):
        canvas.create_image(mode.width // 2, mode.height // 2, image=mode.bkgd)
        canvas.create_image(mode.width // 2, mode.height // 2, image=mode.logo)
        canvas.create_text(mode.width//2, mode.height - 20, text="Press any Key to Begin!", font=('Comic Sans MS', 20, 'bold italic')  )

class HelpMode(Mode):
    def appStarted(mode):
        mode.bkgdImg = mode.loadImage("https://i.imgur.com/RRMBLpx.png")
        mode.bkgdImg = mode.bkgdImg.resize((mode.width, mode.height), resample=0)
        mode.bkgd = ImageTk.PhotoImage(mode.bkgdImg)



    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.mode)

    def mousePressed(mode, event):
        mode.app.setActiveMode(mode.app.mode)

    def redrawAll(mode, canvas):
        canvas.create_image(mode.width // 2, mode.height // 2, image=mode.bkgd)


class Mode(Mode):
    def appStarted(mode):
        mode.isDrawing = False
        # MENU AND BUTTONS

        mode.mic = sr.Microphone()
        mode.recognition = sr.Recognizer()
        mode.menuHeight = mode.height // 7
        mode.statsHeight = mode.height // 30


        mode.targetLogo = ImageTk.PhotoImage(mode.scaleImage(mode.loadImage("https://i.imgur.com/TuSjwAS.png"), 1/10))
        mode.micLogo = ImageTk.PhotoImage(mode.scaleImage(mode.loadImage("https://i.imgur.com/q22MI6a.png"), 1/10))
        mode.paintbrushLogo = ImageTk.PhotoImage(mode.scaleImage(mode.loadImage("https://i.imgur.com/aP9wknR.png"), 1/10))
        mode.circleLogo = ImageTk.PhotoImage(mode.scaleImage(mode.loadImage("https://i.imgur.com/WlBL3qX.png"), 1/20))
        mode.triLogo = ImageTk.PhotoImage(mode.scaleImage(mode.loadImage("https://i.imgur.com/h5LH5JF.png"), 1/20))
        mode.rectLogo = ImageTk.PhotoImage(mode.scaleImage(mode.loadImage("https://i.imgur.com/kLGxq07.png"), 1/20))
        
        
        mode.colorsLogo = ImageTk.PhotoImage(mode.scaleImage(mode.loadImage("https://i.imgur.com/kLgOuJ5.png"), 1/10))

        mode.Exit = Button(mode.app._canvas, text="Quit", fg="red",
                    command=quit, height=20, width=20)
        
        mode.colorButton = Button(mode.app._canvas, text="Color Picker",
            image = mode.colorsLogo, compound = "top", command = mode.pickColor)

        mode.speechColorButton = Button(mode.app._canvas, text="Voice Assistant!",
            image = mode.micLogo, compound = "top", command=mode.listenForInput)

        mode.brushOptions = ["fountain pen",
                           "paintbrush",
                           "eraser"]
        # mode.selectedBrush = StringVar(mode.app._canvas)
        # mode.selectedBrush.set(mode.brushOptions[0])
        # mode.brushDropDown = OptionMenu(mode.app._canvas, mode.selectedBrush, *mode.brushOptions)

        mode.selectedBrush = ttk.Combobox(mode.app._canvas, values=mode.brushOptions)
        mode.selectedBrush.set("paintbrush")
        mode.selectedBrush.bind("<<ComboboxSelected>>", mode.noLongerDrawing)

        # mode.brushFrame = Frame(mode.app._canvas, )

        # mode.brushSizes = range(1,50)
        # mode.bSize = IntVar(mode.app._canvas)
        # mode.bSize.set(mode.brushSizes[4])
        mode.sizes = range(0,25)
        mode.bSize = ttk.Combobox(mode.app._canvas, values=list(mode.sizes))
        mode.bSize.set(5)
        mode.bSize.bind("<<ComboboxSelected>>", mode.noLongerDrawing())

        mode.circleButton = Button(mode.app._canvas, text="Circles",
            image=mode.circleLogo, compound="top", command=mode.selectCircle)
        mode.rectButton = Button(mode.app._canvas, text="Rectangles",
            image = mode.rectLogo, compound = "top", command = mode.selectRectangle)
        mode.triButton = Button(mode.app._canvas, text="Triangles",
            image = mode.triLogo, compound = "top", command = mode.selectTriangle)



        mode.legitMenu = Menu(mode.app._root)
        mode.app._root.config(menu=mode.legitMenu)
        fileMenu = Menu(mode.legitMenu)
        fileMenu.add_command(label="Exit", command=quit)
        fileMenu.add_command(label="Save", command=mode.saveCanvasScreenshot)
        fileMenu.add_command(label="Load", command=mode.loadCanvas)
        fileMenu.add_command(label="Help", command=mode.changeToHelp)
        mode.legitMenu.add_cascade(label="File", menu=fileMenu)
        mode.legitMenu.add_command(label="Clear Canvas", command=mode.clearCanvas)

        
        mode.menuButtons = [mode.selectedBrush, mode.bSize, mode.circleButton, mode.rectButton, mode.triButton, mode.colorButton, mode.speechColorButton, mode.Exit]

        mode.color = "blue"


        #Painting Area
        mode.mouseX, mode.mouseY = mode.width//2, mode.height//2
        mode.cursor = mode.targetLogo
        mode.app._root.configure(cursor='plus')

        mode.brushDict = {'paintbrush': 3, 'fountain pen': 1}
        
        mode.drawingW = mode.width
        mode.drawingHeight = mode.height - mode.menuHeight - mode.statsHeight
        mode.drawingRange = range(mode.menuHeight, mode.height-mode.statsHeight)
        
        mode.bkgdImg = mode.loadImage("https://i.imgur.com/nABPMt2.jpg")
        mode.bkgdImg = mode.bkgdImg.resize((mode.drawingW, mode.drawingHeight), resample=0)
        mode.bkgd = ImageTk.PhotoImage(mode.bkgdImg)


        mode.objectList = []
        mode.circleR = 3*int(mode.bSize.get())
        mode.lastCircle = None

        mode.lastX, mode.lastY = 0, 0

    def clearCanvas(mode):
        mode.objectList = []
        mode.bkgdImg = mode.loadImage("https://i.imgur.com/RRMBLpx.png")
        mode.bkgdImg = mode.bkgdImg.resize((mode.width, mode.height), resample=0)
        mode.bkgd = ImageTk.PhotoImage(mode.bkgdImg)

    def canvasScreenshot(mode):
        mode.app._showRootWindow()
        x0 = mode.app._root.winfo_rootx() + mode.app._canvas.winfo_x()
        y0 = mode.app._root.winfo_rooty() + mode.app._canvas.winfo_y() + mode.menuHeight
        result = ImageGrabber.grab((x0,y0,x0+mode.app.width,y0+mode.app.height-mode.statsHeight-mode.menuHeight))
        return result
    
    def saveCanvasScreenshot(mode):
        path = filedialog.asksaveasfilename(initialdir=os.getcwd(), title='Select file: ',filetypes = (('png files','*.png'),('all files','*.*')))
        if (path):
            # defer call to let filedialog close (and not grab those pixels)
            if (not path.endswith('.png')): path += '.png'
            print("Saving!")
            mode.app._deferredMethodCall(afterId='saveCanvasScreenshot', afterDelay=0, afterFn=lambda:mode.canvasScreenshot().save(path))

    def loadCanvas(mode):
        path = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select file: ',filetypes = (('png files','*.png'),('all files','*.*')))
        if (path):
            print("path found")
            mode.clearCanvas()
            mode.bkgdImg = mode.loadImage(path)
            print("image loaded")
            mode.bkgdImg = mode.bkgdImg.resize((mode.width, mode.height), resample=0)
            mode.bkgd = ImageTk.PhotoImage(mode.bkgdImg)

    def selectCircle(mode):
        if mode.detectBrush() != "circle":
            mode.app._root.configure(cursor='circle')
            mode.deselectAll()
            mode.selectedBrush.set("circle")
            mode.circleButton.config(relief=SUNKEN)
        else:
            mode.selectedBrush.set(mode.brushOptions[0])
            mode.circleButton.config(relief=RAISED)

    def selectTriangle(mode):
        if mode.detectBrush() != "triangle":
            mode.app._root.configure(cursor='circle')
            mode.deselectAll()
            mode.selectedBrush.set("triangle")
            mode.triButton.config(relief=SUNKEN)
        else:
            mode.deselectAll()
            mode.selectedBrush.set(mode.brushOptions[0])
            
    def selectRectangle(mode):
        if mode.detectBrush() != "rectangle":
            mode.app._root.configure(cursor='circle')
            mode.deselectAll()
            mode.selectedBrush.set("rectangle")
            mode.rectButton.config(relief=SUNKEN)
        else:
            mode.selectedBrush.set(mode.brushOptions[0])
            mode.deselectAll()    

    def deselectAll(mode):
            mode.rectButton.config(relief=RAISED)
            mode.circleButton.config(relief=RAISED)
            mode.triButton.config(relief=RAISED)
            mode.selectedBrush.set("fountain pen")

    def changeToHelp(mode):
        mode.app.setActiveMode(mode.app.helpMode)

    def listenForInput(mode):
        brushTest = False
        sizeCheck = False
        with mode.mic as source:
            print(f"Current Color: {mode.color}\nSay Command:")
            mode.speechColorButton.config(relief=SUNKEN)
            mode.recognition.adjust_for_ambient_noise(source)
            audio = mode.recognition.listen(source)
            print("Processing...")
            try: recognized = mode.recognition.recognize_google(audio)
            except:
                mode.speechColorButton.config(relief=RAISED)
                print(f"Input! Current Brush: {mode.detectBrush()}, Current Color: {mode.color}")
                return
            if "cancel" in recognized:
                mode.speechColorButton.config(relief=RAISED)
                return
            potentialWords = listSubsetter(recognized.split(" "))
            bestWord = ""
            bestBrush = ""
            bestSize = -1
            print(recognized)
            if "brush" in recognized:
                brushTest = True
            for word in potentialWords:
                if word.lower() in colorListLegit and len(word) > len(bestWord):
                    bestWord = word.lower()
                if (word in ("paintbrush", "fountainpen", "circle", "circles",
                            "triangle", "triangles", "rectangle", "rectangles", "eraser")
                            and word != mode.detectBrush()):
                        bestBrush = word
                if "size" in word.lower():
                    sizeCheck = True
                    print("check the size!")
                if sizeCheck and word.isdigit():
                    bestSize = int(word)
                    print("gonna size like", bestSize)
            if bestWord != "":
                mode.color = bestWord
                print(f"Color Updated! New Color: {mode.color}")
            else:
                print(f"Color not recognized! Current Color: {mode.color}")
            if brushTest and bestBrush != "":
                print(f"Brush not recognized! Current Brush: {mode.detectBrush()}")
            if bestBrush != "":
                mode.deselectAll()
                if bestBrush[-1] == "s":
                    bestBrush = bestBrush[:-1]
                if bestBrush == "fountainpen":
                    bestBrush = "fountain pen"
                    print(bestBrush)
                mode.selectedBrush.set(bestBrush)
                print(f"Brush Updated! New Brush: {mode.detectBrush()}")
            if sizeCheck and bestSize < 0:
                print(f"Size not recognized! Current Size: {mode.detectSize()}")
            if bestSize > 0:
                mode.bSize.set(bestSize)
                print(f"Size Updated! New Size: {mode.detectSize()}")
            mode.speechColorButton.config(relief=RAISED)

                
    def pickColor(mode):
        color = askcolor()
        mode.color = color[1]
    
    def detectBrush(mode):
        return mode.selectedBrush.get()

    def detectSize(mode):
        return int(mode.bSize.get())
        

    def keyPressed(mode, event):
        if event.key == "s":
            mode.app.saveCanvasSnapshot()
        elif event.key == "Space":
            mode.listenForInput()
        elif event.key == "h":
            mode.app.setActiveMode(mode.app.helpMode)
        elif event.key == "Esc":
            quit()

        
    def noLongerDrawing(mode, *args):
        mode.isDrawing = False
            
    def mouseMoved(mode, event):
        if event.y in mode.drawingRange:
            if (mode.mouseX, mode.mouseY) == (None, None):
                    mode.lastX, mode.lastY = event.x, event.y
                    mode.mouseX, mode.mouseY = event.x, event.y
                    return
            mode.lastX, mode.lastY = mode.mouseX, mode.mouseY
            mode.mouseX, mode.mouseY = event.x, event.y
        else:
            mode.noLongerDrawing()
            mode.mouseX, mode.mouseY = None, None

    def mousePressed(mode, event):
        if event.y in mode.drawingRange:
            if mode.detectBrush() in ("paintbrush", "fountain pen"):
                mode.isDrawing = True
            elif mode.detectBrush() == "circle":
                mode.objectList.append(Circle(event.x, event.y, mode.circleR, mode.color))
            elif mode.detectBrush() == "triangle":
                mode.objectList.append(Triangle(event.x, event.y, mode.circleR, mode.color))
            elif mode.detectBrush() == "rectangle":
                mode.objectList.append(Rectangle(event.x, event.y, mode.circleR, mode.color))
            elif mode.detectBrush() == "eraser":
                mode.objectList.append([mode.mouseX, mode.mouseY, event.x, event.y, "paintbrush", "white", int(mode.bSize.get())])

    def mouseDragged(mode, event):
        if event.y in mode.drawingRange:
            if mode.isDrawing:
                if (mode.mouseX, mode.mouseY) == (None, None):
                    mode.lastX, mode.lastY = event.x, event.y
                    mode.mouseX, mode.mouseY = event.x, event.y
                elif mode.detectBrush() in ("paintbrush", "fountain pen"):
                    mode.objectList.append([mode.mouseX, mode.mouseY, event.x, event.y, mode.detectBrush(), mode.color, int(mode.bSize.get())])
                elif mode.detectBrush() == "eraser":
                    mode.objectList.append([mode.mouseX, mode.mouseY, event.x, event.y, "paintbrush", "white", int(mode.bSize.get())])
                mode.lastX, mode.lastY = mode.mouseX, mode.mouseY
                mode.mouseX, mode.mouseY = event.x, event.y

    def mouseReleased(mode, event):
        if mode.isDrawing:
            mode.noLongerDrawing()

    def timerFired(mode):
        mode.circleR = 3 * mode.detectSize()
        if mode.detectBrush() not in ("circle", "rectangle", "triangle"):
            mode.app._root.configure(cursor='pencil')
        elif mode.detectBrush() == "eraser":
            mode.app._root.configure(cursor='plus')
            

    def drawStats(mode, canvas):
        statsHeight = mode.statsHeight
        statsWidth = mode.width//3
        canvas.create_rectangle(0, mode.height - statsHeight, mode.width, mode.height)        
        for i in range(3):
            canvas.create_rectangle(i*statsWidth,mode.height-statsHeight, (i+1)*statsWidth,mode.height)
        canvas.create_text(5, mode.height - statsHeight,
                text=f"\tColor: {mode.color}", anchor="nw", fill=mode.color)
        canvas.create_text(statsWidth + 5, mode.height - statsHeight,
                text= f"     Current Brush: {mode.detectBrush()}", anchor= "nw")
        canvas.create_text(statsWidth * 2 + 5, mode.height - statsHeight,
            text =f"\t({mode.mouseX},{mode.mouseY})",
            anchor="nw")


    def drawObjects(mode, canvas):
        for obj in mode.objectList:
            if type(obj) == Circle:
                x, y, r, color = obj.x, obj.y, obj.radius, obj.color
                canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)
            elif type(obj) == Triangle:
                x, y, r, color = obj.x, obj.y, obj.radius, obj.color
                (x1, y1) = (x, y-r)
                (x2, y2) = (x+math.cos(math.pi*7/6)*r, y-math.sin(math.pi*7/6)*r)
                (x3, y3) = (x+math.cos(math.pi*11/6)*r, y-math.sin(math.pi*11/6)*r)
                canvas.create_polygon(x1, y1, x2, y2, x3, y3, fill=color)

            elif type(obj) == Rectangle:
                x, y, r, color = obj.x, obj.y, obj.radius, obj.color
                canvas.create_rectangle(x - r, y - r, x + r, y + r, fill=color)
            else:
                x1, y1, x2, y2, brushType, color, size = obj
                if brushType == "paintbrush":
                    canvas.create_line(x1, y1 , x2 , y2 , smooth=1, width=size ,fill=color)
                elif brushType == "fountain pen":
                    for i in range(-size//2,size//2):
                        canvas.create_line(x1 + i, y1 + i, x2 + i, y2 + i, smooth=1, fill=color)

    def redrawAll(mode, canvas):
        canvas.create_image(mode.drawingW // 2, mode.drawingHeight // 2 + mode.menuHeight, image=mode.bkgd)
        canvas.create_rectangle(0, 0, mode.width, mode.menuHeight, fill="gray")
        buttonCount = len(mode.menuButtons)
        buttonWidth = mode.width//buttonCount
        for i in range(buttonCount):
            button = mode.menuButtons[i]
            if type(button) == ttk.Combobox:
                button.place(x=i * buttonWidth, y=0, height=(mode.menuHeight // 3), width=buttonWidth)
            else: button.place(x=i * buttonWidth, y=0, height=mode.menuHeight, width=buttonWidth)
        mode.drawObjects(canvas)
        canvas.create_rectangle(0, mode.height - mode.statsHeight, mode.width, mode.height, fill="gray")
        mode.drawStats(canvas)
        

app = TKPAINTER(width = 800, height = 600)