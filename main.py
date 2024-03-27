import tkinter as tk
import random
import os
import json

class Main:
    '''Main class used to connect the other objects'''
    def __init__(self):
        '''Creates the other objects'''
        self.Level_Folder_Path = os.getcwd() + r"\Level_Folder\ "[:-1]

        self.Win = Root(self)
        self.Level = LevelOperator(self)

        self.Win.SetMenu()

        self.Win.mainloop()

    @property
    def Level_Files_List(self) -> list:
        '''Method binded with the Property decorator to be called like an attribut,
        returning the list of the names of the json files stored in the folder Level_Folder'''

        return sorted([file[:-5] for file in os.listdir(self.Level_Folder_Path) if file.endswith(".json")])


    def CallMenu(self):
        '''Prepares the game to open the menu by destroying the widget buttons from levels,
        cleaning the labels and canvas, and unbinding the keyboard before openning the Menu screen'''
        self.Win.Menu_Button.destroy()
        self.Win.Recur_Button.destroy()
        self.Win.ReselLabels()
        self.Win.Canvas.delete('Level_Object')
        self.Win.unbind('<Key>')
        self.Win.SetMenu()

    def CallLevel(self, level_name):
        '''Setup the level called by calling the Win method displaying it,
        creating and reseting the needed attributs and binding the keyboard
        to detect key presses'''
        self.Win.SetLevel(level_name)
        self.current_level = level_name
        self.Pile = []
        self.Win.bind('<Key>', self.KeyPress)


    def KeyPress(self, event):
        '''Method binded to the entire keyboard during a level and reacting to
        the arrows as player path input, storing them,
        the backspace to delete inputs,
        and Enter (Return) key to start the level'''
        key_pressed = event.keysym
        if key_pressed == 'Return'\
        and len(self.Pile) > 0:
            self.Win.Menu_Button.destroy()
            self.Win.Recur_Button.destroy()
            self.Win.unbind('<Key>')
            self.Level.RunLevel(self.current_level)
            return

        elif key_pressed == 'BackSpace'\
        and len(self.Pile) > 0:
            self.Pile.pop()

        elif key_pressed in ('Up','Down','Left','Right')\
        and len(self.Pile) < 15:
            self.Pile.append(key_pressed)

        self.Win.UpdateInputLabels()


    def Victory(self):
        '''Called when victory occurs, calling the victory animation then calling the Menu'''
        self.Win.Canvas.VictoryAnimation()
        self.CallMenu()

    def ResetLevel(self):
        '''Called when a lose occurs, calling the death animation then reseting the level before calling it back'''
        self.Win.Canvas.DeathAnimation()
        self.Win.UpdateMemoryLabel()
        self.CallLevel(self.current_level)


    def StartAutoSolve(self):
        '''Binded with the AutoSolve Button, it extracts the level data from its json file,
        calls the recursive AutoSolve method then sends the results to the method displaying them'''
        with open(self.Level_Folder_Path + self.current_level +'.json', 'r') as f:
            lv_data = json.load(f)

        player_coo = lv_data['Player_Starter_Coo']
        self.victory_cell_coo = lv_data['Victory_Cell_Move']
        self.red_cells = lv_data['Red_Cells_Move']

        self.Visited_Boxes = [[] for i in range(15)]

        path : str = self.AutoSolveRecur(player_coo, '0,0', -1)
        self.Win.DisplayAutoSolve(path)

    def AutoSolveRecur(self, prev_pos, move, step):
        '''Recursive method simulating every player movement possible with a random priority order to create varying results,
        storing them to prevent multiple paths leading to the same box in the same amount of moves, effectively saving ressources.
        Returns its move upon reaching the Victory Cell and 'Fail' upon meeting one of the lose conditions
        A move is a string composed of two values separated by a comma to be split.
        The path is a string composed of an moves separated by a semicolon to be split during the path displaying'''

        # Update Player Coo
        curr_pos = [prev_pos[0]+int(move.split(',')[0]), prev_pos[1]+int(move.split(',')[1])]

        # Victory Check
        if curr_pos == self.victory_cell_coo[step-1] or curr_pos == self.victory_cell_coo[step]:
            return move

        # Death Check : Out of moves, Out of Bounds, Encountered Red Cell
        if self.RecurDeathCheck(curr_pos, step):
            return 'Fail'

        # Else add current_position to Visited_Boxes to prevent creating
        # multiple similar path
        self.Visited_Boxes[step].append(curr_pos)

        # Define available moves
        move_list = ['0,75', '0,-75', '75,0', '-75,0']

        # Simulate player moving in all 4 directions in a random order
        # Return 'Fail' if every children failed, else return children
        # path plus its own
        Recur1 = self.AutoSolveRecur(curr_pos, move_list.pop(random.randint(0,3)), step+1)
        if Recur1 != 'Fail':
            return move+';'+Recur1

        Recur2 = self.AutoSolveRecur(curr_pos, move_list.pop(random.randint(0,2)), step+1)
        if Recur2 != 'Fail':
            return move+';'+Recur2

        Recur3 = self.AutoSolveRecur(curr_pos, move_list.pop(random.randint(0,1)), step+1)
        if Recur3 != 'Fail':
            return move+';'+Recur3

        Recur4 = self.AutoSolveRecur(curr_pos, move_list[0], step+1)
        if Recur4 != 'Fail':
            return move+';'+Recur4

        return 'Fail'

    def RecurDeathCheck(self, curr_pos, step) -> bool:
        '''Separated from AutoSolveRecur, checks player death conditions'''
        return step >= 14\
        or curr_pos[0] < 0\
        or curr_pos[0] >= 750\
        or curr_pos[1] < 0\
        or curr_pos[1] >= 375\
        or [True for red_cell in self.red_cells if curr_pos == red_cell[step-1] or curr_pos == red_cell[step]]\
        or curr_pos in self.Visited_Boxes[step]

