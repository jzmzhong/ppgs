from setuptools import setup


with open('README.md') as file:
    long_description = file.read()


setup(
    name='ppgs',
    description='Phonetic posteriorgrams',
    version='0.0.1',
    author='Interactive Audio Lab',
    author_email='interactiveaudiolab@gmail.com',
    url='https://github.com/interactiveaudiolab/ppgs',
    extras_require={
        'train': [
            'apprise',
            'encodec',
            'espnet',
            'g2pM',
            'gdown>=4.6.2',
            'humanfriendly',
            'librosa',
            'nltk',
            'pyyaml',
            'tensorboard',
            'torch_complex',
        ]
    },
    install_requires=[
        'accelerate',
        'deepspeed',
        'moviepy',
        'numpy',
        'pyfoal',
        'pypar',
        'torch',
        'torchaudio',
        'tqdm',
        'transformers',
        'opencv-python',
        'yapecs>=0.0.7',
    ],
    packages=['ppgs'],
    package_data={'ppgs': ['assets/*', 'assets/*/*']},
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['phonemes', 'ppg', 'pronunciation', 'speech'],
    classifiers=['License :: OSI Approved :: MIT License'],
    license='MIT')
