from setuptools import setup, find_packages

setup(
    name="ODB",  # Nombre de tu proyecto
    version="0.1",
    packages=find_packages(include=["app", "app.*"]),  # Ajustamos a la estructura actual
    install_requires=[
        "opencv-python",
        "numpy",
        "flask",
        "pytesseract"
    ],
    entry_points={
        "console_scripts": [
            "start-app = app.main:app.run"  # Este comando ejecutará app/main.py
        ]
    },
    author="Tu Nombre",
    description="Proyecto ODB",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/ODB",  # Cambia esto si tienes un repo
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