################################################################################

class Root(tk.Tk):
    '''Root class, inhereted from the Tk window class in charge of the widgets'''
    def __init__(self, main):
        '''Creates the root object method 'tksleep',
        Stores the address of Main,
        Creates the Labels, storing their adresses in lists'''
        super().__init__()

        # Creating a root method to add delay,
        # called like sleep() for time module
        # but without freezing the window
        # it was entirely found on Stack Overflow
        ### From Stack Overflow ###
        def tksleep(self, time:float) -> None:
            self.after(int(time*1000), self.quit)
            self.mainloop()
        tk.Misc.tksleep = tksleep
        ###########################

        self.Main = main
        self.Canvas = Canvas(self.Main, self)

        self.title("OverMove")
        self.geometry("%dx%d" % (800,600)) # window size
        self.resizable(0,0)

        self.CharacterConversion = {
            'Up'    : '⮝', '0,-75' : '⮝',
            'Down'  : '⮟', '0,75'  : '⮟',
            'Left'  : '⮜', '-75,0' : '⮜',
            'Right' : '⮞', '75,0'  : '⮞'}
        ### Labels Creation ###
        # invisible Label to pad the other widgets
        tk.Label(self, width = 0).grid(row=0, column=0, padx = 4)

        # Location Text Label
        tk.Label(self, width = 1, height = 3, pady = 7, bg='white', borderwidth=3, relief="solid").grid(row=0, column=1, columnspan=10, sticky='ew', pady = 5)
        self.location = tk.StringVar()
        tk.Label(self, textvariable = self.location, width = 1, height = 1, font=('Arial', 20), bg='white', pady = 7, anchor="w", justify="left").grid(row=0, column=2, columnspan=3, sticky='ew', pady = 5)

        # Creating the textvars for the Input labels
        self.Input_Label_Textvariable_List = [tk.StringVar() for _ in range(15)]
        # Creating the Input Labels
        self.Input_Label_List = [
            tk.Label(self, textvariable = Textvar, width = 1, height = 1, bg="white", borderwidth=3, relief="solid", font=('Arial', 25), pady = 4)
            for Textvar in self.Input_Label_Textvariable_List
            ]
        # Placing the Input labels on the grid
        i = 0
        for label in self.Input_Label_List:
            label.grid(row=2, column=i+1, sticky='ew', pady = 5)
            i += 1

        # Creating the textvars for the Memory labels
        self.Memory_Label_Textvariable_List = [tk.StringVar() for _ in range(15)]
        # Creating the Memory labels
        self.Memory_Label_List = [
            tk.Label(self, textvariable = Textvar, width = 1, height = 1, bg="white", borderwidth=3, relief="solid", font=('Arial', 25), pady = 4)
            for Textvar in self.Memory_Label_Textvariable_List
            ]
        # Placing the Memory labels on the grid
        i = 0
        for label in self.Memory_Label_List:
            label.grid(row=1, column=i+1, sticky='ew', pady = 5)
            i += 1

    def MenuClick(self, event):
        '''Calls the level stored in the tags of the last Canvas object clicked'''
        element_tags = self.Canvas.gettags("current")

        if len(element_tags) == 0:
            return

        self.Main.CallLevel(element_tags[0])


    def SetMenu(self):
        '''Displays the menu screen'''
        self.location.set("Menu")

        self.Canvas.SetMenu(self.Main.Level_Files_List)

        self.bind('<Button-1>', self.MenuClick)


    def SetLevel(self, level):
        '''Displays the level called'''
        self.location.set(level)

        self.unbind('<Button-1>')

        self.Recur_Button = tk.Button(self, text ='Auto Solve', font=('Arial', 18), bg='white', pady = 9, relief=tk.SOLID, borderwidth=3, command = self.Main.StartAutoSolve)
        self.Recur_Button.grid(row=0, column=13, columnspan=3, sticky='ew')

        self.Menu_Button = tk.Button(self, text ='Menu', font=('Arial', 18), bg='white', pady = 9, relief=tk.SOLID, borderwidth=3, command = self.Main.CallMenu)
        self.Menu_Button.grid(row=0, column=11, columnspan=2, sticky='ew')

        self.Canvas.SetLevel(level)

    def UpdateInputLabels(self):
        '''Updates every Input Label. Called after player input'''
        for i in range(len(self.Input_Label_Textvariable_List)):
            if i < len(self.Main.Pile):
                self.Input_Label_Textvariable_List[i].set(self.CharacterConversion[self.Main.Pile[i]])

            else:
                self.Input_Label_Textvariable_List[i].set('')

    def PlayerUpdate(self):
        '''Changes the background of the label containing the current player move played,
        Calls Canvas to update player cell'''
        self.Input_Label_List[self.Main.Level.step-1].config(bg="white")
        self.Input_Label_List[self.Main.Level.step].config(bg="cornflower blue")
        self.Canvas.CanPlayerUpdate()

    def CellUpdate(self):
        '''Calls Canvas to update the victory and red cells'''
        self.Canvas.CanCellUpdate()

    def UpdateMemoryLabel(self):
        '''Called when reseting a level
        Stores the moves from the Input Labels to the Memory Labels before reseting the Input Labels
        Colors the background of the Memory Label containing the last instruction played'''
        for i in range(15):
            self.Input_Label_List[i].config(bg="white")
            self.Memory_Label_List[i].config(bg="white")
            self.Memory_Label_Textvariable_List[i].set(self.Input_Label_Textvariable_List[i].get())
            self.Input_Label_Textvariable_List[i].set('')

        self.Memory_Label_List[self.Main.Level.step-1].config(bg="firebrick1")

    def ReselLabels(self):
        '''Resets the colour and text of the Input and Memory Labels'''
        for i in range(15):
            self.Input_Label_List[i].config(bg="white")
            self.Memory_Label_List[i].config(bg="white")
            self.Input_Label_Textvariable_List[i].set('')
            self.Memory_Label_Textvariable_List[i].set('')

    def DisplayAutoSolve(self, path):
        '''Display results of AutoSolve in memory label'''

        path = path.split(';')[1:]

        for i in range(15):
            self.Memory_Label_List[i].config(bg="white")
            self.Memory_Label_Textvariable_List[i].set('')

        i = 0
        for move in path:
            self.Memory_Label_Textvariable_List[i].set(self.CharacterConversion[move])

            i += 1

