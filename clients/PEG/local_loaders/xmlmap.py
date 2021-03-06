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

# Most of this code was copied from the FIFE file xmlmap.py
# It is part of the local code base now so we can customize what happens
# as we read map files

import fife 
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET

import loaders
from serializers import *
import time

FORMAT = '1.0'

class XMLMapLoader(fife.ResourceLoader):
    def __init__(self, engine, data, callback):
        """ The XMLMapLoader parses the xml map using several section. 
        Each section fires a callback (if given) which can e. g. be
        used to show a progress bar.
        
        The callback sends two values, a string and a float (which shows
        the overall process): callback(string, float)
        
        Inputs:
            engine = FIFE engine
            data = Engine object for PARPG data
            callback = function callback
        """
        fife.ResourceLoader.__init__(self)
        self.thisown = 0
        
        self.callback = callback

        self.engine = engine
        self.data = data
        self.vfs = self.engine.getVFS()
        self.model = self.engine.getModel()
        self.pool = self.engine.getImagePool()
        self.anim_pool = self.engine.getAnimationPool()
        self.map = None
        self.source = None
        self.time_to_load = 0

        self.n_space = None

    def _err(self, msg):
        raise SyntaxError(''.join(['File: ', self.source, ' . ', msg]))

    def loadResource(self, location):
        start_time = time.time()
        self.source = location.getFilename()
        f = self.vfs.open(self.source)
        f.thisown = 1
        tree = ET.parse(f)
        root = tree.getroot()
            
        map = self.parseMap(root)
        self.time_to_load = time.time() - start_time
        return map

    def parseMap(self, map_elt):
        if not map_elt:
            self._err(\
                'No <map> element found at top level of map file definition.')
        id,format = map_elt.get('id'),map_elt.get('format')

        if not format == FORMAT: self._err(''.join(['This file has format ', \
                                            format, \
                                            ' but this loader has format ', \
                                            FORMAT]))
        if not id: self._err('Map declared without an identifier.')

        map = None
        try:
            self.map = self.model.createMap(str(id))
            self.map.setResourceFile(self.source)
        # NameClash appears as general fife.Exception; any ideas?
        except fife.Exception, e: 
            print e.getMessage()
            print ''.join(['File: ', self.source, '. The map ', str(id), \
                           ' already exists! Ignoring map definition.'])
            return None

        # xml-specific directory imports. This is used by xml savers.
        self.map.importDirs = []

        if self.callback is not None:
            self.callback('created map', float(0.25) )

        self.parseImports(map_elt, self.map)
        
        self.parseLayers(map_elt, self.map)    
        
        self.parseCameras(map_elt, self.map)

        return self.map

    def parseImports(self, map_elt, map):
        parsedImports = {}

        if self.callback:        
            tmp_list = map_elt.findall('import')
            i = float(0)
        
        for item in map_elt.findall('import'):
            file = item.get('file')
            if file:
                file = reverse_root_subfile(self.source, file)
            dir = item.get('dir')
            if dir:
                dir = reverse_root_subfile(self.source, dir)

            # Don't parse duplicate imports
            if (dir,file) in parsedImports:
                print "Duplicate import:" ,(dir,file)
                continue
            parsedImports[(dir,file)] = 1

            if file and dir:
                loaders.loadImportFile('/'.join(dir, file), self.engine)
            elif file:
                loaders.loadImportFile(file, self.engine)
            elif dir:
                loaders.loadImportDirRec(dir, self.engine)
                map.importDirs.append(dir)
            else:
                print 'Empty import statement?'
                
            if self.callback:
                i += 1                
                self.callback('loaded imports', \
                              float( i / float(len(tmp_list)) * 0.25 + 0.25 ))


    def parseLayers(self, map_elt, map):
        if self.callback is not None:        
            tmp_list = map_elt.findall('layer')
            i = float(0)

        for layer in map_elt.findall('layer'):
            id = layer.get('id')
            grid_type = layer.get('grid_type')
            x_scale = layer.get('x_scale')
            y_scale = layer.get('y_scale')
            rotation = layer.get('rotation')
            x_offset = layer.get('x_offset')
            y_offset = layer.get('y_offset')
            pathing = layer.get('pathing')
            transparency = layer.get('transparency')

            if not x_scale: x_scale = 1.0
            if not y_scale: y_scale = 1.0
            if not rotation: rotation = 0.0
            if not x_offset: x_offset = 0.0
            if not y_offset: y_offset = 0.0
            if not pathing: pathing = "cell_edges_only"
	    if not transparency:
		    transparency = 0
	    else:
		    transparency = int(transparency)
	    

            if not id: self._err('<layer> declared with no id attribute.')
            if not grid_type: self._err(''.join(['Layer ', str(id), \
                                            ' has no grid_type attribute.']))

            allow_diagonals = pathing == "cell_edges_and_diagonals"
            cell_grid = self.model.getCellGrid(grid_type)
            if not cell_grid: self._err('<layer> declared with invalid '\
                                       'cell grid type. (%s)' % grid_type)

            cell_grid.setRotation(float(rotation))
            cell_grid.setXScale(float(x_scale))
            cell_grid.setYScale(float(y_scale))
            cell_grid.setXShift(float(x_offset))
            cell_grid.setYShift(float(y_offset))

            layer_obj = None
            try:
                layer_obj = map.createLayer(str(id), cell_grid)
            except fife.Exception, e:
                print e.getMessage()
                print 'The layer ' + str(id) + \
                        ' already exists! Ignoring this layer.'
                continue

            strgy = fife.CELL_EDGES_ONLY
            if pathing == "cell_edges_and_diagonals":
                strgy = fife.CELL_EDGES_AND_DIAGONALS
            if pathing == "freeform":
                strgy = fife.FREEFORM
            layer_obj.setPathingStrategy(strgy)

	    layer_obj.setLayerTransparency(transparency)

            self.parseInstances(layer, layer_obj)

            if self.callback is not None:
                i += 1
                self.callback('loaded layer :' + \
                              str(id), float( i / float(len(tmp_list)) * \
                                              0.25 + 0.5 ) )

        # cleanup
        if self.callback is not None:
            del tmp_list
            del i

    def parseInstances(self, layer_elt, layer):
        inst_elt = layer_elt.find('instances')

        instances = inst_elt.findall('i')
        instances.extend(inst_elt.findall('inst'))
        instances.extend(inst_elt.findall('instance'))
        for instance in instances:

            object_id = instance.get('object')
            if not object_id:
                object_id = instance.get('obj')
            if not object_id:
                object_id = instance.get('o')

            if not object_id: self._err('<instance> does not specify an '\
                                        'object attribute.')

            n_space = instance.get('namespace')
            if not n_space:
                n_space = instance.get('ns')
            if not n_space:
                n_space = self.n_space

            if not n_space: self._err('<instance> %s does not specify an '\
                                      'object namespace, and no default is '\
                                      'available.' % str(object_id))

            self.n_space = n_space

            object = self.model.getObject(str(object_id), str(n_space))
            if not object:
                print ''.join(['Object with id=', str(object_id), ' ns=', \
                               str(n_space), \
                               ' could not be found. Omitting...'])
                continue

            x = instance.get('x')
            y = instance.get('y')
            z = instance.get('z')
            stack_pos = instance.get('stackpos')
            id = instance.get('id')

            if x:
                x = float(x)
                self.x = x
            else:
                self.x = self.x + 1
                x = self.x

            if y:
                y = float(y)
                self.y = y
            else:
                y = self.y

            if z:
                z = float(z)
            else:
                z = 0.0

            if not id:
                id = ''
            else:
                id = str(id)

            inst = layer.createInstance(object, \
                                        fife.ExactModelCoordinate(x,y,z), \
                                        str(id))

            if id: inst.setId(id)
            rotation = instance.get('r')
            if not rotation:
                rotation = instance.get('rotation')
            if not rotation:
                angles = object.get2dGfxVisual().getStaticImageAngles()
                if angles:
                    rotation = angles[0]
                else:
                    rotation = 0
            else:
                rotation = int(rotation)
            inst.setRotation(rotation)

            fife.InstanceVisual.create(inst)
            if (stack_pos):
                inst.get2dGfxVisual().setStackPosition(int(stack_pos))

            if (object.getAction('default')):
                target = fife.Location(layer)
                inst.act('default', target, True)
                
            #Check for PARPG specific object attributes
            object_type = instance.get('object_type')
            if object_type:
                inst_dict = {}
                inst_dict["type"] = object_type
                inst_dict["id"] = id
                inst_dict["xpos"] = x
                inst_dict["ypos"] = y
                inst_dict["gfx"] = object_id
                inst_dict["is_open"] = instance.get('is_open')
                inst_dict["locked"] = instance.get('locked')
                inst_dict["name"] = instance.get('name')
                inst_dict["text"] = instance.get('text')
                if instance.get('dialogue'):
                    inst_dict['dialogue'] = instance.get('dialogue')
                inst_dict["target_map_name"] = instance.get('target_map_name')
                inst_dict["target_map"] = instance.get('target_map')
                inst_dict["target_x"] = instance.get('target_x')
                inst_dict["target_y"] = instance.get('target_y')

                self.data.createObject(layer, inst_dict, inst)
                
    def parseCameras(self, map_elt, map):
        if self.callback:        
            tmp_list = map_elt.findall('camera')
            i = float(0)

        for camera in map_elt.findall('camera'):
            id = camera.get('id')
            zoom = camera.get('zoom')
            tilt = camera.get('tilt')
            rotation = camera.get('rotation')
            ref_layer_id = camera.get('ref_layer_id')
            ref_cell_width = camera.get('ref_cell_width')
            ref_cell_height = camera.get('ref_cell_height')
            view_port = camera.get('viewport')

            if not zoom: zoom = 1
            if not tilt: tilt = 0
            if not rotation: rotation = 0

            if not id: self._err('Camera declared without an id.')
            if not ref_layer_id: self._err(''.join(['Camera ', str(id), \
                                                    ' declared with no '\
                                                    'reference layer.']))
            if not (ref_cell_width and ref_cell_height):
                self._err(''.join(['Camera ', str(id), \
                                   ' declared without reference cell '\
                                   'dimensions.']))

            try:
                if view_port:
                    cam = self.engine.getView().addCamera(str(id), \
                                    map.getLayer(str(ref_layer_id)), \
                                    fife.Rect(\
                                    *[int(c) for c in view_port.split(',')]),\
                                    fife.ExactModelCoordinate(0,0,0))
                else:
                    screen = self.engine.getRenderBackend()
                    cam = self.engine.getView().addCamera(str(id), \
                                    map.getLayer(str(ref_layer_id)), \
                                    fife.Rect(0, 0, screen.getScreenWidth(), \
                                              screen.getScreenHeight()), \
                                              fife.ExactModelCoordinate(0, 0,\
                                                                        0))

                cam.setCellImageDimensions(int(ref_cell_width), \
                                           int(ref_cell_height))
                cam.setRotation(float(rotation))
                cam.setTilt(float(tilt))
                cam.setZoom(float(zoom))
            except fife.Exception, e:
                print e.getMessage()
                
            if self.callback:
                i += 1
                self.callback('loaded camera: ' +  str(id), \
                              float( i / len(tmp_list) * 0.25 + 0.75 ) )    
