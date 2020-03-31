# manage.py

import unittest
from flask.cli import FlaskGroup
import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

from openpoiservice import create_app, db

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()
cli = FlaskGroup(create_app=create_app)

from openpoiservice.utils import parser

@cli.command()
def test():
    """Runs the unit tests without test coverage."""

    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if not result.wasSuccessful():
        sys.exit(1)
    sys.exit(0)


@cli.command()
def create_db():
    """Creates the db tables."""
    db.create_all()


@cli.command()
def drop_db():
    """Drops the db tables."""
    db.drop_all()

@cli.command()
def import_data():
    """Imports osm pbf data to postgis."""

    osm_files = []
    osm_dir = os.path.join(os.getcwd(), 'osm')

    for dirName, subdirList, fileList in os.walk(osm_dir):
        for fname in fileList:
            if fname.endswith('.osm') or fname.endswith('.pbf') and not dirName.endswith('tests/data'):
                osm_files.append(Path(os.path.join(dirName, fname)))

    if not osm_files:
        logger.error(f"No OSM files found in {osm_dir}")
        exit(1)

    logger.info('Starting to import OSM data from\n\t{}'.format("\n\t".join([str(p.resolve()) for p in osm_files])))
    parser.run_import(osm_files)
    exit(0)


if __name__ == '__main__':
    cli()