################################################################################

class Canvas(tk.Canvas):
    '''Canvas inhereted from the Tkinter Canvas widget charged of canvas object creation and storage'''
    def __init__(self, main, root):
        '''Stores the adresses of Main and Win'''
        super().__init__(root, width=750, height=375, highlightbackground='black', highlightthickness=3)
        self.grid(row=3, column=1, columnspan=15 , padx=10, pady=5)

        self.Win = root
        self.Main = main


    def SetMenu(self, level_list):
        '''Diplays the Canvas part of the menu
        Draws the level buttons from a text object and a rectangle object with the name of their level in the tags'''
        menu_buttons_pos = ((135,110),(295,110),(455,110),(615,110),(135,265),(295,265),(455,265),(615,265))
        i = 0
        for posx, posy in menu_buttons_pos:
            self.create_rectangle(posx-60, posy-35, posx+60, posy+35, fill='SteelBlue3', outline="grey26",width=5, tags=(level_list[i], "Menu_Objects"))
            self.create_text(posx, posy, text=level_list[i], font=("Arial", 25), tags=(level_list[i], "Menu_Objects"))
            i += 1

    def SetLevel(self, level):
        '''Draws the Canvas part of a level,
        extracting the level's informations from its json file and displaying them'''
        self.delete('Menu_Objects', 'Level_Object')

        # Drawing the grid
        for i in range(10):
            self.create_line(75*i,0,75*i,375, fill="black", width=2, tags=('grid', 'Level_Object'))
        for i in range(5):
            self.create_line(0,75*i,750,75*i, fill="black", width=2, tags=('grid', 'Level_Object'))

        with open(self.Main.Level_Folder_Path + level +'.json', 'r') as f:
            lv_data = json.load(f)

        player_coo = lv_data['Player_Starter_Coo']
        victory_cell_coo = lv_data['Victory_Cell_Starting_Coo']
        red_cells = lv_data['Red_Cells_Starter_Coo']
        arrows = lv_data['Arrow']

        self.create_rectangle(player_coo[0]+10, player_coo[1]+10, player_coo[0]+65, player_coo[1]+65, fill='blue', tags=('Player_Cell', 'Level_Object'))
        self.create_rectangle(victory_cell_coo[0]+5, victory_cell_coo[1]+5, victory_cell_coo[0]+70, victory_cell_coo[1]+70, outline='blue', width=10, tags=('Victory_Cell', 'Level_Object'))

        for red_cell in red_cells:
            self.create_rectangle(red_cell[0]+5, red_cell[1]+5, red_cell[0]+70, red_cell[1]+70, outline='red', width=10, tags=('Red_Cell', 'Level_Object'))

        for arrow in arrows:
            if len(arrow) < 5:
                self.create_text(arrow[0]*75+37.5, arrow[1]*75+37.5, text=arrow[2], fill=arrow[3], font=("Arial", 28), tags=('arrows', 'Level_Object'))
            else:
                match arrow[-1]:
                    case 'left':
                        self.create_text(arrow[0]*75+27.5, arrow[1]*75+37.5, text=arrow[2], fill=arrow[3], font=("Arial", 28), tags=('arrows', 'Level_Object'))
                    case 'right':
                        self.create_text(arrow[0]*75+47.5, arrow[1]*75+37.5, text=arrow[2], fill=arrow[3], font=("Arial", 28), tags=('arrows', 'Level_Object'))
                    case 'up':
                        self.create_text(arrow[0]*75+37.5, arrow[1]*75+27.5, text=arrow[2], fill=arrow[3], font=("Arial", 28), tags=('arrows', 'Level_Object'))
                    case 'down':
                        self.create_text(arrow[0]*75+37.5, arrow[1]*75+47.5, text=arrow[2], fill=arrow[3], font=("Arial", 28), tags=('arrows', 'Level_Object'))
                    case _:
                        print('arrow position unknown')


    def CanPlayerUpdate(self):
        '''Erases the Player Cell and draws it at the new position'''
        self.delete('Player_Cell')

        self.create_rectangle(self.Main.Level.player_coo[0]+10,
                              self.Main.Level.player_coo[1]+10,
                              self.Main.Level.player_coo[0]+65,
                              self.Main.Level.player_coo[1]+65,
                              fill='blue', tags=('Player_Cell', 'Level_Object'))

    def CanCellUpdate(self):
        '''Erases the Victory and Red Cells and draws them at their new position'''
        self.delete('Victory_Cell', 'Red_Cell')

        self.create_rectangle(self.Main.Level.victory_cell_coo[self.Main.Level.step-1][0]+5,
                              self.Main.Level.victory_cell_coo[self.Main.Level.step-1][1]+5,
                              self.Main.Level.victory_cell_coo[self.Main.Level.step-1][0]+70,
                              self.Main.Level.victory_cell_coo[self.Main.Level.step-1][1]+70,
                              outline='blue', width=10, tags=('Victory_Cell', 'Level_Object'))

        for red_cell in self.Main.Level.red_cells:
            self.create_rectangle(red_cell[self.Main.Level.step-1][0]+5,
                                  red_cell[self.Main.Level.step-1][1]+5,
                                  red_cell[self.Main.Level.step-1][0]+70,
                                  red_cell[self.Main.Level.step-1][1]+70,
                                  outline='red', width=10, tags=('Red_Cell', 'Level_Object'))

    def VictoryAnimation(self):
        '''Plays the victory animation requiring the tksleep method created in the initialisation of the Win
        to add delay in a concise and intuitive way'''

        self.Win.tksleep(0.5)
        self.create_rectangle(225 , 110, 525, 265, outline='black', width=5, fill='white', tags='Level_Object')
        self.Win.tksleep(0.5)

        text = self.Main.current_level
        Victory_Level_Text = self.create_text(375, 160, font=('Helvetica 35 bold'), tags="Level_Object")
        for i in range(len(text)):
            self.itemconfig(Victory_Level_Text, text=text[0:i+1])
            self.Win.tksleep(0.1)

        text = 'Victory'
        Victory_Message_Text = self.create_text(375, 215 ,font=('Helvetica 35 bold'), tags="Level_Object")
        for i in range(len(text)):
            self.itemconfig(Victory_Message_Text, text=text[0:i+1])
            self.Win.tksleep(0.1)

        self.Win.tksleep(1)
        for i in range(5):
            for j in range(5):
                self.create_rectangle(i*75,j*75,i*75+75,j*75+75,width=0, fill='blue', tags='Level_Object')
                self.create_rectangle(750-(i*75),375-(j*75),750-(i*75+75),375-(j*75+75),width=0, fill='blue', tags='Level_Object')
                self.Win.tksleep(0.06)

    def DeathAnimation(self):
        '''Plays the death animation, also using the tklsleep method'''
        self.delete("Player_Cell")
        circle_size = 10
        for i in range(5):
            self.create_oval(self.Main.Level.player_coo[0]+10-circle_size*i,
                             self.Main.Level.player_coo[1]+10-circle_size*i,
                             self.Main.Level.player_coo[0]+60+circle_size*i,
                             self.Main.Level.player_coo[1]+60+circle_size*i, outline='blue', width=20, tags="death_circle")
            self.Win.tksleep(0.05)
            self.delete("death_circle")

