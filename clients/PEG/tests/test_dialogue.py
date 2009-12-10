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

import os
import sys
import unittest
from scripts.dialogue import DialogueEngine
from scripts.dialoguevalidator import DialogueValidator, DialogueFormatException

class TestDialogue(unittest.TestCase):
    def setUp(self):
        self.tree = {
            'NPC': 'Mr. Npc',
            'START': 'main',
            'AVATAR': 'gui/icons/npc.png',
            'SECTIONS': {
                'main': [
                    { "say": "Greetings stranger" },
                    { "responses": [
                        ["Hi, can you tell me where I am?", "friendly"],
                        ["Watch your words", "aggro"],
                        ["This one toggles", "toggles", "show == True"],
                        ["Always display this one", "display", "True and True"],
                        ["response3", "end"],
                    ] }
                ],
                'friendly': [
                    { "say": "You sure are lost" },
                    { "responses": [
                        ["Thanks, I know", "thanks"],
                        ["Wait what did you say before?", "back"],
                    ] }
                ],
                'aggro': [
                    { "say": "Die Pig! PAAAAR!!!!" },
                    { "responses": [
                        ["ruh-ro raggy!", "toggles"],
                        ["Uh, just kidding??", "back"],
                    ] }
                ],
                'toggles': [
                    { "say": "you turn me on!" },
                    { "responses": [
                        ["you turn me off", "back"],
                    ] }
                ],
                'display': [
                    { "say": "Forever Young!" },
                    { "responses": [
                        ["Alphaville sucks!", "back"],
                    ] }
                ],
                'thanks': [
                    { "say": "We haven't seen one of your kind in ages" },
                    { "responses": [
                        ["Blah blah blah", "display"],
                        ["Say the other thing again", "back"],
                    ] }
                ],
            }
        }
        # record actions in test_vars
        test_vars = { "say": None, "responses": [] }

        def sayCb(state, text):
            state["say"] = text

        self.replies = ["resp1", "back", "end"]

        def npcAvatarCb(state, image):
            state['npc_avatar'] = image

        def responsesCb(state, responses):
            state['responses'] = responses

        callbacks = {
            "say": sayCb,
            "responses": responsesCb,
            "npc_avatar": npcAvatarCb
        }

        self.dialogue = DialogueEngine(self.tree, callbacks, test_vars)

    def assertSay(self, text):
        self.assertEqual(text, self.dialogue.state['say'])

    def assertResponses(self, responses):
        self.assertEqual(responses, self.dialogue.state['responses'])

    def assertNpcImage(self, image):
        self.assertEqual(image, self.dialogue.state['npc_avatar'])

    def testSimple(self):
        """Test basic dialogue interaction"""
        self.dialogue.state['show'] = False
        self.dialogue.run()

        self.assertNpcImage('gui/icons/npc.png')
        self.assertSay('Greetings stranger')
        self.assertResponses([
            ["Hi, can you tell me where I am?", "friendly"],
            ["Watch your words", "aggro"],
            ["Always display this one", "display", "True and True"],
            ["response3", "end"],
        ])
        self.dialogue.reply(0)

        self.assertSay('You sure are lost')
        self.assertResponses([
            ["Thanks, I know", "thanks"],
            ["Wait what did you say before?", "back"]
        ])
        self.dialogue.state['show'] = True
        self.dialogue.reply(1)

        self.assertSay('Greetings stranger')
        self.assertResponses([
            ["Hi, can you tell me where I am?", "friendly"],
            ["Watch your words", "aggro"],
            ["This one toggles", "toggles", "show == True"],
            ["Always display this one", "display", "True and True"],
            ["response3", "end"],
        ])
        self.dialogue.reply(0)

        self.assertSay('You sure are lost')
        self.dialogue.reply(1)

        self.assertSay('Greetings stranger')
        self.dialogue.reply(0)

        self.assertSay('You sure are lost')
        self.dialogue.reply(0)

        self.assertSay("We haven't seen one of your kind in ages")
        self.dialogue.reply(1)

        self.assertSay('You sure are lost')
        self.dialogue.reply(1)

        self.assertSay('Greetings stranger')

    def testAllDialogueFiles(self):
        """ Runs the validator on all dialogue files available. """
        
        val = DialogueValidator()
        diag_dir = os.path.join(os.path.curdir, "dialogue");
        num_faulty_files = 0
        
        # Test the dialogue files 
        for dialogue in os.listdir(diag_dir):
            fname = os.path.join(diag_dir, dialogue)
            if os.path.isfile(fname) :
                try:
                    assert(val.validateDialogueFromFile(fname,"."))
                except DialogueFormatException as dfe:
                    print "\nError found in file: ", fname 
                    print "Error was: %s" % (dfe)
                    num_faulty_files += 1
        
        # Test the internal tree 
        try:
            assert(val.validateDialogue(self.tree,"."))
        except DialogueFormatException, dfe:
            print "\nError found in internal tree: ", fname 
            print "Error was: %s" % (dfe)
            num_faulty_files += 1            
        
        assert(num_faulty_files == 0)
  
if __name__ == "__main__":
    unittest.main()
