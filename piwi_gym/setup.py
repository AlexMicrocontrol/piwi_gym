from setuptools import setup

setup(
    name='piwi_gym',
    version='0.0.665',
    description='Another Trading Gym',
    author='Alexander Sch.',
    license='GNU General Public License v3.0',
    zip_safe=False,
    install_requires=['gym', 'keras', 'tensorflow',
                      'asyncio', 'numpy',
                      'prettyprinter', 'talib',
                      'dash', 'plotly', 'dash_daq',
                      'dash_html_components','dash_core_components',
                      'pandas', 'sklearn']
)