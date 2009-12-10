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

import yaml
import types
import os

class DialogueFormatException(Exception):
    """ Exception thrown when the DialogueValidator has encountered an 
    error. """
    pass

class DialogueValidator(object):

    def validateDialogue(self, tree, topdir):
        """ Checks whether a given tree is containing a valid dialogue.
        @type tree
        @param tree
        @type topdir: string
        @param topdir: Top directory where to start searching for files.
        @raises: dialogueFormatException on error
        @return: true on success"""
    
        self.tree = tree 
        self.topdir = topdir
        
        # Test if the required top nodes are present
        for node in ("NPC", "AVATAR", "START"):
            if not node in self.tree or not isinstance(self.tree[node],\
                                                       types.StringType):
                raise DialogueFormatException("Node: " + node + \
                                              " not found or invalid type")
        
        
        self.__validateAvatar()

        # Test if the sections node is present 
        if not "SECTIONS" in self.tree or not isinstance(self.tree["SECTIONS"],\
                                                         types.DictionaryType):
            raise DialogueFormatException("Node: SECTIONS not found or invalid")

        # Start node should be valid 
        if not self.tree["START"] in self.tree["SECTIONS"]:
            raise DialogueFormatException("Main section " + self.tree["START"] \
                                          + " could not be found")

        # Validate all sections
        for section in self.tree["SECTIONS"]:
            self.__validateSection(self.tree["SECTIONS"][section], section)
            
        return True 
    
    def validateDialogueFromFile(self, file_name, topdir="."):
        """ Checks whether a yaml file is containing a valid dialogue 
        @type file_name: string 
        @param file_name: File name of the yaml file to validate
        @type topdir: string
        @param topdir: Top directory where to start searching for files.
        @raises: DialogueFormatException on error
        @return: True on success"""

        tree = yaml.load(file(file_name))
        return self.validateDialogue(tree, topdir)

    def __validateAvatar(self):
        """ Check that the avatar is an existing file. 
        @raises: DialogueFormatException on error. """
        fname = os.path.join(self.topdir,self.tree["AVATAR"])
        if not os.path.isfile(fname):
            raise DialogueFormatException("Avatar file could not " +\
                                          "be found: " + fname)

        
    def __validateSection(self, section, section_name):
        """ Checks whether a section is a valid section.
        @type section: dictionary
        @type section_name: string
        @param section: Section to validate
        @param section_name: Name of the section to validate
        @raises: DialogueFormatException on error """

        for entry in section:
            for action in entry:
                # Verify if the commands are known and if their parameters have
                # the correct type.
                if action == "say":
                    if not isinstance(entry[action], types.StringType):
                        raise DialogueFormatException(
                            "Section: " + section_name + " has an invalid " +\
                            action + " node")
                elif action == "responses":
                    if not isinstance(entry[action], types.ListType):
                        raise DialogueFormatException(                        
                            "Section: " + section_name + " has an invalid " +\
                            action + " node")
                    self.__validateResponses(entry["responses"], section_name)
                elif action == "meet":
                    if not isinstance(entry[action], types.StringType):
                        raise DialogueFormatException(\
                            "Section: " + section_name + " has an invalid " +\
                            action + " node")
                    #TODO: verify person 
                elif action in ("complete_quest", "start_quest", \
                                "delete_quest"):
                    if not isinstance(entry[action], types.StringType):
                        raise DialogueFormatException(\
                            "Section: " + section_name + " has an invalid " +\
                            action + " node")
                    #TODO: verify quest
                elif action in ("get_stuff", "take_stuff"):
                    if not isinstance(entry[action], types.StringType):
                        raise DialogueFormatException(\
                            "Section: " + section_name + " has an invalid " +\
                            action + " node")
                    #TODO: verify object
                elif action in ("increase_value", "decrease_value", \
                                "set_value"):
                    if not isinstance(entry[action], types.DictionaryType):
                        raise DialogueFormatException(\
                            "Section: " + section_name + " has an invalid " +\
                            action + " node")                    
                    #TODO: verify value checks 
                elif action == "dialogue":
                    if not isinstance(entry[action], types.StringType) \
                       or not self.__isValidSectionName(entry[action]):
                        raise DialogueFormatException(\
                            "Section: " + section_name + " has an invalid " +\
                            action + " node")
                else :
                    raise DialogueFormatException("Section: " + section_name + \
                                                  " has an unknown action: " +\
                                                  action)
            

    def __validateResponses(self, responses, section_name):
        """ Checks if the list of responses is a valid list.
        @type responses: List
        @param respones: A list of response
        @type section_name: String
        @param section_name: The section name these responses belong to
        @raise DialogueFormatException on error 
        @return True When the lists is a valid list"""
        
        for option in responses:
            if not isinstance(option[0], types.StringType):
                raise DialogueFormatException("Response should be a string")
            
            if not self.__isValidSectionName(option[1]):
                raise DialogueFormatException("Section: " + section_name + \
                                              " contains an invalid target: " +\
                                              option[1] + " in response")
            
            #TODO: option[2] might be a conditional 
        
    def __isValidSectionName(self, name):
        """ Checks if a given name is valid section
        @type name: string
        @param name: Name of the section to check
        @return True when name is a valid section name, False otherwise"""
        
        if name=="back" or name=="end":
            return True

        if name in self.tree["SECTIONS"]:
            return True;

        # Handle 'back name' used to go back 'n' in the stack.
        if name.startswith("back "):
            return self.__isValidSectionName(name.split(" ")[1])
        
        return False;

