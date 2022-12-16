from vedo import Mesh
from numpy import array
from numpy.random import random

from Open3dFactory import Open3dFactory
from Open3dVisualizer import Open3dVisualizer


# 1. Create the Factory, bind it to a new Database
factory = Open3dFactory(database_name='mesh',
                        remove_existing=True)

# 2. Add objects to the Factory, then launch the Visualizer
armadillo = Mesh('armadillo.obj')
factory.add_mesh(positions=armadillo.points(),
                 cells=armadillo.cells(),
                 at=0,
                 c='green',
                 alpha=0.8,
                 scalar_field=armadillo.points()[:, 1],
                 wireframe=True)
factory.add_mesh(positions=armadillo.points(),
                 cells=armadillo.cells(),
                 at=1,
                 c='green',
                 wireframe=True)
factory.add_points(positions=armadillo.points(),
                   at=2,
                   c='red',
                   point_size=5,
                   alpha=0.8)
factory.add_arrows(positions=armadillo.points()[0:2],
                   vectors=array([armadillo.normals()[0], armadillo.normals()[1] * 5]),
                   at=2,
                   alpha=0.5)
Open3dVisualizer.launch(database_path=factory.get_path(),
                        offscreen=False,
                        fps=20)

# 3. Run a few steps
dofs = armadillo.points().shape
for step in range(500):
    factory.update_mesh(object_id=0,
                        positions=armadillo.points() + 0.1 * random(dofs))
    factory.update_mesh(object_id=1,
                        positions=armadillo.points() + 0.1 * random(dofs))
    factory.update_points(object_id=2,
                          positions=armadillo.points() + 0.1 * random(dofs))
    factory.render()
factory.close()
