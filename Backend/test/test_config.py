import os.path
from unittest import TestCase

from Backend.common.config import generate_config
from config.definitions import ROOT_DIR


class ConfigTest(TestCase):
    def test_generate_config(self):
        # Generating config for default config file
        # Prepare
        expected_dir = os.path.join(ROOT_DIR, "upload")
        expected_host = "localhost"
        expected_port = "5310"
        expected_db_name = "ohdsi"
        expected_user_name = "postgres"
        expected_password = "postgres"
        expected_schema = "cds_cdm"

        # Test
        csv_dir, config = generate_config()

        # Assert
        self.assertEqual(csv_dir, expected_dir, "Should extract csv directory from config file.")
        self.assertEqual(config['host'], expected_host, "Should extract correct value")
        self.assertEqual(config['port'], expected_port, "Should extract correct value")
        self.assertEqual(config['db_name'], expected_db_name, "Should extract correct value")
        self.assertEqual(config['username'], expected_user_name, "Should extract correct value")
        self.assertEqual(config['password'], expected_password, "Should extract correct value")
        self.assertEqual(config['db_schema'], expected_schema, "Should extract correct value")
