# This file is part of PARPG.
# 
# PARPG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PARPG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PARPG.  If not, see <http://www.gnu.org/licenses/>.

from scripts.objects.base import GameObject, Container, Carryable
from scripts.objects.composed import CarryableContainer, SingleItemContainer as Slot
import copy

class Inventory(CarryableContainer):
    """The class to represent inventory 'model': allow operations with
    inventory contents, perform weight/bulk calculations, etc"""
    def __init__(self, **kwargs):
        """Initialise instance"""
        CarryableContainer.__init__(self, **kwargs)
        self.items = {"head": Slot(name="head"), "neck": Slot(name="neck"), "shoulders": Slot(name="shoulders"),
                      "chest": Slot(), "abdomen": Slot(), "left_arm": Slot(),
                      "right_arm": Slot(),"groin": Slot(), "hips": Slot(),
                      "left_leg": Slot(), "right_leg": Slot(),
                      "left_hand": Slot(), "right_hand": Slot(),
                      "ready": CarryableContainer(),
                      "backpack": CarryableContainer()}
        for key,item in self.items.iteritems():
            item.name = key
        self.item_lookup = {}

    def placeItem(self,item, index=None):
        self.items["backpack"].placeItem(item, index)
        self.item_lookup[item.ID] = "backpack"


        
    def takeItem(self,item):
        if not item.ID in self.item_lookup:
            raise ValueError ('I do not contain this item: %s' % item)
        self.items[self.item_lookup[item.ID]].takeItem(item)
        self.item_lookup[item.ID] = None

    def getWeight(self):
        """Total weight of all items in container + container's own weight"""
        return sum((item.weight for item in self.items.values()), self.own_weight)

    def setWeightDummy(self, weight):
        pass

    weight = property(getWeight, setWeightDummy, "Total weight of container")


    def count(self):
        return sum(item.count() for item in self.items.values())
    
    def takeOff(self, item):
        return self.moveItemToSlot(item, "backpack")

    def moveItemToSlot(self,item,slot,index=None):
        if not slot in self.items:
            raise(ValueError,"%s: No such slot" % slot)

        if item.ID in self.item_lookup:
            self.items[self.item_lookup[item.ID]].takeItem(item)
        try:
            self.items[slot].placeItem(item, index)
        except ValueError:
            if index == None :
                offending_item = self.items[slot].items[0]
            else :
                offending_item = self.items[slot].items[index]
            self.items[slot].takeItem(offending_item)
            self.items[slot].placeItem(item, index)
            self.placeItem(offending_item)
        self.item_lookup[item.ID] = slot
     
    def getItemsInSlot(self, slot, index=None):
        if not slot in self.items:
            raise(ValueError,"%s: No such slot" % slot)
        if index != None:
            return self.items[slot].items.get(index)
        else:
            return copy.copy(self.items[slot].items)

    def isSlotEmpty(self, slot):
        if not slot in self.items:
            raise(ValueError,"%s: No such slot" % slot)
        return self.items[slot].count() == 0

    def has(self, item):
        return item.ID in self.item_lookup;

    def findItemByID(self, ID):
        if ID not in self.item_lookup:
            return None
        return self.items[self.item_lookup[ID]].findItemByID(ID)

    def findItem(self, **kwargs):
        """Find an item in inventory by various attributes. All parameters are optional.
           @type name: String
           @param name: Unique or non-unique object name. If the name is non-unique, first matching object is returned
           @type kind: String
           @param kind: One of the possible object kinds like "openable" or "weapon" (see base.py)
           @return: The item matching criteria or None if none was found
        """

        for slot in self.items:
            item_found = self.items[slot].findItem(**kwargs)
            if item_found != None:
                return item_found
        return None

    def __repr__(self):
        return "[%s:%s "%(self.name, self.ID)+reduce((lambda a,b: str(a) +', '+str(b)), self.items.values())+" ]"
