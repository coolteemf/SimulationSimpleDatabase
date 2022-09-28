from typing import Dict, Optional, Any
from numpy import array, ndarray, stack, zeros, c_
from vedo import utils
from SSD.Core.Storage.Database import Database


class VedoTable:

    def __init__(self,
                 db: Database,
                 table_name: str):

        # Table information
        self.database = db
        self.table_name = table_name
        self.table_type = table_name.split('_')[0]

        # Select the good method according to the Table type
        create_columns = {'Visual': self.__create_visual_columns,
                          'Mesh': self.__create_mesh_columns,
                          'Points': self.__create_points_columns,
                          'Arrows': self.__create_arrows_columns,
                          'Markers': self.__create_markers_columns,
                          'Symbols': self.__create_symbols_columns}
        format_data = {'Visual': self.__format_visual_data,
                       'Mesh': self.__format_mesh_data,
                       'Points': self.__format_points_data,
                       'Arrows': self.__format_arrows_data,
                       'Markers': self.__format_markers_data,
                       'Symbols': self.__format_symbols_data}
        self.create_columns = create_columns[self.table_type]
        self.format_data = format_data[self.table_type]

    def send_data(self, data_dict: Dict[str, Any], update: bool):

        if update:
            self.database.update(table_name=self.table_name,
                                 data=self.format_data(data_dict=data_dict))
        else:
            self.database.add_data(table_name=self.table_name,
                                   data=self.format_data(data_dict=data_dict))

    ##########################
    # CREATE COLUMNS METHODS #
    ##########################

    def __create_visual_columns(self, visual_table: Optional[str] = None):

        self.database.create_table(table_name=self.table_name,
                                   fields=[('at', int, 0),
                                           ('colormap', str, 'jet')])
        return self

    def __create_mesh_columns(self, visual_table: Optional[str] = None):

        self.database.create_table(table_name=self.table_name,
                                   fields=[('positions', ndarray),
                                           ('cells', ndarray),
                                           ('wireframe', bool),
                                           ('compute_normals', bool),
                                           ('line_width', float),
                                           ('c', str),
                                           ('alpha', float),
                                           ('scalar_field', ndarray),
                                           ('visual_fk', visual_table)])
        return self

    def __create_points_columns(self, visual_table: Optional[str] = None):

        self.database.create_table(table_name=self.table_name,
                                   fields=[('positions', ndarray),
                                           ('point_size', int),
                                           ('c', str),
                                           ('alpha', float),
                                           ('scalar_field', ndarray),
                                           ('visual_fk', visual_table)])
        return self

    def __create_arrows_columns(self, visual_table: Optional[str] = None):

        self.database.create_table(table_name=self.table_name,
                                   fields=[('positions', ndarray),
                                           ('vectors', ndarray),
                                           ('res', int),
                                           ('c', str),
                                           ('alpha', float),
                                           ('scalar_field', ndarray),
                                           ('visual_fk', visual_table)])
        return self

    def __create_markers_columns(self, visual_table: Optional[str] = None):

        self.database.create_table(table_name=self.table_name,
                                   fields=[('normal_to', int),
                                           ('indices', ndarray),
                                           ('symbol', str),
                                           ('size', float),
                                           ('filled', bool),
                                           ('c', str),
                                           ('alpha', float),
                                           ('scalar_field', ndarray),
                                           ('visual_fk', visual_table)])
        return self

    def __create_symbols_columns(self, visual_table: Optional[str] = None):

        self.database.create_table(table_name=self.table_name,
                                   fields=[('positions', ndarray),
                                           ('orientations', ndarray),
                                           ('symbol', str),
                                           ('size', float),
                                           ('filled', bool),
                                           ('c', str),
                                           ('alpha', float),
                                           ('scalar_field', ndarray),
                                           ('visual_fk', visual_table)])
        return self

    #######################
    # FORMAT DATA METHODS #
    #######################

    @classmethod
    def __format_visual_data(cls, data_dict: Dict[str, Any]):

        return data_dict

    @classmethod
    def __format_mesh_data(cls, data_dict: Dict[str, Any]):

        visual_data = {}
        for field in ['at', 'colormap']:
            if field in data_dict:
                visual_data[field] = data_dict.pop(field)

        data_dict_copy = data_dict.copy()
        for field, value in data_dict_copy.items():
            if value is None:
                data_dict.pop(field)
            elif field in ['positions', 'cells', 'scalar_field']:
                data_dict[field] = cls.parse_vector(value, coords=field == 'positions')

        if len(visual_data) != 0:
            data_dict['visual_fk'] = visual_data
        return data_dict

    @classmethod
    def __format_points_data(cls, data_dict: Dict[str, Any]):

        visual_data = {}
        for field in ['at', 'colormap']:
            if field in data_dict:
                visual_data[field] = data_dict.pop(field)

        data_dict_copy = data_dict.copy()
        for field, value in data_dict_copy.items():
            if value is None:
                data_dict.pop(field)
            elif field in ['positions', 'scalar_field']:
                data_dict[field] = cls.parse_vector(value, coords=field == 'positions')

        if len(visual_data) != 0:
            data_dict['visual_fk'] = visual_data
        return data_dict

    @classmethod
    def __format_arrows_data(cls, data_dict: Dict[str, Any]):

        visual_data = {}
        for field in ['at', 'colormap']:
            if field in data_dict:
                visual_data[field] = data_dict.pop(field)

        data_dict_copy = data_dict.copy()
        for field, value in data_dict_copy.items():
            if value is None:
                data_dict.pop(field)
            elif field in ['positions', 'vectors', 'scalar_field']:
                data_dict[field] = cls.parse_vector(value, coords=field in ['positions', 'vectors'])

        if len(visual_data) != 0:
            data_dict['visual_fk'] = visual_data
        return data_dict

    @classmethod
    def __format_markers_data(cls, data_dict: Dict[str, Any]):

        visual_data = {}
        for field in ['at', 'colormap']:
            if field in data_dict:
                visual_data[field] = data_dict.pop(field)

        data_dict_copy = data_dict.copy()
        for field, value in data_dict_copy.items():
            if value is None:
                data_dict.pop(field)
            elif field in ['positions', 'indices', 'scalar_field']:
                data_dict[field] = cls.parse_vector(value, coords=field in ['positions'])

        if len(visual_data) != 0:
            data_dict['visual_fk'] = visual_data
        return data_dict

    @classmethod
    def __format_symbols_data(cls, data_dict: Dict[str, Any]):

        visual_data = {}
        for field in ['at', 'colormap']:
            if field in data_dict:
                visual_data[field] = data_dict.pop(field)

        data_dict_copy = data_dict.copy()
        for field, value in data_dict_copy.items():
            if value is None:
                data_dict.pop(field)
            elif field in ['positions', 'orientations', 'scalar_field']:
                data_dict[field] = cls.parse_vector(value, coords=field in ['positions', 'orientations'])

        if len(visual_data) != 0:
            data_dict['visual_fk'] = visual_data
        return data_dict

    @classmethod
    def parse_vector(cls, vec, coords=True):

        # Ensure sequence format
        if utils.isSequence(vec):
            if len(vec) > 0 and not utils.isSequence(vec[0]):
                vec = [vec]
            vec = array(vec)

            # Coordinates operations
            # if coords:
            #     # Assume vector is in the format [all_x, all_y, all_z]
            #     if len(vec) == 3:
            #         if utils.isSequence(vec[0]) and len(vec[0]) > 3:
            #             vec = stack((vec[0], vec[1], vec[2]), axis=1)
            #     # Assume vector is in the format [all_x, all_y, 0]
            #     elif len(vec) == 2:
            #         vec = stack((vec[0], vec[1], zeros(len(vec[0]))), axis=1)
            #     # Make it 3d
            #     if len(vec) and len(vec[0]) == 2:
            #         vec = c_[array(vec), zeros(len(vec))]
            # print(vec)

        return vec