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

import time
import fife
import pychan
from sounds import SoundEngine
from datetime import date
from scripts.common.eventlistenerbase import EventListenerBase
from local_loaders.loaders import loadMapFile
from sounds import SoundEngine
from settings import Setting
from scripts.gui import hud
from scripts.gui.popups import *
from pychan.tools import callbackWithArguments as cbwa
from map import Map

TDS = Setting()

# simple sign function
def sign(x):
    if x == 0.0:
        return 0.0
    elif x > 0.0:
        return 1.0
    else:
        return -1.0

# this file should be the meta-file for all FIFE-related code
# engine.py handles is our data model, whilst this is our view
# in order to not replicate data, some of our data model will naturally
# reside on this side of the fence (PC xpos and ypos, for example).
# we should aim to never replicate any data as this leads to maintenance
# issues (and just looks plain bad).
# however, any logic needed to resolve this should sit in engine.py

class World(EventListenerBase):
    """World holds the data needed by fife to render the engine
       The engine keeps a copy of this class"""
    def __init__(self, engine):
        """Constructor for engine
           @type engine: fife.Engine
           @param engine: A fife.Engine instance
           @return: None"""
        super(World, self).__init__(engine, reg_mouse=True, reg_keys=True)
        # self.engine is a fife.Engine object, not an Engine object
        self.engine = engine
        self.event_manager = engine.getEventManager()
        self.quitFunction = None

        # self.data is an engine.Engine object, but is set in run.py
        self.data = None
        self.mouseCallback = None

        # self.map is a Map object, set to none here
        self.active_map = None
        self.maps = {}

        self.action_number = 1

        # init the sound
        self.sounds = SoundEngine(engine)

        # don't force restart if skipping to new section
        if TDS.readSetting("PlaySounds") == "1":
            if not self.sounds.music_init:
                self.sounds.playMusic("/music/preciouswasteland.ogg")

        # The current highlighted object
        self.highlight_obj = None
        
        # Last saved mouse coords
        self.last_mousecoords = None

        # faded objects in top layer
        self.faded_objects = set()

        # current map scroll velocity vector
        self.scroll_vect = [0.0, 0.0]
        # scroll speed - should be moved to settings
        self.scroll_speed = 0.05

    def initHud(self):
        """Initialize the hud member
        @return: None"""

        hud_callbacks = {
            'saveGame': self.saveGame,
            'loadGame': self.loadGame,
            'quitGame': self.quitGame,
        }
        self.hud = hud.Hud(self.engine, TDS, self.data, hud_callbacks)
    
    def quitGame(self):
        """Quits the game
           @return: None"""
        self.quitFunction()

    def saveGame(self, *args, **kwargs):
        """Saves the game state, delegates call to engine.Engine
           @return: None"""
        self.data.save(*args, **kwargs)

    def loadGame(self, *args, **kwargs):
        """Loads the game state, delegates call to engine.Engine
           @return: None"""
        self.data.load(*args, **kwargs)

    def loadMap(self, map_name, filename):
        """Loads a map and stores it under the given name in the maps list.
           @type map_name: String
           @param map_name: The name of the map to load
           @type filename: String
           @param filename: File which contains the map to be loaded
           @return: None"""
        if not map_name in self.maps:
            map = Map(self.engine, self.data)
            self.maps[map_name] = map
            map.load(filename)
        else:
            self.setActiveMap(map_name)

    def setActiveMap(self, map_name):
        """Sets the active map that is to be rendered.
           @type map_name: String
           @param map_name: The name of the map to load
           @return: None"""
        # Turn off the camera on the old map before we turn on the camera
        # on the new map.
        self.active_map.cameras[self.active_map.my_cam_id].setEnabled(False)
        # Make the new map active.
        self.active_map = self.maps[map_name]
        self.active_map.makeActive()

    def displayObjectText(self, obj, text):
        """Display on screen the text of the object over the object.
           @type obj: fife.instance
           @param obj: object to draw over
           @type text: String
           @param text: text to display over object
           @return: None"""
        obj.say(str(text), 1000)

    def keyPressed(self, evt):
        """Whenever a key is pressed, fife calls this routine.
           @type evt: fife.event
           @param evt: The event that fife caught
           @return: None"""
        key = evt.getKey()
        key_val = key.getValue()

        if(key_val == key.Q):
            # we need to quit the game
            self.hud.quitGame()
        if(key_val == key.T):
            self.active_map.toggleRenderer('GridRenderer')
        if(key_val == key.F1):
            # display the help screen and pause the game
            self.hud.displayHelp()
        if(key_val == key.F5):
            self.active_map.toggleRenderer('CoordinateRenderer')
        if(key_val == key.F7):
            # F7 saves a screenshot to fife/clients/parpg/screenshots
            t = "screenshots/screen-%s-%s.png" % \
                    (date.today().strftime('%Y-%m-%d'),\
                    time.strftime('%H-%M-%S'))
            print "PARPG: Saved:",t
            self.engine.getRenderBackend().captureScreen(t)
        if(key_val == key.F10):
            # F10 shows/hides the console
            self.engine.getGuiManager().getConsole().toggleShowHide()
        if(key_val == key.I):
            # I opens and closes the inventory
            self.hud.toggleInventory()
        if(key_val == key.A):
            # A adds a test action to the action box
            # The test actions will follow this format: Action 1,
            # Action 2, etc.
            self.hud.addAction("Action " + str(self.action_number))
            self.action_number += 1
        if(key_val == key.ESCAPE):
            # Escape brings up the main menu
            self.hud.displayMenu()
            # Hide the quit menu
            self.hud.quit_window.hide()
        if(key_val == key.M):
            self.sounds.toggleMusic()
        if(key_val == key.PAUSE):
            # Pause pause/unpause the game 
            self.togglePause()

        # map scrolling
        if key_val == key.UP:
            self.startMapScroll(0, -1)
        if key_val == key.DOWN:
            self.startMapScroll(0, 1)
        if key_val == key.LEFT:
            self.startMapScroll(-1, 0)
        if key_val == key.RIGHT:
            self.startMapScroll(1, 0)

    def keyReleased(self, evt):
        """Whenever a key is pressed, fife calls this routine.
           @type evt: fife.event
           @param evt: The event that fife caught
           @return: None"""
        key = evt.getKey()
        key_val = key.getValue()

        # map scrolling
        if key_val == key.UP:
            self.stopMapScroll(0, -1)
        if key_val == key.DOWN:
            self.stopMapScroll(0, 1)
        if key_val == key.LEFT:
            self.stopMapScroll(-1, 0)
        if key_val == key.RIGHT:
            self.stopMapScroll(1, 0)

    def mouseReleased(self, evt):
        """If a mouse button is released, fife calls this routine.
           We want to wait until the button is released, because otherwise
           pychan captures the release if a menu is opened.
           @type evt: fife.event
           @param evt: The event that fife caught
           @return: None"""
        self.hud.hideContextMenu()
        scr_point = fife.ScreenPoint(evt.getX(), evt.getY())
        if(evt.getButton() == fife.MouseEvent.LEFT):
            self.data.handleMouseClick(self.getCoords(scr_point))
        elif(evt.getButton() == fife.MouseEvent.RIGHT):
            # is there an object here?
            instances = self.active_map.cameras[self.active_map.my_cam_id].\
                            getMatchingInstances(scr_point, \
                                                 self.active_map.agent_layer)
            info = None
            for inst in instances:
                # check to see if this is an active item
                if(self.data.objectActive(inst.getId())):
                    # yes, get the data
                    info = self.data.getItemActions(inst.getId())
                    break

            # take the menu items returned by the engine or show a
            # default menu if no items
            data = info or \
                [["Walk", "Walk here", self.onWalk, self.getCoords(scr_point)]]
            # show the menu
            self.hud.showContextMenu(data, (scr_point.x, scr_point.y))

    def onWalk(self, click):
        """Callback sample for the context menu."""
        self.hud.hideContainer()
        self.data.game_state.PC.run(click)

    def refreshTopLayerInstanceTransparencies(self):
        """Fade or unfade TopLayer instances if the PC is under them."""

        # get the PC's screen coordinates
        camera = self.active_map.cameras[self.active_map.my_cam_id]
        point = self.data.game_state.PC.behaviour.agent.getLocation()
        scr_coords = camera.toScreenCoordinates(point.getMapCoordinates())

        # find all instances on TopLayer that fall on those coordinates
        instances = camera.getMatchingInstances(scr_coords,
                        self.active_map.top_layer)
        instance_ids = [ instance.getId() for instance in instances ]
        faded_objects = self.faded_objects

        # fade instances
        for instance_id in instance_ids:
            if instance_id not in faded_objects:
                faded_objects.add(instance_id)
                instance.get2dGfxVisual().setTransparency(128)

        # unfade previously faded instances
        for instance_id in faded_objects.copy():
            if instance_id not in instance_ids:
                faded_objects.remove(instance_id)
                self.active_map.top_layer.getInstance(instance_id).\
                        get2dGfxVisual().setTransparency(0)

    def teleport(self, position):
        """Called when a door is used that moves a player to a new
           location on the same map. the setting of position may want
           to be created as its own method down the road.
           @type position: String Tuple
           @param position: X,Y coordinates passed from engine.changeMap
           @return: fife.Location
        """
        print position
        coord = fife.DoublePoint3D(float(position[0]), float(position[1]), 0)
        location = fife.Location(self.active_map.agent_layer)
        location.setMapCoordinates(coord)
        self.data.game_state.PC.teleport(location)

    def mouseMoved(self, evt):
        """Called when the mouse is moved
           @type evt: fife.event
           @param evt: The event that fife caught
           @return: None"""
        self.last_mousecoords = fife.ScreenPoint(evt.getX(), evt.getY())
        self.highlightFrontObject()

    def highlightFrontObject(self):
        """Highlights the object that is at the current mouse coordinates"""
        if self.last_mousecoords:
            front_obj = self.getObjectAtCoords(self.last_mousecoords)
            if front_obj != None:
                if self.highlight_obj == None or front_obj.getId() != self.highlight_obj.getId():
                    if self.highlight_obj:
                        self.displayObjectText(self.highlight_obj,"")
                    self.active_map.outline_render.removeAllOutlines()
                    self.highlight_obj = front_obj
                    self.active_map.outline_render.addOutlined(self.highlight_obj, 0, \
                                                               137, 255, 2)
                        # get the text
                    item = self.data.objectActive(self.highlight_obj.getId())
                    if item is not None:
                        self.displayObjectText(self.highlight_obj, item.name)
            else:
                if self.highlight_obj:
                    self.displayObjectText(self.highlight_obj,"")
                self.active_map.outline_render.removeAllOutlines()
                self.highlight_obj = None
                
    def getObjectAtCoords(self, coords):
        """Get the object which is at the given coords
            @type coords: fife.Screenpoint
            @param coords: Coordinates where to check for an object
            @rtype: fife.Object
            @return: An object or None"""
        i=self.active_map.cameras[self.active_map.my_cam_id].\
            getMatchingInstances(coords, self.active_map.agent_layer)
        # no object returns an empty tuple
        if(i != ()):
            front_y = 0
            

            for obj in i:
                # check to see if this in our list at all
                if(self.data.objectActive(obj.getId())):
                    # check if the object is on the foreground
                    obj_map_coords = \
                                      obj.getLocation().getMapCoordinates()
                    obj_screen_coords = self.active_map.\
                        cameras[self.active_map.my_cam_id]\
                        .toScreenCoordinates(obj_map_coords)

                    if obj_screen_coords.y > front_y:
                        #Object on the foreground
                        front_y = obj_screen_coords.y
                        return obj
                    else:
                        return None
        else:
            return None

    def getCoords(self, click):
        """Get the map location x, y coordinates from the screen coordinates
           @type click: fife.ScreenPoint
           @param click: Screen coordinates
           @rtype: fife.Location
           @return: The map coordinates"""
        coord = self.active_map.cameras[self.active_map.my_cam_id].\
                    toMapCoordinates(click, False)
        coord.z = 0
        location = fife.Location(self.active_map.agent_layer)
        location.setMapCoordinates(coord)
        return location

    def togglePause(self):
        """ Pause/Unpause the game.
            @return: nothing"""
        
        self.active_map.togglePause()
    
    def deleteMaps(self):
        """Clear all currently loaded maps from FIFE as well as clear our
            local map cache
            @return: nothing"""
        self.engine.getView().clearCameras()
        self.engine.getModel().deleteMaps()
        self.engine.getModel().deleteObjects()

        self.maps = {}

    def startMapScroll(self, vx, vy):
        # ignore doubled or contrary requests 
        if self.scroll_vect[0] == 0.0:
            self.scroll_vect[0] = sign(vx)*self.scroll_speed

        if self.scroll_vect[1] == 0.0:
            self.scroll_vect[1] = sign(vy)*self.scroll_speed

    def stopMapScroll(self, vx, vy):
        pass
        # ignore contrary requests
        if sign(self.scroll_vect[0]) == sign(vx):
            self.scroll_vect[0] = 0.0

        if sign(self.scroll_vect[1]) == sign(vy):
            self.scroll_vect[1] = 0.0

    def pump(self):
        """Routine called during each frame. Our main loop is in ./run.py"""
        # uncomment to instrument
        # t0 = time.time()
        self.highlightFrontObject()
        self.refreshTopLayerInstanceTransparencies()
        # print "%05f" % (time.time()-t0,)

        # perform map scrolling
        camera = self.active_map.cameras[self.active_map.my_cam_id]
        coords = camera.getLocationRef().getMapCoordinates()
        delta_time = self.engine.getTimeManager().getTimeDelta() 
        coords.x += self.scroll_vect[0]*delta_time
        coords.y += self.scroll_vect[1]*delta_time
        camera.getLocationRef().setMapCoordinates(coords)
        camera.refresh()
