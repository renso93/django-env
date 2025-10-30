# Fichier de configuration du test runner pour permettre la découverte des tests
# dans le projet et les applications Django.

import os
import sys
from django.test.runner import DiscoverRunner

class ProjectTestRunner(DiscoverRunner):
    """Test runner personnalisé qui assure que les tests sont découverts correctement."""
    def setup_test_environment(self, **kwargs):
        # Assurez-vous que src/ est dans le PYTHONPATH
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root_dir not in sys.path:
            sys.path.append(root_dir)
        super().setup_test_environment(**kwargs)

    def run_tests(self, test_labels, **kwargs):
        """Override run_tests pour fournir des labels par défaut."""
        if not test_labels:
            test_labels = ['blogpost.tests', 'blogpost.tests_api']
        return super().run_tests(test_labels, **kwargs)