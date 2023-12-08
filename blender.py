import numpy as np
import glm

from material import Material, MaterialLibrary
from mesh import Mesh
from log import Logger

'''
Functions for reading models from blender. 
Reference: 
https://en.wikipedia.org/wiki/Wavefront_.obj_file

The following are limitations for further use:
    - Face format (how many of v/vt/vn are used on each line) must be consistent
      for the whole file (the case for my models).
    - Not all line types are covered (e.g. s, o or l lines aren't covered)
'''

logger = Logger(False, True, True)


class Obj:
    """A class for loading a .obj file."""
    def __init__(self, filename):
        self.filename = filename
        
        # Vertex coordinates, texture coordinates and normal coordinates
        self.vlist = []
        self.vtlist = []
        self.vnlist = []
        
        # Indices for v, vt and vn respectively for each face
        self.flist = []
        self.ftlist = []
        self.fnlist = []
        self.mlist = []
        
        self.lnlist = []
        self.mesh_list = []
        
        self.library = None
                
        self.varray = None
        self.vtarray = None
        self.farray = None
    
    
    def load_obj_file(self):
        '''
        Function for loading a Blender3D object file. minimalistic, and partial,
        but sufficient for this course. You do not really need to worry about it.
        '''
        logger.info(f"Loading mesh(es) from Blender file {self.filename}...")
        
        mesh_id = 0
        
        # current material object
        material = None

        with open(self.filename) as objfile:
            line_num = 0 # count line number for easier error locating

            # loop over all lines in the file
            for line in objfile:
                # Process line and increment line number
                data = Obj.process_line(line)
                line_num += 1

                # Skip empty line
                if data is None:
                    continue

                elif data[0] == 'vertex':
                    self.vlist.append(data[1])

                elif data[0] == 'vertex-texture':
                    self.vtlist.append(data[1])
                
                elif data[0] == "vertex-normal":
                    self.vnlist.append(data[1])

                elif data[0] == 'face':
                    # data[1] means the face data.
                    
                    # How many values provided per face element.
                    # f v1 ... => size = 1
                    # f v1/vt1 ... => size = 2
                    # f v1//vn1 ... => size = 2
                    # f v1/vt1/vn1 ... => size = 3
                    # Any other size is invalid.
                    size = len(data[1][0])
                    
                    if size not in [1, 2, 3]:        
                        logger.error("Expected 1-3 arguments per face, got {size}.\
                                     \n{data[1][0]}")
                    
                    n = len(data[1])               
                    
                    # Attempt to reduce the n-sided face into n-2 triangles
                    # Works for most shapes, but this order of triangles is
                    # not necessarily correct (e.g. non-convex shapes)
                    for i in range(1, n-1):
                        sub_face = [data[1][0], data[1][i], data[1][i+1]]
                        
                        self.ftlist.extend([vert[1] for vert in sub_face])
                        self.fnlist.extend([vert[2] for vert in sub_face])
                        self.flist.append([vert[:-1] for vert in sub_face])
                        
                        self.mesh_list.append(mesh_id)
                        self.mlist.append(material)
                        self.lnlist.append(line_num)
                                                    
                elif data[0] == 'material-lib':
                    self.library = Obj.load_material_library('models/{}'.format(data[1]))

                # material indicate a new mesh in the file, so we store the previous one if not empty and start
                # a new one.
                elif data[0] == 'material':
                    material = self.library.names[data[1]]
                    mesh_id += 1
                    logger.info(f"[{line_num}] Loading mesh with material: {data[1]}")

        logger.info(f"File read. Found {len(self.vlist)} vertices and {len(self.flist)} faces.")

        return self.__create_meshes_from_blender()
    
    
    @staticmethod
    def process_line(line):
        '''
        Function for reading the Blender3D object file, line by line. Clearly
        minimalistic and slow as it is, but it will do the job nicely for this course.
        '''
        label = None
        fields = line.split()
        
        if len(fields) == 0:
            return None
        
        match fields[0]:
            case '#':
                return None
            case 'v':
                label = "vertex"
                if len(fields) != 4:
                    logger.error("3 entries expected for vertex")
                    return None
            case 'vt':
                label = "vertex-texture"
                if len(fields) != 3:
                    if len(fields) == 4 and fields[3] == 0.000:
                        print(fields[3])
                        # Ignore third coordinate as it is 0
                        fields = fields[:-1]
                        print(fields)
                    else:
                        logger.error("2 entries expected for vertex texture")
                        return None
            case 'vn':
                label = "vertex-normal"
                if len(fields) != 4:
                    logger.error("3 entries expected for vertex normal")
                    return None
            case 'f':
                label = 'face'

                # multiple formats for faces lines, eg
                # f 586/1 1860/2 1781/3
                # f vi/ti/ni
                # f vi//ni
                # where vi is the vertex index
                # ti is the texture index
                # ni is the normal index (optional)
                face = []
                for v in fields[1:]:
                    vert = []
                    current_str = ""
                    for char in v:
                        if char != "/":
                            current_str += char
                        else:
                            if current_str == "":
                                vert.append(0)
                            else:
                                vert.append(np.uint32(current_str))
                            current_str = ""
                    
                    # If vt or vn are missing, append zeroes
                    for i in range(3 - len(vert)):
                        vert.append(0)
                    face.append(vert)
                return (label, face)
            case 'mtllib':
                label = "material-lib"
                if len(fields) != 2:
                    logger.error("Material library missing filename")
                    return None
                else:
                    return (label, fields[1])
            case 'usemtl':
                label = "material"
                if len(fields) != 2:
                    logger.error("Material missing filename")
                    return None
                else:
                    return (label, fields[1])
            case 's' 'l' 'o':
                return None
            case _:
                logger.warning(f"Unknown line: {fields}")
                return None

        return (label, [float(token) for token in fields[1:]])

    
    @staticmethod
    def load_material_library(file_name):
        library = MaterialLibrary()
        material = None

        logger.info(f"Loading material library {file_name}...")

        mtllines = []
        with open(file_name) as mtlfile:
            mtllines = mtlfile.readlines()
            
        for line in mtllines:
            fields = line.split()
            
            if len(fields) == 0:
                continue
            
            if fields[0] == '#':
                continue # Comment
                
            val = fields[1]
            
            if len(fields) == 4:
                val = glm.vec3(float(fields[1]), float(fields[2]),
                               float(fields[3]))
            
            if fields[0] == 'newmtl':
                if material is not None:
                    library.add_material(material)

                material = Material(fields[1])
                logger.info(f"Found material definition: {material.name}")
            elif fields[0] == 'Ka':
                material.Ka = val
            elif fields[0] == 'Kd':
                material.Kd = val
            elif fields[0] == 'Ks':
                material.Ks = val
            elif fields[0] == 'Ns':
                material.Ns = float(val)
            elif fields[0] == 'd':
                material.d = float(val)
            elif fields[0] == 'Tr':
                material.d = 1.0 - float(val)
            elif fields[0] == 'illum':
                material.illumination = int(val)
            elif fields[0] == 'map_Kd':
                material.texture = fields[1]
                
                # Material scale parameter - used by the road texture
                # Passed to shaders.
                if material.texture[0:2] == "-s":
                    val = glm.vec3([float(fields[2]), float(fields[3]),
                              float(fields[4])])
                    material.tex_scale = val
                    material.texture = fields[5]
                                                
        library.add_material(material)

        logger.info(f"Finished loading {len(library.materials)} materials")

        return library


    def __create_meshes_from_blender(self):
        fstart = 0
        mesh_id = 1
        meshes = []
            
        # Create np array objects for vlist and (optionally) vtlist
        self.varray = np.array(self.vlist, dtype='f')
        self.vtarray = np.array(self.vtlist, dtype='f')
    
        # Obj has no faces or materials
        if fstart >= len(self.mlist):
            return
        
        material = self.mlist[fstart]
    
        for f in range(len(self.flist)):
            if mesh_id != self.mesh_list[f]:  # new mesh is denoted by change in material
                logger.info(f"Creating new mesh {mesh_id}, faces {fstart}-{f},\
line {self.lnlist[fstart]}, with material {self.mlist[fstart]}:\
{self.library.materials[self.mlist[fstart]].name}")

                try:
                    mesh = self.__create_mesh(fstart, f, material)
                    meshes.append(mesh)
                except:
                    logger.error("Could not load mesh!")
                    raise
    
                mesh_id = self.mesh_list[f]
    
                # start the next mesh
                fstart = f
                material = self.mlist[fstart]
    
        # add the last mesh
        try:
            mesh = self.__create_mesh(fstart, len(self.flist), material)
            meshes.append(mesh)
        except:
            logger.error("Could not load mesh!")
            raise
    
        logger.info(f"Created {len(meshes)} mesh(es) from Blender file.")
        return meshes


    def __create_mesh(self, fstart, findex, material):
        # select faces for this mesh
        self.farray = np.array(self.flist[fstart:findex], dtype=np.uint32)
    
        # and vertices
        vmax = np.max(self.farray[:, :, 0].flatten())
        vmin = np.min(self.farray[:, :, 0].flatten()) - 1
    
        # fix blender texture intexing
        textures = self.__fix_blender_textures()
        if textures is not None:
            textures = textures[vmin:vmax, :]
            
        normal_list = []
        normal_array = None
        
        # If normals are assigned, the first, and every element in fnlist will
        # be non-zero. Just need to check the first element.
        if self.fnlist[0] != 0:
            num_faces = len(self.fnlist) / 3
            if not isinstance(num_faces, int):
                logger.error(f"Number of face normals is incorrect.\n{num_faces * 3}")
            normal_array = np.array(normal_list, dtype="f")
    
        return Mesh(
            vertices=self.varray[vmin:vmax, :],
            faces=self.farray[:, :, 0] - vmin - 1,
            material=self.library.materials[material],
            normals=normal_array,
            textureCoords=textures
        )


    def __fix_blender_textures(self):
        '''
        Corrects the indexing of textures in Blender file for OpenGL.
        Blender allows for multiple indexing of vertices and textures, which is not supported by OpenGL.
        This function ensures that indexing is consistent.
        :param textures: Original Blender texture UV values
        :param faces: Blender faces multiple-index
        :return: a new texture array indexed according to vertices.
        '''
        # (OpenGL, unlike Blender, does not allow for multiple indexing!)
    
        if self.ftlist[0] == 0:
            logger.warning("No texture indices provided, setting texture coordinate array as None")
            return None
    
        # Create an array of size (num_vertices, 2)
        new_textures = np.zeros((self.varray.shape[0], 2), dtype='f')
    
        for f in range(self.farray.shape[0]):
            for j in range(self.farray.shape[1]):
                new_textures[self.farray[f, j, 0] - 1, :] = self.vtarray[self.farray[f, j, 1] - 1, :]
    
        return new_textures
