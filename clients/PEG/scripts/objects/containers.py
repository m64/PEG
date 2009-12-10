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

"""Containes classes defining concrete container game objects like crates,
barrels, chests, etc."""

__all__ = ["WoodenCrate", "Footlocker"]

_AGENT_STATE_NONE, _AGENT_STATE_OPENED, _AGENT_STATE_CLOSED, _AGENT_STATE_OPENING, _AGENT_STATE_CLOSING = xrange(5)

from composed import ImmovableContainer
from composed import CarryableItem
import fife

class WoodenCrate (ImmovableContainer):
    def __init__ (self, ID, name = 'Wooden Crate', \
            text = 'A battered crate', gfx = 'crate', **kwargs):
        events = {'takeAllButton':self.close,
          'closeButton':self.close}
        ImmovableContainer.__init__(self, ID = ID, name = name, gfx = gfx, \
                text = text, events = events, **kwargs)
        self.placeItem(CarryableItem(ID=987,name="Dagger456"))

    def close(self, *args, **kwargs):
        self.hideContainer()
        super (WoodenCrate,self).close()

    def open(self, *args, **kwargs):
        super (WoodenCrate,self).open(*args,**kwargs)
        self.showContainer()
        
class Footlocker(ImmovableContainer, fife.InstanceActionListener):
    def __init__ (self, ID, agent_layer=None, name = 'Footlocker', \
               text = 'A Footlocker', gfx = 'lock_box_metal01', **kwargs):
        events = {'takeAllButton':self.close,
                  'closeButton':self.close}
        ImmovableContainer.__init__(self, ID = ID, name = name, gfx = gfx, \
                text = text, events = events, **kwargs)
        self.placeItem(CarryableItem(ID=987,name="Dagger456"))

        fife.InstanceActionListener.__init__(self)
        self.layer = agent_layer
        self.agent = self.layer.getInstance(self.ID)
        self.agent.addActionListener(self)
        self.state = _AGENT_STATE_CLOSED
        self.agent.act('closed', self.agent.getLocation())
        
    def onInstanceActionFinished(self, instance, action):
        """What the NPC does when it has finished an action.
           Called by the engine and required for InstanceActionListeners.
           @type instance: fife.Instance
           @param instance: self.agent (the NPC listener is listening for this
            instance)
           @type action: ???
           @param action: ???
           @return: None"""
        if self.state == _AGENT_STATE_OPENING:
            self.agent.act('opened', self.agent.getFacingLocation(), True)
            self.state = _AGENT_STATE_OPENED
            self.showContainer()
        if self.state == _AGENT_STATE_CLOSING:
            self.agent.act('closed', self.agent.getFacingLocation(), True)
            self.state = _AGENT_STATE_CLOSED
        
    def open (self):
        super (Footlocker,self).open()
        if self.state != _AGENT_STATE_OPENED and self.state != _AGENT_STATE_OPENING:
            self.agent.act('open', self.agent.getLocation())
            self.state = _AGENT_STATE_OPENING

    def close(self):
        super (Footlocker,self).close()
        self.hideContainer()
        if self.state != _AGENT_STATE_CLOSED and self.state != _AGENT_STATE_CLOSING:
            self.agent.act('close', self.agent.getLocation())
            self.state = _AGENT_STATE_CLOSING       
