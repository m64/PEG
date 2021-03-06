#!/usr/bin/python

#   This file is part of PARPG.

#   PARPG is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   PARPG is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/>.

import shutil
import fife
import pychan
import pychan.widgets as widgets
from pychan.tools import callbackWithArguments as cbwa
from scripts.gui.filebrowser import FileBrowser
from scripts.gui.context_menu import ContextMenu
from scripts.gui import inventorygui
from scripts.gui.popups import ExaminePopup, ContainerGUI
from scripts.gui.dialoguegui import DialogueGUI

class Hud(object):
    """Main Hud class"""
    def __init__(self, engine, settings, data, callbacks):
        """Initialise the instance.
           @type engine: fife.Engine
           @param engine: An instance of the fife engine
           @type settings: settings.Setting
           @param settings: The settings data
           @type inv_model: dict
           @type callbacks: dict
           @param callbacks: a dict of callbacks
               saveGame: called when the user clicks on Save
               loadGame: called when the user clicks on Load
               quitGame: called when the user clicks on Quit
           @return: None"""
        pychan.init(engine, debug = True)

        # TODO: perhaps this should not be hard-coded here
        self.hud = pychan.loadXML("gui/hud.xml")
        self.engine = engine
        self.settings = settings
        self.data = data
        self.inventory = None
        


        self.save_game_callback = callbacks['saveGame']
        self.load_game_callback = callbacks['loadGame']
        self.quit_callback      = callbacks['quitGame']

        self.box_container = None
        self.examine_box = None

        self.actions_box = self.hud.findChild(name="actionsBox")
        self.actions_text = []
        self.menu_displayed = False
        self.inventory_storage = None
        self.initializeHud()
        self.initializeMainMenu()
        self.initializeContextMenu()
        self.initializeOptionsMenu()
        self.initializeHelpMenu()
        self.initializeEvents()
        self.initializeQuitDialog()

    def initializeHud(self):
        """Initialize and show the main HUD
           @return: None"""
        self.events_to_map = {"menuButton":self.displayMenu,}
        self.hud.mapEvents(self.events_to_map) 
        # set HUD size according to screen size
        screen_width = int(self.settings.readSetting('ScreenWidth'))
        self.hud.findChild(name="mainHudWindow").size = (screen_width, 65)
        self.hud.findChild(name="inventoryButton").position = \
                                                    (screen_width-59, 7)
        # add ready slots
        ready1 = self.hud.findChild(name='hudReady1')
        ready2 = self.hud.findChild(name='hudReady2')
        ready3 = self.hud.findChild(name='hudReady3')
        ready4 = self.hud.findChild(name='hudReady4')
        actions_scroll_area = self.hud.findChild(name='actionsScrollArea')
        if (screen_width <=800) :
            gap = 0
        else :
            gap = 40
        # annoying code that is both essential and boring to enter
        ready1.position = (160+gap, 7)
        ready2.position = (220+gap, 7)
        ready3.position = (screen_width-180-gap, 7)
        ready4.position = (screen_width-120-gap, 7)
        actions_scroll_area.position = (280+gap, 5)
        actions_width = screen_width - 470 - 2*gap

        # and finally add an actions box
        self.hud.findChild(name="actionsBox").min_size = (actions_width, 0)
        actions_scroll_area.min_size = (actions_width, 55)
        actions_scroll_area.max_size = (actions_width, 55)
        # now it should be OK to display it all
        self.hud.show()

    def refreshActionsBox(self):
        """Refresh the actions box so that it displays the contents of
           self.actions_text
           @return: None"""
        self.actions_box.items = self.actions_text

    def addAction(self, action):
        """Add an action to the actions box.
           @type action: string
           @param action: The text that you want to display in the actions box
           @return: None"""
        self.actions_text.insert(0, action)
        self.refreshActionsBox()

    def showHUD(self):
        """Show the HUD.
           @return: None"""
        self.hud.show()

    def hideHUD(self):
        """Hide the HUD.
           @return: None"""
        self.hud.hide()

    def initializeInventory(self):
        inv_callbacks = {
            'refreshReadyImages': self.refreshReadyImages,
            'toggleInventoryButton': self.toggleInventoryButton,
        }
        self.inventory_storage = self.data.game_state.PC.inventory
        if self.inventory == None:
            self.inventory = inventorygui.InventoryGUI(self.engine,
                                                       self.inventory_storage,
                                                       inv_callbacks)
        self.refreshReadyImages()
        

    def initializeContextMenu(self):
        """Initialize the Context Menu
           @return: None"""
        self.context_menu = ContextMenu (self.engine, [], (0,0))
        self.context_menu.hide()

    def showContextMenu(self, data, pos):
        """Display the Context Menu with data at pos
           @type data: list
           @param data: data to pass to context menu
           @type pos: tuple
           @param pos: tuple of x and y coordinates
           @return: None"""
        self.context_menu = ContextMenu(self.engine, data, pos)

    def hideContextMenu(self):
        """Hides the context menu
           @return: None"""
        self.context_menu.hide()

    def initializeMainMenu(self):
        """Initalize the main menu.
           @return: None"""
        self.main_menu = pychan.loadXML("gui/hud_main_menu.xml")
        self.menu_events = {"resumeButton":self.hideMenu, 
                            "optionsButton":self.displayOptions,
                            "helpButton":self.displayHelp}
        self.main_menu.mapEvents(self.menu_events)

    def displayMenu(self):
        """Displays the main in-game menu.
           @return: None"""
        if (self.menu_displayed == False):
            self.main_menu.show()
            self.menu_displayed = True
        elif (self.menu_displayed == True):
            self.hideMenu()

    def hideMenu(self):
        """Hides the main in-game menu.
           @return: None"""
        self.main_menu.hide()
        self.menu_displayed = False


    def initializeHelpMenu(self):
        """Initialize the help menu
           @return: None"""
        self.help_dialog = pychan.loadXML("gui/help.xml")
        help_events = {"closeButton":self.help_dialog.hide}
        self.help_dialog.mapEvents(help_events)
        main_help_text = u"Welcome to Post-Apocalyptic RPG or PARPG![br][br]"\
        "This game is still in development, so please expect for there to be "\
        "bugs and[br]feel free to tell us about them at "\
        "http://www.forums.parpg.net.[br]This game uses a "\
        "\"Point 'N' Click\" interface, which means that to move around,[br]"\
        "just click where you would like to go and your character will move "\
        "there.[br]PARPG also utilizes a context menu. To access this, just "\
        "right click anywhere[br]on the screen and a menu will come up. This "\
        "menu will change depending on[br]what you have clicked on, hence "\
        "it's name \"context menu\".[br][br]"
        
        k_text = u" Keybindings" 
        k_text += "[br] A : Add a test action to the actions display"
        k_text += "[br] I : Toggle the inventory screen"
        k_text += "[br] F5 : Take a screenshot"
        k_text += "[br]      (saves to <parpg>/screenshots/)"
        k_text += "[br] F10 : Toggle console"
        k_text += "[br] PAUSE : (Un)Pause the game"
        k_text += "[br] Q : Quit the game"
        self.help_dialog.distributeInitialData({
                "MainHelpText":main_help_text,
                "KeybindText":k_text
                })

    def displayHelp(self):
        """Display the help screen.
           @return: None"""
        self.help_dialog.show()

    def switchResolutions(self):
        """ Sync the contents of the resolution box (windowed or fullscreen
            resolutions to the selection made in the Fullscreen checkbox.
            @return: None"""
            
        if self.options_menu.collectData('FullscreenBox'):
            self.options_menu.distributeInitialData({
                                'ResolutionBox' : self.resolutions_fullscreen
                                                     })
        else:
            self.options_menu.distributeInitialData({
                                'ResolutionBox' : self.resolutions_windowed
                                                     })
        
    def initializeOptionsMenu(self):
        """Initialize the options menu, this will generate a list of fullscreen
           resolutions and a list of windowed resolutions. Next to this the 
           current active settings are read and also selected in the matching
           widgets.
           @return: None"""
           
        self.options_menu = pychan.loadXML("gui/hud_options.xml")
        self.options_events = {"applyButton":self.applyOptions,
                               "closeButton":self.options_menu.hide,
                               "defaultsButton":self.setToDefaults,
                               "FullscreenBox": self.switchResolutions,
                               "InitialVolumeSlider":self.updateVolumeText}
        
        settings = self.engine.getSettings()
        # The settings need to be set to fullscreen for the call to 
        # getPossibleResolutions() to function.
        current_fullscreen = settings.isFullScreen()
        settings.setFullScreen(True)
        
        available_fullscreen_resolutions = settings.getPossibleResolutions()
        available_windowed_resolutions = ((1920, 1200), (1920, 1080), \
                                          (1856, 1392), (1792, 1344), \
                                          (1680, 1050), (1600, 1200), \
                                          (1600, 1024), (1440,  900), \
                                          (1400, 1050), (1360,  768), \
                                          (1280, 1024), (1280,  960), \
                                          (1152,  864), (1024,  768))
        # Filter too small resolutions from the fullscreen resolutions
        self.resolutions_fullscreen = []
        for x in available_fullscreen_resolutions:
            if x[0] >= 1024 and x[1] >= 768:
                self.resolutions_fullscreen.append(str(x[0]) + 'x' + str(x[1]))

        # Filter too large resolution from the windowed resolutions 
        self.resolutions_windowed = []
        for x in available_windowed_resolutions:
            if x[0] <= available_fullscreen_resolutions[0][0] and \
            x[1] <= available_fullscreen_resolutions[0][1]:
                self.resolutions_windowed.append(str(x[0]) + 'x' + str(x[1]))        
        
        settings.setFullScreen(current_fullscreen)
        self.render_backends = ['OpenGL', 'SDL']
        self.render_number = 0
        if (str(self.settings.readSetting('RenderBackend')) == "SDL"):
            self.render_number = 1
        initial_volume = float(self.settings.readSetting('InitialVolume'))
        initial_volume_text = str('Initial Volume: %.0f%s' %
                                (int(initial_volume*10), "%"))
        initial_data_to_distribute = {    
                'RenderBox'          : self.render_backends,
                'InitialVolumeLabel' : initial_volume_text
                }

        s_fullscreen = self.settings.readSetting(name="FullScreen")
        s_sounds = self.settings.readSetting(name="PlaySounds")
        s_render = self.render_number
        s_volume = initial_volume

        # Find the current active resolution so we can select it 
        screen_width = self.settings.readSetting(name="ScreenWidth")
        screen_height = self.settings.readSetting(name="ScreenHeight")
        index_res = str(screen_width + 'x' + screen_height)
        try:
            if int(s_fullscreen) == 0:
                s_resolution = self.resolutions_windowed.index(index_res)
            else:
                s_resolution = self.resolutions_fullscreen.index(index_res)
            resolution_in_list = True
        except:
            resolution_in_list = False
            
        data_to_distribute = {
                'FullscreenBox'      : int(s_fullscreen), 
                'SoundsBox'          : int(s_sounds),
                'RenderBox'          : s_render,
                'InitialVolumeSlider': s_volume
                }

        if int(s_fullscreen) == 0:
            initial_data_to_distribute['ResolutionBox'] = self.resolutions_windowed
        else:
            initial_data_to_distribute['ResolutionBox'] = self.resolutions_fullscreen
            
        if (resolution_in_list == True):
            data_to_distribute['ResolutionBox'] = s_resolution

        self.options_menu.distributeInitialData(initial_data_to_distribute)
        self.options_menu.distributeData(data_to_distribute)
        self.options_menu.mapEvents(self.options_events)

    def saveGame(self):
        """ Called when the user wants to save the game.
            @return: None"""
        save_browser = FileBrowser(self.engine,
                                   self.save_game_callback,
                                   save_file=True,
                                   gui_xml_path="gui/savebrowser.xml",
                                   extensions = ('.dat'))
        save_browser.showBrowser()
            
    def newGame(self):
        """Called when user request to start a new game.
           @return: None"""
        print 'new game'

    def loadGame(self):
        """ Called when the user wants to load a game.
            @return: None"""
        load_browser = FileBrowser(self.engine,
                                   self.load_game_callback,
                                   save_file=False,
                                   gui_xml_path='gui/loadbrowser.xml',
                                   extensions=('.dat'))
        load_browser.showBrowser()
    
    def initializeQuitDialog(self):
        """Creates the quit confirmation dialog
           @return: None"""
        self.quit_window = pychan.widgets.Window(title=unicode("Quit?"), \
                                                 min_size=(200,0))

        hbox = pychan.widgets.HBox()
        are_you_sure = "Are you sure you want to quit?"
        label = pychan.widgets.Label(text=unicode(are_you_sure))
        yes_button = pychan.widgets.Button(name="yes_button", 
                                           text=unicode("Yes"),
                                           min_size=(90,20),
                                           max_size=(90,20))
        no_button = pychan.widgets.Button(name="no_button",
                                          text=unicode("No"),
                                          min_size=(90,20),
                                          max_size=(90,20))

        self.quit_window.addChild(label)
        hbox.addChild(yes_button)
        hbox.addChild(no_button)
        self.quit_window.addChild(hbox)

        events_to_map = { "yes_button": self.quit_callback,
                          "no_button":  self.quit_window.hide }
        
        self.quit_window.mapEvents(events_to_map)


    def quitGame(self):
        """Called when user requests to quit game.
           @return: None"""

        self.quit_window.show()

    def toggleInventoryButton(self):
        """Manually toggles the inventory button.
           @return: None"""
        button = self.hud.findChild(name="inventoryButton")
        if button.toggled == 0:
            button.toggled = 1
        else:
            button.toggled = 0

    def toggleInventory(self, toggleImage=True):
        """Displays the inventory screen
           @return: None"""
        if self.inventory == None:
            self.initializeInventory()
        self.inventory.toggleInventory(toggleImage)

    def refreshReadyImages(self):
        """Make the Ready slot images on the HUD be the same as those 
           on the inventory
           @return: None"""
        for ready in range(1,5):
            button = self.hud.findChild(name=("hudReady%d" % ready))
            if self.inventory_storage == None :
                origin = None
            else:
               origin = self.inventory_storage.getItemsInSlot('ready', ready-1)
            if origin == None:
                self.setImages(button, self.inventory.slot_empty_images['ready'])
            else:
                self.setImages(button,origin.getInventoryThumbnail())

    def setImages(self, widget, image):
        """Set the up, down, and hover images of an Imagebutton.
           @type widget: pychan.widget
           @param widget: widget to set
           @type image: string
           @param image: image to use
           @return: None"""
        widget.up_image = image
        widget.down_image = image
        widget.hover_image = image

    def initializeEvents(self):
        """Intialize Hud events
           @return: None"""
        events_to_map = {}

        # when we click the toggle button don't change the image
        events_to_map["inventoryButton"] = cbwa(self.toggleInventory, False)
        events_to_map["saveButton"] = self.saveGame
        events_to_map["loadButton"] = self.loadGame

        hud_ready_buttons = ["hudReady1", "hudReady2", \
                             "hudReady3", "hudReady4"]

        for item in hud_ready_buttons:
            events_to_map[item] = cbwa(self.readyAction, item)

        self.hud.mapEvents(events_to_map)

        menu_events = {}
        menu_events["newButton"] = self.newGame
        menu_events["quitButton"] = self.quitGame
        menu_events["saveButton"] = self.saveGame
        menu_events["loadButton"] = self.loadGame
        self.main_menu.mapEvents(menu_events)

    def updateVolumeText(self):
        """
        Update the initial volume label to reflect the value of the slider
        """
        volume = float(self.options_menu.collectData("InitialVolumeSlider"))
        volume_label = self.options_menu.findChild(name="InitialVolumeLabel")
        volume_label.text = unicode("Initial Volume: %.0f%s" %
                                    (int(volume*10), "%"))

    def requireRestartDialog(self):
        """Show a dialog asking the user to restart PARPG in order for their
           changes to take effect.
           @return: None"""
        require_restart_dialog = pychan.loadXML('gui/hud_require_restart.xml')
        require_restart_dialog.mapEvents(\
                                {'okButton':require_restart_dialog.hide})
        require_restart_dialog.show()

    def applyOptions(self):
        """Apply the current options.
           @return: None"""
        # At first no restart is required
        self.require_restart = False

        # get the current values of each setting from the options menu
        enable_fullscreen = self.options_menu.collectData('FullscreenBox')
        enable_sound = self.options_menu.collectData('SoundsBox')
        screen_resolution = self.options_menu.collectData('ResolutionBox')
        if enable_fullscreen:
            partition = self.resolutions_fullscreen[screen_resolution].partition('x')
        else:
            partition = self.resolutions_windowed[screen_resolution].partition('x')
        screen_width = partition[0]
        screen_height = partition[2]
        render_backend = self.options_menu.collectData('RenderBox')
        initial_volume = self.options_menu.collectData('InitialVolumeSlider')
        initial_volume = "%.1f" % initial_volume

        # get the options that are being used right now from settings.xml
        s_fullscreen = self.settings.readSetting('FullScreen')
        s_sounds = self.settings.readSetting('PlaySounds')
        s_render = self.settings.readSetting('RenderBackend')
        s_volume = self.settings.readSetting('InitialVolume')

        s_screen_height = self.settings.readSetting('ScreenHeight')
        s_screen_width = self.settings.readSetting('ScreenWidth')
        s_resolution = s_screen_width + 'x' + s_screen_height

        # On each:
        # - Check to see whether the option within the xml matches the
        #   option within the options menu
        # - If they do not match, set the option within the xml to
        #   to be what is within the options menu
        # - Require a restart

        if (int(enable_fullscreen) != int(s_fullscreen)):
            self.setOption('FullScreen', int(enable_fullscreen))
            self.require_restart = True
            
        if (int(enable_sound) != int(s_sounds)):
            self.setOption('PlaySounds', int(enable_sound))
            self.require_restart = True

        if (screen_resolution != s_resolution):
            self.setOption('ScreenWidth', int(screen_width))
            self.setOption('ScreenHeight', int(screen_height))
            self.require_restart = True

        # Convert the number from the list of render backends to
        # the string that FIFE wants for its settings.xml
        if (render_backend == 0):
            render_backend = 'OpenGL'
        else:
            render_backend = 'SDL'

        if (render_backend != str(s_render)):
            self.setOption('RenderBackend', render_backend)
            self.require_restart = True

        if (initial_volume != float(s_volume)):
            self.setOption('InitialVolume', initial_volume)
            self.require_restart = True
        
        # Write all the settings to settings.xml
        self.settings.tree.write('settings.xml')
        
        # If the changes require a restart, popup the dialog telling
        # the user to do so
        if (self.require_restart):
            self.requireRestartDialog()
        # Once we are done, we close the options menu
        self.options_menu.hide()

    def setOption(self, name, value):
        """Set an option within the xml.
           @type name: string
           @param name: The name of the option within the xml
           @type value: any
           @param value: The value that the option 'name' should be set to
           @return: None"""
        element = self.settings.root_element.find(name)
        if(element != None):
            if(value != element.text):
                element.text = str(value)
        else:
            print 'Setting,', name, 'does not exist!'

    def setToDefaults(self):
        """Reset all the options to the options in settings-dist.xml.
           @return: None"""
        shutil.copyfile('settings-dist.xml', 'settings.xml')
        self.requireRestartDialog()
        self.options_menu.hide()

    def displayOptions(self):
        """Display the options menu.
           @return: None"""
        self.options_menu.show()
    
    def readyAction(self, ready_button):
        """ Called when the user selects a ready button from the HUD """
        text = "Used the item from %s" % ready_button
        self.addAction(text)
        
    def createBoxGUI(self, title, container, events = ()):
        """Creates a window to display the contents of a box
           @type title: string
           @param title: The title for the window
           @param items: The box to display
           @param events: The events of the window
           @return: A new ContainerGui"""
        box_container = ContainerGUI(self.engine, \
                                              unicode(title), container)
        box_container.container_gui.mapEvents(events)
        return box_container

    def hideContainer(self):
        """Hide the container box
           @return: None"""
        if self.box_container:
            self.box_container.hideContainer()

    def createExamineBox(self, title, desc):
        """Create an examine box. It displays some textual description of an
           object
           @type title: string
           @param title: The title of the examine box
           @type desc: string
           @param desc: The main body of the examine box
           @return: None"""

        if self.examine_box is not None:
            self.examine_box.closePopUp()
        self.examine_box = ExaminePopup(self.engine, title, desc)
        self.examine_box.showPopUp()

    def showDialogue(self, npc):
        """Show the NPC dialogue window
           @type npc: actors.NonPlayerCharacter
           @param npc: the npc that we are having a dialogue with
           @return: None"""
        dialogue = DialogueGUI(
                    npc,
                    self.data.game_state.quest_engine,
                    self.data.game_state.PC)
        dialogue.initiateDialogue()
