import os
from setuptools import find_packages, setup
from glob import glob

package_name = 'uav'

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            # Tạo đường dẫn đích tương ứng trong thư mục 'share' của ROS 2
            paths.append((os.path.join('share', package_name, path), [os.path.join(path, filename)]))
    return paths

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # THÊM 3 DÒNG NÀY ĐỂ ROS 2 NHẬN DIỆN CÁC FILE MÔ PHỎNG:
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        # (os.path.join('share', package_name, 'models'), glob('models/*')),
        (os.path.join('share', package_name, 'models/arena_map/materials/scripts'), glob('models/arena_map/materials/scripts/*')),
        (os.path.join('share', package_name, 'models/arena_map/materials/textures'), glob('models/arena_map/materials/textures/*')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        # THÊM DÒNG NÀY ĐỂ NHẬN FILE YAML:
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='zunibui',
    maintainer_email='buidungitmo2227@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'takeoff = uav.takeoff:main',
        ],
    },
)
