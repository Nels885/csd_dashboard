from dashboard.tests.base import UnitTest

from tools.models import ThermalChamber
from ..utils import thermal_chamber_use


class ApiUtilsTestCase(UnitTest):

    def setUp(self):
        super(ApiUtilsTestCase, self).setUp()
        ThermalChamber.objects.create(operating_mode="FROID", xelon_number="A123456789", created_by=self.user)
        ThermalChamber.objects.create(operating_mode="CHAUD", xelon_number="A987654321", created_by=self.user)

    def test_thermal_chamber_use_hot(self):
        temp = "41°C"
        thermal_chamber_use(temp)
        thermals = ThermalChamber.objects.filter(start_time__isnull=False, stop_time__isnull=True)
        self.assertEqual(len(thermals), 1)
        for thermal in thermals:
            self.assertEqual(thermal.operating_mode, "CHAUD")

        temp = "25°C"
        thermal_chamber_use(temp)
        thermals = ThermalChamber.objects.filter(start_time__isnull=False, stop_time__isnull=False, active=False)
        self.assertEqual(len(thermals), 1)
        for thermal in thermals:
            self.assertEqual(thermal.operating_mode, "CHAUD")

    def test_thermal_chamber_use_freeze(self):
        temp = "-1°C"
        thermal_chamber_use(temp)
        thermals = ThermalChamber.objects.filter(start_time__isnull=False, stop_time__isnull=True)
        self.assertEqual(len(thermals), 1)
        for thermal in thermals:
            self.assertEqual(thermal.operating_mode, "FROID")

        temp = "25°C"
        thermal_chamber_use(temp)
        thermals = ThermalChamber.objects.filter(start_time__isnull=False, stop_time__isnull=False, active=False)
        self.assertEqual(len(thermals), 1)
        for thermal in thermals:
            self.assertEqual(thermal.operating_mode, "FROID")

    def test_thermal_chamber_use_hors_ligne(self):
        temp = "41°C"
        thermal_chamber_use(temp)
        temp = "Hors ligne"
        thermal_chamber_use(temp)
        thermals = ThermalChamber.objects.filter(start_time__isnull=False, stop_time__isnull=False, active=False)
        self.assertEqual(len(thermals), 1)

        temp = "-20°C"
        thermal_chamber_use(temp)
        temp = "Hors ligne"
        thermal_chamber_use(temp)
        thermals = ThermalChamber.objects.filter(start_time__isnull=False, stop_time__isnull=False, active=False)
        self.assertEqual(len(thermals), 2)