class LevelOperator:
    '''Class operating the running time of a level'''
    def __init__(self, main):
        '''Storing the Main object adresses'''
        self.Main = main


    def RunLevel(self, level):
        '''The name is self explanatory, called when a level in ran
        Extracting the level data from its file and starting a recursive loop alternating between player and cell movement
        checking if the player won or lost at every step'''

        self.current_level = level
        self.step = 0

        with open(self.Main.Level_Folder_Path + level +'.json', 'r') as f:
            lv_data = json.load(f)

        self.player_coo = lv_data['Player_Starter_Coo']
        self.victory_cell_coo = lv_data['Victory_Cell_Move']
        self.red_cells = lv_data['Red_Cells_Move']

        self.PlayerMove()


    def PlayerMove(self):
        '''Updates the player position according to the next move stored in the Pile
        Calls Win to update the Labels and Canvas
        Checks the victory and failure conditions then calls the next step in the recursive loop'''
        # Update Player Coo
        direction = self.Main.Pile[self.step]

        match direction:
            case 'Up':
                self.player_coo[1] -= 75
            case 'Down':
                self.player_coo[1] += 75
            case 'Left':
                self.player_coo[0] -= 75
            case 'Right':
                self.player_coo[0] += 75


        self.Main.Win.PlayerUpdate()

        if self.CheckVictory():
            self.Main.Victory()

        elif self.CheckRedCells()\
        or self.CheckBound():
            self.Main.ResetLevel()

        else:
            self.Main.Win.after(300, self.CellMove)


    def CellMove(self):
        '''Updates the step
        Calls Win to update the Labels and Canvas
        Checks the victory and failure conditions then calls PlayerMove back'''
        self.step += 1
        self.Main.Win.CellUpdate()

        if self.CheckVictory():
            self.Main.Victory()

        elif self.CheckRedCells()\
        or self.CheckMoves():
            self.Main.ResetLevel()

        else:
            self.Main.Win.after(300, self.PlayerMove)

    def CheckBound(self) -> bool:
        '''True if the player position is outside of the canvas'''
        return self.player_coo[0] < 0 or self.player_coo[0] >= 750 or self.player_coo[1] < 0 or self.player_coo[1] >= 375

    def CheckVictory(self) -> bool:
        '''True if the player encountered the victory cell'''
        return self.player_coo == self.victory_cell_coo[self.step-1]

    def CheckRedCells(self) -> bool:
        '''True if the player encountered a red cell'''
        return self.player_coo in [red_cell[self.step-1] for red_cell in self.red_cells]

    def CheckMoves(self) -> bool:
        '''True if the player has reached his last move inputed'''
        return self.step == len(self.Main.Pile)



if __name__ == '__main__':
    Main()
