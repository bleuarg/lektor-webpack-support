from setuptools import setup


tests_require = [
    'lektor',
    'pytest',
    'pytest-cov',
    'pytest-mock',
]

setup(
    name='lektor-frontend-build',
    author='Patrick Davies',
    author_email='me@patrickdavies.ca',
    url='https://github.com/bleuarg/lektor-webpack-support',
    version='0.1.0',
    license='BSD',
    description='Adds support for webpack to Lektor',
    py_modules=['lektor_frontend_build'],
    tests_require=tests_require,
    extras_require={'test': tests_require},
    entry_points={
        'lektor.plugins': [
            'frontend-build-system = lektor_frontend_build:FrontendBuildPlugin',
        ]
    }
)
