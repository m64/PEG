#!/usr/bin/python

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re 
import os

class Console:
    def __init__(self, app_listener):
        """ 
        Constructor
        @type appListener: ApplicationListener
        @param appListener: ApplicationListener object providing a link with
        the engine, the world and the model"""
        exit_help   = "Terminate application"
        grid_help   = "Toggle grid display"
        run_help    = "Toggle player run/walk"
        help_help   = "Show this help string"
        load_help   = "Usage: load directory file"
        python_help = "Run some python code"
        quit_help   = "Terminate application"
        save_help   = "Usage: save directory file"
        pause_help  = "Pause/Unpause the game"

        self.commands = [
            {"cmd":"exit"  ,"callback":self.handleQuit  ,"help": exit_help},
            {"cmd":"grid"  ,"callback":self.handleGrid  ,"help": grid_help},
            {"cmd":"help"  ,"callback":self.handleHelp  ,"help": help_help},
            {"cmd":"load"  ,"callback":self.handleLoad  ,"help": load_help},
            {"cmd":"pause" ,"callback":self.handlePause ,"help": pause_help},
            {"cmd":"python","callback":self.handlePython,"help": python_help},
            {"cmd":"run"   ,"callback":self.handleRun   ,"help": run_help},
            {"cmd":"save"  ,"callback":self.handleSave  ,"help": save_help},
            {"cmd":"quit"  ,"callback":self.handleQuit  ,"help": quit_help},
        ]
        self.app_listener = app_listener
        self.world = self.app_listener.world 
        self.engine = self.app_listener.model
        self.game_state = self.app_listener.world.data.game_state

    def handleQuit(self, command):
        """ 
        Implements the quit console command 
        @type command: string
        @param command: The command to run
        @return: The resultstring"""
        
        self.app_listener.quitGame()
        return "Terminating ..."

    def handlePause(self, command):
        """
        Implements the pause console command
        @type command: string
        @param command: The command to run
        @return: The resultstring"""
        
        self.world.togglePause()
        return "Game (un)paused"
    
    def handleGrid(self, command):
        """ 
        Implements the grid console command 
        @type command: string
        @param command: The command to run
        @return: The resultstring"""

        self.app_listener.world.active_map.toggleRenderer('GridRenderer')
        return "Grid toggled"

    def handleRun(self, command):
        """
        Toggles run/walk mode of the PC player
        @type command: string
        @param command: The command to run.
        @return: The response"""
        
        if self.app_listener.model.pc_run == 1:
            self.app_listener.model.pc_run = 0
            return "PC is now walking"
        else:
            self.app_listener.model.pc_run = 1
            return "PC is now running"
            

    def handleHelp(self, command):
        """ 
        Implements the help console command 
        @type command: string
        @param command: The command to run
        @return: The resultstring"""

        res=""
        for cmd in self.commands:
            res += "%10s: %s\n" % (cmd["cmd"], cmd["help"])

        return res

    def handlePython(self, command):
        """ 
        Implements the python console command 
        @type command: string
        @param command: The command to run
        @return: The resultstring"""

        result = None
        python_regex = re.compile('^python')
        python_matches = python_regex.match(command.lower())
        if (python_matches is not None):
            end_python = command[python_matches.end() + 1:]
            try:
                result = str(eval(compile(end_python,'<string>','eval')))
            except Exception, e:
                result = str(e)
                
        return result

    def handleLoad(self, command):
        """ 
        Implements the load console command 
        @type command: string
        @param command: The command to run
        @return: The resultstring"""

        result = None
        load_regex = re.compile('^load')
        l_matches = load_regex.match(command.lower())
        if (l_matches is not None):
            end_load = l_matches.end()
            try:
                l_args = command.lower()[end_load + 1:].strip()
                l_path, l_filename = l_args.split(' ')
                self.app_listener.model.load_save = True
                self.app_listener.model.savegame = os.path.join(l_path, l_filename)
                result = "Load triggered"

            except Exception, l_error:
                self.app_listener.engine.getGuiManager().getConsole().println('Error: ' + str(l_error))
                result="Failed to load file"

        return result

    def handleSave(self, command):
        """ 
        Implements the save console command 
        @type command: string
        @param command: The command to run
        @return: The resultstring"""

        save_regex = re.compile('^save')
        s_matches = save_regex.match(command.lower())
        if (s_matches != None):
            end_save = s_matches.end()
            try:
                s_args = command.lower()[end_save+1:].strip()
                s_path, s_filename = s_args.split(' ')
                self.app_listener.model.save(s_path, s_filename)
                result = "Saved to file: " + s_path + s_filename

            except Exception, s_error:
                self.app_listener.engine.getGuiManager().getConsole(). \
                    println('Error: ' + str(s_error))
                result = "Failed to save file"

        return result 


    def handleConsoleCommand(self, command):
        """
        Implements the console logic 
        @type command: string
        @param command: The command to run
        @return: The response string """

        result = None        
        for cmd in self.commands:
            regex = re.compile('^' + cmd["cmd"])
            if regex.match(command.lower()):
                result=cmd["callback"](command)

        if result is None:
            result = "Invalid command, enter help for more information"

        return result 

                  

