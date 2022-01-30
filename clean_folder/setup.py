from setuptools import setup, find_packages

setup(
    name='clean_folder',
    version='0.0.1',
    description='Script that sorts files and sub-folders by categories in a selected folder',
    url='https://github.com/Yurii-Shpak/goit-python/tree/main/clean_folder',
    author='Yurii Shpak',
    author_email='yshpak.gora@gmail.com',
    license='MIT',
    packages=find_packages(),
    entry_points={'console_scripts': ['clean-folder = clean_folder.clean:main']}
)