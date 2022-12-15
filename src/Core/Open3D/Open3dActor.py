from typing import Any, Optional, Dict
import open3d as o3d
from vedo.colors import get_color
from numpy import array, ndarray, asarray, sort, concatenate, unique
from matplotlib.colors import Normalize
from matplotlib.pyplot import get_cmap


class Open3dActor:

    def __init__(self,
                 actor_type: str,
                 actor_name: str,
                 actor_group: int):
        """

        :param actor_type:
        :param actor_name:
        :param actor_group:
        """

        # Actor information
        self.type: str = actor_type
        self.name: str = actor_name
        self.group: str = str(actor_group)
        self.instance: Optional[o3d.geometry.Geometry3D] = None
        self.material = o3d.visualization.rendering.MaterialRecord()

        # Actor data
        self.__object_data: Optional[Dict[str, Any]] = None
        self.__cmap_data: Optional[Dict[str, Any]] = None

        # Actor specialization methods
        create = {'Mesh': self.__create_mesh}
        update = {'Mesh': self.__update_mesh}
        cmap = {'Mesh': self.__cmap_mesh}
        self.__create_object = create[self.type]
        self.__update_object = update[self.type]
        self.__cmap_object = cmap[self.type]

    def create(self,
               object_data: Dict[str, Any]):
        """

        :param object_data:
        """

        # Sort data
        cmap_data = {}
        for field in ['colormap', 'scalar_field']:
            if field in object_data:
                cmap_data[field] = object_data.pop(field)
        # Register Actor data
        self.__object_data = object_data
        self.__cmap_data = cmap_data
        # Create the object
        self.__create_object(self.__object_data)
        # Apply the colormap
        if len(cmap_data.keys()) > 1:
            self.apply_cmap(self.__cmap_data)

    def update(self,
               object_data: Dict[str, Any]):
        """

        :param object_data:
        """

        # Sort data
        cmap_data = {'scalar_field': object_data.pop('scalar_field')} if 'scalar_field' in object_data else {}
        # Register Actor data
        for key, value in object_data.items():
            if value is not None:
                self.__object_data[key] = value
        for key, value in cmap_data.items():
            if value is not None:
                self.__cmap_data[key] = value
        # Update the object
        self.__update_object(self.__object_data)
        # Apply the colormap
        if len(cmap_data.keys()) > 0:
            self.apply_cmap(self.__cmap_data)

    def apply_cmap(self,
                   cmap_data: Dict[str, Any]):
        """

        :param cmap_data:
        """

        scalar_field = cmap_data['scalar_field']
        if len(scalar_field) > 0:
            # Normalize scalar field
            cmap_norm = Normalize(vmin=min(scalar_field[0]),
                                  vmax=max(scalar_field[0]))
            cmap = get_cmap(cmap_data['colormap'])
            vertex_colors = cmap(cmap_norm(scalar_field[0]))[:, 0:3]
            # Apply colors
            self.__cmap_object(vertex_colors)

    ########
    # MESH #
    ########

    def __create_mesh(self,
                      data: Dict[str, Any]):

        # Create the material
        alpha = 1 if not 0. <= data['alpha'] <= 1. else data['alpha']
        color = list(get_color(rgb=data['c']))
        self.material.base_color = array(color + [alpha])
        self.material.shader = 'defaultLitTransparency'

        # Create instance
        if data['wireframe']:
            self.material.line_width = data['line_width']
            self.material.shader = 'unlitLine'
            edges = concatenate([sort(data['cells'][:, col], axis=1) for col in [[0, 1], [1, 2], [2, 0]]])
            edges = unique(edges, axis=0)
            self.instance = o3d.geometry.LineSet(points=o3d.utility.Vector3dVector(data['positions']),
                                                 lines=o3d.utility.Vector2iVector(edges))
        else:
            self.instance = o3d.geometry.TriangleMesh(vertices=o3d.utility.Vector3dVector(data['positions']),
                                                      triangles=o3d.utility.Vector3iVector(data['cells']))
            self.instance.compute_vertex_normals()

    def __update_mesh(self,
                      data: Dict[str, Any]):

        if self.__object_data['wireframe']:
            self.instance.points = o3d.utility.Vector3dVector(data['positions'])
        else:
            self.instance.vertices = o3d.utility.Vector3dVector(data['positions'])

    def __cmap_mesh(self,
                    vertex_colors: ndarray):

        alpha = 1 if not 0. <= self.__object_data['alpha'] <= 1. else self.__object_data['alpha']

        if self.__object_data['wireframe']:
            line_color = vertex_colors[asarray(self.instance.lines)[:, 0]]
            self.instance.colors = o3d.utility.Vector3dVector(line_color)
            self.material.base_color = array([1., 1., 1.] + [alpha])
        else:
            self.instance.vertex_colors = o3d.utility.Vector3dVector(vertex_colors)
            self.material.base_color = array([1., 1., 1.] + [alpha])
