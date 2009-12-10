#/usr/bin/python

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

import fife
import pychan
from scripts.gui import drag_drop_data as data_drag
from scripts.items import item_image_dict
from pychan.tools import callbackWithArguments as cbwa

class ContainerGUI():
    def __init__(self, engine, title, container):
        """
        A class to create a window showing the contents of a container.
        
        @type engine: fife.Engine
        @param engine: an instance of the fife engine
        @type title: string
        @param title: The title of the window
        @type data: list or string
        @param data: A list of 9 items to use for the slots 1 - 9 
                     OR
                     one item to be used for all the slots
        @return: None
        """
        self.engine = engine
        pychan.init(self.engine, debug=True)
        self.container_gui = pychan.loadXML("gui/container_base.xml")
        self.container_gui.findChild(name="topWindow").title = title
    
        data_drag.dragging = False
        self.original_cursor_id = self.engine.getCursor().getId()
        self.container = container
        
        self.resetMouseCursor()
            
    def updateImage(self, button):
        if (button.item == None):
            image = self.empty_images[button.name]
        else:
            image = button.item.getInventoryThumbnail()
        button.up_image = image
        button.down_image = image
        button.hover_image = image
      
    def showContainer(self):
        """
        Show the container
        @return: None
        """
        # Prepare slots 1 through 9
        empty_image = "gui/inv_images/inv_backpack.png"
        slot_count = 9
        self.empty_images = dict()
        self.events_to_map = {}
        for counter in range(1, slot_count):
            slot_name = "Slot%i" % counter
            self.empty_images[slot_name] = empty_image
            widget = self.container_gui.findChild(name=slot_name)
            widget.item = self.container.items.get(counter-1)
            widget.index = counter-1
            self.updateImage(widget)
            self.events_to_map[slot_name] = cbwa(self.dragDrop, slot_name)

        self.container_gui.mapEvents(self.events_to_map)

        self.container_gui.show()

    def hideContainer(self):
        """
        Hide the container
        @return: None
        """
        if self.container_gui.isVisible():
            self.container_gui.hide()
        
    def setMouseCursor(self, image, dummy_image, mc_type="native"): 
        """Set the mouse cursor to an image.
           @type image: string
           @param image: The image you want to set the cursor to
           @type dummy_image: string
           @param dummy_image: ???
           @type type: string
           @param type: ???
           @return: None"""
        cursor = self.engine.getCursor()
        cursor_type = fife.CURSOR_IMAGE
        img_pool = self.engine.getImagePool()
        if(mc_type == "target"):
            target_cursor_id = img_pool.addResourceFromFile(image)  
            dummy_cursor_id = img_pool.addResourceFromFile(dummy_image)
            cursor.set(cursor_type, dummy_cursor_id)
            cursor.setDrag(cursor_type, target_cursor_id,-16,-16)
        else:
            cursor_type = fife.CURSOR_IMAGE
            zero_cursor_id = img_pool.addResourceFromFile(image)
            cursor.set(cursor_type, zero_cursor_id)
            cursor.setDrag(cursor_type, zero_cursor_id)
            
    def resetMouseCursor(self):
        """Reset cursor to default image.
           @return: None"""
        c = self.engine.getCursor()
        img_pool = self.engine.getImagePool()
        cursor_type = fife.CURSOR_NATIVE
        # this is the path to the default image
        cursor_id = self.original_cursor_id
        c.setDrag(cursor_type, cursor_id)
        c.set(cursor_type, cursor_id)
        
    def dragDrop(self, obj):
        """Decide whether to drag or drop the image.
           @type obj: string
           @param obj: The name of the object within 
                       the dictionary 'self.buttons'
           @return: None"""
        if(data_drag.dragging == True):
            self.dropObject(obj)
        elif(data_drag.dragging == False):
            self.dragObject(obj)
                
    def dragObject(self, obj):
        """Drag the selected object.
           @type obj: string
           @param obj: The name of the object within
                       the dictionary 'self.buttons'
           @return: None"""
        # get the widget from the container_gui with the name obj
        drag_widget = self.container_gui.findChild(name = obj)
        drag_item = drag_widget.item
        # only drag if the widget is not empty
        if (drag_item != None):
            # get the item that the widget is 'storing'
            data_drag.dragged_item = drag_widget.item
            # get the up and down images of the widget
            up_image = drag_widget.up_image
            down_image = drag_widget.down_image
            # set the mouse cursor to be the widget's image
            self.setMouseCursor(up_image.source, down_image.source)
            data_drag.dragged_image = up_image.source
            data_drag.dragging = True
            data_drag.dragged_widget = drag_widget
            data_drag.dragged_container=self.container

            # after dragging the 'item', set the widgets' images
            # so that it has it's default 'empty' images
            drag_widget.item = None
            self.updateImage(drag_widget)
            
    def dropObject(self, obj):
        """Drops the object being dropped
           @type obj: string
           @param obj: The name of the object within
                       the dictionary 'self.buttons' 
           @return: None"""
        drop_widget = self.container_gui.findChild(name = obj)
        if drop_widget != data_drag.dragged_widget:
            data_drag.dragged_container.takeItem(data_drag.dragged_item)
            self.container.placeItem(data_drag.dragged_item, drop_widget.index)
        drop_widget.item = data_drag.dragged_item
        self.updateImage(drop_widget)
        data_drag.dragging = False
        #reset the mouse cursor to the normal cursor
        self.resetMouseCursor()


class ExaminePopup():
    """
    Create a popup for when you click examine on an object
    """
    def __init__(self, engine, object_title, desc):
        """
        Initialize the popup
        
        @type engine: fife.Engine
        @param engine: an instance of the fife engine
        @type object_title: string
        @param object_title: The title for the window, probably should just be
            the name of the object
        @type desc: string
        @param desc: The description of the object
        @return: None
        """
        self.engine = engine
        pychan.init(self.engine, debug=True)

        self.examine_window = pychan.widgets.\
                                Window(title=unicode(object_title),
                                       position_technique="center:center",
                                       min_size=(175,175))

        self.scroll = pychan.widgets.ScrollArea(name='scroll', size=(150,150))
        self.description = pychan.widgets.Label(name='descText',
                                                text=unicode(desc),
                                                wrap_text=True)
        self.description.max_width = 170
        self.scroll.addChild(self.description)
        self.examine_window.addChild(self.scroll)
        
        self.close_button = pychan.widgets.Button(name='closeButton',
                                                  text=unicode('Close'))
        self.examine_window.addChild(self.close_button)

        self.examine_window.mapEvents({'closeButton':self.examine_window.hide})

    def closePopUp(self):
        if self.examine_window.isVisible():
            self.examine_window.hide()
    
    def showPopUp(self):
        self.examine_window.show()
