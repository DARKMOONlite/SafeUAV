from setuptools import find_packages, setup

package_name = 'SafeUAV'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sebastian',
    maintainer_email='Sebastian.Schroder@sperospace.com',
    description='ros 2 wrapper for SafeUAV',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'SafeUAV = SafeUAV.SafeUAV:main'
        ],
    },
)
